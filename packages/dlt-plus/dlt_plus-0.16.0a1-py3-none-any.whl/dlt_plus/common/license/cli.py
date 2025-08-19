"""Cli for licensing"""

from typing import Optional
import argparse

from dlt.cli import echo as fmt, SupportsCliCommand
from dlt_plus.common.constants import LICENSE_PUBLIC_KEY

from .license import (
    discover_license,
    discover_private_key,
    create_license,
    get_known_scopes,
    prettify_license,
    validate_license,
    DltPrivateKeyNotFoundException,
)


# try to find the private key
private_key: Optional[str] = None
try:
    private_key = discover_private_key()
except DltPrivateKeyNotFoundException:
    pass


def print_license() -> None:
    """
    Print the found license
    """
    fmt.echo("Searching dlt license in environment or secrets toml")
    license = discover_license()
    fmt.echo("License found")
    validate_license(LICENSE_PUBLIC_KEY, license)
    fmt.echo(prettify_license(license, with_license=False))


def issue_license(licensee_name: str, license_type: str, days_valid: int, scope: str) -> None:
    """
    Issue a new license
    """
    if license_type not in ["trial", "commercial"]:
        fmt.error("License type must be trial or commercial")
        exit(0)
    if not private_key:
        exit(0)

    # convert from command line scope to space separated scope
    if scope:
        scope = " ".join(map(str.strip, scope.split(",")))

    fmt.echo(f"Generating license for {licensee_name}, valid for {days_valid} days.")
    license = create_license(
        private_key=private_key,
        days_valid=days_valid,
        licensee_name=licensee_name,
        license_type=license_type,  # type: ignore
        scope=scope,
    )
    fmt.echo("License generated")
    fmt.echo(prettify_license(license, with_license=True))


class LicenseCommand(SupportsCliCommand):
    command = "license"
    help_string = "View dlt+ license status"

    def configure_parser(self, parser: argparse.ArgumentParser) -> None:
        self.parser = parser

        subparsers = parser.add_subparsers(
            title="Available subcommands", dest="license_command", required=True
        )
        subparsers.add_parser("show", help="Show the installed license")
        subparsers.add_parser("scopes", help="Show available scopes")

        if private_key:
            known_scopes = get_known_scopes()
            issue_parser = subparsers.add_parser(
                "issue", help="Issue a new license", description="Issue a new license"
            )
            issue_parser.add_argument("licensee_name", help="Name of the licensee")
            issue_parser.add_argument(
                "days_valid",
                nargs="?",
                help="Amount of days the license will be valid",
                default=30,
                type=int,
            )
            issue_parser.add_argument(
                "license_type",
                nargs="?",
                help="Type of license, can be trial or commercial",
                choices=["trial", "commercial"],
                default="trial",
            )
            issue_parser.add_argument(
                "scope",
                nargs="?",
                help=f"Scope of the license, a comma separated list of the scopes: {known_scopes}",
                default="*",
            )

    def execute(self, args: argparse.Namespace) -> None:
        if args.license_command == "show":
            print_license()
        elif args.license_command == "issue":
            issue_license(args.licensee_name, args.license_type, int(args.days_valid), args.scope)
        elif args.license_command == "scopes":
            fmt.echo("Known scopes:")
            fmt.echo(get_known_scopes())
