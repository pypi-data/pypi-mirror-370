"""Utility functions for date conversion and validation."""

from jdatetime import JalaliDate
from datetime import datetime
import os


def jalali_to_gregorian(jalali_date_str):
    """Convert Jalali date string (YYYY/MM/DD) to Gregorian date string (YYYY-MM-DD)."""
    try:
        parts = jalali_date_str.split('/')
        if len(parts) != 3:
            raise ValueError("Invalid date format")
        
        year, month, day = map(int, parts)
        jalali_date = JalaliDate(year, month, day)
        gregorian_date = jalali_date.to_gregorian()
        
        return gregorian_date.strftime('%Y-%m-%d')
    except Exception as e:
        raise ValueError(f"Error converting Jalali date: {str(e)}")


def validate_jalali_date(date_str):
    """Validate Jalali date format and values."""
    try:
        parts = date_str.split('/')
        if len(parts) != 3:
            return False
        
        year, month, day = map(int, parts)
        JalaliDate(year, month, day)
        return True
    except:
        return False


def get_desktop_path():
    """Get the path to the user's desktop."""
    return os.path.join(os.path.expanduser('~'), 'Desktop')
