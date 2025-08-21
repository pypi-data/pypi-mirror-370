"""
Core functionality for the Calendar widget.

This module provides the main Calendar class, data processing, event handling,
and DPI scaling support for the Calendar widget.
"""

import calendar
import datetime
import logging
import tkinter as tk
from dataclasses import dataclass
from typing import Dict, Optional, Tuple

from . import view
from .style import (
    get_calendar_theme,
    get_calendar_themes,
    get_day_names,
    get_month_name,
)

# Default popup dimensions
DEFAULT_POPUP_WIDTH = 235
DEFAULT_POPUP_HEIGHT = 175
WEEK_NUMBERS_WIDTH_OFFSET = 20


@dataclass
class CalendarConfig:  # pylint: disable=R0902
    """Configuration for Calendar widget."""

    year: Optional[int] = None
    month: Optional[int] = None
    months: int = 1
    show_week_numbers: bool = False
    week_start: str = "Sunday"
    day_colors: Optional[Dict[str, str]] = None
    holidays: Optional[Dict[str, str]] = None
    grid_layout: Optional[Tuple[int, int]] = None
    show_month_headers: bool = True
    selectmode: str = "single"
    show_navigation: bool = True
    theme: str = "light"
    date_callback: Optional[callable] = None
    year_view_callback: Optional[callable] = None
    popup_width: Optional[int] = None
    popup_height: Optional[int] = None
    date_format: str = "%Y-%m-%d"
    month_selection_mode: bool = False
    year_selection_mode: bool = False
    year_range_start: Optional[int] = None
    year_range_end: Optional[int] = None


# Import DPI functions for scaling support
try:
    from ...win.dpi import get_scaling_factor, scale_font_size
except ImportError:
    # Fallback functions if DPI module is not available
    def get_scaling_factor(_root):
        return 1.0

    def scale_font_size(original_size, _root=None, _scaling_factor=None):
        return original_size


