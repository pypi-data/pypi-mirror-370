import os
import json
import shutil
import argparse

from typing import Dict, List, Optional

from dlt.common import logger
from dlt.common.storages import FileStorage
from dlt.cli import SupportsCliCommand, CliCommandException, echo as fmt
from dlt.cli.utils import REQUIREMENTS_TXT, PYPROJECT_TOML
from dlt.cli.echo import always_choose


from dlt_plus.common.cli import add_project_opts

from ..entity_factory import EntityFactory
from ..run_context import (
    ProjectRunContext,
    list_dlt_packages,
    project_from_args,
    read_profile_pin,
    save_profile_pin,
)
from ..config.config import Project
from dlt_plus.project.cli.helpers import project_from_args_with_cli_output

from .helpers import (
    DEFAULT_VERIFIED_SOURCES_REPO,
    init_project,
    add_source,
    init_pipeline,
    add_profile,
)

from dlt_plus.project.exceptions import ProjectRunContextNotAvailable
from dlt_plus.common.license import require_license


class ProjectCommand(SupportsCliCommand):
    command = "project"
    help_string = "Manage dlt+ projects"
    description = (
        "Commands to manage dlt+ projects. Run without arguments to list all projects in scope."
    )

    def configure_parser(self, parser: argparse.ArgumentParser) -> None:
        self.parser = parser
        add_project_opts(parser)

        subparsers = parser.add_subparsers(title="Available subcommands", dest="project_command")

        # config command
        config_parser = subparsers.add_parser("config", help="Configuration management commands")

        config_subparsers = config_parser.add_subparsers(dest="config_command", required=True)

        config_subparsers.add_parser("validate", help="Validate configuration file")

        # show command
        show_parser = config_subparsers.add_parser("show", help="Show configuration")
        show_parser.add_argument(
            "--format", choices=["json", "yaml"], default="yaml", help="Output format"
        )
        show_parser.add_argument(
            "--section", help="Show specific configuration section (e.g., sources, pipelines)"
        )

        # clean command
        clean_local_parser = subparsers.add_parser(
            "clean",
            help=(
                "Cleans local data for the selected profile. local_dir defined in project "
                "file, it gets deleted. Pipelines and transformations working dir are also deleted "
                "by default. Data in remote destinations is not affected"
            ),
        )
        clean_local_parser.add_argument(
            "--skip-data-dir",
            action="store_true",
            default=False,
            help="Do not delete pipelines and transformations working dir.",
        )

        # init command
        init_parser = subparsers.add_parser("init", help="Initialize a new dlt+ project")
        init_parser.add_argument(
            "--project-name",
            "-n",
            help=("Optinal Name of your dlt project"),
        )
        init_parser.add_argument(
            "source",
            nargs="?",
            help=("Name of a source for your dlt project"),
        )
        init_parser.add_argument(
            "destination",
            nargs="?",
            help="Name of a destination for your dlt project",
        )
        init_parser.add_argument(
            "--package",
            nargs="?",
            help="Create a pip package with given name instead of a flat project",
        )
        init_parser.add_argument(
            "--force",
            action="store_true",
            default=False,
            help="Overwrite project even if it already exists",
        )
        init_parser.add_argument(
            "--location",
            default=DEFAULT_VERIFIED_SOURCES_REPO,
            help="Advanced. Uses a specific url or local path to verified sources repository.",
        )
        init_parser.add_argument(
            "--branch",
            default=None,
            help=(
                "Advanced. Uses specific branch of the verified sources repository to fetch the"
                " template."
            ),
        )
        init_parser.add_argument(
            "--eject-source",
            default=False,
            action="store_true",
            help=(
                "Ejects the source code of the core source like sql_database or rest_api so they"
                " will be editable by you."
            ),
        )
        init_parser.add_argument(
            "--add-pipeline-script",
            action="store_true",
            help="Create an example pipeline script.",
        )

        # other commands
        subparsers.add_parser(
            "list",
            help=("List all projects that could be found in installed dlt packages"),
        )
        subparsers.add_parser(
            "info",
            help=("List basic project info of current project."),
        )
        subparsers.add_parser(
            "audit",
            help=("Creates and locks resource and secrets audit for a current profile."),
        )
        subparsers.add_parser(
            "mcp",
            help=("Run an MCP server for the project"),
        )

    def execute(self, args: argparse.Namespace) -> None:
        if args.project_command == "list":
            list_projects()
        elif args.project_command == "init":
            init_command(args)
        else:
            run_context = project_from_args_with_cli_output(args)

            if args.project_command == "clean":
                clean_local_data(run_context, args)
            elif args.project_command == "audit":
                create_audit(run_context)
            elif args.project_command == "info":
                show_info(run_context)
            elif args.project_command == "config":
                if args.config_command == "validate":
                    success = validate_config(run_context.project, args.profile)
                    if not success:
                        exit(1)

                elif args.config_command == "show":
                    show_config(run_context.project, args.format, args.section)
            elif args.project_command == "mcp":
                from mcp.server.fastmcp import FastMCP
                from dlt_plus.mcp.tools.mcp_tools import ProjectMCPTools

                logger.info(f"Starting MCP server for project: {run_context.name}")

                project_tools = ProjectMCPTools(run_context)
                mcp = FastMCP(f"dlt+ project: {run_context.name}")
                project_tools.register_with(mcp)

                mcp.run(transport="stdio")
            else:
                self.parser.print_usage()


