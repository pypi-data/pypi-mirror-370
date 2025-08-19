"""Profile management commands for the MontyCloud DAY2 CLI."""

# pylint: disable=redefined-outer-name

import configparser
import json
import os
from typing import Optional

import click
from rich.console import Console
from rich.table import Table

from day2.client.config import Config
from day2.client.profile import ProfileManager
from day2.client.user_context import get_user_context

console = Console()


def get_profile_manager() -> ProfileManager:
    """Get a ProfileManager instance respecting DAY2_CONFIG_PATH environment variable."""
    return ProfileManager()


def show_no_profiles_message(output: Optional[str]) -> None:
    """Display a consistent 'no profiles configured' message.

    Args:
        output: Output format ("json" or None for table format)
    """
    if output and output.lower() == "json":
        console.print(json.dumps({"error": "No profiles configured"}, indent=2))
    else:
        console.print("[yellow]No profiles configured.[/yellow]")
        console.print("\n[dim]To get started:[/dim]")
        console.print("  1. Run [cyan]day2 auth login[/cyan] to set up authentication")
        console.print(
            "  2. Or create a profile with [cyan]day2 profile create <name>[/cyan]"
        )


def determine_current_profile() -> Optional[str]:
    """Determine the currently active profile.

    Returns:
        The name of the current profile, or None if no profiles are configured.
    """
    env_profile = os.environ.get("DAY2_PROFILE")
    profile_manager = get_profile_manager()
    default_profile = profile_manager.get_default_profile()
    existing_profiles = profile_manager.list_profiles()

    # Determine current profile
    if env_profile:
        return env_profile
    if default_profile:
        return default_profile
    if existing_profiles:
        return "default"
    # No profiles configured at all
    return None


def ensure_default_profile() -> Optional[str]:
    """Ensure that a default profile exists.

    If no profiles exist, creates a default profile with system defaults.
    If profiles exist but no default is set, returns None.

    Returns:
        The name of the default profile, or None if no default could be determined.
    """
    # Check if a default profile is set or a profile named 'default' exists
    profile_name = get_profile_manager().get_default_profile()
    if profile_name:
        return profile_name

    # If no profiles exist at all, create a default profile
    if not get_profile_manager().list_profiles():
        # Try to get user context for tenant ID
        config = Config()
        user_context = get_user_context()
        if user_context and user_context.tenant_id:
            config.tenant_id = user_context.tenant_id
            console.print(
                f"Using tenant ID from user context: {user_context.tenant_id}"
            )

        get_profile_manager().create_profile("default", config)
        console.print("Created default profile with system defaults.")
        return "default"

    # Profiles exist but no default is set
    return None


@click.group()
def profile() -> None:
    """Profile management commands."""