class Calendar(tk.Frame):  # pylint: disable=R0902
    """
    A customizable calendar widget for Tkinter.
    Features:
    - Multiple months display
    - Week numbers
    - Customizable day colors
    - Holiday highlighting
    - Language support via tkface.lang
    - Configurable week start (Sunday/Monday)
    - Month selection mode (3x4 month grid)
    """

    def __init__(  # pylint: disable=R0917,R0915,R0902
        self,
        parent,
        config: Optional[CalendarConfig] = None,
        year: Optional[int] = None,
        month: Optional[int] = None,
        months: int = 1,
        show_week_numbers: bool = False,
        week_start: str = "Sunday",
        day_colors: Optional[Dict[str, str]] = None,
        holidays: Optional[Dict[str, str]] = None,
        grid_layout: Optional[Tuple[int, int]] = None,
        show_month_headers: bool = True,
        selectmode: str = "single",
        show_navigation: bool = True,
        theme: str = "light",
        date_callback: Optional[callable] = None,
        year_view_callback: Optional[callable] = None,
        popup_width: Optional[int] = None,
        popup_height: Optional[int] = None,
        **kwargs,
    ):
        """
        Initialize the Calendar widget.

        Args:
            parent: Parent widget
            config: Calendar configuration object (optional)
            **kwargs: Additional arguments passed to tk.Frame
        """
        # Use config if provided, otherwise use individual parameters
        if config is None:
            config = CalendarConfig(
                year=year,
                month=month,
                months=months,
                show_week_numbers=show_week_numbers,
                week_start=week_start,
                day_colors=day_colors,
                holidays=holidays,
                grid_layout=grid_layout,
                show_month_headers=show_month_headers,
                selectmode=selectmode,
                show_navigation=show_navigation,
                theme=theme,
                date_callback=date_callback,
                year_view_callback=year_view_callback,
                popup_width=popup_width,
                popup_height=popup_height,
                date_format=kwargs.pop("date_format", "%Y-%m-%d"),
                month_selection_mode=kwargs.pop("month_selection_mode", False),
                year_selection_mode=kwargs.pop("year_selection_mode", False),
            )

        # pylint: disable=R0902
        self.date_callback = config.date_callback
        self.year_view_callback = config.year_view_callback
        self.date_format = config.date_format
        self.month_selection_mode = config.month_selection_mode
        self.year_selection_mode = config.year_selection_mode
        self.year_range_start = config.year_range_start
        self.year_range_end = config.year_range_end
        super().__init__(parent, **kwargs)
        self.logger = logging.getLogger(__name__)

        # Set default values
        year = config.year or datetime.date.today().year
        month = config.month or datetime.date.today().month
        # Validate week_start
        if config.week_start not in ["Sunday", "Monday", "Saturday"]:
            raise ValueError("week_start must be 'Sunday', 'Monday', or 'Saturday'")
        # Validate theme and initialize theme colors
        try:
            self.theme_colors = get_calendar_theme(config.theme)
            self.theme = config.theme
        except ValueError as exc:
            themes = get_calendar_themes()
            raise ValueError(f"theme must be one of {list(themes.keys())}") from exc
        # pylint: disable=R0902
        self.year = year
        self.month = month
        self.months = config.months
        self.show_week_numbers = config.show_week_numbers
        self.week_start = config.week_start
        self.day_colors = config.day_colors or {}
        self.holidays = config.holidays or {}
        self.show_month_headers = config.show_month_headers
        self.selectmode = config.selectmode
        self.show_navigation = config.show_navigation
        # Popup size settings
        self.popup_width = (
            config.popup_width
            if config.popup_width is not None
            else DEFAULT_POPUP_WIDTH
        )
        self.popup_height = (
            config.popup_height
            if config.popup_height is not None
            else DEFAULT_POPUP_HEIGHT
        )
        # DPI scaling support
        try:
            self.dpi_scaling_factor = get_scaling_factor(self)
        except (OSError, ValueError, AttributeError) as e:
            self.logger.debug("Failed to get DPI scaling factor: %s, using 1.0", e)
            self.dpi_scaling_factor = 1.0
        # Selection state
        self.selected_date = None
        self.selected_range = None
        self.selection_callback = None
        # Today color (can be overridden)
        self.today_color = None
        self.today_color_set = True  # Default to showing today color
        # Store original colors for hover effect restoration
        self.original_colors = {}
        # Grid layout settings
        if config.grid_layout is not None:
            self.grid_rows, self.grid_cols = config.grid_layout
        else:
            # Auto-calculate grid layout based on number of months
            if config.months <= 3:
                self.grid_rows, self.grid_cols = 1, config.months
            elif config.months <= 6:
                self.grid_rows, self.grid_cols = 2, 3
            elif config.months <= 12:
                self.grid_rows, self.grid_cols = 3, 4
            else:
                self.grid_rows, self.grid_cols = 4, 4
        # Calendar instance - will be reused for efficiency
        self.cal = calendar.Calendar()
        self._update_calendar_week_start()
        # Widget storage
        self.month_frames = []
        self.day_labels = []
        self.week_labels = []
        self.year_view_labels = []  # For month selection mode
        self.year_selection_labels = []  # For year selection mode
        # Month selection mode attributes
        self.year_view_window = None
        self.year_view_year_label = None
        # Year selection mode attributes
        self.year_selection_header_label = None
        # Create widgets
        if self.year_selection_mode:
            # Create year selection content
            view._create_year_selection_content(self)  # pylint: disable=W0212
        elif self.month_selection_mode:
            # Create year view content
            view._create_year_view_content(self)  # pylint: disable=W0212
        else:
            # Create normal calendar widgets
            view._create_widgets(self)  # pylint: disable=W0212
            view._update_display(self)  # pylint: disable=W0212
        # Update DPI scaling after widget creation
        try:
            self.update_dpi_scaling()
        except (OSError, ValueError, AttributeError) as e:
            self.logger.debug(
                "Failed to update DPI scaling during initialization: %s", e
            )

    def _update_calendar_week_start(self):
        """Update calendar week start setting efficiently."""
        if self.week_start == "Monday":
            self.cal.setfirstweekday(calendar.MONDAY)
        elif self.week_start == "Saturday":
            self.cal.setfirstweekday(calendar.SATURDAY)
        else:  # Sunday
            self.cal.setfirstweekday(calendar.SUNDAY)

    def _get_week_start_offset(self, date: datetime.date) -> int:
        """Get the offset for week start calculation efficiently."""
        if self.week_start == "Monday":
            return date.weekday()
        if self.week_start == "Saturday":
            return (date.weekday() + 2) % 7
        # Sunday
        return (date.weekday() + 1) % 7

    def _get_week_ref_date(self, week_dates):
        """Get the reference date for week number calculation."""
        if self.week_start == "Monday":
            # Monday is already the first day of the week
            return week_dates[0]
        if self.week_start == "Saturday":
            # Saturday start: Monday is the third day (index 2)
            return week_dates[2]
        # Sunday start: Monday is the second day (index 1)
        return week_dates[1]

    def _get_scaled_font(self, base_font):
        """Get font with DPI scaling applied."""
        try:
            if isinstance(base_font, tuple):
                family, size, *style = base_font
                scaled_size = scale_font_size(size, self, self.dpi_scaling_factor)
                return (family, scaled_size, *style)
            return base_font
        except (ValueError, TypeError, AttributeError) as e:
            self.logger.debug("Failed to scale font: %s, using original font", e)
            return base_font

    def _is_year_first_in_format(self) -> bool:
        """
        Determine if year comes first in the date format by analyzing
        format string.
        """
        try:
            year_pos = self.date_format.find("%Y")
            month_pos = self.date_format.find("%m")
            day_pos = self.date_format.find("%d")
            # If no year in format, default to year first
            if year_pos == -1:
                return True
            # Check if year appears before month or day
            if month_pos != -1 and year_pos < month_pos:
                return True
            if day_pos != -1 and year_pos < day_pos:
                return True
            return False
        except (AttributeError, TypeError) as e:
            self.logger.debug(
                "Failed to determine year position in format: "
                "%s, defaulting to year first",
                e,
            )
            return True

    def _get_display_date(self, month_index: int) -> datetime.date:
        """Get the date for a specific month frame, handling overflow."""
        # Use datetime arithmetic for more efficient month overflow handling
        base_date = datetime.date(self.year, self.month, 1)
        # Calculate target month and year using calendar module
        target_month = base_date.month + month_index
        target_year = base_date.year + (target_month - 1) // 12
        target_month = ((target_month - 1) % 12) + 1
        return datetime.date(target_year, target_month, 1)

    def _get_month_days_list(self, display_year: int, display_month: int):
        """Return a list of month day numbers using calendar iterator."""
        return list(self.cal.itermonthdays(display_year, display_month))

    def _get_month_header_texts(
        self, display_year: int, display_month: int
    ) -> tuple[str, str]:
        """Return (year_text, month_text) for headers."""
        year_text = str(display_year)
        month_text = get_month_name(self, display_month, short=True)
        return year_text, month_text

    def _get_year_range_text(self) -> str:
        """Return the current year range header text."""
        return f"{self.year_range_start} - {self.year_range_end}"

    def _get_day_names_for_headers(self) -> list[str]:
        """Return day names for header labels."""
        return get_day_names(self, short=True)

    def _compute_week_numbers(self, display_year: int, display_month: int) -> list[str]:
        """
        Compute week numbers for up to 6 weeks of a given month.

        Returns a list of length 6 containing the ISO week number as string
        or an empty string when the row should be blank.
        """
        month_calendar = self.cal.monthdatescalendar(display_year, display_month)
        week_numbers: list[str] = []
        for week in range(6):
            if week < len(month_calendar):
                week_dates = month_calendar[week]
                week_has_month_days = any(
                    date.year == display_year and date.month == display_month
                    for date in week_dates
                )
                if week_has_month_days:
                    reference_date = self._get_week_ref_date(week_dates)
                    week_numbers.append(str(reference_date.isocalendar()[1]))
                else:
                    week_numbers.append("")
            else:
                week_numbers.append("")
        return week_numbers

    def _get_day_cell_value(
        self,
        _display_year: int,  # pylint: disable=unused-argument
        _display_month: int,  # pylint: disable=unused-argument
        day_index: int,
        month_days,
    ) -> tuple[bool, Optional[int]]:
        """
        Determine whether the cell should show an adjacent-month day or a
        normal day number.

        Returns (use_adjacent, day_number). When use_adjacent is True, the
        caller should render using _set_adjacent_month_day. When False, the
        day_number is guaranteed to be an integer for the current month.
        """
        if day_index < len(month_days):
            day_num = month_days[day_index]
            if day_num == 0:
                return True, None
            return False, int(day_num)
        return True, None

    def _set_adjacent_month_day(  # pylint: disable=too-many-positional-arguments
        self, label, year: int, month: int, week: int, day: int
    ):
        """Set display for adjacent month days."""
        # Calculate the date for this position using datetime arithmetic
        first_day = datetime.date(year, month, 1)
        # Get the first day of the week for this month efficiently
        first_weekday = self._get_week_start_offset(first_day)
        # Calculate the date for this position
        days_from_start = week * 7 + day - first_weekday
        clicked_date = first_day + datetime.timedelta(days=days_from_start)
        # Check if the date is valid (not in current month) using calendar module
        _, last_day = calendar.monthrange(year, month)
        current_month_start = datetime.date(year, month, 1)
        current_month_end = datetime.date(year, month, last_day)
        if clicked_date < current_month_start or clicked_date > current_month_end:
            # Adjacent month day
            label.config(
                text=str(clicked_date.day),
                bg=self.theme_colors["adjacent_day_bg"],
                fg=self.theme_colors["adjacent_day_fg"],
            )
        else:
            # Empty day
            label.config(
                text="",
                bg=self.theme_colors["day_bg"],
                fg=self.theme_colors["day_fg"],
            )

    def _calculate_year_range(self, center_year: int) -> tuple[int, int]:
        """Calculate 12-year range centered on the given year."""
        start_year = center_year - 5
        end_year = center_year + 6
        return start_year, end_year

    def _initialize_year_range(self, center_year: int):
        """Initialize year range for year selection mode."""
        self.year_range_start, self.year_range_end = self._calculate_year_range(
            center_year
        )

    def _on_prev_month(self, month_index: int):
        """Handle previous month navigation."""
        current_date = self._get_display_date(month_index)
        # Use datetime replace for cleaner arithmetic
        if current_date.month == 1:
            prev_date = current_date.replace(year=current_date.year - 1, month=12)
        else:
            prev_date = current_date.replace(month=current_date.month - 1)
        self.set_date(prev_date.year, prev_date.month)

    def _on_next_month(self, month_index: int):
        """Handle next month navigation."""
        current_date = self._get_display_date(month_index)
        # Use datetime replace for cleaner arithmetic
        if current_date.month == 12:
            next_date = current_date.replace(year=current_date.year + 1, month=1)
        else:
            next_date = current_date.replace(month=current_date.month + 1)
        self.set_date(next_date.year, next_date.month)

    def _on_prev_year(self, month_index: int):
        """Handle previous year navigation."""
        current_date = self._get_display_date(month_index)
        prev_date = current_date.replace(year=current_date.year - 1)
        self.set_date(prev_date.year, prev_date.month)

    def _on_next_year(self, month_index: int):
        """Handle next year navigation."""
        current_date = self._get_display_date(month_index)
        next_date = current_date.replace(year=current_date.year + 1)
        self.set_date(next_date.year, next_date.month)

    def _on_month_header_click(self, _month_index: int):
        """Handle month header click - switch to month selection."""
        if self.year_view_callback:
            self.year_view_callback()

    def _on_year_header_click(self):
        """Handle year header click - switch to year selection."""
        self.year_selection_mode = True
        self.month_selection_mode = False
        self._initialize_year_range(self.year)
        view._create_year_selection_content(self)  # pylint: disable=W0212
        # Force UI refresh
        try:
            self.update_idletasks()
            self.update()
        except Exception:  # pylint: disable=broad-except
            pass

    def _on_year_selection_header_click(self):
        """Handle year selection header click - switch back to year view."""
        self.year_selection_mode = False
        self.month_selection_mode = True
        view._create_year_view_content(self)  # pylint: disable=W0212

    def _on_date_click(self, month_index: int, week: int, day: int):
        """Handle date button click."""
        # Get the first day of the month using existing helper
        first_day = self._get_display_date(month_index)
        # Get the first day of the week for this month efficiently
        first_weekday = self._get_week_start_offset(first_day)
        # Calculate the date for this position using datetime arithmetic
        days_from_start = week * 7 + day - first_weekday
        clicked_date = first_day + datetime.timedelta(days=days_from_start)
        # Handle selection based on mode
        if self.selectmode == "single":
            self.selected_date = clicked_date
            self.selected_range = None
        elif self.selectmode == "range":
            if self.selected_range is None:
                self.selected_range = (clicked_date, clicked_date)
            else:
                start_date, _end_date = self.selected_range
                if clicked_date < start_date:
                    self.selected_range = (clicked_date, start_date)
                else:
                    self.selected_range = (start_date, clicked_date)
        # Update display
        view._update_display(self)  # pylint: disable=W0212
        # Call callback if set
        if self.selection_callback:
            if self.selectmode == "single":
                self.selection_callback(clicked_date)
            else:
                self.selection_callback(self.selected_range)

    def _on_prev_year_view(self):
        """Handle previous year navigation in month selection."""
        self.year -= 1
        view._update_year_view(self)  # pylint: disable=W0212

    def _on_next_year_view(self):
        """Handle next year navigation in month selection."""
        self.year += 1
        view._update_year_view(self)  # pylint: disable=W0212

    def _on_prev_year_range(self):
        """Handle previous year range navigation in year selection."""
        self.year_range_start -= 10
        self.year_range_end -= 10
        view._update_year_selection_display(self)  # pylint: disable=W0212

    def _on_next_year_range(self):
        """Handle next year range navigation in year selection."""
        self.year_range_start += 10
        self.year_range_end += 10
        view._update_year_selection_display(self)  # pylint: disable=W0212

    def _on_year_view_month_click(self, month: int):
        """Handle month click in month selection."""
        self.month = month
        self.month_selection_mode = False
        self.year_selection_mode = False
        # Return to normal month view
        view._destroy_year_container(self)  # pylint: disable=W0212
        view._create_widgets(self)  # pylint: disable=W0212
        view._update_display(self)  # pylint: disable=W0212
        # Call date callback if available
        if self.date_callback:
            self.date_callback(self.year, month)

    def _on_year_selection_year_click(self, selected_year: int):
        """Handle year click in year selection."""
        self.year = selected_year
        self.year_selection_mode = False
        self.month_selection_mode = True
        # Switch to month selection view
        view._create_year_view_content(self)  # pylint: disable=W0212
        view._update_year_view(self)  # pylint: disable=W0212
        # Force UI refresh to ensure new content is rendered
        try:
            self.update_idletasks()
            self.update()
        except Exception:  # pylint: disable=broad-except
            pass

    def set_date(self, year: int, month: int):
        """Set the displayed year and month."""
        self.year = year
        self.month = month
        # If in month selection mode, update year view
        if self.month_selection_mode:
            view._update_year_view(self)  # pylint: disable=W0212
        else:
            view._update_display(self)  # pylint: disable=W0212

    def set_holidays(self, holidays: Dict[str, str]):
        """Set holiday colors dictionary."""
        self.holidays = holidays
        if not self.month_selection_mode and not self.year_selection_mode:
            view._update_display(self)  # pylint: disable=W0212

    def set_day_colors(self, day_colors: Dict[str, str]):
        """Set day of week colors dictionary."""
        self.day_colors = day_colors
        if not self.month_selection_mode and not self.year_selection_mode:
            view._update_display(self)  # pylint: disable=W0212

    def set_theme(self, theme: str):
        """Set the calendar theme."""
        try:
            self.theme_colors = get_calendar_theme(theme)
            self.theme = theme
        except ValueError as exc:
            themes = get_calendar_themes()
            raise ValueError(f"theme must be one of {list(themes.keys())}") from exc
        if (
            self.month_selection_mode
            and hasattr(self, "year_view_window")
            and self.year_view_window
        ):
            # Recreate year view with new theme
            self.year_view_window.destroy()
            self.year_view_window = None
            self.year_view_year_label = None
            self.year_view_labels.clear()
            view._create_year_view_content(self)  # pylint: disable=W0212
        else:
            view._update_display(self)  # pylint: disable=W0212
        # Update DPI scaling after theme change
        try:
            self.update_dpi_scaling()
        except (OSError, ValueError, AttributeError) as e:
            self.logger.debug("Failed to update DPI scaling during theme change: %s", e)

    def set_today_color(self, color: str):
        """Set the today color."""
        if color == "none":
            self.today_color = None
            self.today_color_set = False
        else:
            self.today_color = color
            self.today_color_set = True
        if not self.month_selection_mode and not self.year_selection_mode:
            view._update_display(self)  # pylint: disable=W0212

    def set_week_start(self, week_start: str):
        """Set the week start day."""
        if week_start not in ["Sunday", "Monday", "Saturday"]:
            raise ValueError("week_start must be 'Sunday', 'Monday', or 'Saturday'")
        self.week_start = week_start
        self._update_calendar_week_start()
        view._recreate_widgets(self)  # pylint: disable=W0212

    def set_show_week_numbers(self, show: bool):
        """Set whether to show week numbers."""
        self.show_week_numbers = show
        view._recreate_widgets(self)  # pylint: disable=W0212

    def refresh_language(self):
        """Refresh the display to reflect language changes."""
        if (
            self.month_selection_mode
            and hasattr(self, "year_view_window")
            and self.year_view_window
        ):
            # Recreate year view with new language
            self.year_view_window.destroy()
            self.year_view_window = None
            self.year_view_year_label = None
            self.year_view_labels.clear()
            view._create_year_view_content(self)  # pylint: disable=W0212
        else:
            view._update_display(self)  # pylint: disable=W0212
        # Update DPI scaling after language change
        try:
            self.update_dpi_scaling()
        except (OSError, ValueError, AttributeError):
            # Ignore DPI scaling errors during language change
            pass

    def set_months(self, months: int):
        """Set the number of months to display."""
        if months < 1:
            raise ValueError("months must be at least 1")
        self.months = months
        # Update grid layout
        if months <= 3:
            self.grid_rows, self.grid_cols = 1, months
        elif months <= 6:
            self.grid_rows, self.grid_cols = 2, 3
        elif months <= 12:
            self.grid_rows, self.grid_cols = 3, 4
        else:
            self.grid_rows, self.grid_cols = 4, 4
        # Store current settings
        current_day_colors = self.day_colors.copy()
        current_holidays = self.holidays.copy()
        current_month_selection_mode = self.month_selection_mode
        # Destroy all existing widgets completely
        if hasattr(self, "canvas"):
            self.canvas.destroy()
        if hasattr(self, "scrollbar"):
            self.scrollbar.destroy()
        if hasattr(self, "months_container"):
            self.months_container.destroy()
        if hasattr(self, "year_container"):
            self.year_container.destroy()
        # Clear all lists
        self.month_frames.clear()
        self.day_labels.clear()
        self.week_labels.clear()
        self.original_colors.clear()
        if hasattr(self, "month_headers"):
            self.month_headers.clear()
        if hasattr(self, "year_labels"):
            self.year_labels.clear()
        self.year_view_labels.clear()
        # Restore settings
        self.day_colors = current_day_colors
        self.holidays = current_holidays
        self.month_selection_mode = current_month_selection_mode
        # Recreate everything
        if self.month_selection_mode:
            view._create_year_view_content(self)  # pylint: disable=W0212
        else:
            view._create_widgets(self)  # pylint: disable=W0212
            view._update_display(self)  # pylint: disable=W0212
        # Update DPI scaling after recreation
        try:
            self.update_dpi_scaling()
        except (OSError, ValueError, AttributeError):
            # Ignore DPI scaling errors during recreation
            pass

    def get_selected_date(self) -> Optional[datetime.date]:
        """Get the currently selected date (if any)."""
        return self.selected_date

    def get_selected_range(
        self,
    ) -> Optional[Tuple[datetime.date, datetime.date]]:
        """Get the currently selected date range (if any)."""
        return self.selected_range

    def get_popup_geometry(self, parent_widget: tk.Widget) -> str:
        """
        Calculate the optimal geometry for popup windows (calendar and year
        view).

        Args:
            parent_widget: The widget to which the popup is anchored.

        Returns:
            str: The geometry string for the popup window.
        """
        parent_widget.update_idletasks()
        x = parent_widget.winfo_rootx()
        y = parent_widget.winfo_rooty() + parent_widget.winfo_height()
        # Calculate width and height
        width = self.popup_width
        if self.show_week_numbers:
            width += WEEK_NUMBERS_WIDTH_OFFSET
        width *= self.months
        height = self.popup_height
        # Adjust position to ensure popup stays within screen bounds
        try:
            # Get screen dimensions
            screen_width = parent_widget.winfo_screenwidth()
            screen_height = parent_widget.winfo_screenheight()
            # Adjust x position if popup would go off the right edge
            if x + width > screen_width:
                x = max(0, screen_width - width)
            # Adjust y position if popup would go off the bottom edge
            if y + height > screen_height:
                # Try to show popup above the widget instead
                y = max(0, parent_widget.winfo_rooty() - height)
                # If still off screen, adjust to fit
                if y + height > screen_height:
                    y = max(0, screen_height - height)
        except (AttributeError, TypeError, OSError) as e:
            self.logger.debug(
                "Failed to adjust popup position: %s, using original position", e
            )
        return f"{width}x{height}+{x}+{y}"

    def bind_date_selected(self, callback):
        """Bind a callback function to date selection events."""
        self.selection_callback = callback

    def set_selected_date(self, date: datetime.date):
        """Set the selected date."""
        self.selected_date = date
        self.selected_range = None
        if not self.month_selection_mode and not self.year_selection_mode:
            view._update_display(self)  # pylint: disable=W0212

    def set_selected_range(self, start_date: datetime.date, end_date: datetime.date):
        """Set the selected date range."""
        self.selected_range = (start_date, end_date)
        self.selected_date = None
        if not self.month_selection_mode and not self.year_selection_mode:
            view._update_display(self)  # pylint: disable=W0212

    def set_popup_size(self, width: Optional[int] = None, height: Optional[int] = None):
        """
        Set the popup size for both calendar and month selection.

        Args:
            width: Width in pixels (None to use default)
            height: Height in pixels (None to use default)
        """
        if width is not None:
            self.popup_width = width
        else:
            self.popup_width = DEFAULT_POPUP_WIDTH
        if height is not None:
            self.popup_height = height
        else:
            self.popup_height = DEFAULT_POPUP_HEIGHT

    def update_dpi_scaling(self):
        """Update DPI scaling factor and refresh display."""
        try:
            old_scaling = self.dpi_scaling_factor
            self.dpi_scaling_factor = get_scaling_factor(self)
            # Only update if scaling factor has changed
            if abs(old_scaling - self.dpi_scaling_factor) > 0.01:
                if self.year_selection_mode:
                    # Don't update display in year selection mode
                    pass
                elif not self.month_selection_mode:
                    view._update_display(self)  # pylint: disable=W0212
                else:
                    view._update_year_view(self)  # pylint: disable=W0212
        except (OSError, ValueError, AttributeError) as e:
            self.logger.warning(
                "Failed to update DPI scaling: %s, using 1.0 as fallback", e
            )
            self.dpi_scaling_factor = 1.0

    # Public methods for backward compatibility
    def _get_day_names(self, short: bool = False):
        """Get localized day names."""
        return get_day_names(self, short)

    def _get_month_name(self, month: int, short: bool = False):
        """Get localized month name."""
        return get_month_name(self, month, short)

    def _update_display(self):
        """Update the calendar display."""
        # Check if in year selection mode
        if self.year_selection_mode:
            return
        view._update_display(self)  # pylint: disable=W0212
