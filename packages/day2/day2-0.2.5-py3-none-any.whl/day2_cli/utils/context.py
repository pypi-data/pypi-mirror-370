"""Utilities for handling global CLI context and options."""

import json
from pathlib import Path
from typing import Any, Callable, Dict, Optional

import click
from rich.console import Console

from day2 import Session

console = Console()


# Legacy functions - keeping for backward compatibility during transition
def get_global_context(local_output: Optional[str] = None) -> Dict[str, Any]:
    """Legacy function - creates session without profile for backward compatibility."""
    return {
        "session": Session(),
        "output_format": local_output,
        "profile": None,
    }


def get_global_session() -> Session:
    """Legacy function - creates session without profile for backward compatibility."""
    return Session()


def resolve_tenant_id(
    session: Session, local_tenant_id: Optional[str] = None
) -> Optional[str]:
    """Resolve tenant ID from local option, session, or config file.

    Args:
        session: Session object to get tenant_id from
        local_tenant_id: Local tenant ID option that takes precedence

    Returns:
        Resolved tenant ID or None if not available
    """
    # Local option takes precedence
    if local_tenant_id:
        return local_tenant_id

    # Try to get from session
    tenant_id = session.tenant_id
    if tenant_id:
        return tenant_id

    # Try to load from config file directly (for backward compatibility)
    config_dir = Path.home() / ".day2"
    config_file = config_dir / "config"
    if config_file.exists():
        try:
            with open(config_file, "r", encoding="utf-8") as f:
                config = json.load(f)
                tenant_id = config.get("tenant_id")
                if isinstance(tenant_id, str):
                    return tenant_id
        except (json.JSONDecodeError, IOError):
            pass

    return None


def require_tenant_id(session: Session, local_tenant_id: Optional[str] = None) -> str:
    """Resolve tenant ID and raise error if not available.

    Args:
        session: Session object to get tenant_id from
        local_tenant_id: Local tenant ID option that takes precedence

    Returns:
        Resolved tenant ID

    Raises:
        click.ClickException: If no tenant ID is available
    """
    tenant_id = resolve_tenant_id(session, local_tenant_id)

    if not tenant_id:
        console.print(
            "[red]Error: No tenant ID provided and no default tenant configured.[/red]"
        )
        console.print(
            "[yellow]Tip: Use --tenant-id option or create a profile with tenant ID: "
            "'day2 profile create tenant-name --tenant-id YOUR_TENANT_ID'[/yellow]"
        )
        import sys

        from day2_cli.utils.exit_codes import ExitCodes

        sys.exit(ExitCodes.USER_ERROR)

    return tenant_id


# Legacy function - keeping for backward compatibility during transition
def get_global_context_with_tenant(
    local_output: Optional[str] = None,
    local_tenant_id: Optional[str] = None,
    require_tenant: bool = False,
) -> Dict[str, Any]:
    """Legacy function - use get_enhanced_context instead."""
    return get_enhanced_context(
        output=local_output,
        profile=None,
        tenant_id=local_tenant_id,
        require_tenant=require_tenant,
    )


# CLI Option Decorators
def with_output_option(f: Callable) -> Callable:
    """Decorator to add --output option to a command."""
    return click.option(
        "--output",
        type=click.Choice(["table", "json"], case_sensitive=False),
        help="Output format (table or json)",
    )(f)


def with_profile_option(f: Callable) -> Callable:
    """Decorator to add --profile option to a command."""
    return click.option(
        "--profile",
        help="Configuration profile to use",
    )(f)


def with_tenant_id_option(required: bool = False) -> Callable:
    """Decorator to add --tenant-id option to a command.

    Args:
        required: Whether the tenant-id option is required
    """

    def decorator(f: Callable) -> Callable:
        return click.option(
            "--tenant-id",
            required=required,
            help="ID of the tenant" + (" (required)" if required else ""),
        )(f)

    return decorator


def with_common_options(
    include_tenant_id: bool = False, require_tenant_id_option: bool = False
) -> Callable:
    """Decorator to add common CLI options (output, profile, and optionally tenant-id).

    Args:
        include_tenant_id: Whether to include --tenant-id option
        require_tenant_id_option: Whether --tenant-id is required (only used if include_tenant_id=True)
    """

    def decorator(f: Callable) -> Callable:
        # Apply decorators in reverse order (they stack)
        if include_tenant_id:
            f = with_tenant_id_option(required=require_tenant_id_option)(f)
        f = with_profile_option(f)
        f = with_output_option(f)
        return f

    return decorator


def get_enhanced_context(
    output: Optional[str] = None,
    profile: Optional[str] = None,
    tenant_id: Optional[str] = None,
    require_tenant: bool = False,
) -> Dict[str, Any]:
    """Get context from local command options only.

    Args:
        output: Output format option from command
        profile: Profile option from command
        tenant_id: Tenant ID option from command
        require_tenant: Whether to raise an error if tenant ID is not available

    Returns:
        Dictionary containing session, output_format, profile, and tenant_id
    """
    # Create session with provided profile
    session = Session(profile=profile)

    # Resolve tenant ID if needed
    resolved_tenant_id = None
    if require_tenant or tenant_id is not None:
        if require_tenant:
            resolved_tenant_id = require_tenant_id(session, tenant_id)
        else:
            resolved_tenant_id = resolve_tenant_id(session, tenant_id)

    # Resolve output format: use provided output, otherwise fall back to session config
    resolved_output_format = (
        output if output is not None else session.config.output_format
    )

    return {
        "session": session,
        "output_format": resolved_output_format,
        "profile": profile,
        "tenant_id": resolved_tenant_id,
    }