@profile.command("create")
@click.argument("profile-name")
@click.option("--tenant-id", help="Tenant ID to use with this profile")
@click.option(
    "--advanced",
    is_flag=True,
    help="Enable advanced configuration options (base URL, timeouts, etc.)",
)
@click.option(
    "--non-interactive", is_flag=True, help="Create profile without interactive prompts"
)
@click.option("--set-default", is_flag=True, help="Set this profile as the default")
@click.option("--base-url", help="Base URL for the API (advanced option)")
@click.option("--api-version", help="API version (advanced option)")
@click.option(
    "--timeout", type=int, help="Request timeout in seconds (advanced option)"
)
@click.option("--max-retries", type=int, help="Maximum retries (advanced option)")
@click.option(
    "--retry-backoff", type=float, help="Retry backoff factor (advanced option)"
)
@click.option(
    "--output-format", type=click.Choice(["table", "json"]), help="Output format"
)
def create_profile(
    profile_name: str,
    tenant_id: Optional[str] = None,
    advanced: bool = False,
    non_interactive: bool = False,
    set_default: bool = False,
    base_url: Optional[str] = None,
    api_version: Optional[str] = None,
    timeout: Optional[int] = None,
    max_retries: Optional[int] = None,
    retry_backoff: Optional[float] = None,
    output_format: Optional[str] = None,
) -> None:
    """Create a new configuration profile for managing a specific tenant or environment.

    Profiles allow you to switch between different tenant contexts while sharing
    the same authentication credentials.

    PROFILE-NAME: Name of the profile to create.

    By default, this command prompts only for essential options (tenant ID).
    Use --advanced to enable base URL and timeout configuration prompts.
    """
    try:
        # Check if profile already exists
        if get_profile_manager().profile_exists(profile_name):
            console.print(
                f"[bold red]Error:[/bold red] Profile '{profile_name}' already exists"
            )
            return

        # Validate advanced options usage
        advanced_options_provided = any(
            [base_url, api_version, timeout, max_retries, retry_backoff]
        )

        if advanced_options_provided and not advanced:
            console.print(
                "[yellow]Tip: Use --advanced flag for cleaner workflow when setting "
                "custom base URLs or timeout settings[/yellow]"
            )

        # Get default base_url from config (avoid network calls)
        default_base_url = Config().base_url

        if non_interactive:
            # Non-interactive mode: use provided options or defaults
            # Tenant ID is highly recommended for MSP workflows
            if not tenant_id:
                console.print(
                    "[yellow]Warning: No tenant ID provided. Consider using --tenant-id for better MSP workflow organization[/yellow]"
                )
                console.print(
                    "[dim]Profile will use auto-detection during authentication[/dim]"
                )

            config = Config()
            if tenant_id:
                config.tenant_id = tenant_id
            if base_url:
                config.base_url = base_url
            if api_version:
                config.api_version = api_version
            if timeout:
                config.timeout = timeout
            if max_retries:
                config.max_retries = max_retries
            if retry_backoff:
                config.retry_backoff_factor = retry_backoff
            if output_format:
                config.output_format = output_format

            get_profile_manager().create_profile(profile_name, config)
            console.print(f"[green]✓[/green] Profile '{profile_name}' created")

            if tenant_id:
                console.print(f"  Tenant ID: {tenant_id}")
            if base_url:
                console.print(f"  Base URL: {base_url}")
        else:
            # Interactive mode: MSP-friendly by default, advanced if requested
            console.print(f"[bold blue]Creating profile '{profile_name}'[/bold blue]")

            if advanced:
                console.print("Advanced Configuration:\n")
            else:
                console.print("Creating profile for tenant management\n")

            # Create config with defaults
            config = Config()

            # Override with any provided options first and show confirmations
            if tenant_id:
                config.tenant_id = tenant_id
                console.print(f"  ✓ Tenant ID: {tenant_id}")
            if base_url:
                config.base_url = base_url
                console.print(f"  ✓ Base URL: {base_url}")
            if api_version:
                config.api_version = api_version
            if timeout:
                config.timeout = timeout
            if max_retries:
                config.max_retries = max_retries
            if retry_backoff:
                config.retry_backoff_factor = retry_backoff
            if output_format:
                config.output_format = output_format

            # MSP-friendly flow: Always prompt for tenant ID first
            if not tenant_id:
                prompted_tenant_id = click.prompt(
                    "Tenant ID",
                    default="",
                    show_default=False,
                )
                if prompted_tenant_id.strip():
                    # Show raw input first, then confirm with stripped version
                    console.print(f"  ✓ Tenant ID: {prompted_tenant_id}")
                    config.tenant_id = prompted_tenant_id.strip()

            # Advanced mode: Prompt for base URL and other advanced settings
            if advanced:
                if not base_url:
                    prompted_base_url = click.prompt(
                        "Base URL", default=default_base_url, show_default=True
                    )
                    config.base_url = prompted_base_url
                    console.print(f"  ✓ Base URL: {prompted_base_url}")

                # Prompt for output format
                if not output_format:
                    prompted_output_format = click.prompt(
                        "Output format",
                        type=click.Choice(["table", "json"], case_sensitive=False),
                        default=config.output_format,
                        show_default=True,
                    )
                    config.output_format = prompted_output_format
                    console.print(f"  ✓ Output format: {prompted_output_format}")

                if not api_version:
                    prompted_api_version = click.prompt(
                        "API version",
                        default=config.api_version,
                        show_default=True,
                    )
                    config.api_version = prompted_api_version

                if not timeout:
                    prompted_timeout = click.prompt(
                        "Request timeout (seconds)",
                        type=int,
                        default=config.timeout,
                        show_default=True,
                    )
                    config.timeout = prompted_timeout

                if not max_retries:
                    prompted_max_retries = click.prompt(
                        "Maximum retries for failed requests",
                        type=int,
                        default=config.max_retries,
                        show_default=True,
                    )
                    config.max_retries = prompted_max_retries

                if not retry_backoff:
                    prompted_retry_backoff = click.prompt(
                        "Retry backoff factor",
                        type=float,
                        default=config.retry_backoff_factor,
                        show_default=True,
                    )
                    config.retry_backoff_factor = prompted_retry_backoff

            else:
                # MSP-friendly mode: Only prompt for output format, skip base URL
                if not output_format:
                    prompted_output_format = click.prompt(
                        "Output format",
                        type=click.Choice(["table", "json"], case_sensitive=False),
                        default=config.output_format,
                        show_default=True,
                    )
                    config.output_format = prompted_output_format
                    console.print(f"  ✓ Output format: {prompted_output_format}")

                # Show tip about advanced options
                console.print(
                    "\n[dim]Use --advanced flag for custom endpoints and timeout settings[/dim]"
                )

            get_profile_manager().create_profile(profile_name, config)

            # Set as default if requested
            if set_default:
                get_profile_manager().set_default_profile(profile_name)

            # Create completion message with tenant info if available
            if config.tenant_id:
                console.print(
                    f"\n[green]✓[/green] Profile '{profile_name}' created for tenant {config.tenant_id}"
                )
            else:
                console.print(f"\n[green]✓[/green] Profile '{profile_name}' created")

            if set_default:
                console.print(
                    f"[green]✓[/green] Profile '{profile_name}' set as default"
                )

        console.print("\n[bold]Next steps:[/bold]")
        if not set_default:
            console.print(
                f"1. Switch to the profile: [cyan]day2 profile use {profile_name}[/cyan]"
            )
            console.print(
                f"2. Use the profile: [cyan]day2 tenant list --profile {profile_name}[/cyan]"
            )
        else:
            console.print(
                f"1. Use the profile: [cyan]day2 tenant list --profile {profile_name}[/cyan]"
            )

    except ValueError as e:
        console.print(f"[bold red]Error:[/bold red] {str(e)}")


