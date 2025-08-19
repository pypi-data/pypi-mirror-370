import os
import re
from typing import Any, List, Dict, NamedTuple, Optional, Callable, cast
import tempfile
from abc import ABC, abstractmethod

import sqlglot
import unicodedata

import pyarrow as pa  # type: ignore[import-untyped]
import pandas as pd  # type: ignore[import-untyped]
import numpy as np
import pyarrow.parquet as pq  # type: ignore[import-untyped]
from mcp.server.fastmcp import FastMCP
from mcp.server.fastmcp.server import AnyUrl
from mcp.server.fastmcp.resources import FunctionResource

from dlt import Pipeline
from dlt.common.schema.utils import is_valid_schema_name
from dlt.common.libs.pandas import pandas_to_arrow
from dlt.destinations.dataset.dataset import ReadableDBAPIDataset

from dlt_plus.project import Catalog, ProjectRunContext


# TODO: use our transformations (local) cache so we can store large data
class CacheEntry(NamedTuple):
    result: pa.Table
    query: str
    input_cache_entry: Optional[str]


class BaseMCPTools(ABC):
    RECENT_CACHE_KEY = "_recent"

    def __init__(self) -> None:
        self.result_cache: Dict[str, CacheEntry] = {}
        self._recent_count = 0

    @abstractmethod
    def register_with(self, mcp_server: FastMCP) -> None:
        """Register tools with the MCP server."""
        pass

    def register_resource(
        self,
        mcp_server: FastMCP,
        fn: Callable[[], Any],
        uri: str,
        name: str,
        description: str,
        mime_type: str,
    ) -> None:
        resource = FunctionResource(
            uri=AnyUrl(uri),
            name=name,
            description=description,
            mime_type=mime_type,
            fn=fn,
        )
        mcp_server.add_resource(resource)

    def register_resource_template(
        self,
        mcp_server: FastMCP,
        fn: Callable[..., Any],
        uri_template: str,
        name: str,
        description: str,
        mime_type: str,
    ) -> None:
        mcp_server._resource_manager.add_template(fn, uri_template, name, description, mime_type)

    def recent_result_resource(self) -> str:
        return self._return_from_cache(self.RECENT_CACHE_KEY)

    def bookmark_resource(self, bookmark: str) -> str:
        return self._return_from_cache(bookmark)

    def _make_table_schema(self, dataset: ReadableDBAPIDataset, table_name: str) -> Dict[str, Any]:
        """
        Construct and return a normalized table schema dictionary for the specified table.
        """
        from dlt.common.libs.pyarrow import get_py_arrow_datatype
        from dlt.destinations.impl.duckdb.sql_client import DuckDbSqlClient

        # get schema and clone the table
        schema = dataset.schema
        table_schema: Dict[str, Any] = schema.get_table(table_name)  # type: ignore[assignment]
        # add sql dialect which is destination type
        if isinstance(dataset.sql_client, DuckDbSqlClient):
            dialect = "duckdb"
        else:
            assert dataset._destination is not None
            dialect = dataset._destination.destination_type
        table_schema["sql_dialect"] = dialect
        # normalize names
        table_schema["normalized_name"] = dataset.sql_client.escape_column_name(
            schema.naming.normalize_tables_path(table_schema["name"])
        )
        for col_schema in table_schema["columns"].values():
            col_schema["normalized_name"] = dataset.sql_client.escape_column_name(
                schema.naming.normalize_tables_path(col_schema["name"])
            )
            col_schema["arrow_data_type"] = str(
                get_py_arrow_datatype(col_schema, dataset.sql_client.capabilities, "UTC")
            )
        stored_schema = schema.to_dict(remove_defaults=True, bump_version=False)
        return stored_schema["tables"][table_name]  # type: ignore[return-value]

    def _execute_sql(
        self,
        dataset: ReadableDBAPIDataset,
        sql: str,
        bookmark: Optional[str] = None,
    ) -> str:
        # use sqlglot to parse. reject any MDL statement you can find
        parsed = sqlglot.parse(sql)
        if any(
            isinstance(expr, (sqlglot.exp.Insert, sqlglot.exp.Update, sqlglot.exp.Delete))
            for expr in parsed
        ):
            raise ValueError("Data modification statements are not allowed")

        table = dataset(sql).arrow()
        return self._return_or_cache(table, sql, bookmark)

    def _return_or_cache(
        self,
        table: pa.Table,
        query: Optional[str] = None,
        save_bookmark: Optional[str] = None,
        input_bookmark: Optional[str] = None,
    ) -> str:
        info = self._cache_arrow(
            table, query, self.RECENT_CACHE_KEY, input_bookmark
        )  # cache last result
        if save_bookmark:
            return self._cache_arrow(table, query, save_bookmark, input_bookmark)
        else:
            return self._return_df(table, info)

    def _return_df(self, table: pa.Table, info: str = "") -> str:
        # just copy metadata
        df = table.to_pandas().copy(deep=False)

        # Remove non ascii characters from the columns. Those hang claude desktop - server
        # at least on Windows
        for col in df.select_dtypes(include=["object"]).columns:
            df[col] = df[col].apply(
                lambda x: unicodedata.normalize("NFKD", str(x))
                .encode("ascii", "ignore")
                .decode("ascii")
                .replace("\n", " ")
                .replace("\r", " ")
            )
        if info:
            info += "csv delimited with | containing header starts in next line:\n"
        return str(info + df.to_csv(index=False, sep="|"))

    def _cache_arrow(
        self,
        table: pa.Table,
        query: Optional[str] = None,
        save_bookmark: Optional[str] = None,
        input_bookmark: Optional[str] = None,
    ) -> str:
        # info = ""
        if not is_valid_schema_name(save_bookmark):
            raise ValueError(
                f"Invalid bookmark name: {save_bookmark}. Only strings that are valid Python "
                "identifiers are accepted."
            )
        info = f"Result with {len(table)} row(s) bookmarked under {save_bookmark}\n"
        self.result_cache[save_bookmark] = CacheEntry(table, query, input_bookmark)
        # write bookmark as pq, this is EXEPRIMENTAL to see if exposing data frames directly
        # makes sense
        if save_bookmark == self.RECENT_CACHE_KEY:
            # do not overwrite recents
            self._recent_count += 1
            save_bookmark = save_bookmark + f".{self._recent_count}"

        pq_file = os.path.join(tempfile.gettempdir(), save_bookmark + ".parquet")
        pq.write_table(table, pq_file)
        info += f"Result is also available as parquet file in {pq_file}\n"

        return info

    def _return_from_cache(self, cache_url: str) -> str:
        if not (cache_entry := self.result_cache.get(cache_url)):
            raise ValueError(f"{cache_url} bookmark not found")
        return self._return_df(cache_entry.result)


