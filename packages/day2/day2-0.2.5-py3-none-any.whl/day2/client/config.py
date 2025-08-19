"""Configuration for the MontyCloud SDK."""

import configparser
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Dict, Optional


@dataclass
class Config:
    """Configuration for the MontyCloud SDK.

    Attributes:
        base_url: Base URL for the MontyCloud API
        api_version: API version to use
        timeout: Request timeout in seconds
        max_retries: Maximum number of retries for failed requests
        retry_backoff_factor: Exponential backoff factor for retries
        tenant_id: Default tenant ID for operations
        retry_min_delay: Minimum delay between retries in seconds
        retry_max_delay: Maximum delay between retries in seconds
        output_format: Output format for CLI commands (table or json)
    """

    # Base URL for the MontyCloud API
    base_url: str = "https://api.montycloud.com/day2/api"

    # API version
    api_version: str = "v1"

    # Request timeout in seconds
    timeout: int = 30

    # Maximum number of retries for failed requests
    max_retries: int = 3

    # Retry backoff factor
    retry_backoff_factor: float = 1.0

    # Default tenant ID
    tenant_id: str = ""

    # Minimum retry delay in seconds
    retry_min_delay: float = 2.0

    # Maximum retry delay in seconds
    retry_max_delay: float = 10.0

    # CLI output format (table or json)
    output_format: str = "table"

    # Profile name
    profile: str = ""

    @property
    def api_url(self) -> str:
        """Get the full API URL.

        Returns:
            Full API URL including version.
        """
        return f"{self.base_url}/{self.api_version}"

    def to_dict(self) -> Dict[str, Any]:
        """Convert config to dictionary.

        Returns:
            Dict[str, Any]: Dictionary representation of config
        """
        return {
            "base_url": self.base_url,
            "api_version": self.api_version,
            "timeout": self.timeout,
            "max_retries": self.max_retries,
            "retry_backoff_factor": self.retry_backoff_factor,
            "tenant_id": self.tenant_id,
            "retry_min_delay": self.retry_min_delay,
            "retry_max_delay": self.retry_max_delay,
            "output_format": self.output_format,
            "profile": self.profile,
        }

    @classmethod
    def from_dict(cls, config_dict: Dict[str, Any]) -> "Config":
        """Create a Config object from a dictionary.

        Args:
            config_dict: Dictionary containing configuration values

        Returns:
            Config object initialized with values from dictionary.
        """
        return cls(**config_dict)

    @classmethod
    def from_file(cls, config_path: Optional[Path] = None) -> "Config":
        """Load configuration from file.

        Args:
            config_path: Path to the configuration file. If None, uses ~/.day2/config

        Returns:
            Config: Configuration object with values from file or defaults
        """
        if config_path is None:
            config_path = Path.home() / ".day2" / "config"

        if config_path.exists():
            try:
                config_parser = configparser.ConfigParser()
                config_parser.read(config_path)

                # Parse values with appropriate type conversion
                return cls(
                    base_url=config_parser.get(
                        "DEFAULT", "base_url", fallback=cls.base_url
                    ),
                    api_version=config_parser.get(
                        "DEFAULT", "api_version", fallback=cls.api_version
                    ),
                    timeout=config_parser.getint(
                        "DEFAULT", "timeout", fallback=cls.timeout
                    ),
                    max_retries=config_parser.getint(
                        "DEFAULT", "max_retries", fallback=cls.max_retries
                    ),
                    retry_backoff_factor=float(
                        config_parser.get(
                            "DEFAULT",
                            "retry_backoff_factor",
                            fallback=str(cls.retry_backoff_factor),
                        )
                    ),
                    tenant_id=config_parser.get("DEFAULT", "tenant_id", fallback=""),
                    retry_min_delay=float(
                        config_parser.get(
                            "DEFAULT",
                            "retry_min_delay",
                            fallback=str(cls.retry_min_delay),
                        )
                    ),
                    retry_max_delay=float(
                        config_parser.get(
                            "DEFAULT",
                            "retry_max_delay",
                            fallback=str(cls.retry_max_delay),
                        )
                    ),
                    # Output format
                    output_format=config_parser.get(
                        "DEFAULT", "output_format", fallback=cls.output_format
                    ),
                )
            except (configparser.Error, ValueError, IOError):
                # Fall back to defaults if file can't be read
                return cls()

        return cls()

    def save_to_file(self, config_path: Optional[Path] = None) -> None:
        """Save configuration to file.

        Args:
            config_path: Path to save configuration to. If None, uses ~/.day2/config
        """
        if config_path is None:
            config_path = Path.home() / ".day2" / "config"

        # Create parent directory if it doesn't exist
        config_path.parent.mkdir(parents=True, exist_ok=True)

        # Load existing config if it exists
        config_parser = configparser.ConfigParser()
        if config_path.exists():
            config_parser.read(config_path)

        # Convert config to dict and update the DEFAULT section
        config_dict = self.to_dict()
        for key, value in config_dict.items():
            if value is not None and value != "":
                if "DEFAULT" not in config_parser:
                    config_parser["DEFAULT"] = {}
                config_parser["DEFAULT"][key] = str(value)

        # Write to file
        with open(config_path, "w", encoding="utf-8") as f:
            config_parser.write(f)
