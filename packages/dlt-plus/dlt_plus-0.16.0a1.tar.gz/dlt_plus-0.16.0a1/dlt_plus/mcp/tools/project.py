"""This module defines functions that will be registered as tools on the MCP server.
The LLM tool definition is derived from the function name, signature, and docstring.
This information should be optimized for LLM readability. Here are important considerations:
- Consistent naming of functions and arguments (e.g., `add_source`,  `add_destination`)
- Mention `dlt` or `dlt+` in the docstring. This helps the LLM understand to use a given tool when
the user asks dlt related questions
- Be brief and efficient. Tool definitions are sent on each LLM call, adding a large number of token
which can significantly inflate costs
- Avoid complex type annotations. They add a lot of tokens and can be confusing to the LLM
- Despite the return type, all tool results are converted to strings by the MCP.
- Instead of raising an excepiton which would halt the MCP server, you can return a string. This
will be read by the LLM and could allow it to self-correct
Importantly, this could clash with mypy requirements
"""
# mypy: disable-error-code="return-value, no-any-return"

import pathlib
from typing import Any, Literal, Optional

import sqlglot
from dlt.common.pipeline import LoadInfo

from mcp.server.fastmcp import Context
from mcp.server.fastmcp.utilities.logging import get_logger

from dlt_plus.project import PipelineManager, Catalog
from dlt_plus.project.cli.write_state import ProjectWriteState
from dlt_plus.project.run_context import ensure_project
from dlt_plus.project.cli import helpers as cli_helpers
from dlt_plus.mcp.tools import helpers
from dlt.cli.init_command import DEFAULT_VERIFIED_SOURCES_REPO
from dlt.cli.echo import suppress_echo, always_choose

logger = get_logger(__name__)


def current_profile() -> str:
    """Get the current dlt profile"""
    run_context = ensure_project()
    return run_context.profile


def add_source(
    source_name: str,
    source_type: str,
    location: str = DEFAULT_VERIFIED_SOURCES_REPO,
    branch: str = None,
    eject_source: bool = False,
    ctx: Context = None,
) -> None:
    """Add a new source or source template to the dlt+ project.
    If specified, the verified sources can be cloned from a custom destination (url or directory)
    params:
        source_name: name of the source
        source_type: type of the source
        location (optional): ADVANCED location of the repository to pull verified sources from, can
            be url or directory
        branch: (optional) ADVANCED branch of the source repository
        eject_source: (optional) ADVANCED if True, code for core-sources (rest-api, filesystem,
            sql-database) will be ejected to the project directory. This allows you to modify the
            source code.
    """
    # TODO use conditional tools once dynamic tool definition is widely supported by client
    if (run_context := ctx.fastmcp.project_context) is None:
        return "No dlt+ project is selected. Use `select_or_create_dlt_project()` first."
    state = ProjectWriteState.from_run_context(run_context)
    with suppress_echo():
        with always_choose(always_choose_default=True, always_choose_value="Y"):
            cli_helpers.add_source(
                state,
                source_name,
                source_type,
                location=location,
                branch=branch,
                eject_source=eject_source,
            )
    state.commit()
    # TODO we don't want to pass secrets to LLMs
    # return run_context.project.config.sources.get(source_name)


def add_destination(destination_name: str, destination_type: str, ctx: Context = None) -> None:
    """Add a new destination to the dlt+ project.

    Returns the destination configuration.
    """
    # TODO use conditional tools once dynamic tool definition is widely supported by client
    if (run_context := ctx.fastmcp.project_context) is None:
        return "No dlt+ project is selected. Use `select_or_create_dlt_project()` first."
    state = ProjectWriteState.from_run_context(run_context)
    cli_helpers.add_destination(state, destination_name, destination_type)
    state.commit()
    # TODO we don't want to pass secrets to LLMs
    # return run_context.project.config.destinations.get(destination_name)