#
# Command implementations
#
@require_license(scope="dlt_plus.project")
def init_command(args: argparse.Namespace) -> None:
    cwd = os.getcwd()

    # cannot create project if already exists in same directory
    try:
        run_context = project_from_args(args)
        if run_context.project.project_dir == cwd and not args.force:
            fmt.error(
                "Current directory %s already contains a dlt+ project, "
                "use --force to overwrite. Aborting..." % fmt.bold(cwd)
            )
            raise CliCommandException()
    except ProjectRunContextNotAvailable:
        pass

    fmt.echo("Will create a dlt+ project in %s." % fmt.bold(cwd))
    fmt.echo(
        "Package name: %s" % fmt.bold(args.package)
        if args.package
        else "No package name provided, will create a flat project"
    )

    if not fmt.confirm("Do you want to proceed?", default=True):
        exit(0)

    run_context, state = init_project(
        cwd, args.project_name if args.project_name else None, args.package
    )
    with always_choose(always_choose_default=True, always_choose_value="Y"):
        if args.source and not args.destination:
            add_source(
                state,
                args.source,
                destination_type=args.destination,
                location=args.location,
                branch=args.branch,
                eject_source=args.eject_source,
                add_example_pipeline_script=args.add_pipeline_script,
                dependency_system=PYPROJECT_TOML if args.package else REQUIREMENTS_TXT,
            )
        if args.source and args.destination:
            init_pipeline(
                state,
                args.source,
                args.destination,
                pipeline_name="my_pipeline",
                location=args.location,
                branch=args.branch,
                eject_source=args.eject_source,
                add_example_pipeline_script=args.add_pipeline_script,
                dependency_system=PYPROJECT_TOML if args.package else REQUIREMENTS_TXT,
            )
    add_profile(state, "dev")

    state.commit(allow_overwrite=args.force)
    fmt.echo()
    if args.source and args.destination:
        fmt.echo("You can now run your pipeline with `dlt pipeline my_pipeline run.`")


def pin_profile(run_context: ProjectRunContext, profile: str) -> None:
    pinned_profile = read_profile_pin(run_context)
    if pinned_profile:
        fmt.echo("Pinned profile: %s" % fmt.bold(pinned_profile))
    else:
        fmt.echo("No pinned profile")
    if profile:
        save_profile_pin(run_context, profile)
        fmt.echo("New pinned profile: %s" % fmt.bold(profile))


