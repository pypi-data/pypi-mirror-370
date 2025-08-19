"""
Utility functions for parsing and formatting ISO date/time strings.
"""

from __future__ import annotations

import re
from datetime import datetime, timezone


def parse_iso_datetime(date_str: str) -> datetime:
    """
    Parse an ISO 8601 date/time string into a datetime object.

    Handles timestamps ending with 'Z' as UTC.

    Args:
        date_str: ISO 8601 formatted date/time string.

    Returns:
        A timezone-aware datetime object.

    Raises:
        ValueError: If the input string is not a valid ISO format.
    """
    if date_str.endswith("Z"):
        date_str = date_str[:-1] + "+00:00"

    match = re.search(r"\.(\d+)(?=[+-]\d{2}:\d{2}|$)", date_str)
    if match:
        frac = match.group(1)
        if 1 <= len(frac) <= 5:
            date_str = date_str.replace("." + frac, "." + frac.ljust(6, "0"))

    return datetime.fromisoformat(date_str)


def format_iso_datetime(dt: datetime) -> str:
    """
    Format a datetime object into an ISO 8601 string ending with 'Z'.

    Args:
        dt: datetime object (naive or timezone-aware).

    Returns:
        A string representing the datetime in ISO 8601 format.
    """
    if dt.tzinfo is None:
        dt = dt.replace(tzinfo=timezone.utc)
    return dt.astimezone(timezone.utc).isoformat().replace("+00:00", "Z")