@profile.command("update")
@click.argument("profile-name")
@click.option("--tenant-id", help="Update tenant ID to use with this profile")
@click.option(
    "--advanced",
    is_flag=True,
    help="Enable advanced configuration options (base URL, timeouts, etc.)",
)
@click.option(
    "--non-interactive", is_flag=True, help="Update profile without interactive prompts"
)
@click.option("--base-url", help="Base URL for the API (advanced option)")
@click.option("--api-version", help="API version (advanced option)")
@click.option(
    "--timeout", type=int, help="Request timeout in seconds (advanced option)"
)
@click.option("--max-retries", type=int, help="Maximum retries (advanced option)")
@click.option(
    "--retry-backoff", type=float, help="Retry backoff factor (advanced option)"
)
@click.option(
    "--output-format", type=click.Choice(["table", "json"]), help="Output format"
)
def update_profile(
    profile_name: str,
    tenant_id: Optional[str] = None,
    advanced: bool = False,
    non_interactive: bool = False,
    base_url: Optional[str] = None,
    api_version: Optional[str] = None,
    timeout: Optional[int] = None,
    max_retries: Optional[int] = None,
    retry_backoff: Optional[float] = None,
    output_format: Optional[str] = None,
) -> None:
    """Update an existing profile's settings.

    PROFILE-NAME: Name of the profile to update.

    By default, this command will prompt for configuration options interactively.
    Use --non-interactive to update only the provided options.
    Use --advanced to access base URL, timeout, and retry configuration.
    """
    try:
        # Check if profile exists
        if not get_profile_manager().profile_exists(profile_name):
            console.print(
                f"[bold red]Error:[/bold red] Profile '{profile_name}' doesn't exist"
            )
            return

        # Get existing config
        config = get_profile_manager().get_profile_config(profile_name)

        if non_interactive:
            # Non-interactive mode: update only specified fields
            updated = False

            # Validate advanced options usage
            advanced_options_provided = any(
                [base_url, api_version, timeout, max_retries, retry_backoff]
            )

            if advanced_options_provided and not advanced:
                console.print(
                    "[yellow]Tip: Use --advanced flag for cleaner workflow when setting "
                    "custom base URLs or timeout settings[/yellow]"
                )

            # Update all provided fields
            if tenant_id:
                config.tenant_id = tenant_id
                updated = True
            if base_url:
                config.base_url = base_url
                updated = True
            if api_version:
                config.api_version = api_version
                updated = True
            if timeout:
                config.timeout = timeout
                updated = True
            if max_retries:
                config.max_retries = max_retries
                updated = True
            if retry_backoff:
                config.retry_backoff_factor = retry_backoff
                updated = True
            if output_format:
                config.output_format = output_format
                updated = True

            if updated:
                get_profile_manager().update_profile(profile_name, config)
                console.print(f"[green]✓[/green] Profile '{profile_name}' updated")

                # Show what was updated
                if tenant_id:
                    console.print(f"  Tenant ID: {tenant_id}")
                if base_url:
                    console.print(f"  Base URL: {base_url}")
                if api_version:
                    console.print(f"  API Version: {api_version}")
                if timeout:
                    console.print(f"  Timeout: {timeout}s")
                if max_retries:
                    console.print(f"  Max Retries: {max_retries}")
                if retry_backoff:
                    console.print(f"  Retry Backoff: {retry_backoff}")
                if output_format:
                    console.print(f"  Output Format: {output_format}")
            else:
                console.print("[yellow]No updates specified[/yellow]")
        else:
            # Interactive mode: show current values and prompt for updates
            console.print(f"[bold blue]Updating profile '{profile_name}'[/bold blue]")

            if advanced:
                console.print("Advanced Configuration:\n")
            else:
                console.print("Updating profile for tenant management\n")

            console.print("Current settings:\n")

            # Show current configuration
            console.print(f"  Base URL: [cyan]{config.base_url}[/cyan]")
            console.print(f"  Tenant ID: [cyan]{config.tenant_id or 'Not set'}[/cyan]")
            console.print(f"  Output Format: [cyan]{config.output_format}[/cyan]")
            console.print()

            updated = False

            # Apply any provided options first
            if base_url:
                config.base_url = base_url
                console.print(f"  ✓ Base URL: {base_url}")
                updated = True
            if api_version:
                config.api_version = api_version
                console.print(f"  ✓ API Version: {api_version}")
                updated = True
            if timeout:
                config.timeout = timeout
                console.print(f"  ✓ Timeout: {timeout}s")
                updated = True
            if max_retries:
                config.max_retries = max_retries
                console.print(f"  ✓ Max Retries: {max_retries}")
                updated = True
            if retry_backoff:
                config.retry_backoff_factor = retry_backoff
                console.print(f"  ✓ Retry Backoff: {retry_backoff}")
                updated = True
            if output_format:
                config.output_format = output_format
                console.print(f"  ✓ Output Format: {output_format}")
                updated = True

            # Prompt for tenant ID update (unless already provided)
            if not tenant_id:
                current_tenant = config.tenant_id or ""
                new_tenant_id = click.prompt(
                    "New Tenant ID (press Enter to keep current)",
                    default=current_tenant,
                    show_default=False,
                )
                if new_tenant_id != current_tenant:
                    config.tenant_id = (
                        new_tenant_id if new_tenant_id and new_tenant_id.strip() else ""
                    )
                    updated = True
            else:
                config.tenant_id = tenant_id
                updated = True

            # Prompt for output format update (unless already provided)
            if not output_format:
                new_output_format = click.prompt(
                    "Output format",
                    type=click.Choice(["table", "json"], case_sensitive=False),
                    default=config.output_format,
                    show_default=False,
                )
                if new_output_format != config.output_format:
                    config.output_format = new_output_format
                    updated = True

            # Handle remaining advanced settings if in advanced mode
            if advanced:
                # Advanced mode: Prompt for base URL if not already provided
                if not base_url:
                    new_base_url = click.prompt(
                        "New Base URL (press Enter to keep current)",
                        default=config.base_url,
                        show_default=False,
                    )
                    if new_base_url != config.base_url:
                        config.base_url = new_base_url
                        updated = True

                # Prompt for API version if not already provided
                if not api_version:
                    new_api_version = click.prompt(
                        "API version",
                        default=config.api_version,
                        show_default=False,
                    )
                    if new_api_version != config.api_version:
                        config.api_version = new_api_version
                        updated = True
                # Prompt for timeout update if not already provided
                if not timeout:
                    new_timeout = click.prompt(
                        "Request timeout (seconds)",
                        type=int,
                        default=config.timeout,
                        show_default=False,
                    )
                    if new_timeout != config.timeout:
                        config.timeout = new_timeout
                        updated = True

                # Prompt for max retries update if not already provided
                if not max_retries:
                    new_max_retries = click.prompt(
                        "Maximum retries for failed requests",
                        type=int,
                        default=config.max_retries,
                        show_default=False,
                    )
                    if new_max_retries != config.max_retries:
                        config.max_retries = new_max_retries
                        updated = True

                # Prompt for retry backoff factor update if not already provided
                if not retry_backoff:
                    new_retry_backoff_factor = click.prompt(
                        "Retry backoff factor",
                        type=float,
                        default=config.retry_backoff_factor,
                        show_default=False,
                    )
                    if new_retry_backoff_factor != config.retry_backoff_factor:
                        config.retry_backoff_factor = new_retry_backoff_factor
                        updated = True
            else:
                # Non-advanced mode: Show tip about advanced options
                console.print(
                    "\n[dim]Use --advanced flag for custom endpoints and timeout settings[/dim]"
                )

            if updated:
                get_profile_manager().update_profile(profile_name, config)
                console.print(
                    f"\n[green]✓[/green] Profile '{profile_name}' updated with settings:"
                )
                console.print(f"  Base URL: {config.base_url}")
                console.print(f"  Tenant ID: {config.tenant_id or 'Not set'}")
                console.print(f"  Output Format: {config.output_format}")
            else:
                console.print("\n[yellow]No changes made[/yellow]")

    except ValueError as e:
        console.print(f"[bold red]Error:[/bold red] {str(e)}")


