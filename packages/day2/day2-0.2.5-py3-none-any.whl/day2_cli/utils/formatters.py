"""Formatters for the MontyCloud DAY2 CLI."""

from day2.exceptions import (
    AuthenticationError,
    ClientError,
    ProfileNotFoundError,
    ResourceNotFoundError,
    ServerError,
    TenantContextError,
    ValidationError,
)


def format_error(error: Exception) -> str:
    """Format an error message for display in the CLI.

    Args:
        error: Exception to format.

    Returns:
        Formatted error message.
    """
    if isinstance(error, ValidationError):
        return f"[red]Validation Error: {str(error)}[/red]"
    if isinstance(error, ResourceNotFoundError):
        return f"[red]Resource Not Found: {str(error)}[/red]"
    if isinstance(error, AuthenticationError):
        return f"[red]Authentication Error: {str(error)}[/red]"
    if isinstance(error, TenantContextError):
        return f"[red]Tenant Context Error: {str(error)}[/red]"
    if isinstance(error, ProfileNotFoundError):
        return f"[red]Error: {str(error)}[/red]"
    if isinstance(error, ClientError):
        return f"[red]Client Error: {str(error)}[/red]"
    if isinstance(error, ServerError):
        return f"[red]Server Error: {str(error)}[/red]"
    return f"[red]Error: {str(error)}[/red]"
