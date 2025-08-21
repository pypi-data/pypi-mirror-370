"""
Datetime utilities for the Reasoning Kernel.

This module provides datetime utilities that use modern, timezone-aware patterns
to replace deprecated datetime.utcnow() usage throughout the codebase.

Author: AI Assistant & Reasoning Kernel Team
Date: 2025-01-27
"""

from datetime import datetime
from datetime import timezone
from typing import Union


def utc_now() -> datetime:
    """Get the current UTC time as a timezone-aware datetime object.

    This function replaces deprecated datetime.utcnow() calls throughout the codebase
    with the modern, timezone-aware equivalent.

    Returns:
        datetime: Current UTC time as timezone-aware datetime
    """
    return datetime.now(timezone.utc)


def ensure_timezone_aware(dt: Union[datetime, str]) -> datetime:
    """Ensure a datetime object is timezone-aware.

    Args:
        dt: datetime object or ISO format string

    Returns:
        datetime: Timezone-aware datetime object
    """
    if isinstance(dt, str):
        # Parse ISO format string
        dt = datetime.fromisoformat(dt.replace("Z", "+00:00"))

    if dt.tzinfo is None:
        # Assume UTC if no timezone info
        dt = dt.replace(tzinfo=timezone.utc)

    return dt


def to_utc_isoformat(dt: Union[datetime, None] = None) -> str:
    """Convert datetime to UTC ISO format string.

    Args:
        dt: datetime object, defaults to current UTC time

    Returns:
        str: ISO format string in UTC
    """
    if dt is None:
        dt = utc_now()

    # Ensure timezone-aware
    dt = ensure_timezone_aware(dt)

    # Convert to UTC and format
    return dt.astimezone(timezone.utc).isoformat()