def show_info(run_context: ProjectRunContext) -> None:
    fmt.echo("Project name: %s" % fmt.bold(run_context.name))
    fmt.echo("Project dir: %s" % fmt.bold(run_context.run_dir))
    fmt.echo("Default profile: %s" % fmt.bold(run_context.project.settings["default_profile"]))
    fmt.echo("Active profile: %s" % fmt.bold(run_context.profile))
    fmt.echo("Settings for active profile:")
    fmt.echo("\tData dir: %s" % fmt.bold(run_context.data_dir))
    fmt.echo("\tLocal files: %s" % fmt.bold(run_context.local_dir))
    fmt.echo("\tSettings dir: %s" % fmt.bold(run_context.settings_dir))


def list_projects() -> None:
    packages = list_dlt_packages()
    if len(packages) == 0:
        fmt.echo("No installed dlt packages found")
    else:
        fmt.echo("Found ", nl=False)
        fmt.echo(fmt.bold(str(len(packages))), nl=False)
        fmt.echo(" dlt package(s):")
        for info in packages:
            fmt.echo(
                "%s (%s): " % (fmt.bold(info.package_name), fmt.bold(info.module_name)),
                nl=False,
            )
            fmt.echo(info.docstring)
        fmt.echo()


def create_audit(run_context: ProjectRunContext) -> None:
    import tomlkit
    import difflib

    from dlt.common import pendulum, json
    from dlt.common.schema import Schema
    from dlt.common.storages import FilesystemConfiguration
    from dlt.common.destination.client import DestinationClientDwhConfiguration
    from dlt.cli.config_toml_writer import WritableConfigValue, write_values

    project_config = run_context.project
    factory = EntityFactory(project_config)
    # TODO: add versioning to project files

    audit_doc = tomlkit.loads(
        f"# secrets and resource audit for {project_config.name} on {pendulum.now().isoformat()}"
    )
    # lock the secrets
    secrets_lock = tomlkit.table(False)
    audit_doc["secrets-lock"] = secrets_lock
    # lock the known resources
    resources = tomlkit.table(False)
    audit_doc["resources"] = resources

    # get the datasets and destinations they are on
    destination_datasets: Dict[str, List[str]] = {}
    for dataset_name in sorted(project_config.datasets):  # make sure we do this deterministically
        for destination_name in factory._resolve_dataset_destinations(dataset_name):
            datasets_ = destination_datasets.setdefault(destination_name, [])
            datasets_.append(dataset_name)
            datasets_.sort()  # deterministic

    # TODO: also write source secrets.
    # for source_name in config.sources:
    #     source_ = factory.get_source(source_name)
    #     source_._ref.spec

    for destination_name in sorted(project_config.destinations):
        destination_ = factory.get_destination(destination_name)
        # create mock credentials to avoid credentials being resolved
        init_config = destination_.spec()
        init_config.update(destination_.config_params)
        credentials = destination_.spec.credentials_type(init_config)()
        credentials.__is_resolved__ = True
        config = destination_.spec(credentials=credentials)
        try:
            # write secrets
            config = destination_.configuration(config, accept_partial=True)
            config_value = WritableConfigValue(
                destination_.destination_name, destination_.spec, config, ("destination",)
            )
            write_values(secrets_lock, [config_value], overwrite_existing=False)  # type: ignore[arg-type]

            # write resources
            # TODO: figure our host and database if provided
            if isinstance(config, FilesystemConfiguration):
                resources[destination_name] = {
                    "resource_type": "filesystem",
                    "type": config.protocol,
                    "location": str(config),
                }
            elif isinstance(config, DestinationClientDwhConfiguration):
                resources[destination_name] = {
                    "resource_type": "warehouse",
                    "type": config.destination_type,
                    "location": str(config),
                }
            else:
                resources[destination_name] = {
                    "resource_type": "destination",
                    "type": config.destination_type,
                    "location": str(config),
                }
            # write access type
            if destination_name in destination_datasets:
                for dataset_name in destination_datasets[destination_name]:
                    dataset_cfg = project_config.datasets[dataset_name]
                    schema_contract = dataset_cfg.get("contract") or "evolve"
                    schema_contract = Schema.expand_schema_contract_settings(schema_contract)
                    resources[destination_name][dataset_name] = {  # type: ignore[index]
                        "access": "rw" if schema_contract["tables"] == "evolve" else "r",
                        "schema": schema_contract,
                    }

        except Exception:
            fmt.error(f"{destination_name} cannot be audited!")
            raise CliCommandException()
    # save or compare the audit
    audit_fn = f"{run_context.profile}.audit.toml"
    audit_path = run_context.get_setting(audit_fn)
    if os.path.isfile(audit_path):
        with open(audit_path, "r", encoding="utf-8") as f:
            existing_audit = tomlkit.load(f)
        fmt.echo("Found audit for profile %s" % fmt.bold(run_context.profile), nl=False)
        fmt.echo(" in %s:" % fmt.bold(audit_path))
        # compare normalized strings
        existing_audit_str = json.dumps(existing_audit.unwrap(), sort_keys=True, pretty=True)
        new_audit_str = json.dumps(audit_doc.unwrap(), sort_keys=True, pretty=True)
        diff = difflib.unified_diff(
            existing_audit_str.splitlines(),
            new_audit_str.splitlines(),
            fromfile="Existing " + audit_fn,
            tofile="New " + audit_fn,
            lineterm="",
        )
        diff_output = "\n".join(diff)
        if diff_output:
            fmt.error("Detected changes from the last audit")
            fmt.echo(diff_output)
            raise CliCommandException(-2)
        else:
            fmt.echo("No changes detected")
    else:
        with open(audit_path, "w", encoding="utf-8") as f:
            tomlkit.dump(audit_doc, f)
        fmt.echo("Generated audit for profile %s" % fmt.bold(run_context.profile), nl=False)
        fmt.echo(" in %s:" % fmt.bold(audit_path))


