"""Authentication commands for the MontyCloud DAY2 CLI."""

# pylint: disable=redefined-outer-name

import configparser
import datetime
import json
import os
import sys
from pathlib import Path
from typing import Optional

import click
from rich.console import Console
from rich.table import Table

from day2.auth.credentials import Credentials
from day2.client.config import Config
from day2.client.profile import ProfileManager
from day2.client.user_context import UserContext
from day2.session import Session
from day2_cli.utils.context import get_global_session

console = Console()


@click.group()
def auth() -> None:
    """Authentication commands."""


@auth.command("configure", hidden=True)
@click.option(
    "--api-key", prompt=False, hide_input=True, help="Your MontyCloud Day2 API key"
)
@click.option("--api-secret-key", help="Your MontyCloud Day2 API secret key (required)")
@click.option(
    "--verbose",
    "-v",
    is_flag=True,
    help="Show verbose information about configuration process",
)
def configure(
    api_key: Optional[str], api_secret_key: Optional[str], verbose: bool
) -> None:
    """Configure authentication credentials (deprecated).

    This command is deprecated. Use 'day2 auth login' instead.
    """
    console.print(
        "[yellow]Warning: 'configure' is deprecated. Use 'day2 auth login' instead.[/yellow]"
    )
    # Create configuration directory if it doesn't exist
    config_dir = Path.home() / ".day2"
    if verbose:
        console.print(f"[dim]Configuration directory: {config_dir}[/dim]")
    config_dir.mkdir(exist_ok=True)
    if verbose:
        console.print("[dim]✓ Configuration directory ready[/dim]")

    # Save API key to credentials file
    credentials_file = config_dir / "credentials"
    if verbose:
        console.print(f"[dim]Credentials file: {credentials_file}[/dim]")
    config_parser = configparser.ConfigParser()
    existing_api_key = None
    if credentials_file.exists():
        if verbose:
            console.print("[dim]Reading existing credentials...[/dim]")
        try:
            config_parser.read(credentials_file)
            if "DEFAULT" in config_parser:
                existing_api_key = config_parser["DEFAULT"].get("api_key")
                if verbose and existing_api_key:
                    console.print(
                        f"[dim]✓ Found existing API key (...{existing_api_key[-4:]})[/dim]"
                    )
        except (configparser.Error, IOError):
            if verbose:
                console.print("[dim]⚠ Could not read existing credentials file[/dim]")
    else:
        if verbose:
            console.print("[dim]No existing credentials file found[/dim]")

    if not api_key:
        # Show masked key if it exists
        prompt_text = "Your MontyCloud Day2 API key"
        if existing_api_key:
            masked_key = f"{'*' * (len(existing_api_key) - 4)}{existing_api_key[-4:]}"
            prompt_text = f"Your MontyCloud Day2 API key [{masked_key}]"

        # Prompt for key, allowing empty input to keep existing key
        new_key = click.prompt(prompt_text, default="", show_default=False)

        # Use existing key if user just pressed Enter
        if not new_key and existing_api_key:
            api_key = existing_api_key
        elif new_key:
            api_key = new_key
        else:
            # User provided empty input and no existing key
            console.print("[bold red]Error:[/bold red] API key is required.")
            return

    # Ensure api_key is str type for mypy
    assert api_key is not None

    # Ensure DEFAULT section exists
    if "DEFAULT" not in config_parser:
        config_parser["DEFAULT"] = {}

    config_parser["DEFAULT"]["api_key"] = api_key

    # Handle API secret key similar to API key
    existing_api_secret_key = None
    if "DEFAULT" in config_parser:
        existing_api_secret_key = config_parser["DEFAULT"].get("api_secret_key")

    if not api_secret_key:
        # Show masked key if it exists
        prompt_text = "Your MontyCloud Day2 API secret key"
        if existing_api_secret_key:
            masked_key = f"{'*' * (len(existing_api_secret_key) - 4)}{existing_api_secret_key[-4:]}"
            prompt_text = f"Your MontyCloud Day2 API secret key [{masked_key}]"

        # Prompt for key, allowing empty input to keep existing key
        new_key = click.prompt(prompt_text, default="", show_default=False)

        # Use existing key if user just pressed Enter
        if not new_key and existing_api_secret_key:
            api_secret_key = existing_api_secret_key
        elif new_key:
            api_secret_key = new_key
        else:
            # User provided empty input and no existing key
            console.print("[bold red]Error:[/bold red] API secret key is required.")
            return

    # Ensure api_secret_key is str type for mypy
    assert api_secret_key is not None
    config_parser["DEFAULT"]["api_secret_key"] = api_secret_key

    with open(credentials_file, "w", encoding="utf-8") as f:
        config_parser.write(f)

    # Create a default profile if none exists
    profile_manager = ProfileManager()

    # Try to fetch user context - but make this optional
    # Create a default profile if none exists
    if not profile_manager.list_profiles():
        # Create a default profile with system defaults
        default_config = Config()

        # Try to get tenant ID from credentials if provided
        if "DEFAULT" in config_parser and "tenant_id" in config_parser["DEFAULT"]:
            default_config.tenant_id = config_parser["DEFAULT"]["tenant_id"]

        # Create the default profile
        profile_manager.create_profile("default", default_config)
        profile_manager.set_default_profile("default")

        # Note: We'll attempt to fetch user context later when the user uses the CLI
        # This avoids the error during initial configuration
        console.print("[green]Created default profile.[/green]")

    console.print("[green]Authentication configured successfully.[/green]")

    # Show a summary of what was saved
    if api_key:
        if existing_api_key == api_key or "--api-key" in sys.argv:
            console.print(f"API key: [bold]{'*' * 8}{api_key[-4:]}[/bold]")
        console.print(f"API key saved to: {credentials_file}")

    if api_secret_key:
        console.print(f"API secret key: [bold]{'*' * 8}{api_secret_key[-4:]}[/bold]")
        console.print(f"API secret key saved to: {credentials_file}")

    # Show a summary of what was updated
    updates = []
    if api_key and not existing_api_key:
        updates.append("API key")
    if api_secret_key:
        updates.append("API secret key")

    if updates:
        console.print(f"[green]Updated: {', '.join(updates)}[/green]")