@profile.command("delete")
@click.argument("profile-name")
@click.option("--force", is_flag=True, help="Skip confirmation prompt")
def delete_profile(profile_name: str, force: bool = False) -> None:
    """Delete a profile.

    PROFILE-NAME: Name of the profile to delete.
    """
    try:
        # Prevent deletion of the 'default' profile
        if profile_name.lower() == "default":
            console.print(
                "[bold red]Error:[/bold red] Cannot delete the 'default' profile. "
                "This profile is required for system operations."
            )
            return

        # Check if profile exists
        if not get_profile_manager().profile_exists(profile_name):
            console.print(
                f"[bold red]Error:[/bold red] Profile '{profile_name}' doesn't exist"
            )
            return

        # Ask for confirmation unless --force is used
        if not force:
            if not click.confirm(
                f"Are you sure you want to delete profile '{profile_name}'? This action cannot be undone."
            ):
                console.print("Profile deletion cancelled.")
                return

        # Use the SDK's ProfileManager to delete the profile
        get_profile_manager().delete_profile(profile_name)
        console.print(f"[green]Profile '{profile_name}' deleted.[/green]")
    except ValueError as e:
        console.print(f"[bold red]Error:[/bold red] {str(e)}")


@profile.command("list")
@click.option(
    "--output",
    type=click.Choice(["table", "json"], case_sensitive=False),
    help="Output format (table or json)",
)
@click.option(
    "--detailed",
    is_flag=True,
    help="Show detailed information for each profile",
)
def list_profiles(output: Optional[str] = None, detailed: bool = False) -> None:
    """List all available profiles."""
    if detailed:
        # Use the enhanced ProfileManager method to get detailed profile information
        profile_details = get_profile_manager().list_profiles_with_details()

        if output and output.lower() == "json":
            if not profile_details:
                console.print(json.dumps({"error": "No profiles configured"}, indent=2))
            else:
                console.print(json.dumps({"profiles": profile_details}, indent=2))
        else:
            if not profile_details:
                show_no_profiles_message(output)
                return

            table = Table(title="Available Profiles")
            table.add_column("Profile")
            table.add_column("Default")
            table.add_column("Tenant ID")
            table.add_column("API URL")
            table.add_column("Credentials")
            table.add_column("Output Format")

            for profile in profile_details:
                is_default = "✓" if profile["is_default"] else ""

                table.add_row(
                    profile["name"],
                    is_default,
                    profile["tenant_id"],
                    profile["base_url"],
                    "smart-detected",
                    profile["output_format"],
                )

            console.print(table)
    else:
        # Use the standard ProfileManager method for a simple list
        profiles = get_profile_manager().list_profiles()
        default_profile = get_profile_manager().get_default_profile()

        if output and output.lower() == "json":
            if not profiles:
                console.print(json.dumps({"error": "No profiles configured"}, indent=2))
            else:
                profile_data = {
                    "profiles": profiles,
                    "default_profile": default_profile,
                }
                console.print(json.dumps(profile_data, indent=2))
        else:
            if not profiles:
                show_no_profiles_message(output)
                return

            table = Table(title="Available Profiles")
            table.add_column("Profile")
            table.add_column("Default")

            for profile_name in profiles:
                is_default = "✓" if profile_name == default_profile else ""
                table.add_row(profile_name, is_default)

            console.print(table)


