"""
MontyCloud DAY2 SDK for Python.

This package provides a Pythonic interface to the MontyCloud DAY2 API.
"""

from typing import TYPE_CHECKING, Optional

# Import from the current package for the new structure
from day2._version import __version__
from day2.session import Session

if TYPE_CHECKING:
    from day2.resources.assessment import AssessmentClient
    from day2.resources.cost import CostClient
    from day2.resources.tenant import TenantClient


class _DefaultSessionHolder:
    """Holder class for the default session singleton."""

    session: Optional[Session] = None


# Default session singleton holder
_default_session_holder = _DefaultSessionHolder()


def get_default_session() -> Session:
    """Get the default session, creating it if it doesn't exist.

    Returns:
        Session: The default session instance
    """
    if _default_session_holder.session is None:
        _default_session_holder.session = Session()
    return _default_session_holder.session


def tenant() -> "TenantClient":
    """Get a tenant client using the default session.

    Returns:
        TenantClient: A client for interacting with tenant resources
    """
    return get_default_session().tenant


def assessment() -> "AssessmentClient":
    """Get an assessment client using the default session.

    Returns:
        AssessmentClient: A client for interacting with assessment resources
    """
    return get_default_session().assessment


def cost() -> "CostClient":
    """Get a cost client using the default session.

    Returns:
        CostClient: A client for interacting with cost resources
    """
    return get_default_session().cost


__all__ = [
    "Session",
    "__version__",
    "tenant",
    "assessment",
    "cost",
    "get_default_session",
]
