"""Exit code utilities for the MontyCloud DAY2 CLI."""

import sys
from typing import NoReturn

from rich.console import Console

from day2.exceptions import (
    AuthenticationError,
    ClientError,
    Day2Error,
    ProfileNotFoundError,
    ResourceNotFoundError,
    ServerError,
    TenantContextError,
    ValidationError,
)
from day2_cli.utils.formatters import format_error

console = Console()


class ExitCodes:
    """Standard exit codes for the CLI."""

    SUCCESS = 0
    GENERAL_ERROR = 1
    USER_ERROR = 2
    API_ERROR = 3
    AUTHENTICATION_ERROR = 4
    NOT_FOUND_ERROR = 5
    VALIDATION_ERROR = 6
    SERVER_ERROR = 7


def handle_error_with_exit(error: Exception) -> NoReturn:
    """Handle an error by printing it and exiting with appropriate code.

    Args:
        error: The exception to handle

    Exits:
        With appropriate exit code based on error type
    """
    console.print(format_error(error))

    # Determine exit code based on error type
    if isinstance(error, AuthenticationError):
        sys.exit(ExitCodes.AUTHENTICATION_ERROR)
    elif isinstance(error, ValidationError):
        sys.exit(ExitCodes.VALIDATION_ERROR)
    elif isinstance(error, ResourceNotFoundError):
        sys.exit(ExitCodes.NOT_FOUND_ERROR)
    elif isinstance(error, ProfileNotFoundError):
        sys.exit(ExitCodes.USER_ERROR)
    elif isinstance(error, ServerError):
        sys.exit(ExitCodes.SERVER_ERROR)
    elif isinstance(error, ClientError):
        sys.exit(ExitCodes.USER_ERROR)
    elif isinstance(error, TenantContextError):
        sys.exit(ExitCodes.USER_ERROR)
    elif isinstance(error, Day2Error):
        sys.exit(ExitCodes.API_ERROR)
    else:
        sys.exit(ExitCodes.GENERAL_ERROR)


def exit_with_error(message: str, exit_code: int = ExitCodes.USER_ERROR) -> NoReturn:
    """Exit with an error message and specific exit code.

    Args:
        message: Error message to display
        exit_code: Exit code to use (default: USER_ERROR)

    Exits:
        With the specified exit code
    """
    console.print(f"[red]Error: {message}[/red]")
    sys.exit(exit_code)
