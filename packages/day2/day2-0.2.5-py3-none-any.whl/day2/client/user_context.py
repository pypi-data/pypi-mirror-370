"""User context management for the MontyCloud DAY2 SDK."""

import configparser
import logging
from pathlib import Path
from typing import Any, Dict, Optional

logger = logging.getLogger(__name__)

# Constants
USER_CONTEXT_FILE = "user_context"


class UserContext:
    """Manages user context information from the MontyCloud API."""

    def __init__(
        self,
        tenant_id: Optional[str] = None,
        user_id: Optional[str] = None,
        email: Optional[str] = None,
        name: Optional[str] = None,
        username: Optional[str] = None,
        tenant_name: Optional[str] = None,
    ):
        """Initialize user context.

        Args:
            tenant_id: The tenant ID associated with the user.
            user_id: The user ID of the authenticated user.
            email: The email of the authenticated user.
            name: The name of the authenticated user.
            username: The username of the authenticated user.
            tenant_name: The name of the tenant.
        """
        self.tenant_id = tenant_id
        self.user_id = user_id
        self.email = email
        self.name = name
        self.username = username
        self.tenant_name = tenant_name

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "UserContext":
        """Create a UserContext instance from a dictionary.

        Args:
            data: Dictionary containing user context data.

        Returns:
            A new UserContext instance.
        """
        return cls(
            tenant_id=data.get("TenantId"),
            user_id=data.get("UserId"),
            email=data.get("Email"),
            name=data.get("Name"),
            username=data.get("Username"),
            tenant_name=data.get("TenantName"),
        )

    def to_dict(self) -> Dict[str, Optional[str]]:
        """Convert the user context to a dictionary.

        Returns:
            Dictionary representation of the user context.
        """
        return {
            "tenant_id": self.tenant_id,
            "user_id": self.user_id,
            "email": self.email,
            "name": self.name,
            "username": self.username,
            "tenant_name": self.tenant_name,
        }

    @classmethod
    def load(cls, config_dir: Optional[Path] = None) -> Optional["UserContext"]:
        """Load user context from the user context file.

        Args:
            config_dir: Directory containing the user context file.
                If not provided, uses the default ~/.day2 directory.

        Returns:
            UserContext instance if the file exists and contains valid data,
            None otherwise.
        """
        if not config_dir:
            config_dir = Path.home() / ".day2"

        user_context_path = config_dir / USER_CONTEXT_FILE

        if not user_context_path.exists():
            logger.debug("User context file not found at %s", user_context_path)
            return None

        try:
            config_parser = configparser.ConfigParser()
            config_parser.read(user_context_path)

            if "DEFAULT" in config_parser:
                data = config_parser["DEFAULT"]
                return cls(
                    tenant_id=data.get("tenant_id"),
                    user_id=data.get("user_id"),
                    email=data.get("email"),
                    name=data.get("name"),
                    username=data.get("username"),
                    tenant_name=data.get("tenant_name"),
                )
            return None
        except (configparser.Error, IOError) as e:
            logger.warning("Failed to load user context: %s", e)
            return None

    def save(self, config_dir: Optional[Path] = None) -> None:
        """Save user context to the user context file.

        Args:
            config_dir: Directory to save the user context file to.
                If not provided, uses the default ~/.day2 directory.
        """
        if not config_dir:
            config_dir = Path.home() / ".day2"

        config_dir.mkdir(exist_ok=True)
        user_context_path = config_dir / USER_CONTEXT_FILE

        try:
            config_parser = configparser.ConfigParser()
            config_parser["DEFAULT"] = {}

            # Add all user context data to DEFAULT section
            data = self.to_dict()
            for key, value in data.items():
                if value is not None:
                    config_parser["DEFAULT"][key] = str(value)

            with open(user_context_path, "w", encoding="utf-8") as f:
                config_parser.write(f)
            logger.debug("Saved user context to %s", user_context_path)
        except IOError as e:
            logger.warning("Failed to save user context: %s", e)


def get_user_context(config_dir: Optional[Path] = None) -> Optional[UserContext]:
    """Get the user context from the user context file.

    Args:
        config_dir: Directory containing the user context file.
            If not provided, uses the default ~/.day2 directory.

    Returns:
        UserContext instance if the file exists and contains valid data,
        None otherwise.
    """
    return UserContext.load(config_dir)
