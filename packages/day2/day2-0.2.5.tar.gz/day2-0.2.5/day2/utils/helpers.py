"""Helper utilities for the MontyCloud DAY2 SDK."""

from datetime import datetime
from typing import Optional, Union


def format_datetime(
    dt: Optional[Union[datetime, str]] = None,
    format_str: str = "%Y-%m-%d %H:%M:%S",
    default: str = "N/A",
) -> str:
    """Format a datetime object or string to a standard format.

    Args:
        dt: Datetime object or string to format. If None, returns the default value.
        format_str: Format string to use for datetime formatting.
        default: Default value to return if dt is None.

    Returns:
        Formatted datetime string or default value if dt is None.
    """
    if dt is None:
        return default

    if isinstance(dt, datetime):
        return dt.strftime(format_str)
    return str(dt)
