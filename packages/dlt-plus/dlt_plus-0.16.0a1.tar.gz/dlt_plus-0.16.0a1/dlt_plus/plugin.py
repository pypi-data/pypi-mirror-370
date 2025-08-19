import os
from typing import Any, Dict, Optional, Type

from dlt.common.configuration import plugins as _plugins
from dlt.common.configuration.specs.pluggable_run_context import SupportsRunContext

from dlt.cli import SupportsCliCommand

from dlt_plus.project.exceptions import ProjectRunContextNotAvailable
from dlt_plus.project.run_context import is_project_dir


@_plugins.hookimpl(specname="plug_run_context")
def _plug_run_context_impl(
    run_dir: Optional[str], runtime_kwargs: Optional[Dict[str, Any]]
) -> Optional[SupportsRunContext]:
    """Called when run new context is created"""

    from dlt_plus.project.run_context import (
        create_project_context,
        find_project_dir,
    )

    # use explicit dir or find one starting from cwd
    project_dir = (
        run_dir
        if run_dir and is_project_dir(run_dir)
        else find_project_dir()
        if not run_dir
        else None
    )
    runtime_kwargs = runtime_kwargs or {}
    profile = runtime_kwargs.get("profile")
    if project_dir:
        # TODO: get local_dir, data_dir, and verify settings_dir. allow them to override
        #   settings in project config
        return create_project_context(
            project_dir, profile=profile, validate=runtime_kwargs.get("validate", False)
        )
    else:
        if runtime_kwargs.get("required"):
            raise ProjectRunContextNotAvailable(project_dir or run_dir or os.getcwd())

    # no run dir pass through to next plugin
    return None


@_plugins.hookimpl(specname="plug_cli")
def _plug_cli_transformation() -> Type[SupportsCliCommand]:
    from dlt.common.exceptions import MissingDependencyException

    try:
        from dlt_plus.transformations.cli import TransformationCommand

        return TransformationCommand
    except (MissingDependencyException, ImportError):
        # TODO: we need a better mechanism to plug in placeholder commands for non installed
        # packages
        from dlt.cli import SupportsCliCommand

        class _PondCommand(SupportsCliCommand):
            command = "transformation"
            help_string = "Please install dlt_plus[cache] to enable transformations"

        return _PondCommand


@_plugins.hookimpl(specname="plug_cli")
def _plug_cli_cache() -> Type[SupportsCliCommand]:
    from dlt_plus.cache.cli import CacheCommand
    from dlt.common.exceptions import MissingDependencyException

    try:
        from dlt_plus.cache.cli import CacheCommand

        return CacheCommand
    except (MissingDependencyException, ImportError):
        from dlt.cli import SupportsCliCommand

        class _CacheCommand(SupportsCliCommand):
            command = "cache"
            help_string = "Please install dlt_plus[cache] to use local transformation cache"

        return _CacheCommand


@_plugins.hookimpl(specname="plug_cli")
def _plug_cli_project() -> Type[SupportsCliCommand]:
    from dlt_plus.project.cli.project_command import ProjectCommand

    return ProjectCommand


@_plugins.hookimpl(specname="plug_cli")
def _plug_cli_pipeline() -> Type[SupportsCliCommand]:
    from dlt_plus.project.cli.pipeline_command import ProjectPipelineCommand

    return ProjectPipelineCommand


@_plugins.hookimpl(specname="plug_cli")
def _plug_cli_dataset() -> Type[SupportsCliCommand]:
    from dlt_plus.project.cli.dataset_command import DatasetCommand

    return DatasetCommand


@_plugins.hookimpl(specname="plug_cli")
def _plug_cli_source() -> Type[SupportsCliCommand]:
    from dlt_plus.project.cli.source_command import SourceCommand

    return SourceCommand


@_plugins.hookimpl(specname="plug_cli")
def _plug_cli_mcp() -> Type[SupportsCliCommand]:
    from dlt_plus.project.cli.mcp_command import MCPCommand

    return MCPCommand


@_plugins.hookimpl(specname="plug_cli")
def _plug_cli_destination() -> Type[SupportsCliCommand]:
    from dlt_plus.project.cli.destination_command import DestinationCommand

    return DestinationCommand


@_plugins.hookimpl(specname="plug_cli")
def _plug_cli_profile() -> Type[SupportsCliCommand]:
    from dlt_plus.project.cli.profile_command import ProfileCommand

    return ProfileCommand


@_plugins.hookimpl(specname="plug_cli")
def _plug_cli_license() -> Type[SupportsCliCommand]:
    from dlt_plus.common.license.cli import LicenseCommand

    return LicenseCommand


@_plugins.hookimpl(specname="plug_cli")
def _plug_cli_dbt() -> Type[SupportsCliCommand]:
    from dlt_plus.dbt_generator.cli import DbtCommand

    return DbtCommand