def add_pipeline(
    pipeline_name: str, source_name: str, destination_name: str, ctx: Context = None
) -> None:
    """Add a new pipeline to the dlt+ project.

    Returns the pipeline configuration.
    """
    # TODO use conditional tools once dynamic tool definition is widely supported by client
    if (run_context := ctx.fastmcp.project_context) is None:
        return "No dlt+ project is selected. Use `select_or_create_dlt_project()` first."
    state = ProjectWriteState.from_run_context(run_context)
    cli_helpers.add_pipeline(state, pipeline_name, source_name, destination_name)
    state.commit()
    # TODO we don't want to pass secrets to LLMs
    # return run_context.project.config.pipelines.get(pipeline_name)


# TODO don't pass secrets to LLMs
def get_configuration(
    entity_name: str,
    entity_type: Literal["sources", "destinations", "pipelines", "datasets"],
    ctx: Context = None,
) -> Any:
    """Get the configuration of dlt+ project entity (source, destination, pipeline, dataset)"""
    # TODO use conditional tools once dynamic tool definition is widely supported by client
    if (run_context := ctx.fastmcp.project_context) is None:
        return "No dlt+ project is selected. Use `select_or_create_dlt_project()` first."
    return run_context.project.config.get(entity_type, {}).get(entity_name)


def available_sources(ctx: Context = None) -> dict[str, dict[str, str]]:
    """List all available source types and templates"""
    return {
        "core": cli_helpers.get_available_core_sources(),
        "verified": helpers.get_verified_sources(),
        "templates": cli_helpers.get_available_source_templates(),
    }


def available_destinations() -> list[str]:
    """List all available destination types"""
    return cli_helpers.get_available_destinations()


def available_datasets(ctx: Context = None) -> list[str]:
    """List all available datasets in the project"""
    # TODO use conditional tools once dynamic tool definition is widely supported by client
    if (run_context := ctx.fastmcp.project_context) is None:
        return "No dlt+ project is selected. Use `select_or_create_dlt_project()` first."
    catalog = Catalog(run_context)
    return list(catalog.datasets.keys())


def available_tables(dataset_name: str, ctx: Context = None) -> list[str]:
    """List all available tables in the dataset"""
    # TODO use conditional tools once dynamic tool definition is widely supported by client
    if (run_context := ctx.fastmcp.project_context) is None:
        return "No dlt+ project is selected. Use `select_or_create_dlt_project()` first."
    catalog = Catalog(run_context)
    return catalog[dataset_name].schema.data_table_names()


def run_pipeline_preview(pipeline_name: str, ctx: Context = None) -> LoadInfo:
    """Run a preview of a dlt pipeline.

    This only processes the first 10 rows to assess if the pipeline is working properly.
    """
    # TODO use conditional tools once dynamic tool definition is widely supported by client
    if (run_context := ctx.fastmcp.project_context) is None:
        return "No dlt+ project is selected. Use `select_or_create_dlt_project()` first."
    updated_context = ensure_project(run_context.run_dir, run_context.profile)
    pipeline_manager = PipelineManager(updated_context.project)
    try:
        load_info = pipeline_manager.run_pipeline(pipeline_name, limit=10)
    except Exception as e:
        return e
    return load_info


def table_preview(dataset_name: str, table: str, ctx: Context = None) -> dict[str, Any]:
    """Get the first row from the specified table."""
    # TODO use conditional tools once dynamic tool definition is widely supported by client
    if (run_context := ctx.fastmcp.project_context) is None:
        return "No dlt+ project is selected. Use `select_or_create_dlt_project()` first."
    updated_context = ensure_project(run_context.run_dir, run_context.profile)

    # TODO refactor try/except to specific line or at the tool manager level
    # the inconsistent errors are probably due to database locking
    try:
        catalog = Catalog(updated_context)
        return catalog[dataset_name][table].limit(1).df().to_dict()
    except Exception:
        return (
            "Tool `table_preview()` failed. Verify the `pipeline_name` and the `table_name`. "
            "If the error persist, try starting a new conversation."
        )