@auth.command("whoami")
@click.option(
    "--output",
    "-o",
    type=click.Choice(["table", "json"]),
    default="table",
    help="Output format",
)
@click.option("--refresh", is_flag=True, help="Force refresh user information from API")
@click.option(
    "--verbose",
    "-v",
    is_flag=True,
    help="Show verbose information about cache usage and API calls",
)
def whoami(output: str, refresh: bool, verbose: bool) -> None:
    """Display current user and authentication status."""
    try:
        # Create a session with global profile
        session = get_global_session()

        # Get user context - use cached unless refresh is requested
        user_context = None
        if not refresh:
            if verbose:
                console.print("[dim]Checking for cached user context...[/dim]")
            user_context = UserContext.load()
            if verbose:
                if user_context:
                    console.print(
                        f"[dim]✓ Found cached user context for {user_context.user_id}[/dim]"
                    )
                else:
                    console.print("[dim]✗ No cached user context found[/dim]")

        # If no cached context or refresh requested, fetch from API
        if not user_context or refresh:
            if refresh:
                console.print("[dim]Refreshing user information...[/dim]")
            else:
                console.print("[dim]Fetching user information...[/dim]")
            user_context = session.user.get_user()
            if user_context:
                # Cache the fresh data
                if verbose:
                    console.print("[dim]Saving user context to cache...[/dim]")
                user_context.save()
                if verbose:
                    console.print("[dim]✓ User context cached[/dim]")

        if not user_context:
            console.print(
                "[red]Error: Not authenticated or unable to retrieve user information.[/red]"
            )
            console.print(
                "[yellow]Please run 'day2 auth login' to authenticate.[/yellow]"
            )
            return

        # Get tenant name - use cached if available, otherwise fetch from API
        tenant_name = (
            user_context.tenant_name if hasattr(user_context, "tenant_name") else None
        )
        if not tenant_name and session.tenant_id:
            try:
                if verbose:
                    console.print("[dim]Fetching tenant name from API...[/dim]")
                tenant_response = session.tenant.get_tenant(session.tenant_id)
                if tenant_response:
                    tenant_name = tenant_response.name
                    # Update cached user context with tenant name
                    user_context.tenant_name = tenant_name
                    user_context.save()
                    if verbose:
                        console.print("[dim]✓ Tenant name cached[/dim]")
            except (ImportError, AttributeError, ValueError):
                if verbose:
                    console.print("[dim]✗ Failed to fetch tenant name[/dim]")
                # Tenant name is optional
        elif tenant_name and verbose:
            console.print(f"[dim]✓ Using cached tenant name: {tenant_name}[/dim]")

        # Display user information
        if output == "json":
            # Output as JSON
            user_data = {
                "user_id": user_context.user_id,
                "email": user_context.email,
                "name": user_context.name,
                "username": user_context.username,
                "tenant_id": session.tenant_id,
                "tenant_name": tenant_name,
                "profile": session.config.profile or "default",
                "api_endpoint": session.config.base_url,
            }
            console.print(json.dumps(user_data, indent=2))
        else:
            # Output as table
            table = Table(show_header=False, box=None)
            table.add_column("Property", style="cyan")
            table.add_column("Value", style="green")

            # Show name and email if available, otherwise fallback to user ID
            if user_context.name or user_context.email:
                display_name = user_context.name or user_context.username or "Unknown"
                if user_context.email:
                    display_name += f" ({user_context.email})"
                table.add_row("User", display_name)
            else:
                table.add_row("User", user_context.user_id or "N/A")

            table.add_row("Profile", session.config.profile or "default")

            if session.tenant_id and tenant_name:
                table.add_row("Tenant", f"{tenant_name} ({session.tenant_id})")
            elif session.tenant_id:
                table.add_row("Tenant", session.tenant_id)
            else:
                table.add_row("Tenant", "Not set")

            table.add_row("API Endpoint", session.config.base_url)

            console.print(table)

    except (ImportError, AttributeError, ValueError) as e:
        console.print(f"[red]Error: {str(e)}[/red]")
        console.print("[yellow]Please run 'day2 auth login' to authenticate.[/yellow]")


