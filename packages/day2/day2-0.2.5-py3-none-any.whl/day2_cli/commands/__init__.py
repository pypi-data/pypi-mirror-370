"""CLI commands for the MontyCloud DAY2 CLI."""

from day2_cli.commands.assessment import assessment
from day2_cli.commands.auth import auth
from day2_cli.commands.bot import bot
from day2_cli.commands.cost import cost
from day2_cli.commands.profile import profile
from day2_cli.commands.report import report
from day2_cli.commands.resource import resource
from day2_cli.commands.tenant import tenant

__all__ = [
    "auth",
    "tenant",
    "assessment",
    "report",
    "cost",
    "profile",
    "bot",
    "resource",
]
