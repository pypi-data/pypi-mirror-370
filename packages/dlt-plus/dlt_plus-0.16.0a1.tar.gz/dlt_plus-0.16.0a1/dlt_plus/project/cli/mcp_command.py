import argparse

from dlt_plus.version import __version__
from dlt.common import logger
from dlt.cli import SupportsCliCommand, utils
from dlt_plus.common.license import ensure_license_with_scope
from dlt_plus.common.license.license import DltLicenseException

DEFAULT_DLT_MCP_PORT = 43654
DEFAULT_DLT_PLUS_MCP_PORT = 43655


class MCPCommand(SupportsCliCommand):
    command = "mcp"
    help_string = "Launch a dlt MCP server"
    description = (
        "The MCP server allows LLMs to interact with your dlt pipelines and your dlt+ projects."
    )

    def configure_parser(self, parser: argparse.ArgumentParser) -> None:
        self.parser = parser
        subparser = parser.add_subparsers(title="Available subcommands", dest="mcp_command")

        subcommands = {
            "run": DEFAULT_DLT_MCP_PORT,
            "run_plus": DEFAULT_DLT_PLUS_MCP_PORT,
        }

        for command, default_port in subcommands.items():
            command_parser = subparser.add_parser(
                command,
                help=f"Launch dlt{'+' if command == 'run_plus' else ''} MCP server from current environment and working directory",  # noqa: E501
            )
            command_parser.add_argument("--sse", action="store_true", help="Use SSE transport mode")
            command_parser.add_argument(
                "--port",
                type=int,
                default=default_port,
                help=f"Port to use (default: {default_port})",
            )

    def execute(self, args: argparse.Namespace) -> None:
        if args.mcp_command == "run":
            start_mcp(port=args.port, sse=args.sse)

        elif args.mcp_command == "run_plus":
            try:
                ensure_license_with_scope("*")
                start_mcp_plus(port=args.port, sse=args.sse)
            except DltLicenseException:
                start_mcp(port=args.port, sse=args.sse)


@utils.track_command("mcp_run", True, f"dlt_plus=={__version__}")
def start_mcp(port: int, sse: bool) -> None:
    from dlt_plus.mcp.server import DltMCP

    transport = "stdio" if not sse else "sse"
    if sse:
        logger.info("Starting dlt MCP server with SSE transport on port %s", port)
    else:
        logger.warning("Starting dlt MCP server")

    mcp_server = DltMCP(project_mode=False, sse_port=port)
    mcp_server.run(transport)


def start_mcp_plus(port: int, sse: bool) -> None:
    from dlt_plus.mcp.server import DltMCP

    transport = "stdio" if not sse else "sse"
    if sse:
        logger.info("Starting dlt+ MCP server with SSE transport on port %s", port)
    else:
        logger.warning("Starting dlt+ MCP server")

    mcp_server = DltMCP(project_mode=True, sse_port=port)
    mcp_server.run(transport)
