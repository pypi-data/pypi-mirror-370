"""Main CLI entry point for the MontyCloud DAY2 CLI."""

# pylint: disable=redefined-outer-name

import sys

import click
from rich.console import Console

from day2 import __version__
from day2_cli.commands.assessment import assessment

# Import from day2 package
# Import from day2_cli package
from day2_cli.commands.auth import auth
from day2_cli.commands.bot import bot
from day2_cli.commands.cost import cost
from day2_cli.commands.profile import profile
from day2_cli.commands.report import report
from day2_cli.commands.resource import resource
from day2_cli.commands.tenant import tenant
from day2_cli.utils.formatters import format_error

console = Console()


@click.group()
@click.version_option(package_name="day2")
def cli() -> None:
    """DAY2 CLI.

    A command-line interface for interacting with the MontyCloud DAY2 API.
    """


# Add command groups
cli.add_command(auth)
cli.add_command(profile)
cli.add_command(tenant)
cli.add_command(assessment)
cli.add_command(cost)
cli.add_command(resource)
cli.add_command(report)
cli.add_command(bot)


def main() -> None:
    """Main entry point for the CLI."""
    try:
        cli()
    except (ValueError, KeyError, RuntimeError, IOError) as e:
        console.print(format_error(e))
        sys.exit(1)


if __name__ == "__main__":
    main()