class PipelineMCPTools(BaseMCPTools):
    def __init__(self, pipeline: Pipeline):
        super().__init__()
        self.pipeline = pipeline

    def register_with(self, mcp_server: FastMCP) -> None:
        pipeline_name = self.pipeline.pipeline_name
        mcp_server.add_tool(
            self.available_tables,
            name=f"available_tables_in_{pipeline_name}",
            description=f"All available tables in the pipeline {pipeline_name}",
        )
        mcp_server.add_tool(
            self.table_head,
            name=f"table_head_in_pipeline_{pipeline_name}",
            description=f"Get the first 10 rows of the table in the pipeline {pipeline_name}",
        )
        mcp_server.add_tool(
            self.table_schema,
            name=f"table_schema_in_pipeline_{pipeline_name}",
            description=f"Get the schema of the table in the pipeline {pipeline_name}",
        )
        mcp_server.add_tool(
            self.query_sql,
            name=f"query_sql_in_pipeline_{pipeline_name}",
            description=(
                f"Executes sql statement on a given pipeline {pipeline_name} as returns the result "
                "as | delimited csv. Use this tool for simple analysis where the number of rows is "
                "small ie. below 100. SQL dialect: Use table and column names discovered in "
                "`available_tables` and `table_schema` tools. Use SQL dialect as indicated in "
                "`table_schema`. Do not qualify table names with schema names."
            ),
        )
        mcp_server.add_tool(
            self.bookmark_sql,
            name=f"bookmark_sql_in_pipeline_{pipeline_name}",
            description=(
                f"Executes sql statement on a pipeline {pipeline_name} and bookmarks it under "
                "given bookmark for further processing. Use this tool when you need to select "
                "and transform a large result or when you want to reuse results of the query. "
            ),
        )

    def available_tables(self) -> Dict[str, Any]:
        return {
            "schemas": {
                schema_name: [table["name"] for table in schema.data_tables()]
                for schema_name, schema in self.pipeline.schemas.items()
            }
        }

    def table_head(self, table_name: str) -> pd.DataFrame:
        return self.pipeline.dataset()[table_name].head(10).df()

    def table_schema(self, table: str) -> Dict[str, Any]:
        return self._make_table_schema(cast(ReadableDBAPIDataset, self.pipeline.dataset()), table)

    def query_sql(self, sql: str) -> str:
        return self._execute_sql(cast(ReadableDBAPIDataset, self.pipeline.dataset()), sql)

    def bookmark_sql(self, sql: str, bookmark: str) -> str:
        return self._execute_sql(cast(ReadableDBAPIDataset, self.pipeline.dataset()), sql, bookmark)