@auth.command("login")
@click.option(
    "--profile", help="Profile name to create/update (defaults to current profile)"
)
@click.option(
    "--api-key", help="Your MontyCloud Day2 API key (will prompt if not provided)"
)
@click.option(
    "--api-secret-key",
    help="Your MontyCloud Day2 API secret key (required, will prompt if not provided)",
)
@click.option(
    "--base-url",
    help="Base URL for the API (default: https://api.montycloud.com/day2/api)",
)
@click.option(
    "--verbose", "-v", is_flag=True, help="Enable verbose output to see API calls"
)
def login(
    profile: Optional[str],
    api_key: Optional[str],
    api_secret_key: Optional[str],
    base_url: Optional[str],
    verbose: bool,
) -> None:
    """Authenticate and create/update a profile.

    This command authenticates with the Day2 API, automatically detects your tenant,
    and creates or updates a profile with these settings.
    """
    # Enable verbose logging if requested
    if verbose:
        import logging

        logging.basicConfig(
            level=logging.DEBUG, format="[%(levelname)s] %(name)s: %(message)s"
        )

    try:
        # Determine which profile to use
        profile_manager = ProfileManager()
        profile_explicitly_provided = bool(profile)

        if not profile:
            # Use environment variable, then default profile, then "default"
            profile = (
                os.environ.get("DAY2_PROFILE")
                or profile_manager.get_default_profile()
                or "default"
            )
        else:
            # Profile was explicitly provided via --profile flag
            # Validate that it exists to prevent typos and confusion
            if not profile_manager.profile_exists(profile):
                available_profiles = profile_manager.list_profiles()
                if available_profiles:
                    # Check for potential typos by finding similar profile names
                    import difflib

                    close_matches = difflib.get_close_matches(
                        profile, available_profiles, n=3, cutoff=0.6
                    )

                    if close_matches:
                        suggestion_list = ", ".join(close_matches)
                        error_msg = (
                            f"Profile '{profile}' doesn't exist.\n"
                            f"Did you mean: {suggestion_list}?\n"
                            f"Available profiles: {', '.join(available_profiles)}\n\n"
                            f"To create a new profile, use: day2 profile create {profile}"
                        )
                    else:
                        profile_list = ", ".join(available_profiles)
                        error_msg = (
                            f"Profile '{profile}' doesn't exist.\n"
                            f"Available profiles: {profile_list}\n\n"
                            f"To create a new profile, use: day2 profile create {profile}"
                        )
                else:
                    error_msg = (
                        f"Profile '{profile}' doesn't exist.\n"
                        f"No profiles exist yet. You can either:\n"
                        f"  1. Run 'day2 auth login' without --profile to create a default profile\n"
                        f"  2. Create the profile first: day2 profile create {profile}"
                    )
                raise click.ClickException(error_msg)

        # Get existing profile config if it exists
        existing_config = None
        existing_api_key = None
        existing_api_secret_key = None

        if profile_manager.profile_exists(profile):
            existing_config = profile_manager.get_profile_config(profile)
            # Try to get existing credentials
            try:
                existing_session = Session(profile=profile, use_user_context=False)
                existing_api_key = existing_session.credentials.api_key
                existing_api_secret_key = existing_session.credentials.secret_key
            except (ImportError, AttributeError, ValueError):
                pass

        # If API key not provided, prompt with existing value shown
        if not api_key:
            if existing_api_key:
                masked_key = (
                    f"{'*' * (len(existing_api_key) - 4)}{existing_api_key[-4:]}"
                )
                api_key = click.prompt(
                    f"API key [{masked_key}]",
                    default="",
                    hide_input=True,
                    show_default=False,
                )
                if not api_key:  # User pressed enter, keep existing
                    api_key = existing_api_key
                    console.print(
                        f"  ✓ Using existing API key (...{existing_api_key[-4:]})"
                    )
                else:
                    # Show confirmation of what was entered
                    console.print(
                        f"  ✓ API key entered (...{api_key[-4:] if api_key else 'None'})"
                    )
            else:
                api_key = click.prompt("API key", hide_input=True)
                # Show confirmation of what was entered
                console.print(
                    f"  ✓ API key entered (...{api_key[-4:] if api_key else 'None'})"
                )

        # If API secret key not provided, prompt with existing value shown
        if not api_secret_key:
            if existing_api_secret_key:
                masked_key = f"{'*' * (len(existing_api_secret_key) - 4)}{existing_api_secret_key[-4:]}"
                api_secret_key = click.prompt(
                    f"API secret key [{masked_key}]",
                    default="",
                    hide_input=True,
                    show_default=False,
                )
                if not api_secret_key:  # User pressed enter, keep existing
                    api_secret_key = existing_api_secret_key
                    console.print(
                        f"  ✓ Using existing API secret key (...{existing_api_secret_key[-4:]})"
                    )
                else:
                    # Show confirmation of what was entered
                    console.print(
                        f"  ✓ API secret key entered (...{api_secret_key[-4:] if api_secret_key else 'None'})"
                    )
            else:
                api_secret_key = click.prompt("API secret key", hide_input=True)
                # Show confirmation of what was entered
                console.print(
                    f"  ✓ API secret key entered (...{api_secret_key[-4:] if api_secret_key else 'None'})"
                )

        # Use provided base_url or existing one
        if not base_url and existing_config:
            base_url = existing_config.base_url

        # Show what configuration is being used
        actual_base_url = (
            base_url
            or (existing_config.base_url if existing_config else None)
            or "https://api.montycloud.com/day2/api"
        )
        console.print(f"\n[dim]Using profile: {profile}[/dim]")
        console.print(f"[dim]API endpoint: {actual_base_url}[/dim]")
        console.print("[dim]Authenticating...[/dim]\n")

        # Create a temporary session to fetch user info
        session = Session(
            api_key=api_key,
            api_secret_key=api_secret_key,
            base_url=base_url,
            use_user_context=False,
        )

        # Fetch user context
        user_context = session.user.get_user()
        if not user_context:
            console.print(
                "[red]Error: Failed to authenticate with the provided credentials.[/red]"
            )
            console.print(
                "[yellow]Please check your API key, secret key, and base URL.[/yellow]"
            )
            sys.exit(1)

        # Get tenant name and update user context
        tenant_name = None
        if user_context.tenant_id:
            try:
                tenant_response = session.tenant.get_tenant(user_context.tenant_id)
                if tenant_response:
                    tenant_name = tenant_response.name
                    # Update user context with tenant name for caching
                    user_context.tenant_name = tenant_name
            except (ImportError, AttributeError, ValueError):
                pass  # Tenant name is optional

        # Display authentication info
        console.print("[green]✓[/green] Authenticated successfully.")

        # Show user information
        if user_context.name or user_context.email:
            display_name = user_context.name or user_context.username or "Unknown"
            if user_context.email:
                display_name += f" ({user_context.email})"
            console.print(f"[green]✓[/green] User: {display_name}")
        elif user_context.user_id:
            console.print(f"[green]✓[/green] User ID: {user_context.user_id}")

        if user_context.tenant_id:
            tenant_display = (
                f"{tenant_name} (id: {user_context.tenant_id})"
                if tenant_name
                else user_context.tenant_id
            )
            console.print(f"[green]✓[/green] Your tenant: {tenant_display}")
            console.print(
                "[dim]Note: You can switch to other accessible tenants by updating the profile[/dim]"
            )

        # Create/update profile with all settings
        # Get existing config or create new one
        if profile_manager.profile_exists(profile):
            config = profile_manager.get_profile_config(profile)
        else:
            config = Config()

        # Update config with new values
        config.tenant_id = user_context.tenant_id or ""
        if base_url:
            config.base_url = base_url

        # Determine credential storage scope
        credential_profile_name = profile  # Default to the determined profile

        # Check if DEFAULT credentials already exist
        credentials_file = Path.home() / ".day2" / "credentials"
        has_default_credentials = False
        if credentials_file.exists():
            cred_parser = configparser.ConfigParser()
            cred_parser.read(credentials_file)
            # Check if DEFAULT section exists with credentials
            if "DEFAULT" in cred_parser and cred_parser["DEFAULT"].get("api_key"):
                has_default_credentials = True

        # Check if we should prompt for credential scope
        # Don't prompt if:
        # 1. This is first time setup (no DEFAULT credentials exist)
        # 2. User explicitly provided --profile
        # 3. Current profile is "default"
        should_prompt = (
            has_default_credentials  # Only prompt if DEFAULT credentials already exist
            and not profile_explicitly_provided  # User didn't specify --profile
            and profile != "default"  # User has an active non-default profile
            and (
                os.environ.get("DAY2_PROFILE") or profile_manager.get_default_profile()
            )  # Profile is actively set
        )

        if should_prompt:
            console.print(f"\nCurrent profile: [cyan]{profile}[/cyan]")
            console.print("Store credentials for:")
            console.print("  [1] All profiles (shared) \\[default]")
            console.print(f"  [2] Current profile ({profile}) only")

            choice = click.prompt("Choice", default="1", show_default=False)

            if choice == "2":
                # Store for specific profile - use profile name as-is
                credential_profile_name = profile
                console.print(
                    f"  ✓ Will store credentials for profile '{profile}' only"
                )
            else:
                # Store shared - use "default" to force DEFAULT section
                credential_profile_name = "default"
                console.print("  ✓ Will store shared credentials for all profiles")

        # Determine credential section based on user choice
        if should_prompt:
            # User was prompted and made an explicit choice
            if credential_profile_name == "default":
                # User explicitly chose "all profiles" - force DEFAULT section
                credential_section = "DEFAULT"
            else:
                # User chose specific profile - use profile name
                credential_section = credential_profile_name
        else:
            # No prompt was shown
            if not has_default_credentials:
                # First time setup
                if profile_explicitly_provided and profile != "default":
                    # User explicitly specified a non-default profile - respect their choice
                    credential_section = credential_profile_name
                    console.print(
                        f"\n[dim]First time setup - storing credentials for profile {profile}[/dim]"
                    )
                else:
                    # No explicit profile or profile is "default" - use DEFAULT section
                    credential_section = "DEFAULT"
                    console.print(
                        "\n[dim]First time setup - storing credentials for all profiles[/dim]"
                    )
            else:
                # Use the profile name (which will check profile first, then DEFAULT)
                credential_section = credential_profile_name

        if verbose:
            if credential_section == "DEFAULT":
                console.print(
                    f"[dim]Smart detection: Using shared credentials for {profile}[/dim]"
                )
            else:
                console.print(
                    f"[dim]Smart detection: Using profile-specific credentials for {profile}[/dim]"
                )

        # Use the Credentials class to save credentials with case-insensitive handling
        Credentials.save_credentials_to_section(
            api_key=api_key,
            api_secret_key=api_secret_key,
            section_name=credential_section,
            credentials_file_path=credentials_file,
        )

        # Show which credential section is being used (only if not already shown in verbose mode)
        if not verbose and not should_prompt:  # Don't show if we already prompted
            # Get the normalized section name that was actually used
            normalized_section = Credentials.normalize_section_name(credential_section)
            if normalized_section == "DEFAULT":
                console.print(f"[dim]Using shared credentials for {profile}[/dim]")
            else:
                console.print(
                    f"[dim]Using profile-specific credentials for {profile}[/dim]"
                )

        # Save or update the profile
        if profile_manager.profile_exists(profile):
            profile_manager.update_profile(profile, config)
            console.print(f"Profile '{profile}' updated")
        else:
            profile_manager.create_profile(profile, config)
            console.print(f"Profile '{profile}' created")

        # Save user context
        user_context.save()

        # Set as default if it's the first profile or if it's named "default"
        profiles = profile_manager.list_profiles()
        if len(profiles) == 1 or profile == "default":
            profile_manager.set_default_profile(profile)
            console.print(f"Profile '{profile}' set as default")

    except (ImportError, AttributeError, ValueError) as e:
        console.print(f"[red]Error: {str(e)}[/red]")
        sys.exit(1)


