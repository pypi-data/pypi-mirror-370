"""User resource client for the MontyCloud DAY2 SDK."""

import logging
from typing import TYPE_CHECKING, Optional

from day2.client.base import BaseClient
from day2.client.user_context import UserContext

if TYPE_CHECKING:
    from day2.session import Session

logger = logging.getLogger(__name__)


class UserClient(BaseClient):
    """Client for user-related API operations."""

    def __init__(self, session: "Session") -> None:
        """Initialize a new UserClient.

        Args:
            session: MontyCloud session.
        """
        super().__init__(session, "user")

    def get_user(self) -> Optional[UserContext]:
        """Get information about the authenticated user.

        Returns:
            UserContext containing the user's information if successful,
            None if the request fails.
        """
        try:
            # Use _make_request instead of directly calling session.request
            response_data = self._make_request("GET", "auth/user")
            if response_data:
                logger.debug("Retrieved user context: %s", response_data)
                return UserContext.from_dict(response_data)
            logger.warning("Failed to get user context: empty response")
            return None
        except Exception as e:  # pylint: disable=broad-except
            logger.warning("Error retrieving user context: %s", e)
            return None