class ProjectMCPTools(BaseMCPTools):
    def __init__(self, run_context: ProjectRunContext):
        super().__init__()
        self.run_context = run_context
        self.catalog = Catalog(run_context)

    def register_with(self, mcp_server: FastMCP) -> None:
        mcp_server.add_tool(
            self.get_profile,
            name="get_profile",
            description="Get the current profile",
        )
        mcp_server.add_tool(
            self.available_datasets,
            name="available_datasets",
            description="List all available datasets in the project",
        )
        mcp_server.add_tool(
            self.available_tables,
            name="available_tables",
            description="List all available tables in the dataset",
        )
        mcp_server.add_tool(
            self.table_head,
            name="table_head",
            description="Print first 10 rows in the table",
        )
        mcp_server.add_tool(
            self.table_schema,
            name="table_schema",
            description="Get the schema of the table",
        )
        mcp_server.add_tool(
            self.query_sql,
            name="query_sql",
            description=(
                "Executes sql statement on a given dataset as returns the result as | delimited "
                "csv. Use this tool for simple analysis where the number of rows is small i.e. "
                "below 100. SQL dialect: Use table and column names discovered in "
                "`available_tables` and `table_schema` tools. Use SQL dialect as indicated in "
                "`table_schema`. Do not qualify table names with schema names. "
            ),
        )
        mcp_server.add_tool(
            self.bookmark_sql,
            name="bookmark_sql",
            description=(
                "Executes sql statement on a given dataset and bookmarks it under given bookmark "
                "for further processing. Use this tool when you need to select and transform "
                "a large result or when you want to reuse results of the query. "
                "To obtain full result use `read_result_from_bookmark` or `recent_result` tools. "
                "You transform the result using `transform_bookmark_and_return` tool. "
                "SQL dialect: Use table and column names discovered in `available_tables` and "
                "`table_schema` tools. Use SQL dialect as indicated in `table_schema`. Do not "
                "qualify table names with schema names. "
            ),
        )
        mcp_server.add_tool(
            self.read_result_from_bookmark,
            name="read_result_from_bookmark",
            description="Read the result of the bookmark and return it as '|' delimited CSV",
        )
        mcp_server.add_tool(
            self.recent_result,
            name="recent_result",
            description="Read the most recent result and return it as '|' delimited CSV",
        )
        mcp_server.add_tool(
            self.transform_bookmark_and_return,
            name="transform_bookmark_and_return",
            description=(
                "READ THIS VERY CAREFULLY OTHERWISE YOU WILL NOT BE ABLE TO USE THIS TOOL.\n\n"
                "Transforms result under bookmark `bookmark` with Python script `python_script` "
                "which is compiled and evaluated. If bookmark is not specified, the most recent "
                "result is used. This script receives bookmark as DataFrame, transforms it and "
                "returns modified DataFrame which we return from the functions as CSV.\n\n"
                "In script in `python_script`, `df` is a Pandas DataFrame created from bookmark. "
                "You can directly manipulate `df` using Pandas operations. Examples:\n\n"
                "Filter rows where 'age' is greater than 30:\n"
                "```\n"
                "df = df[df['age'] > 30]\n"
                "```\n\n"
                "# Add a new column 'age_group' classifying rows based on the 'age':\n"
                "```\n"
                "df['age_group'] = df['age'].apply(lambda x: 'Senior' if x > 60 else 'Adult')\n"
                "```\n\n"
                "# Rename columns:\n"
                "```\n"
                "df = df.rename(columns={'first_name': 'fname', 'last_name': 'lname'})\n"
                "```\n\n"
                "After the script finishes, `df` will be returned with these transformations "
                "applied as | delimited CSV. NEVER use return at the end of your script. "
                "Assign results back to df! Do not use print statements. Avoid defining functions. "
                "Do not save any files - they won't be visible."
            ),
        )
        self.register_resource(
            mcp_server,
            fn=self.recent_result_resource,
            uri="bookmark://" + self.RECENT_CACHE_KEY,
            name="recent_result",
            description="Result returned by most recently used tool",
            mime_type="text/csv",
        )

        self.register_resource_template(
            mcp_server,
            fn=self.bookmark_resource,
            uri_template="bookmark://{bookmark}",
            name="bookmark",
            description="Result stored under bookmark as | delimited csv",
            mime_type="text/csv",
        )

    def get_profile(self) -> str:
        return "Current profile is: " + self.run_context.profile

    def available_datasets(self) -> List[str]:
        return list(self.catalog.datasets)

    def available_tables(self, dataset: str) -> List[str]:
        return self.catalog[dataset].schema.data_table_names()

    def table_head(self, dataset: str, table: str) -> Any:
        return self.catalog[dataset][table].head(10).df()

    def table_schema(self, dataset_name: str, table_name: str) -> Dict[str, Any]:
        dataset = self.catalog[dataset_name]
        return self._make_table_schema(dataset, table_name)

    def query_sql(self, dataset_name: str, sql: str) -> str:
        dataset = self.catalog[dataset_name]
        return self._execute_sql(dataset, sql)

    def bookmark_sql(self, dataset_name: str, sql: str, bookmark: str) -> str:
        dataset = self.catalog[dataset_name]
        return self._execute_sql(dataset, sql, bookmark)

    def transform_bookmark_and_return(
        self, python_script: str, bookmark: Optional[str] = None
    ) -> str:
        if not (cache_entry := self.result_cache.get(bookmark or self.RECENT_CACHE_KEY)):
            raise ValueError(f"{bookmark} bookmark not found")
        df = cache_entry.result.to_pandas()

        # TODO: parse AST and use visitor
        if "return df" in python_script:
            raise ValueError(
                "Do not return anything from the script. Read the tool description again."
            )
        if "print(" in python_script:
            raise ValueError("Do not print in the script. It is executed remotely.")

        # Create isolated namespaces for execution
        # NOTE: if script contains import that import a module that is not yet imported
        #    server unfortunately disconnects
        local_dict = {"df": df}
        global_dict = {
            "__builtins__": __builtins__,  # consider restricting builtins if necessary
            "pd": pd,
            "np": np,
            "re": re,
            "unicodedata": unicodedata,
            "result_cache": self.result_cache,
            "pa": pa,
        }

        # Compile and execute the script
        code = compile(python_script, "<string>", "exec")
        exec(code, global_dict, local_dict)

        # After execution, `df` should now be transformed
        if "df" not in local_dict:
            raise ValueError("The script did not produce a transformed DataFrame named df.")

        df = local_dict["df"]
        # NOTE: removed from function arguments, was too complicated for LLMs
        save_bookmark: Optional[str] = None
        return self._return_or_cache(
            pandas_to_arrow(df, preserve_index=True), python_script, save_bookmark, bookmark
        )

    def read_result_from_bookmark(self, bookmark: str) -> str:
        return self._return_from_cache(bookmark)

    def recent_result(self) -> str:
        return self._return_from_cache(self.RECENT_CACHE_KEY)