@auth.command("check", hidden=True)
@click.option(
    "--profile", help="Profile to check (defaults to current/default profile)"
)
@click.option(
    "--verbose",
    "-v",
    is_flag=True,
    help="Show verbose connectivity and configuration details",
)
def check_auth(profile: Optional[str], verbose: bool) -> None:
    """Check authentication configuration and connectivity.

    This command shows the current authentication setup and tests
    connectivity without saving any changes.
    """
    try:
        # Show profile being used
        if not profile:
            pm = ProfileManager()
            if verbose:
                console.print("Determining profile to check...")
            profile = (
                os.environ.get("DAY2_PROFILE") or pm.get_default_profile() or "default"
            )
            if verbose:
                env_profile = os.environ.get("DAY2_PROFILE")
                default_profile = pm.get_default_profile()
                if env_profile:
                    console.print(f"Using DAY2_PROFILE: {env_profile}")
                elif default_profile:
                    console.print(f"Using default profile: {default_profile}")
                else:
                    console.print("Using system default profile")

        console.print("[bold]Authentication status:\n")
        console.print(f"Profile: {profile}")

        # Try to create a session
        try:
            if verbose:
                console.print(f"Creating session for profile '{profile}'...")
            session = Session(profile=profile, use_user_context=False)
            if verbose:
                console.print("Session created successfully")

            # Show configuration
            console.print(f"API Endpoint: {session.config.base_url}")

            # Check for API key
            if session.credentials.api_key:
                masked_key = f"{'*' * (len(session.credentials.api_key) - 4)}{session.credentials.api_key[-4:]}"
                console.print(f"API Key: {masked_key}")
            else:
                console.print("API Key: Not configured")

            # Check for API secret key
            if session.credentials.secret_key:
                masked_key = f"{'*' * (len(session.credentials.secret_key) - 4)}{session.credentials.secret_key[-4:]}"
                console.print(f"API Secret Key: {masked_key}")
            else:
                console.print("API Secret Key: Not configured (required)")

            # Check tenant ID
            if session.tenant_id:
                console.print(f"Tenant ID: {session.tenant_id}")
            else:
                console.print("Tenant ID: Not set (will auto-detect)")

            # Test connectivity
            console.print("\nTesting connection...")
            if verbose:
                console.print(f"Making API call to {session.config.base_url}/user")
            user_context = session.user.get_user()

            if user_context:
                console.print("Successfully connected to API")
                console.print(f"User ID: {user_context.user_id}")
                console.print(f"Tenant ID: {user_context.tenant_id}")
                if verbose and hasattr(user_context, "email"):
                    console.print(f"Email: {user_context.email}")
                if verbose and hasattr(user_context, "name"):
                    console.print(f"Name: {user_context.name}")
            else:
                console.print("Failed to connect to API")
                if verbose:
                    console.print("No user context returned from API")

        except (ImportError, AttributeError, ValueError) as e:
            console.print(f"\nConfiguration Error: {str(e)}")
            console.print("\nTroubleshooting tips:")
            console.print("1. Check if the profile exists: day2 profile list")
            console.print("2. Verify profile configuration: day2 profile list")
            console.print(f"3. Re-authenticate: day2 auth login --profile {profile}")

    except (ImportError, AttributeError, ValueError) as e:
        console.print(f"[red]Error: {str(e)}[/red]")