@profile.command("current")
@click.option(
    "--output",
    type=click.Choice(["table", "json"], case_sensitive=False),
    help="Output format (table or json)",
)
def current_profile(output: Optional[str] = None) -> None:
    """Show the currently active profile name and essential configuration."""
    try:
        # Determine current profile using shared logic
        current = determine_current_profile()

        # Handle case where no profiles are configured
        if current is None:
            show_no_profiles_message(output)
            return

        # Get profile configuration without creating a session (no credentials needed)
        try:
            profile_manager = get_profile_manager()

            # Get profile config
            if current == "default":
                config = profile_manager.get_default_config()
            else:
                config = profile_manager.get_profile_config(current)

            # Determine output format - use provided output or profile's configured format
            output_format = output if output else config.output_format

            # Essential profile information only
            profile_data = {
                "name": current,
                "base_url": config.base_url,
                "tenant_id": config.tenant_id or None,
                "output_format": config.output_format,
            }

            if output_format and output_format.lower() == "json":
                console.print(json.dumps(profile_data, indent=2))
            else:
                # Simple table format
                table = Table(title=f"Current Profile: {current}")
                table.add_column("Property", style="cyan")
                table.add_column("Value", style="green")

                # Add essential information
                table.add_row("Profile Name", current)
                table.add_row("Base URL", config.base_url)
                table.add_row("Tenant ID", config.tenant_id or "Not set")
                table.add_row("Output Format", config.output_format)

                console.print(table)

                # Show tip about profile show command for detailed info
                console.print(
                    "\n[dim]Use 'day2 profile show' for detailed configuration[/dim]"
                )

        except (ImportError, AttributeError, ValueError) as e:
            # Try to determine output format from profile config even when session fails
            fallback_output_format = output
            if not fallback_output_format:
                try:
                    # Try to load profile config directly to get output format
                    profile_manager = get_profile_manager()
                    if profile_manager.profile_exists(current):
                        profile_config = profile_manager.get_profile_config(current)
                        fallback_output_format = profile_config.output_format
                    else:
                        fallback_output_format = "table"
                except (ImportError, AttributeError, ValueError, OSError):
                    fallback_output_format = "table"

            if fallback_output_format and fallback_output_format.lower() == "json":
                error_data = {
                    "name": current,
                    "error": str(e).replace("\n", " "),  # Remove newlines to fix JSON
                }
                console.print(json.dumps(error_data, indent=2))
            else:
                console.print(f"Current profile: [cyan]{current}[/cyan]")
                console.print(
                    f"\n[yellow]Warning: Could not load configuration: {str(e)}[/yellow]"
                )

    except (ImportError, AttributeError, ValueError) as e:
        fallback_output_format = output if output else "table"
        if fallback_output_format and fallback_output_format.lower() == "json":
            error_data = {
                "error": str(e).replace("\n", " ")
            }  # Remove newlines to fix JSON
            console.print(json.dumps(error_data, indent=2))
        else:
            console.print(f"[red]Error: {str(e)}[/red]")


