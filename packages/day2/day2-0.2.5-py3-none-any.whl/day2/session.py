"""Session management for the MontyCloud DAY2 SDK."""

import logging
import os
from pathlib import Path
from typing import TYPE_CHECKING, Any, Dict, Optional, TypeVar, cast

from day2.auth.credentials import Credentials
from day2.client.config import Config
from day2.client.profile import ProfileManager
from day2.client.user_context import get_user_context

if TYPE_CHECKING:
    from day2.resources.assessment import AssessmentClient
    from day2.resources.bot import BotClient
    from day2.resources.cost import CostClient
    from day2.resources.report import ReportClient
    from day2.resources.resource import ResourceClient
    from day2.resources.tenant import TenantClient
    from day2.resources.user import UserClient

T = TypeVar("T")

logger = logging.getLogger(__name__)


class Session:
    """Session for interacting with the MontyCloud API.

    The Session manages authentication credentials, tenant context, and client creation.
    It provides access to all DAY2 API resources through dedicated client properties.

    Attributes:
        credentials: Authentication credentials for API access.
        tenant_id: Current tenant ID context for API operations.

    There are multiple ways to create a Session:

    1. Directly with credentials and configuration:
       ```python
       session = Session(api_key="key", api_secret_key="secret", tenant_id="tenant-id")
       ```

    2. From a profile:
       ```python
       session = Session.from_profile("profile-name")
       ```

    3. From the default profile:
       ```python
       session = Session.from_default_profile()
       ```

    Examples:
        Create a session with API credentials:

        >>> session = Session(api_key="your-api-key", api_secret_key="your-secret-key")
        >>> tenants = session.tenant.list_tenants()

        Create a session with custom configuration:

        >>> config = Config(timeout=60, max_retries=5)
        >>> session = Session(api_key="key", api_secret_key="secret", config=config)
    """

    def __init__(
        self,
        api_key: Optional[str] = None,
        api_secret_key: Optional[str] = None,
        credentials: Optional[Credentials] = None,
        tenant_id: Optional[str] = None,
        base_url: Optional[str] = None,
        config: Optional[Config] = None,
        config_path: Optional[Path] = None,
        profile: Optional[str] = None,
        use_user_context: bool = True,
        user_agent_suffix: Optional[str] = None,
    ) -> None:
        """Initialize a new session.

        Args:
            api_key: API key for authentication. If not provided, will attempt to load
                from environment variables or configuration file.
            api_secret_key: API secret key for authentication. Required if api_key is provided.
            credentials: Pre-configured Credentials object. Takes precedence over api_key/api_secret_key.
            tenant_id: Default tenant ID for API operations. Can be changed later with set_tenant().
            base_url: Base URL for API calls.
            config: Configuration object with API settings. If not provided, loads from file or uses defaults.
            config_path: Path to configuration file.
            profile: Profile name to use.
            use_user_context: Whether to use user context for tenant_id if not specified.
            user_agent_suffix: Custom suffix to append to User-Agent header (e.g., "mcp-server/my-tool/1.0.0").

        Raises:
            ValueError: If api_key is provided without api_secret_key.
            AuthenticationError: If no valid credentials are found.
        """
        # Check environment variable for profile
        env_profile = os.environ.get("DAY2_PROFILE")
        profile_to_use = profile or env_profile

        # Initialize configuration first to get credential scope
        if config:
            self._config = config
        else:
            profile_manager = ProfileManager(config_path=config_path)

            # If no explicit profile specified, try to get current profile, then default from ProfileManager
            if not profile_to_use:
                # First check for current/active profile
                current_profile = profile_manager.get_current_profile()
                if current_profile and profile_manager.profile_exists(current_profile):
                    profile_to_use = current_profile
                else:
                    # Fall back to default profile
                    default_profile = profile_manager.get_default_profile()
                    if default_profile and profile_manager.profile_exists(
                        default_profile
                    ):
                        profile_to_use = default_profile

            # Try to load from profile
            if profile_to_use:
                if profile_manager.profile_exists(profile_to_use):
                    self._config = profile_manager.get_profile_config(profile_to_use)
                else:
                    # Import here to avoid circular imports
                    from day2.exceptions import ProfileNotFoundError

                    raise ProfileNotFoundError(profile_to_use)
            else:
                # Fall back to DEFAULT section
                self._config = profile_manager.get_default_config()

        # Initialize credentials with profile info for smart detection
        if credentials:
            self.credentials = credentials
        else:
            self.credentials = Credentials(
                api_key=api_key,
                api_secret_key=api_secret_key,
                profile_name=profile_to_use,
                base_url=self._config.base_url,
            )

        # Override base_url if provided
        if base_url:
            self._config.base_url = base_url

        # Get config directory for user context
        config_dir = None
        if config_path:
            config_dir = config_path.parent

        # Use tenant_id from parameters, or from config file
        # Convert empty strings to None for consistency
        self.tenant_id = tenant_id if tenant_id else None
        if not self.tenant_id and self._config.tenant_id:
            self.tenant_id = (
                self._config.tenant_id if self._config.tenant_id.strip() else None
            )

        # Store the use_user_context flag for later reference
        self.use_user_context = use_user_context

        # Initialize attributes that may be accessed during API calls
        self._clients: Dict[str, Any] = {}
        self.user_agent_suffix = user_agent_suffix

        # If tenant_id is still None and use_user_context is True, try to get it from user context
        if self.tenant_id is None and use_user_context:
            user_context = get_user_context(config_dir)
            if user_context and user_context.tenant_id:
                self.tenant_id = user_context.tenant_id
                logger.debug("Using tenant_id from user context: %s", self.tenant_id)
            # Note: We do NOT fetch user context from API during Session init anymore
            # This prevents file creation issues in Lambda environments
            # User context should only be fetched and saved during auth login

        logger.debug("Initialized session with tenant_id=%s", self.tenant_id)

    def _save_tenant_to_config(self) -> None:
        """Save tenant ID to configuration file."""
        if not self.tenant_id:
            return

        # Use ProfileManager to save the tenant ID
        profile_manager = ProfileManager()

        # Create a Config object with the current settings and updated tenant_id
        config = Config(
            tenant_id=self.tenant_id,
            base_url=self._config.base_url,
            api_version=self._config.api_version,
            timeout=self._config.timeout,
            max_retries=self._config.max_retries,
            retry_backoff_factor=self._config.retry_backoff_factor,
            retry_min_delay=self._config.retry_min_delay,
            retry_max_delay=self._config.retry_max_delay,
            output_format=self._config.output_format,
            profile=self._config.profile,
        )

        # Save using ProfileManager
        if self._config.profile:
            # Update existing profile
            if profile_manager.profile_exists(self._config.profile):
                profile_manager.update_profile(self._config.profile, config)
            else:
                profile_manager.create_profile(self._config.profile, config)
        else:
            # Save to DEFAULT section
            profile_manager.save_default_config(config)

    def client(self, service_name: str) -> Any:
        """Get a service client for the specified service.

        Args:
            service_name: Name of the service to get a client for.

        Returns:
            Client for the specified service.

        Raises:
            ValueError: If the specified service is not supported.
        """
        if service_name not in self._clients:
            self._clients[service_name] = self._create_client(service_name)

        return self._clients[service_name]

    @property
    def tenant(self) -> "TenantClient":
        """Get the tenant client.

        Returns:
            TenantClient instance.
        """
        # Import here to avoid circular imports
        from day2.resources.tenant import (  # pylint: disable=import-outside-toplevel
            TenantClient,
        )

        return cast("TenantClient", self.client("tenant"))

    @property
    def user(self) -> "UserClient":
        """Get the user client.

        Returns:
            UserClient instance.
        """
        # Import here to avoid circular imports
        from day2.resources.user import (  # pylint: disable=import-outside-toplevel
            UserClient,
        )

        return cast("UserClient", self.client("user"))

    @property
    def assessment(self) -> "AssessmentClient":
        """Get the assessment client.

        Returns:
            AssessmentClient: The assessment client.
        """
        return cast("AssessmentClient", self.client("assessment"))

    @property
    def cost(self) -> "CostClient":
        """Get the cost client.

        Returns:
            CostClient: The cost client.
        """
        return cast("CostClient", self.client("cost"))

    @property
    def report(self) -> "ReportClient":
        """Get the report client.

        Returns:
            ReportClient: The report client.
        """
        return cast("ReportClient", self.client("report"))

    @property
    def bot(self) -> "BotClient":
        """Get the bot client.

        Returns:
            BotClient: The bot client.
        """
        return cast("BotClient", self.client("bot"))

    @property
    def resource(self) -> "ResourceClient":
        """Get the resource client.

        Returns:
            ResourceClient: The resource client.
        """
        return cast("ResourceClient", self.client("resource"))

    @property
    def config(self) -> Config:
        """Get the session configuration.

        Returns:
            Config: The session configuration.
        """
        return self._config

    def _create_client(self, service_name: str) -> Any:
        """Create a client for the specified service.

        Args:
            service_name: Name of the service to create a client for.

        Returns:
            Client for the specified service.

        Raises:
            ValueError: If the specified service is not supported.
        """
        # Import the actual classes at runtime to avoid circular imports
        from day2.resources.assessment import AssessmentClient
        from day2.resources.bot import BotClient
        from day2.resources.cost import CostClient
        from day2.resources.report import ReportClient
        from day2.resources.resource import ResourceClient
        from day2.resources.tenant import TenantClient
        from day2.resources.user import UserClient

        service_map = {
            "tenant": TenantClient,
            "assessment": AssessmentClient,
            "cost": CostClient,
            "user": UserClient,
            "report": ReportClient,
            "bot": BotClient,
            "resource": ResourceClient,
        }

        if service_name not in service_map:
            raise ValueError(f"Unsupported service: {service_name}")

        return service_map[service_name](self)

    def set_tenant(self, tenant_id: str) -> None:
        """Set the current tenant context.

        Args:
            tenant_id: Tenant ID to set as the current context.
        """
        logger.debug("Setting tenant context to %s", tenant_id)
        self.tenant_id = tenant_id

        # Save tenant ID to config
        self._save_tenant_to_config()

        # Invalidate existing clients to ensure they use the new tenant
        self._clients = {}

    def clear_tenant(self) -> None:
        """Clear the current tenant context."""
        logger.debug("Clearing tenant context")
        self.tenant_id = None

        # Save tenant ID to config (will remove it)
        self._save_tenant_to_config()

        # Invalidate existing clients to ensure they use the new tenant
        self._clients = {}

    @classmethod
    def from_profile(
        cls, profile_name: str, use_user_context: bool = True
    ) -> "Session":
        """Create a session from a profile.

        Args:
            profile_name: Name of the profile to use.
            use_user_context: Whether to use user context for tenant_id if not specified in profile.

        Returns:
            Session instance.
        """
        return cls(profile=profile_name, use_user_context=use_user_context)

    @classmethod
    def from_default_profile(
        cls, config_path: Optional[Path] = None, use_user_context: bool = True
    ) -> "Session":
        """Create a Session from the default profile.

        Args:
            config_path: Optional path to the configuration file.
            use_user_context: Whether to use user context for tenant_id if not specified in profile.

        Returns:
            Session configured with the default profile or DEFAULT section if no default profile is set.

        Note:
            This method will not raise an error if no default profile is set. Instead, it will
            use the DEFAULT section from the configuration file. If the DAY2_PROFILE environment
            variable is set, it will override the default profile.
        """
        # Check environment variable for profile override
        env_profile = os.environ.get("DAY2_PROFILE")
        if env_profile:
            logger.debug(
                "Using profile from DAY2_PROFILE environment variable: %s", env_profile
            )
            return cls.from_profile(env_profile, use_user_context=use_user_context)

        profile_manager = ProfileManager(config_path=config_path)
        default_profile = profile_manager.get_default_profile()

        if default_profile is not None:
            # Use the default profile if set
            logger.debug("Using default profile: %s", default_profile)
            return cls.from_profile(default_profile, use_user_context=use_user_context)

        # Use the DEFAULT section if no default profile is set
        logger.debug("No default profile set. Using DEFAULT configuration.")
        config = profile_manager.get_default_config()
        return cls(config=config)