@auth.command("cache", hidden=True)
@click.option("--clear", is_flag=True, help="Clear the cached user context")
@click.option(
    "--verbose",
    "-v",
    is_flag=True,
    help="Show verbose information about cache operations",
)
def cache_info(clear: bool, verbose: bool) -> None:
    """Show or clear cached user context information."""
    config_dir = Path.home() / ".day2"
    user_context_file = config_dir / "user_context"

    if verbose:
        console.print(f"Configuration directory: {config_dir}")
        console.print(f"User context file: {user_context_file}")

    if clear:
        if verbose:
            console.print("Checking for cache file to clear...")

        if user_context_file.exists():
            if verbose:
                console.print("Cache file found, removing...")
            user_context_file.unlink()
            console.print("User context cache cleared")
            if verbose:
                console.print("Cache file deleted")
        else:
            if verbose:
                console.print("No cache file exists to clear")
            console.print("No cached user context found")
        return

    # Show cache info
    console.print("[bold]User context:\n")
    console.print(f"Cache file: {user_context_file}")

    if user_context_file.exists():
        try:
            if verbose:
                console.print("Reading cache file...")

            config_parser = configparser.ConfigParser()
            config_parser.read(user_context_file)

            if "DEFAULT" in config_parser:
                data = dict(config_parser["DEFAULT"])
                if verbose:
                    console.print(f"Successfully parsed {len(data)} fields")

                console.print("Status: Found")
                console.print(f"User ID: {data.get('user_id', 'N/A')}")
                console.print(f"Email: {data.get('email', 'N/A')}")
                console.print(f"Name: {data.get('name', 'N/A')}")
                console.print(f"Tenant ID: {data.get('tenant_id', 'N/A')}")
                console.print(f"Tenant Name: {data.get('tenant_name', 'N/A')}")

                timestamp = os.path.getmtime(user_context_file)
                dt = datetime.datetime.fromtimestamp(timestamp)
                console.print(f"Last updated: {dt.strftime('%Y-%m-%d %H:%M:%S')}")

                if verbose:
                    # Show file size
                    file_size = user_context_file.stat().st_size
                    console.print(f"[dim]File size: {file_size} bytes[/dim]")
                    # Show raw data
                    console.print(f"[dim]Raw data: {dict(data)}[/dim]")
            else:
                console.print("Status: [red]Invalid - no DEFAULT section[/red]")

        except (ImportError, AttributeError, ValueError) as e:
            console.print(f"Status: [red]Invalid - {str(e)}[/red]")
    else:
        console.print("Status: [yellow]Not found[/yellow]")