def table_schema(dataset_name: str, table_name: str, ctx: Context = None) -> dict[str, Any]:
    """Get the schema of the specified table."""
    from dlt.common.libs.pyarrow import get_py_arrow_datatype
    from dlt.destinations.impl.duckdb.sql_client import DuckDbSqlClient

    # TODO use conditional tools once dynamic tool definition is widely supported by client
    if (run_context := ctx.fastmcp.project_context) is None:
        return "No dlt+ project is selected. Use `select_or_create_dlt_project()` first."

    # TODO refactor try/except to specific line or at the tool manager level
    # the inconsistent errors are probably due to database locking
    try:
        catalog = Catalog(run_context)
        dataset = catalog[dataset_name]
        # get schema and clone the table
        schema = dataset.schema
        table_schema: dict[str, Any] = schema.get_table(table_name)  # type: ignore[assignment]
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
    except Exception:
        return (
            "Tool `table_schema()` failed. Verify the `pipeline_name` and the `table_name`. "
            "If the error persist, try starting a new conversation."
        )


def execute_sql_query(dataset_name: str, sql_query: str, ctx: Context = None) -> str:
    """Executes sql statement and return results as `|` delimited csv.
    Use this tool for simple analysis where the number of rows is
    small ie. below 100. SQL dialect: Use table and column names discovered in
    `available_tables` and `table_schema` tools. Use SQL dialect as indicated in
    `table_schema`. Do not qualify table names with schema names.
    """
    # TODO use conditional tools once dynamic tool definition is widely supported by client
    if (run_context := ctx.fastmcp.project_context) is None:
        return "No dlt+ project is selected. Use `select_or_create_dlt_project()` first."
    catalog = Catalog(run_context)
    dataset = catalog[dataset_name]
    parsed = sqlglot.parse(sql_query)
    if any(
        isinstance(expr, (sqlglot.exp.Insert, sqlglot.exp.Update, sqlglot.exp.Delete))
        for expr in parsed
    ):
        raise ValueError("Data modification statements are not allowed")

    return helpers._return_df(dataset(sql_query).arrow())


__tools__ = (
    current_profile,
    available_sources,
    available_destinations,
    available_datasets,
    available_tables,
    add_source,
    add_destination,
    add_pipeline,
    get_configuration,
    run_pipeline_preview,
    table_preview,
    table_schema,
    execute_sql_query,
)


# TODO refactor these special tools to somewhere else;
# stateful_tools.py? internal_tools.py? or tools.__init__.py?
# special stateful tools with access to the MCP server
def select_or_create_dlt_project(
    project_dir: str, name: Optional[str] = None, ctx: Context = None
) -> None:
    """Select an existing dlt+ project or create a new one.

    Use only if the user requests it. Don't ask before each command.
    """
    project_context = None
    if pathlib.Path(project_dir).exists():
        try:
            project_context = ensure_project(run_dir=project_dir)
        except Exception:
            pass

    if project_context is None:
        try:
            pathlib.Path(project_dir).mkdir(parents=True, exist_ok=True)
        except Exception:
            return "Failed to created directory `project_dir`"
        project_context, state = cli_helpers.init_project(project_dir, name)
        state.commit()

    if ctx is not None:
        ctx.fastmcp.project_context = project_context
        # TODO add back when the feature is properly working
        # ref: https://github.com/modelcontextprotocol/python-sdk/issues/215
        #     current_tools = [t.name for t in ctx.fastmcp._tool_manager.list_tools()]
        #     for tool in __tools__:
        #         if tool.__name__ not in current_tools:
        #             ctx.fastmcp.add_tool(tool)
        # await ctx.session.send_notification(
        #   ToolListChangedNotification(method="notifications/tools/list_changed")
        # )
