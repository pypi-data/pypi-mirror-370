"""Credential management for the MontyCloud SDK."""

import configparser
import os
from pathlib import Path
from typing import Optional


class Credentials:
    """Manages API keys and other authentication credentials."""

    def __init__(
        self,
        api_key: Optional[str] = None,
        api_secret_key: Optional[str] = None,
        profile_name: Optional[str] = None,
        base_url: Optional[str] = None,
    ):
        """Initialize credentials.

        Args:
            api_key: API key for authentication. If not provided, will attempt to load
                from environment variables or configuration file.
            api_secret_key: API secret key for authentication. If not provided, will attempt to load
                from environment variables or configuration file.
            profile_name: Profile name for credential section determination
            base_url: Base URL for credential section determination
        """
        self.profile_name = profile_name
        self.base_url = base_url

        # Determine which credential section to use
        self.credential_section = self._determine_credential_section(profile_name)

        self.api_key = api_key or self._load_from_env() or self._load_from_config()
        self.secret_key = (
            api_secret_key
            or self._load_api_secret_key_from_env()
            or self._load_api_secret_key_from_config()
        )

        if not self.api_key:
            raise ValueError(
                "No API key provided. Please provide an API key via the constructor, "
                "environment variable DAY2_API_KEY, or configuration file."
            )

    def _get_credentials_file_path(self) -> Path:
        """Get the path to the credentials file.

        Uses the same directory resolution logic as ProfileManager:
        1. Check DAY2_CONFIG_PATH environment variable directory
        2. Fall back to ~/.day2/ directory

        Returns:
            Path to the credentials file.
        """
        if os.environ.get("DAY2_CONFIG_PATH"):
            config_file_path = Path(os.environ["DAY2_CONFIG_PATH"])
            config_dir = config_file_path.parent
        else:
            config_dir = Path.home() / ".day2"

        return config_dir / "credentials"

    def _determine_credential_section(self, profile_name: Optional[str]) -> str:
        """Determine which credential section to use.

        This now uses a simpler approach:
        - If no profile name, use DEFAULT
        - Otherwise, try the profile's own section first
        - The actual loading logic will handle fallback to DEFAULT

        Args:
            profile_name: Profile name

        Returns:
            Credential section name to use (profile name or "DEFAULT")
        """
        if not profile_name:
            return "DEFAULT"

        # Return the profile name - the loading logic will handle checking
        # if credentials exist there and falling back to DEFAULT if needed
        return profile_name

    def _load_from_env(self) -> Optional[str]:
        """Load API key from environment variables.

        Returns:
            API key if found in environment variables, None otherwise.
        """
        return os.environ.get("DAY2_API_KEY")

    def _load_api_secret_key_from_env(self) -> Optional[str]:
        """Load API secret key from environment variables.

        Returns:
            API secret key if found in environment variables, None otherwise.
        """
        return os.environ.get("DAY2_API_SECRET_KEY")

    def _normalize_section_name(self, section_name: str) -> str:
        """Normalize section name for consistent storage.

        Args:
            section_name: The section name to normalize

        Returns:
            Normalized section name (DEFAULT for default, original case for others)
        """
        if section_name.lower() == "default":
            return "DEFAULT"
        return section_name

    def _find_section_case_insensitive(
        self, config_parser: configparser.ConfigParser, section_name: str
    ) -> Optional[str]:
        """Find a section in the config parser, case-insensitively.

        Args:
            config_parser: The ConfigParser instance to search
            section_name: The section name to find (case-insensitive)

        Returns:
            The actual section name if found, None otherwise.
        """
        # Check exact match first
        if config_parser.has_section(section_name):
            return section_name

        # Check case-insensitive match
        for actual_section in config_parser.sections():
            if actual_section.lower() == section_name.lower():
                return actual_section

        # Special handling for DEFAULT section (configparser treats it specially)
        if section_name.upper() == "DEFAULT":
            # Check if DEFAULT exists in any case
            if "DEFAULT" in config_parser:
                return "DEFAULT"
            for actual_section in config_parser.sections():
                if actual_section.lower() == "default":
                    return actual_section

        return None

    def _load_from_config(self) -> Optional[str]:
        """Load API key from credentials file.

        Returns:
            API key if found in credentials file, None otherwise.
        """
        credentials_file = self._get_credentials_file_path()

        if not credentials_file.exists():
            return None

        try:
            config_parser = configparser.ConfigParser()
            config_parser.read(credentials_file)

            # First, always check if the profile has its own credentials
            if self.profile_name:
                profile_section = self._find_section_case_insensitive(
                    config_parser, self.profile_name
                )
                if profile_section:
                    api_key = config_parser.get(
                        profile_section, "api_key", fallback=None
                    )
                    if api_key:
                        # Update credential_section to reflect what we actually used
                        self.credential_section = profile_section
                        return api_key

            # Then try the determined section (case-insensitive)
            actual_section = self._find_section_case_insensitive(
                config_parser, self.credential_section
            )
            if actual_section:
                return config_parser.get(actual_section, "api_key", fallback=None)

            # Fall back to DEFAULT section if profile section doesn't exist (case-insensitive)
            default_section = self._find_section_case_insensitive(
                config_parser, "DEFAULT"
            )
            if default_section:
                return config_parser.get(default_section, "api_key", fallback=None)
            return None
        except (configparser.Error, IOError):
            return None

    def _load_api_secret_key_from_config(self) -> Optional[str]:
        """Load API secret key from credentials file.

        Returns:
            API secret key if found in credentials file, None otherwise.
        """
        credentials_file = self._get_credentials_file_path()

        if not credentials_file.exists():
            return None

        try:
            config_parser = configparser.ConfigParser()
            config_parser.read(credentials_file)

            # First, always check if the profile has its own credentials
            if self.profile_name:
                profile_section = self._find_section_case_insensitive(
                    config_parser, self.profile_name
                )
                if profile_section:
                    secret_key = config_parser.get(
                        profile_section, "api_secret_key", fallback=None
                    )
                    if secret_key:
                        return secret_key

            # Then try the determined section (case-insensitive)
            actual_section = self._find_section_case_insensitive(
                config_parser, self.credential_section
            )
            if actual_section:
                return config_parser.get(
                    actual_section, "api_secret_key", fallback=None
                )

            # Fall back to DEFAULT section if profile section doesn't exist (case-insensitive)
            default_section = self._find_section_case_insensitive(
                config_parser, "DEFAULT"
            )
            if default_section:
                return config_parser.get(
                    default_section, "api_secret_key", fallback=None
                )
            return None
        except (configparser.Error, IOError):
            return None

    def save_to_config(self, section_name: Optional[str] = None) -> None:
        """Save credentials to credentials file.

        Args:
            section_name: Section name to save credentials to. If None, uses DEFAULT.
        """
        if not self.api_key:
            return

        config_dir = Path.home() / ".day2"
        config_dir.mkdir(exist_ok=True)

        credentials_file = config_dir / "credentials"

        # Use provided section name or default to DEFAULT
        target_section = self._normalize_section_name(section_name or "DEFAULT")

        # Load existing credentials if they exist
        config_parser = configparser.ConfigParser()
        if credentials_file.exists():
            config_parser.read(credentials_file)

        # Handle case-insensitive section merging
        self._merge_section_case_insensitive(config_parser, target_section)

        # Update config with API key and secret
        config_parser[target_section]["api_key"] = self.api_key
        if self.secret_key:
            config_parser[target_section]["api_secret_key"] = self.secret_key

        # Save credentials
        with open(credentials_file, "w", encoding="utf-8") as f:
            config_parser.write(f)

    def _merge_section_case_insensitive(
        self, config_parser: configparser.ConfigParser, target_section: str
    ) -> None:
        """Merge existing section with different case into target section.

        Args:
            config_parser: The ConfigParser instance to modify
            target_section: The normalized target section name
        """
        existing_section = self._find_section_case_insensitive(
            config_parser, target_section
        )

        if existing_section and existing_section != target_section:
            # Copy existing values to preserve them
            existing_values = dict(config_parser[existing_section])
            config_parser.remove_section(existing_section)
            config_parser[target_section] = existing_values
        elif not existing_section:
            # Create new section
            config_parser[target_section] = {}

    @classmethod
    def save_credentials_to_section(
        cls,
        api_key: str,
        api_secret_key: Optional[str],
        section_name: str,
        credentials_file_path: Optional[Path] = None,
    ) -> None:
        """Save credentials to a specific section in the credentials file.

        This is a utility method for auth.py to save credentials without creating a Credentials instance.

        Args:
            api_key: API key to save
            api_secret_key: API secret key to save (optional)
            section_name: Section name to save to
            credentials_file_path: Optional custom path to credentials file
        """
        if credentials_file_path:
            credentials_file = credentials_file_path
            credentials_file.parent.mkdir(exist_ok=True)
        else:
            config_dir = Path.home() / ".day2"
            config_dir.mkdir(exist_ok=True)
            credentials_file = config_dir / "credentials"

        # Normalize section name
        normalized_section = cls.normalize_section_name(section_name)

        # Load existing credentials
        config_parser = configparser.ConfigParser()
        if credentials_file.exists():
            config_parser.read(credentials_file)

        # Handle case-insensitive section merging
        cls._merge_section_case_insensitive_static(config_parser, normalized_section)

        # Update credentials
        config_parser[normalized_section]["api_key"] = api_key or ""
        if api_secret_key:
            config_parser[normalized_section]["api_secret_key"] = api_secret_key

        # Save credentials
        with open(credentials_file, "w", encoding="utf-8") as f:
            config_parser.write(f)

    @staticmethod
    def normalize_section_name(section_name: str) -> str:
        """Normalize section name for consistent storage.

        Args:
            section_name: The section name to normalize

        Returns:
            Normalized section name (DEFAULT for default, original case for others)
        """
        if section_name.lower() == "default":
            return "DEFAULT"
        return section_name

    @staticmethod
    def _find_section_case_insensitive_static(
        config_parser: configparser.ConfigParser, section_name: str
    ) -> Optional[str]:
        """Static version of _find_section_case_insensitive for class methods."""
        # Check exact match first
        if config_parser.has_section(section_name):
            return section_name

        # Check case-insensitive match
        for actual_section in config_parser.sections():
            if actual_section.lower() == section_name.lower():
                return actual_section

        # Special handling for DEFAULT section
        if section_name.upper() == "DEFAULT":
            if "DEFAULT" in config_parser:
                return "DEFAULT"
            for actual_section in config_parser.sections():
                if actual_section.lower() == "default":
                    return actual_section

        return None

    @staticmethod
    def _merge_section_case_insensitive_static(
        config_parser: configparser.ConfigParser, target_section: str
    ) -> None:
        """Static version of _merge_section_case_insensitive for class methods."""
        existing_section = Credentials._find_section_case_insensitive_static(
            config_parser, target_section
        )

        if existing_section and existing_section != target_section:
            # Copy existing values to preserve them
            existing_values = dict(config_parser[existing_section])
            config_parser.remove_section(existing_section)
            config_parser[target_section] = existing_values
        elif not existing_section:
            # Create new section
            config_parser[target_section] = {}
