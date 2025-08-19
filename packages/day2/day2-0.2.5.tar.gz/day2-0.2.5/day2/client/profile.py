"""Profile management for the MontyCloud DAY2 SDK."""

import configparser
import os
from pathlib import Path
from typing import TYPE_CHECKING, Any, Dict, List, Optional, TypeVar

from day2.client.constants import (
    CONFIG_DIR,
    CONFIG_FILE,
    DEFAULT_PROFILE_KEY,
    DEFAULT_SECTION,
    KEY_API_VERSION,
    KEY_BASE_URL,
    KEY_MAX_RETRIES,
    KEY_OUTPUT_FORMAT,
    KEY_PROFILE,
    KEY_RETRY_BACKOFF,
    KEY_RETRY_MAX_DELAY,
    KEY_RETRY_MIN_DELAY,
    KEY_TENANT_ID,
    KEY_TIMEOUT,
    PROFILE_PREFIX,
)
from day2.client.user_context import get_user_context

if TYPE_CHECKING:
    from day2.client.config import Config

T = TypeVar("T")


class ProfileManager:
    """Manages DAY2 SDK profiles.

    This class provides methods for creating, updating, deleting, and retrieving
    profiles, as well as setting and getting the default profile.
    """

    def __init__(self, config_path: Optional[Path] = None):
        """Initialize a new ProfileManager.

        Args:
            config_path: Path to the configuration file. If not provided,
                         uses the path from DAY2_CONFIG_PATH environment variable
                         or the default path (~/.day2/config).
        """
        # First check for config_path parameter, then env var, then default path
        if config_path:
            self.config_path = config_path
        elif os.environ.get("DAY2_CONFIG_PATH"):
            config_path_str = os.environ.get("DAY2_CONFIG_PATH")
            self.config_path = (
                Path(config_path_str)
                if config_path_str
                else Path.home() / CONFIG_DIR / CONFIG_FILE
            )
        else:
            self.config_path = Path.home() / CONFIG_DIR / CONFIG_FILE

        self._ensure_config_dir()

    def _ensure_config_dir(self) -> None:
        """Ensure the configuration directory exists."""
        self.config_path.parent.mkdir(parents=True, exist_ok=True)

    def _load_config_parser(self) -> configparser.ConfigParser:
        """Load the configuration file into a ConfigParser.

        Returns:
            ConfigParser with the configuration loaded.
        """
        config_parser = configparser.ConfigParser()

        if self.config_path.exists():
            try:
                config_parser.read(self.config_path)
            except configparser.Error:
                # If there's an error reading the config file, return an empty parser
                pass

        return config_parser

    def _save_config_parser(self, config_parser: configparser.ConfigParser) -> None:
        """Save the ConfigParser to the configuration file.

        Args:
            config_parser: ConfigParser to save.
        """
        with open(self.config_path, "w", encoding="utf-8") as f:
            config_parser.write(f)

    def list_profiles(self) -> List[str]:
        """List all available profiles.

        Returns:
            List of profile names.
        """
        config_parser = self._load_config_parser()
        profiles = []

        for section in config_parser.sections():
            if section.startswith(PROFILE_PREFIX):
                profile_name = section[len(PROFILE_PREFIX) :]
                profiles.append(profile_name)

        return profiles

    def profile_exists(self, name: str) -> bool:
        """Check if a profile exists.

        Args:
            name: Name of the profile.

        Returns:
            True if the profile exists, False otherwise.
        """
        config_parser = self._load_config_parser()
        section = f"{PROFILE_PREFIX}{name}"
        return section in config_parser

    def get_profile_config(self, name: str) -> "Config":
        """Get a profile's configuration.

        Args:
            name: Name of the profile to get.

        Returns:
            Config object with the profile's configuration, or default Config if the profile doesn't exist.
        """
        # Import Config here to avoid circular imports
        from day2.client.config import Config

        # Check if profile exists
        if not self.profile_exists(name):
            return Config()

        # Get profile section
        config_parser = self._load_config_parser()
        profile_section = f"{PROFILE_PREFIX}{name}"
        profile_dict = dict(config_parser[profile_section])

        # Filter out unsupported parameters
        supported_params = {
            KEY_TENANT_ID,
            KEY_BASE_URL,
            KEY_API_VERSION,
            KEY_TIMEOUT,
            KEY_MAX_RETRIES,
            KEY_RETRY_BACKOFF,
            KEY_RETRY_MIN_DELAY,
            KEY_RETRY_MAX_DELAY,
            KEY_OUTPUT_FORMAT,
        }
        filtered_dict = {k: v for k, v in profile_dict.items() if k in supported_params}

        # Create a new dictionary with the correct types
        config_kwargs: dict[str, Any] = {"profile": name}

        # Copy string values directly
        for key in [
            KEY_TENANT_ID,
            KEY_BASE_URL,
            KEY_API_VERSION,
            KEY_OUTPUT_FORMAT,
        ]:
            if key in filtered_dict:
                config_kwargs[key] = filtered_dict[key]

        # Convert numeric values
        if KEY_TIMEOUT in filtered_dict:
            config_kwargs[KEY_TIMEOUT] = int(filtered_dict[KEY_TIMEOUT])
        if KEY_MAX_RETRIES in filtered_dict:
            config_kwargs[KEY_MAX_RETRIES] = int(filtered_dict[KEY_MAX_RETRIES])
        if KEY_RETRY_BACKOFF in filtered_dict:
            config_kwargs[KEY_RETRY_BACKOFF] = float(filtered_dict[KEY_RETRY_BACKOFF])
        if KEY_RETRY_MIN_DELAY in filtered_dict:
            config_kwargs[KEY_RETRY_MIN_DELAY] = float(
                filtered_dict[KEY_RETRY_MIN_DELAY]
            )
        if KEY_RETRY_MAX_DELAY in filtered_dict:
            config_kwargs[KEY_RETRY_MAX_DELAY] = float(
                filtered_dict[KEY_RETRY_MAX_DELAY]
            )

        # Create and return Config object
        return Config(**config_kwargs)

    def get_default_config(self) -> "Config":
        """Get configuration from the DEFAULT section.

        Returns:
            Config object with values from the DEFAULT section.
        """
        # Import Config here to avoid circular imports
        from day2.client.config import Config

        config_parser = self._load_config_parser()

        # Get DEFAULT section values
        config_dict = (
            dict(config_parser[DEFAULT_SECTION])
            if DEFAULT_SECTION in config_parser
            else {}
        )

        # Filter out default_profile key
        if DEFAULT_PROFILE_KEY in config_dict:
            del config_dict[DEFAULT_PROFILE_KEY]

        # Create a new dictionary with the correct types
        config_kwargs: dict[str, Any] = {}

        # Copy string values directly
        for key in [
            KEY_TENANT_ID,
            KEY_BASE_URL,
            KEY_API_VERSION,
            KEY_OUTPUT_FORMAT,
            KEY_PROFILE,
        ]:
            if key in config_dict:
                config_kwargs[key] = config_dict[key]

        # Convert numeric values
        if KEY_TIMEOUT in config_dict:
            config_kwargs[KEY_TIMEOUT] = int(config_dict[KEY_TIMEOUT])
        if KEY_MAX_RETRIES in config_dict:
            config_kwargs[KEY_MAX_RETRIES] = int(config_dict[KEY_MAX_RETRIES])
        if KEY_RETRY_BACKOFF in config_dict:
            config_kwargs[KEY_RETRY_BACKOFF] = float(config_dict[KEY_RETRY_BACKOFF])
        if KEY_RETRY_MIN_DELAY in config_dict:
            config_kwargs[KEY_RETRY_MIN_DELAY] = float(config_dict[KEY_RETRY_MIN_DELAY])
        if KEY_RETRY_MAX_DELAY in config_dict:
            config_kwargs[KEY_RETRY_MAX_DELAY] = float(config_dict[KEY_RETRY_MAX_DELAY])

        # Create and return Config object
        return Config(**config_kwargs)

    def save_default_config(self, config: "Config") -> None:
        """Save configuration to the DEFAULT section.

        Args:
            config: Configuration to save.
        """
        config_parser = self._load_config_parser()

        # Ensure DEFAULT section exists
        if DEFAULT_SECTION not in config_parser:
            config_parser[DEFAULT_SECTION] = {}

        # Convert config to dict
        config_dict = {
            KEY_TENANT_ID: config.tenant_id,
            KEY_BASE_URL: config.base_url,
            KEY_API_VERSION: config.api_version,
            KEY_TIMEOUT: str(config.timeout),
            KEY_MAX_RETRIES: str(config.max_retries),
            KEY_RETRY_BACKOFF: str(config.retry_backoff_factor),
            KEY_RETRY_MIN_DELAY: str(config.retry_min_delay),
            KEY_RETRY_MAX_DELAY: str(config.retry_max_delay),
            KEY_OUTPUT_FORMAT: config.output_format,
        }

        # Filter out empty values
        config_dict = {
            k: v for k, v in config_dict.items() if v is not None and v != ""
        }

        # Update DEFAULT section
        for key, value in config_dict.items():
            config_parser[DEFAULT_SECTION][key] = value

        self._save_config_parser(config_parser)

    def create_profile(self, name: str, config: "Config") -> None:
        """Create a new profile.

        Args:
            name: Name of the profile.
            config: Configuration for the profile.
        Raises:
            ValueError: If the profile already exists.
        """
        config_parser = self._load_config_parser()
        section = f"{PROFILE_PREFIX}{name}"

        if section in config_parser:
            raise ValueError(f"Profile '{name}' already exists")

        # Create profile section with all Config attributes
        profile_data = {
            KEY_TENANT_ID: config.tenant_id,
            KEY_BASE_URL: config.base_url,
            KEY_API_VERSION: config.api_version,
            KEY_TIMEOUT: str(config.timeout),
            KEY_MAX_RETRIES: str(config.max_retries),
            KEY_RETRY_BACKOFF: str(config.retry_backoff_factor),
            KEY_RETRY_MIN_DELAY: str(config.retry_min_delay),
            KEY_RETRY_MAX_DELAY: str(config.retry_max_delay),
            KEY_OUTPUT_FORMAT: config.output_format,
        }

        # Filter out empty values
        profile_data = {
            k: v for k, v in profile_data.items() if v is not None and v != ""
        }

        config_parser[section] = profile_data

        self._save_config_parser(config_parser)

    def update_profile(self, name: str, config: "Config") -> None:
        """Update an existing profile.

        Args:
            name: Name of the profile.
            config: New configuration for the profile.

        Raises:
            ValueError: If the profile doesn't exist.
        """
        config_parser = self._load_config_parser()
        section = f"{PROFILE_PREFIX}{name}"

        if section not in config_parser:
            raise ValueError(f"Profile '{name}' doesn't exist")

        # Update profile section with all Config attributes
        profile_data = {
            KEY_TENANT_ID: config.tenant_id,
            KEY_BASE_URL: config.base_url,
            KEY_API_VERSION: config.api_version,
            KEY_TIMEOUT: str(config.timeout),
            KEY_MAX_RETRIES: str(config.max_retries),
            KEY_RETRY_BACKOFF: str(config.retry_backoff_factor),
            KEY_RETRY_MIN_DELAY: str(config.retry_min_delay),
            KEY_RETRY_MAX_DELAY: str(config.retry_max_delay),
            KEY_OUTPUT_FORMAT: config.output_format,
        }

        # Filter out empty values
        profile_data = {
            k: v for k, v in profile_data.items() if v is not None and v != ""
        }

        config_parser[section] = profile_data

        self._save_config_parser(config_parser)

    def delete_profile(self, name: str) -> None:
        """Delete a profile.

        Args:
            name: Name of the profile.

        Raises:
            ValueError: If the profile doesn't exist.
        """
        config_parser = self._load_config_parser()
        section = f"{PROFILE_PREFIX}{name}"

        if section not in config_parser:
            raise ValueError(f"Profile '{name}' doesn't exist")

        # Check if this is the default profile
        if (
            DEFAULT_SECTION in config_parser
            and DEFAULT_PROFILE_KEY in config_parser[DEFAULT_SECTION]
            and config_parser[DEFAULT_SECTION][DEFAULT_PROFILE_KEY] == name
        ):
            # Remove the default profile setting
            del config_parser[DEFAULT_SECTION][DEFAULT_PROFILE_KEY]

        # Delete the profile section
        config_parser.remove_section(section)

        self._save_config_parser(config_parser)

    def set_default_profile(self, name: str) -> None:
        """Set the default profile.

        Args:
            name: Name of the profile to set as default.

        Raises:
            ValueError: If the profile doesn't exist.
        """
        config_parser = self._load_config_parser()
        section = f"{PROFILE_PREFIX}{name}"

        if section not in config_parser:
            raise ValueError(f"Profile '{name}' doesn't exist")

        # Ensure DEFAULT section exists
        if DEFAULT_SECTION not in config_parser:
            config_parser[DEFAULT_SECTION] = {}

        # Set default profile
        config_parser[DEFAULT_SECTION][DEFAULT_PROFILE_KEY] = name

        self._save_config_parser(config_parser)

    def get_default_profile(self) -> Optional[str]:
        """Get the name of the default profile.

        Returns:
            Name of the default profile. If no default is explicitly set but a profile named 'default' exists,
            returns 'default'. Otherwise, returns None.
        """
        config_parser = self._load_config_parser()

        # First check if a default profile is explicitly set
        if (
            DEFAULT_SECTION in config_parser
            and DEFAULT_PROFILE_KEY in config_parser[DEFAULT_SECTION]
        ):
            return config_parser[DEFAULT_SECTION][DEFAULT_PROFILE_KEY]

        # If no default is set, check if a profile named 'default' exists
        default_profile_section = f"{PROFILE_PREFIX}default"
        if default_profile_section in config_parser:
            return "default"

        return None

    def get_current_profile(self) -> Optional[str]:
        """Get the current/active profile from the DEFAULT section.

        This checks for a 'profile' key in the DEFAULT section that indicates
        which profile should be used as the current/active profile.

        Returns:
            Name of the current profile if set, otherwise None.
        """
        config_parser = self._load_config_parser()

        if (
            DEFAULT_SECTION in config_parser
            and KEY_PROFILE in config_parser[DEFAULT_SECTION]
        ):
            return config_parser[DEFAULT_SECTION][KEY_PROFILE]

        return None

    def list_profiles_with_details(self) -> List[Dict[str, Any]]:
        """List all available profiles with detailed information.

        Returns:
            List of dictionaries with profile details, including whether each profile
            is the default profile.
        """
        profiles = self.list_profiles()
        default_profile = self.get_default_profile()

        result = []
        for profile_name in profiles:
            config = self.get_profile_config(profile_name)
            profile_info = {
                "name": profile_name,
                "is_default": profile_name == default_profile,
                "tenant_id": config.tenant_id,
                "base_url": config.base_url,
                "api_version": config.api_version,
                "timeout": config.timeout,
                "max_retries": config.max_retries,
                "retry_backoff_factor": config.retry_backoff_factor,
                "retry_min_delay": config.retry_min_delay,
                "retry_max_delay": config.retry_max_delay,
                "output_format": config.output_format,
            }
            result.append(profile_info)

        return result

    def reset_to_default(self) -> None:
        """Reset to the system default profile.

        This removes the current default profile setting from the configuration.
        """
        config_parser = self._load_config_parser()

        if (
            DEFAULT_SECTION in config_parser
            and DEFAULT_PROFILE_KEY in config_parser[DEFAULT_SECTION]
        ):
            del config_parser[DEFAULT_SECTION][DEFAULT_PROFILE_KEY]
            self._save_config_parser(config_parser)

    def clear_default_profile(self) -> None:
        """Clear the default profile setting.

        This method is deprecated. Use reset_to_default() instead.
        """
        self.reset_to_default()

    def _fetch_default_context(self) -> Dict[str, Any]:
        """Fetch default context from the user context file or API.

        Returns:
            Dictionary containing default context (tenant_id, user_id).
        """
        try:
            # Get config directory from config_path
            config_dir = None
            if self.config_path:
                config_dir = self.config_path.parent

            # Try to get user context from file
            user_context = get_user_context(config_dir)

            if user_context:
                # Return user context as dictionary
                return {
                    "tenant_id": user_context.tenant_id or "",
                    "user_id": user_context.user_id or "",
                }

            # If no user context is available, return empty dict
            return {}
        except Exception:  # pylint: disable=broad-except
            # Return empty dict if anything fails
            return {}

    def create_profile_interactive(
        self, name: str, full_config: bool = False, ignore_user_context: bool = False
    ) -> None:
        """Create a new profile interactively.

        Args:
            name: Name of the profile.
            full_config: Whether to prompt for all configuration options.
                         If False, only prompts for essential options.
            ignore_user_context: Whether to ignore user context when creating the profile.

        Raises:
            ValueError: If the profile already exists.
        """
        if self.profile_exists(name):
            raise ValueError(f"Profile '{name}' already exists")

        # Fetch default context from API or user context
        default_context = {} if ignore_user_context else self._fetch_default_context()

        # Start with default config
        from day2.client.config import Config

        config = Config()

        # Set tenant ID (with default from user context if available)
        default_tenant = default_context.get("tenant_id", "")

        # Show the default tenant ID if available
        if default_tenant:
            print(f"Tenant ID [auto-detected: {default_tenant}]: ", end="")
        else:
            print("Tenant ID: ", end="")

        tenant_id = input() or default_tenant
        config.tenant_id = tenant_id

        # For mini config, we're done with tenant ID, but let's confirm the base URL
        print(f"Use default API URL ({config.base_url})? [Y/n]: ", end="")
        use_default_url = input().lower() != "n"
        if not use_default_url:
            print("API URL: ", end="")
            config.base_url = input()

        # For mini config, we're done
        if not full_config:
            self.create_profile(name, config)
            return

        # For full config, prompt for all options
        # API Version
        print(f"API Version [{config.api_version}]: ", end="")
        api_version = input()
        if api_version:
            config.api_version = api_version

        # Timeout
        print(f"Timeout (seconds) [{config.timeout}]: ", end="")
        timeout_input = input()
        if timeout_input:
            config.timeout = int(timeout_input)

        # Max Retries
        print(f"Max Retries [{config.max_retries}]: ", end="")
        retries_input = input()
        if retries_input:
            config.max_retries = int(retries_input)

        # Retry Backoff Factor
        print(f"Retry Backoff Factor [{config.retry_backoff_factor}]: ", end="")
        backoff_input = input()
        if backoff_input:
            config.retry_backoff_factor = float(backoff_input)

        # Retry Min Delay
        print(f"Retry Min Delay (seconds) [{config.retry_min_delay}]: ", end="")
        min_delay_input = input()
        if min_delay_input:
            config.retry_min_delay = float(min_delay_input)

        # Retry Max Delay
        print(f"Retry Max Delay (seconds) [{config.retry_max_delay}]: ", end="")
        max_delay_input = input()
        if max_delay_input:
            config.retry_max_delay = float(max_delay_input)

        # Output Format
        print(f"Output Format [{config.output_format}]: ", end="")
        output_format = input()
        if output_format:
            config.output_format = output_format

        # Create the profile
        self.create_profile(name, config)

        # Ask if this should be the default profile
        print(f"Set '{name}' as default profile? [Y/n]: ", end="")
        set_as_default = input().lower() != "n"
        if set_as_default:
            self.set_default_profile(name)