def clean_local_data(run_context: ProjectRunContext, args: argparse.Namespace) -> None:
    config = run_context.project
    # delete all files in tmp folder
    if local_dir := config.settings["local_dir"]:
        # show relative path to the user
        display_dir = os.path.relpath(local_dir, ".")
        if len(display_dir) > len(local_dir):
            display_dir = local_dir
        fmt.echo("Will delete a temporary dir %s" % fmt.style(display_dir, fg="green"))
        if os.path.exists(local_dir):
            shutil.rmtree(local_dir, onerror=FileStorage.rmtree_del_ro)
        # create temp dir
        os.makedirs(local_dir, exist_ok=True)
    else:
        fmt.echo(
            "local_dir not defined in your project file, local storages and caches not wiped out"
        )
    if not args.skip_data_dir:
        data_dir = run_context.data_dir
        fmt.echo(
            "Will delete pipeline working folders & other entities data %s"
            % fmt.style(data_dir, fg="green")
        )
        if os.path.exists(data_dir):
            shutil.rmtree(data_dir, onerror=FileStorage.rmtree_del_ro)
        # create data dir
        os.makedirs(data_dir, exist_ok=True)


def validate_config(project: Project, strict: bool = False) -> bool:
    try:
        required_sections = ["sources", "pipelines"]
        for section in required_sections:
            if section not in project.config:
                fmt.error(f"Error: Missing required section '{section}'")
                return False

        fmt.echo("Configuration validation successful!")
        return True

    except Exception as e:
        fmt.error(f"Error validating configuration: {str(e)}")
        return False


def show_config(project: Project, format: str, section: Optional[str] = None) -> None:
    """Display configuration in the specified format."""
    if section:
        if section not in project.config:
            fmt.error(f"Error: Section '{section}' not found in configuration")
            return
        config_to_show = {section: dict(project.config[section])}  # type: ignore[literal-required]
        # add project section
    else:
        config_to_show = project.config  # type: ignore[assignment]
        # add project section
        config_to_show["project"] = project.settings  # type: ignore

    if format == "json":
        fmt.echo(json.dumps(config_to_show, indent=2))
    else:  # yaml
        import yaml

        fmt.echo(yaml.dump(config_to_show, default_flow_style=False))