@profile.command("use")
@click.argument("profile-name")
def use_profile(profile_name: str) -> None:
    """Switch to a different profile.

    PROFILE-NAME: Name of the profile to switch to.
    """
    try:
        # Use the SDK's ProfileManager to set the default profile
        get_profile_manager().set_default_profile(profile_name)
        console.print(f"[green]Switched to profile '{profile_name}'.[/green]")
    except ValueError as e:
        console.print(f"[bold red]Error:[/bold red] {str(e)}")


@profile.command("show")
@click.argument("profile-name", required=False)
@click.option(
    "--output",
    type=click.Choice(["table", "json"], case_sensitive=False),
    help="Output format (table or json)",
)
def show_profile(
    profile_name: Optional[str] = None, output: Optional[str] = None
) -> None:
    """Show detailed information about a profile.

    PROFILE-NAME: Name of the profile to show. If not provided, shows the current/default profile.
    """
    try:
        # Determine which profile to show
        if not profile_name:
            # Use shared logic to determine current profile
            profile_name = determine_current_profile()

        # Handle case where no profiles are configured
        if profile_name is None:
            show_no_profiles_message(output)
            return

        # Check if profile exists
        if profile_name != "default" and not get_profile_manager().profile_exists(
            profile_name
        ):
            console.print(
                f"[bold red]Error:[/bold red] Profile '{profile_name}' doesn't exist"
            )
            return

        # Get profile config without creating a session
        profile_manager = get_profile_manager()
        if profile_name == "default":
            config = profile_manager.get_default_config()
            is_default = True
        else:
            config = profile_manager.get_profile_config(profile_name)
            default_profile = profile_manager.get_default_profile()
            is_default = profile_name == default_profile

        # Determine output format - use provided output or profile's configured format
        output_format = output if output else config.output_format

        # For profile show, we just display the configured tenant_id
        # No need to fetch runtime data which requires credentials
        display_tenant_id = config.tenant_id

        # Prepare profile data
        profile_data = {
            "name": profile_name,
            "is_default": is_default,
            "tenant_id": display_tenant_id,
            "base_url": config.base_url,
            "api_version": config.api_version,
            "timeout": config.timeout,
            "max_retries": config.max_retries,
            "retry_backoff_factor": config.retry_backoff_factor,
            "retry_min_delay": config.retry_min_delay,
            "retry_max_delay": config.retry_max_delay,
            "output_format": config.output_format,
        }

        if output_format and output_format.lower() == "json":
            console.print(json.dumps(profile_data, indent=2))
        else:
            # Create a table with two columns: Property and Value
            table = Table(title=f"Profile: {profile_name}")
            table.add_column("Property")
            table.add_column("Value")

            # Add default status
            table.add_row("Default Profile", "Yes" if is_default else "No")

            # Add all config properties
            table.add_row("Tenant ID", display_tenant_id or "<not set>")
            table.add_row("API URL", config.base_url)
            table.add_row("API Version", config.api_version)
            table.add_row("Timeout", str(config.timeout))
            table.add_row("Max Retries", str(config.max_retries))
            table.add_row("Retry Backoff Factor", str(config.retry_backoff_factor))
            table.add_row("Retry Min Delay", str(config.retry_min_delay))
            table.add_row("Retry Max Delay", str(config.retry_max_delay))
            table.add_row("Output Format", config.output_format)

            console.print(table)
    except (ValueError, IOError, KeyError, configparser.Error) as e:
        console.print(f"[bold red]Error:[/bold red] {str(e)}")
