"""Date formatting and parsing utilities for Media Archive Manager.

This module provides utilities for formatting and parsing dates in the
application's preferred format (DD.MM.YYYY).

History:
20260309  V1.0: Created date_utils module with format/parse functions
20260309  V1.1: Fixed parse_date to use datetime.strptime instead of date.strptime
20260309  V1.2: Added format_date_for_display and format_date_for_export aliases
"""

from datetime import datetime, date
from typing import Optional
import logging

logger = logging.getLogger(__name__)

# Date format constants
DATE_FORMAT_DISPLAY = "%d.%m.%Y"  # DD.MM.YYYY for display
DATE_FORMAT_ISO = "%Y-%m-%d"      # YYYY-MM-DD for database/ISO


def format_date(date_obj: Optional[date]) -> str:
    """Format a date object to DD.MM.YYYY string.
    
    Args:
        date_obj: Date object to format, or None.
    
    Returns:
        Formatted date string (DD.MM.YYYY) or empty string if date_obj is None.
    
    Example:
        >>> from datetime import date
        >>> format_date(date(2026, 3, 9))
        '09.03.2026'
        >>> format_date(None)
        ''
    """
    if date_obj is None:
        return ""
    try:
        return date_obj.strftime(DATE_FORMAT_DISPLAY)
    except (AttributeError, ValueError) as e:
        logger.error(f"Error formatting date {date_obj}: {e}")
        return ""


def parse_date(date_str: Optional[str]) -> Optional[date]:
    """Parse a date string in DD.MM.YYYY format to date object.
    
    Attempts to parse the string as DD.MM.YYYY format. If that fails,
    tries YYYY-MM-DD format for backward compatibility.
    
    Args:
        date_str: Date string to parse (DD.MM.YYYY or YYYY-MM-DD).
    
    Returns:
        Parsed date object, or None if string is empty or invalid.
    
    Raises:
        ValueError: If date string is invalid and cannot be parsed.
    
    Example:
        >>> parse_date("09.03.2026")
        datetime.date(2026, 3, 9)
        >>> parse_date("2026-03-09")
        datetime.date(2026, 3, 9)
        >>> parse_date("")
        None
    """
    if not date_str or not date_str.strip():
        return None
    
    date_str = date_str.strip()
    
    # Try DD.MM.YYYY format first
    try:
        return datetime.strptime(date_str, DATE_FORMAT_DISPLAY).date()
    except ValueError:
        pass
    
    # Try YYYY-MM-DD format for backward compatibility
    try:
        return datetime.strptime(date_str, DATE_FORMAT_ISO).date()
    except ValueError:
        logger.error(f"Cannot parse date string: {date_str}")
        raise ValueError(f"Invalid date format: {date_str}. Expected DD.MM.YYYY or YYYY-MM-DD")


def format_date_for_display(date_obj: Optional[date]) -> str:
    """Format a date for display in UI (alias for format_date).
    
    Args:
        date_obj: Date object to format.
    
    Returns:
        Formatted date string (DD.MM.YYYY) or empty string if None.
    """
    return format_date(date_obj)


def format_date_for_export(date_obj: Optional[date]) -> str:
    """Format a date for export/CSV (DD.MM.YYYY format).
    
    Args:
        date_obj: Date object to format.
    
    Returns:
        Formatted date string (DD.MM.YYYY) or empty string if None.
    """
    return format_date(date_obj)


def get_today_formatted() -> str:
    """Get today's date formatted as DD.MM.YYYY.
    
    Returns:
        Today's date as formatted string.
    
    Example:
        >>> get_today_formatted()  # Returns something like '09.03.2026'
    """
    return format_date(date.today())
