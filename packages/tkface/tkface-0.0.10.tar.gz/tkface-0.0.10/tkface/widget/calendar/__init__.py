"""
Calendar widget module for tkface.

This module provides a customizable calendar widget with support for:
- Multiple months display
- Week numbers
- Customizable day colors
- Holiday highlighting
- Language support
- Configurable week start
- Month selection mode
"""

from .core import Calendar, CalendarConfig
from .style import get_calendar_theme, get_calendar_themes

__all__ = ["Calendar", "CalendarConfig", "get_calendar_theme", "get_calendar_themes"]