@auth.command("logout")
@click.option(
    "--all",
    "all_profiles",
    is_flag=True,
    help="Clear all credentials for all profiles (deletes entire credentials file)",
)
@click.option(
    "--profile",
    help="Clear credentials for specific profile instead of current profile",
)
@click.option(
    "--verbose",
    "-v",
    is_flag=True,
    help="Show verbose information about what is being cleared",
)
def logout(all_profiles: bool, profile: Optional[str], verbose: bool) -> None:
    """Log out and clear authentication credentials.

    By default, clears credentials only for the current active profile.
    Use --all to clear all credentials for all profiles.
    Use --profile to target a specific profile.
    """
    config_dir = Path.home() / ".day2"
    credentials_file = config_dir / "credentials"

    if verbose:
        console.print(f"[dim]Configuration directory: {config_dir}[/dim]")
        console.print(f"[dim]Credentials file: {credentials_file}[/dim]")

    if not credentials_file.exists():
        if verbose:
            console.print("[dim]No credentials file exists to clear[/dim]")
        console.print("[yellow]No credentials file found.[/yellow]")
        return

    if all_profiles:
        # Nuclear option: delete entire credentials file
        scope_description = "all credentials for all profiles"
        if not click.confirm(f"Are you sure you want to clear {scope_description}?"):
            console.print("[yellow]Operation cancelled.[/yellow]")
            return

        if verbose:
            console.print(
                "[dim]Clearing all credentials (deleting entire file)...[/dim]"
            )
        try:
            credentials_file.unlink()
            console.print("[green]All credentials cleared successfully.[/green]")
            if verbose:
                console.print("[dim]✓ Credentials file deleted[/dim]")
        except IOError as e:
            console.print(f"[red]Failed to clear credentials: {str(e)}[/red]")
        return

    # Profile-specific logout
    try:
        # Determine target profile
        profile_manager = ProfileManager()
        if profile:
            target_profile = profile
            if (
                not profile_manager.profile_exists(target_profile)
                and target_profile != "default"
            ):
                console.print(
                    f"[red]Error: Profile '{target_profile}' doesn't exist.[/red]"
                )
                return
        else:
            # Use current active profile
            target_profile = (
                os.environ.get("DAY2_PROFILE")
                or profile_manager.get_default_profile()
                or "default"
            )

        # Read existing credentials file
        cred_parser = configparser.ConfigParser()
        cred_parser.read(credentials_file)

        # Determine which credential section this profile uses
        # Use same logic as Credentials class: check for profile-specific section first, then DEFAULT
        if target_profile != "default" and target_profile in cred_parser:
            credential_section = target_profile
        else:
            credential_section = "DEFAULT"

        # Check if the credential section actually exists and has content
        if credential_section == "DEFAULT":
            if not cred_parser.defaults():
                console.print(
                    f"[yellow]No credentials found for profile '{target_profile}'.[/yellow]"
                )
                return
        else:
            if credential_section not in cred_parser:
                console.print(
                    f"[yellow]No credentials found for profile '{target_profile}'.[/yellow]"
                )
                return

        # Show scope and confirm
        if credential_section == "DEFAULT":
            scope_description = (
                f"shared credentials (used by profile '{target_profile}' and others)"
            )
        else:
            scope_description = f"credentials for profile '{target_profile}' only"

        if not click.confirm(f"Are you sure you want to clear {scope_description}?"):
            console.print("[yellow]Operation cancelled.[/yellow]")
            return

        if verbose:
            console.print(
                f"[dim]Clearing credentials from section [{credential_section}]...[/dim]"
            )

        # Remove the specific section
        if credential_section == "DEFAULT":
            # For DEFAULT section, we need to clear all defaults
            for key in list(cred_parser.defaults().keys()):
                cred_parser.remove_option("DEFAULT", key)
        else:
            cred_parser.remove_section(credential_section)

        # Write back the modified file (or delete if empty)
        # Check if any sections remain (sections() doesn't include DEFAULT, so check both)
        has_remaining_sections = bool(cred_parser.sections())
        # For DEFAULT section, we need to check if it has content, not if it "exists"
        # because has_section('DEFAULT') always returns False
        has_default_with_content = bool(cred_parser.defaults())

        if has_remaining_sections or has_default_with_content:
            with open(credentials_file, "w", encoding="utf-8") as f:
                cred_parser.write(f)
            if verbose:
                console.print(
                    f"[dim]✓ Removed section [{credential_section}] from credentials file[/dim]"
                )
        else:
            # File would be empty, so delete it
            credentials_file.unlink()
            if verbose:
                console.print(
                    "[dim]✓ Credentials file deleted (was empty after removal)[/dim]"
                )

        if credential_section == "DEFAULT":
            console.print("[green]Shared credentials cleared successfully.[/green]")
            console.print(
                f"[dim]Profile '{target_profile}' and others using shared credentials are now logged out.[/dim]"
            )
        else:
            console.print(
                f"[green]Credentials for profile '{target_profile}' cleared successfully.[/green]"
            )

    except (ImportError, AttributeError, ValueError, configparser.Error) as e:
        console.print(f"[red]Error: {str(e)}[/red]")
        if verbose:
            console.print(f"[dim]Failed to process credentials file: {str(e)}[/dim]")


@auth.command("clear", hidden=True)
@click.confirmation_option(
    prompt="Are you sure you want to clear your authentication credentials?"
)
@click.option(
    "--verbose",
    "-v",
    is_flag=True,
    help="Show verbose information about what is being cleared",
)
def clear(verbose: bool) -> None:
    """Clear authentication credentials (deprecated - use 'logout')."""
    console.print(
        "[yellow]Warning: 'clear' is deprecated. Use 'day2 auth logout' instead.[/yellow]"
    )
    # Call the logout function with default parameters
    logout(all_profiles=True, profile=None, verbose=verbose)
