import os
import pathlib
from typing import Optional

from mcp.server.fastmcp import FastMCP
from mcp.server.fastmcp.prompts.base import Prompt
from mcp.server.fastmcp.utilities.logging import get_logger

from dlt_plus.project.run_context import ProjectRunContext, switch_context
from dlt_plus.project.exceptions import ProjectRunContextNotAvailable
from dlt_plus.mcp import tools
from dlt_plus.mcp import prompts
from dlt_plus.mcp import resources

logger = get_logger(__name__)


class DltMCP(FastMCP):
    def __init__(self, project_mode: bool = False, sse_port: int = 8000) -> None:
        super().__init__(
            name="dlt+",
            dependencies=["dlt-plus", "dlt"],
            log_level="WARNING",  # do not send INFO logs because some clients HANG
            port=sse_port,
        )
        self.project_mode = project_mode
        self._cwd_at_init: pathlib.Path = pathlib.Path.cwd()
        self._project_context: Optional[ProjectRunContext] = None

        if self.project_mode:
            self._infer_project_dir()
            self._register_dlt_plus_features()
        else:
            self._register_dlt_features()

    @property
    def project_context(self) -> Optional[ProjectRunContext]:
        """Reference to the dlt+ project.

        This value is set on the `FastMCP` server instance is available to tools
        via the special `ctx: Context` kwarg. This allows to define stateless tool
        functions while avoiding to specify the project directory for each tool call.
        """
        return self._project_context

    @project_context.setter
    def project_context(self, value: ProjectRunContext) -> None:
        """This setter changes the MCP server process's current working directory.

        This special behavior is only used by the tool `select_or_create_dlt_project()`.
        It allows an MCP instance launched outside of dlt project directory / context
        (e.g., MCP server launched by the IDE over stdio) to be moved to the relevant
        dlt project.
        """
        if not isinstance(value, ProjectRunContext):
            raise TypeError(
                "`DltMCP.project_context` can only be set to a `ProjectRunContext`."
                f" Received object of type `{type(value)}`"
            )

        self._project_context = value
        # TODO when using stdio, there's a way to set cwd at __init__
        # could be use project path is specified `dlt mcp run --project /path/to/project`
        # https://github.com/modelcontextprotocol/python-sdk/pull/292
        os.chdir(value.run_dir)

    def _infer_project_dir(self) -> None:
        maybe_project_dir = str(self._cwd_at_init)
        try:
            self._project_context = switch_context(maybe_project_dir)
            logger.info(f"Loaded dlt+ project at: {self.project_context.run_dir}")
        except ProjectRunContextNotAvailable:
            logger.warning(
                f"No dlt+ project found at: {maybe_project_dir}\n"
                "Use `dlt mcp run_plus` command from the project directory"
                " or use the tool `select_or_create_dlt_project()` to set the project directory"
            )

    def _register_dlt_features(self) -> None:
        """Register MCP tools, resources, and prompts at initialization for dlt OSS."""
        for tool in tools.pipeline.__tools__:
            self.add_tool(tool)
        logger.debug("dlt tools registered.")

        for resource_fn in resources.docs.__resources__:
            self.add_resource(resource_fn())
        logger.debug("dlt resources registered.")

        for prompt_fn in prompts.pipeline.__prompts__:
            self.add_prompt(Prompt.from_function(prompt_fn))
        logger.debug("dlt prompts registered.")

    def _register_dlt_plus_features(self) -> None:
        """Register MCP tools, resources, and prompts at initialization for dlt+."""
        if self.project_context is None:
            self.add_tool(tools.project.select_or_create_dlt_project)

        for tool in tools.project.__tools__:
            self.add_tool(tool)
        logger.debug("dlt+ tools registered.")

        for resource_fn in resources.docs.__resources__:
            self.add_resource(resource_fn())
        logger.debug("dlt+ resources registered.")

        for prompt_fn in prompts.project.__prompts__:
            self.add_prompt(Prompt.from_function(prompt_fn))
        logger.debug("dlt+ prompts registered.")


if __name__ == "__main__":
    mcp_server = DltMCP(project_mode=False)
    mcp_server.run()
