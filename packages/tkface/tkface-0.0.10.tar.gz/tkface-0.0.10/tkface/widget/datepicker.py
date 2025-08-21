"""
Date picker widgets for tkface.

This module provides DateFrame and DateEntry widgets that display
popup calendars for date selection.
"""

import datetime
import logging
import re
import sys
import tkinter as tk
from dataclasses import dataclass
from tkinter import ttk
from typing import Dict, Optional

from . import get_scaling_factor
from .calendar import Calendar, get_calendar_theme, view


@dataclass
class DatePickerConfig:
    """Configuration for DatePicker widgets."""

    date_format: str = "%Y-%m-%d"
    year: Optional[int] = None
    month: Optional[int] = None
    show_week_numbers: bool = False
    week_start: str = "Sunday"
    day_colors: Optional[Dict[str, str]] = None
    holidays: Optional[Dict[str, str]] = None
    selectmode: str = "single"
    theme: str = "light"
    language: str = "en"
    today_color: str = "yellow"
    date_callback: Optional[callable] = None


# Calendar will be imported when needed to avoid circular imports


class _DatePickerBase:
    """Base class for date picker widgets with common functionality."""

    def __init__(  # pylint: disable=R0917
        self,
        parent,
        config: Optional[DatePickerConfig] = None,
        date_format: str = "%Y-%m-%d",
        year: Optional[int] = None,
        month: Optional[int] = None,
        show_week_numbers: bool = False,
        week_start: str = "Sunday",
        day_colors: Optional[Dict[str, str]] = None,
        holidays: Optional[Dict[str, str]] = None,
        selectmode: str = "single",
        theme: str = "light",
        language: str = "en",
        today_color: str = "yellow",
        date_callback: Optional[callable] = None,
        **kwargs,  # pylint: disable=unused-argument
    ):
        # Use config if provided, otherwise use individual parameters
        if config is None:
            config = DatePickerConfig(
                date_format=date_format,
                year=year,
                month=month,
                show_week_numbers=show_week_numbers,
                week_start=week_start,
                day_colors=day_colors,
                holidays=holidays,
                selectmode=selectmode,
                theme=theme,
                language=language,
                today_color=today_color,
                date_callback=date_callback,
            )

        self.logger = logging.getLogger(__name__)
        # Store parent for toplevel access
        self.master = parent
        # Get platform information once
        self.platform = sys.platform
        # DPI scaling support
        try:
            self.dpi_scaling_factor = get_scaling_factor(parent)
        except (ImportError, AttributeError, TypeError) as e:
            self.logger.debug("Failed to get DPI scaling factor: %s, using 1.0", e)
            self.dpi_scaling_factor = 1.0
        self.date_format = config.date_format
        self.selected_date = None
        self.popup = None
        self.date_callback = config.date_callback
        # Calendar will be created when popup is shown
        self.calendar = None
        # Initialize attributes that will be set later
        self.year_view_window = None
        self.year_view_calendar = None
        self._parent_configure_binding = None
        self.calendar_config = {
            "year": config.year,
            "month": config.month,
            "months": 1,
            "show_week_numbers": config.show_week_numbers,
            "week_start": config.week_start,
            "day_colors": config.day_colors,
            "holidays": config.holidays,
            "selectmode": config.selectmode,
            "show_navigation": True,
            "theme": config.theme,
            "date_format": config.date_format,
        }
        # Set today color if specified
        self.today_color = None
        if config.today_color != "yellow":
            self.set_today_color(config.today_color)

    def _on_date_selected(self, date):
        """Handle date selection from calendar."""
        if date:
            self.selected_date = date
            self._update_entry_text(date.strftime(self.date_format))
            self.hide_calendar()
            # Call the callback if provided
            if self.date_callback:
                self.date_callback(date)
            # Reset pressed state for DateEntry
            if hasattr(self, "state"):
                self.state(["!pressed"])

    def _update_entry_text(self, text: str):
        """Update the entry text (to be implemented by subclasses)."""
        raise NotImplementedError

    def _on_popup_click(
        self, event, popup_window, calendar_widget, hide_callback
    ):  # pylint: disable=unused-argument
        """
        Handle click events in the popup to detect clicks outside the
        calendar.
        """
        try:
            # If calendar is in selection overlay modes and click is inside the
            # calendar, do nothing
            if (
                hasattr(self, "calendar")
                and self.calendar
                and (
                    getattr(self.calendar, "year_selection_mode", False)
                    or getattr(self.calendar, "month_selection_mode", False)
                )
            ):
                if not isinstance(event.widget, str) and self._is_child_of_calendar(
                    event.widget, calendar_widget
                ):
                    calendar_widget.focus_set()
                    return "break"

            # Some platforms may deliver a string widget; fall back to pointer check
            if isinstance(event.widget, str):
                x, y = popup_window.winfo_pointerxy()
                xc = popup_window.winfo_rootx()
                yc = popup_window.winfo_rooty()
                w = popup_window.winfo_width()
                h = popup_window.winfo_height()
                if xc <= x <= xc + w and yc <= y <= yc + h:
                    calendar_widget.focus_set()
                    return "break"
                hide_callback()
                return "break"

            if not self._is_child_of_calendar(event.widget, calendar_widget):
                hide_callback()
            else:
                calendar_widget.focus_set()
            return "break"
        except Exception:  # pylint: disable=broad-except
            # On any unexpected error, prefer keeping the popup open
            try:
                calendar_widget.focus_set()
            except Exception:  # pylint: disable=broad-except
                pass
            return "break"

    def _bind_calendar_events(self, widget):
        """Bind events to all child widgets of the calendar."""
        try:
            widget.bind("<ButtonRelease-1>", lambda e: "break")
            for child in widget.winfo_children():
                self._bind_calendar_events(child)
        except (AttributeError, tk.TclError) as e:
            self.logger.debug("Failed to bind calendar events: %s", e)

    def _setup_click_outside_handling(self):
        """Setup click outside handling for regular calendar."""
        self.calendar.bind("<FocusOut>", self._on_focus_out)
        self.popup.bind(
            "<Button-1>",
            lambda e: self._on_popup_click(
                e, self.popup, self.calendar, self.hide_calendar
            ),
        )
        self.popup.bind(
            "<ButtonRelease-1>",
            lambda e: self._on_popup_click(
                e, self.popup, self.calendar, self.hide_calendar
            ),
        )
        # Get the toplevel window from parent
        toplevel = self.master.winfo_toplevel() if hasattr(self, "master") else None
        if toplevel:
            toplevel.bind(
                "<Button-1>",
                lambda e: self._on_main_window_click(e, self.popup, self.hide_calendar),
            )

    def _is_child_of_popup(self, widget):
        """Check if widget is a child of the popup window."""
        current = widget
        while current:
            if current == self.popup:
                return True
            current = current.master
        return False

    def _setup_focus(self):
        """Setup focus for the popup."""
        try:
            self.popup.lift()
            self.calendar.focus_set()
            self.popup.after(50, self.calendar.focus_set)
            self.popup.after(100, self.calendar.focus_force)
        except (AttributeError, tk.TclError) as e:
            self.logger.debug("Failed to setup focus: %s", e)

    def _on_focus_out(self, event):  # pylint: disable=unused-argument
        """Handle focus out events."""
        focus_widget = self.focus_get()  # pylint: disable=no-member
        # If we have a calendar, and focus is within the calendar (including
        # year/month views), do not hide
        try:
            if hasattr(self, "calendar") and self.calendar:
                if focus_widget is not None:
                    if focus_widget == self or self._is_child_of_calendar(
                        focus_widget, self.calendar
                    ):
                        return "break"
                # If calendar is in selection overlay modes, be conservative and
                # keep it open
                if getattr(self.calendar, "year_selection_mode", False) or getattr(
                    self.calendar, "month_selection_mode", False
                ):
                    # If pointer is inside popup, keep focus on calendar
                    try:
                        x, y = self.popup.winfo_pointerxy()
                        xc = self.popup.winfo_rootx()
                        yc = self.popup.winfo_rooty()
                        w = self.popup.winfo_width()
                        h = self.popup.winfo_height()
                        if xc <= x <= xc + w and yc <= y <= yc + h:
                            self.calendar.focus_force()
                            return "break"
                    except Exception:  # pylint: disable=broad-except
                        return "break"
        except Exception:  # pylint: disable=broad-except
            pass

        if focus_widget is not None:
            if focus_widget == self:
                # Don't hide calendar when focus is on the DateEntry itself
                return "break"
            self.hide_calendar()
        else:
            try:
                x, y = self.popup.winfo_pointerxy()
                xc = self.popup.winfo_rootx()
                yc = self.popup.winfo_rooty()
                w = self.popup.winfo_width()
                h = self.popup.winfo_height()
                if xc <= x <= xc + w and yc <= y <= yc + h:
                    self.calendar.focus_force()
                else:
                    self.hide_calendar()
            except (AttributeError, tk.TclError):
                self.hide_calendar()
        return "break"

    def _is_child_of_calendar(self, widget, calendar_widget):
        """Check if widget is a child of calendar widget."""
        if isinstance(widget, str):
            return False
        current = widget
        while current:
            if current == calendar_widget:
                return True
            current = current.master
        return False

    def _on_main_window_click(self, event, popup_window, hide_callback):
        """Handle click events on the main window."""
        if isinstance(event.widget, str):
            return "break"
        if popup_window and popup_window.winfo_exists():
            popup_x = popup_window.winfo_rootx()
            popup_y = popup_window.winfo_rooty()
            popup_w = popup_window.winfo_width()
            popup_h = popup_window.winfo_height()
            # Get the toplevel window from parent
            toplevel = self.master.winfo_toplevel() if hasattr(self, "master") else None
            if toplevel:
                root_x = toplevel.winfo_rootx() + event.x
                root_y = toplevel.winfo_rooty() + event.y
            else:
                root_x = event.x
                root_y = event.y
            if (
                root_x < popup_x
                or root_x > popup_x + popup_w
                or root_y < popup_y
                or root_y > popup_y + popup_h
            ):
                hide_callback()
        return "break"

    def _setup_year_view_click_outside_handling(self):
        """Setup click outside handling for month selection."""
        self.year_view_window.bind(
            "<Button-1>",
            lambda e: self._on_popup_click(
                e,
                self.year_view_window,
                self.year_view_calendar,
                self.hide_year_view,
            ),
        )
        self.year_view_window.bind(
            "<ButtonRelease-1>",
            lambda e: self._on_popup_click(
                e,
                self.year_view_window,
                self.year_view_calendar,
                self.hide_year_view,
            ),
        )
        # Get the toplevel window from parent
        toplevel = self.master.winfo_toplevel() if hasattr(self, "master") else None
        if toplevel:
            toplevel.bind(
                "<Button-1>",
                lambda e: self._on_main_window_click(
                    e, self.year_view_window, self.hide_year_view
                ),
            )

    def _on_calendar_month_selected(
        self, year, month
    ):  # pylint: disable=unused-argument
        """Handle month selection in calendar."""
        self.hide_calendar()
        self.calendar_config["year"] = year
        self.calendar_config["month"] = month
        self.show_calendar()

    def _on_calendar_year_view_request(self):
        """Handle month selection request from calendar."""
        # Instead of creating a new window, switch the current calendar to year
        # view mode
        if self.calendar:
            self.calendar.month_selection_mode = True
            self.calendar.year_selection_mode = False
            # Recreate the calendar content in year view mode
            view._create_year_view_content(self.calendar)  # pylint: disable=W0212
            view._update_year_view(self.calendar)  # pylint: disable=W0212
        else:
            # Fallback to old method
            self.show_year_view()

    def show_year_view(self):
        """Show month selection calendar."""
        if hasattr(self, "year_view_window") and self.year_view_window:
            return
        if self.popup:
            self.popup.withdraw()
        self.year_view_window = tk.Toplevel(self)
        self.year_view_window.withdraw()
        theme = self.calendar_config.get("theme", "light")
        try:
            theme_colors = get_calendar_theme(theme)
        except ValueError as e:
            self.logger.debug(
                "Failed to get theme colors for %s: %s, using light theme", theme, e
            )
            theme_colors = get_calendar_theme("light")
        self.year_view_window.overrideredirect(True)
        self.year_view_window.resizable(False, False)
        self.year_view_window.configure(bg=theme_colors["background"])
        # Get the toplevel window from parent
        toplevel = self.master.winfo_toplevel() if hasattr(self, "master") else None
        if toplevel:
            self.year_view_window.transient(toplevel)
        year_view_config = self.calendar_config.copy()
        year_view_config["month_selection_mode"] = True
        self.year_view_calendar = Calendar(
            self.year_view_window,
            **year_view_config,
            date_callback=self._on_year_view_month_selected,
        )
        # Position the year view using geometry from Calendar
        self.year_view_window.update_idletasks()
        year_view_geometry = self.year_view_calendar.get_popup_geometry(self)
        # Scale year view geometry based on DPI (only scale size, not position)
        try:
            if self.dpi_scaling_factor > 1.0:
                # Parse geometry string and scale only dimensions, not position
                match = re.match(r"(\d+)x(\d+)\+(\d+)\+(\d+)", year_view_geometry)
                if match:
                    width, height, x, y = map(int, match.groups())
                    scaled_width = int(width * self.dpi_scaling_factor)
                    scaled_height = int(height * self.dpi_scaling_factor)
                    # Don't scale position coordinates (x, y) - keep them as is
                    year_view_geometry = f"{scaled_width}x{scaled_height}+{x}+{y}"
        except (ValueError, AttributeError) as e:
            self.logger.debug(
                "Failed to scale year view geometry: %s, using original geometry", e
            )
        self.year_view_window.geometry(year_view_geometry)
        self.year_view_calendar.pack(fill="both", expand=True)
        # Setup click outside handling for year view
        self._setup_year_view_click_outside_handling()
        # Bind Escape key to close year view
        self.year_view_window.bind("<Escape>", lambda e: self.hide_year_view())
        self.year_view_window.deiconify()
        self.year_view_window.lift()
        self.year_view_window.focus_force()
        self.year_view_window.update()
        self.year_view_window.lift()
        # Ensure year view window is on top
        self.year_view_window.attributes("-topmost", True)
        self.year_view_window.attributes("-topmost", False)

    def hide_year_view(self):
        """Hide month selection calendar."""
        if hasattr(self, "year_view_window") and self.year_view_window:
            # Unbind events to prevent memory leaks
            try:
                self.year_view_window.unbind("<Button-1>")
                self.year_view_window.unbind("<ButtonRelease-1>")
                self.year_view_window.unbind("<Escape>")
            except (AttributeError, tk.TclError) as e:
                self.logger.debug("Failed to unbind year view events: %s", e)
            self.year_view_window.destroy()
            self.year_view_window = None
            self.year_view_calendar = None

    def _on_parent_configure(self, event):  # pylint: disable=unused-argument
        """Handle parent window configuration changes."""
        year_view_active = (
            hasattr(self, "year_view_window")
            and self.year_view_window
            and self.year_view_window.winfo_exists()
        )
        if self.popup and self.popup.winfo_exists() and not year_view_active:
            # Recalculate and set geometry
            popup_geometry = self.calendar.get_popup_geometry(self)
            # Scale popup geometry based on DPI (only scale size, not position)
            try:
                if self.dpi_scaling_factor > 1.0:
                    match = re.match(r"(\d+)x(\d+)\+(\d+)\+(\d+)", popup_geometry)
                    if match:
                        width, height, x, y = map(int, match.groups())
                        scaled_width = int(width * self.dpi_scaling_factor)
                        scaled_height = int(height * self.dpi_scaling_factor)
                        # Don't scale position coordinates (x, y) - keep them
                        # as is
                        popup_geometry = f"{scaled_width}x{scaled_height}+{x}+{y}"
            except (ValueError, AttributeError) as e:
                self.logger.debug(
                    "Failed to scale popup geometry: %s, using original geometry", e
                )
            self.popup.geometry(popup_geometry)
        if year_view_active and hasattr(self, "year_view_calendar"):
            # Recalculate and set geometry for year view
            year_view_geometry = self.year_view_calendar.get_popup_geometry(self)
            # Scale year view geometry based on DPI (only scale size, not
            # position)
            try:
                if self.dpi_scaling_factor > 1.0:
                    match = re.match(r"(\d+)x(\d+)\+(\d+)\+(\d+)", year_view_geometry)
                    if match:
                        width, height, x, y = map(int, match.groups())
                        scaled_width = int(width * self.dpi_scaling_factor)
                        scaled_height = int(height * self.dpi_scaling_factor)
                        # Don't scale position coordinates (x, y) - keep them
                        # as is
                        year_view_geometry = f"{scaled_width}x{scaled_height}+{x}+{y}"
            except (ValueError, AttributeError) as e:
                self.logger.debug(
                    "Failed to scale year view geometry in parent configure: %s, "
                    "using original geometry",
                    e,
                )
            self.year_view_window.geometry(year_view_geometry)

    def _bind_parent_movement_events(self):
        """Bind events to monitor parent window movement."""
        if self.popup or (hasattr(self, "year_view_window") and self.year_view_window):
            main_window = self.winfo_toplevel()  # pylint: disable=no-member
            main_window.bind("<Configure>", self._on_parent_configure)
            self._parent_configure_binding = main_window.bind(
                "<Configure>", self._on_parent_configure
            )

    def _unbind_parent_movement_events(self):
        """Unbind parent window movement events."""
        if hasattr(self, "_parent_configure_binding"):
            main_window = self.winfo_toplevel()  # pylint: disable=no-member
            try:
                main_window.unbind("<Configure>", self._parent_configure_binding)
            except (AttributeError, tk.TclError) as e:
                self.logger.debug("Failed to unbind parent configure events: %s", e)
            delattr(self, "_parent_configure_binding")

    def _on_year_view_month_selected(self, year, month):
        """Handle month selection in month selection."""
        # Update calendar config
        self.calendar_config["year"] = year
        self.calendar_config["month"] = month
        # Switch back to normal calendar view
        if self.calendar:
            self.calendar.month_selection_mode = False
            self.calendar.year_selection_mode = False
            # Recreate normal calendar view
            view._destroy_year_container(self.calendar)  # pylint: disable=W0212
            view._create_widgets(self.calendar)  # pylint: disable=W0212
            view._update_display(self.calendar)  # pylint: disable=W0212

    def show_calendar(self):
        """Show the popup calendar."""
        if self.popup:
            return
        self.popup = tk.Toplevel(self)
        self.popup.withdraw()
        self.popup.overrideredirect(True)
        self.popup.resizable(False, False)
        if hasattr(self, "calendar_config") and "theme" in self.calendar_config:
            theme = self.calendar_config["theme"]
            try:
                theme_colors = get_calendar_theme(theme)
                self.popup.configure(bg=theme_colors["background"])
            except ValueError as e:
                self.logger.debug(
                    "Failed to get theme colors for %s: %s, using light theme", theme, e
                )
                theme_colors = get_calendar_theme("light")
                self.popup.configure(bg=theme_colors["background"])
        # Get the toplevel window from parent
        toplevel = self.master.winfo_toplevel() if hasattr(self, "master") else None
        if toplevel:
            self.popup.transient(toplevel)
        self.popup.after(100, self._setup_focus)
        self.calendar = Calendar(
            self.popup,
            **self.calendar_config,
            date_callback=self._on_calendar_month_selected,
            year_view_callback=self._on_calendar_year_view_request,
        )
        self.calendar.bind_date_selected(self._on_date_selected)
        self._bind_calendar_events(self.calendar)
        if self.today_color:
            self.calendar.set_today_color(self.today_color)
        self.calendar.pack(expand=True, fill="both", padx=2, pady=2)
        # Position the popup using geometry from Calendar
        self.popup.update_idletasks()
        popup_geometry = self.calendar.get_popup_geometry(self)
        # Scale popup geometry based on DPI (only scale size, not position)
        try:
            if self.dpi_scaling_factor > 1.0:
                # Parse geometry string and scale only dimensions, not position
                match = re.match(r"(\d+)x(\d+)\+(\d+)\+(\d+)", popup_geometry)
                if match:
                    width, height, x, y = map(int, match.groups())
                    scaled_width = int(width * self.dpi_scaling_factor)
                    scaled_height = int(height * self.dpi_scaling_factor)
                    # Don't scale position coordinates (x, y) - keep them as is
                    popup_geometry = f"{scaled_width}x{scaled_height}+{x}+{y}"
        except (ValueError, AttributeError) as e:
            self.logger.debug(
                "Failed to scale popup geometry in show_calendar: "
                "%s, using original geometry",
                e,
            )
        self.popup.geometry(popup_geometry)
        self.popup.deiconify()
        self.popup.lift()
        self.popup.bind("<Escape>", lambda e: self.hide_calendar())
        self._setup_click_outside_handling()
        self._bind_parent_movement_events()
        self.calendar.focus_set()

    def hide_calendar(self):
        """Hide the popup calendar."""
        if self.popup:
            self._unbind_parent_movement_events()
            self.popup.destroy()
            self.popup = None
            self.calendar = None
        # Reset pressed state for DateEntry
        if hasattr(self, "state"):
            self.state(["!pressed"])

    def get_date(self) -> Optional[datetime.date]:
        """Get the selected date."""
        return (
            self.calendar.get_selected_date() if self.calendar else self.selected_date
        )

    def set_selected_date(self, date: datetime.date):
        """Set the selected date."""
        self.selected_date = date
        if self.calendar:
            self.calendar.set_selected_date(date)
        self._update_entry_text(date.strftime(self.date_format))

    def get_date_string(self) -> str:
        """Get the selected date as a string."""
        selected_date = self.get_date()
        return selected_date.strftime(self.date_format) if selected_date else ""

    def _delegate_to_calendar(self, method_name, *args, **kwargs):
        """Delegate method calls to calendar if it exists."""
        if self.calendar and hasattr(self.calendar, method_name):
            getattr(self.calendar, method_name)(*args, **kwargs)

    def _update_config_and_delegate(self, config_key, value, method_name):
        """Update config and delegate to calendar."""
        self.calendar_config[config_key] = value
        self._delegate_to_calendar(method_name, value)

    def refresh_language(self):
        """Refresh the calendar language."""
        self._delegate_to_calendar("refresh_language")

    def set_today_color(self, color: str):
        """Set the today color."""
        self.today_color = color
        self._delegate_to_calendar("set_today_color", color)

    def set_theme(self, theme: str):
        """Set the calendar theme."""
        self._update_config_and_delegate("theme", theme, "set_theme")

    def set_day_colors(self, day_colors: Dict[str, str]):
        """Set day of week colors dictionary."""
        self._update_config_and_delegate("day_colors", day_colors, "set_day_colors")

    def set_week_start(self, week_start: str):
        """Set the week start day."""
        self._update_config_and_delegate("week_start", week_start, "set_week_start")

    def set_show_week_numbers(self, show: bool):
        """Set whether to show week numbers."""
        self._update_config_and_delegate(
            "show_week_numbers", show, "set_show_week_numbers"
        )

    def set_popup_size(self, width: Optional[int] = None, height: Optional[int] = None):
        """Set the popup size for both calendar and month selection."""
        self._delegate_to_calendar("set_popup_size", width, height)

    def update_dpi_scaling(self):
        """Update DPI scaling factor and refresh display."""
        try:
            old_scaling = self.dpi_scaling_factor
            self.dpi_scaling_factor = get_scaling_factor(self)
        except (ImportError, AttributeError, TypeError) as e:
            self.logger.warning(
                "Failed to update DPI scaling: %s, using 1.0 as fallback", e
            )
            self.dpi_scaling_factor = 1.0
            return

        # Only update if scaling factor has changed significantly
        if abs(old_scaling - self.dpi_scaling_factor) <= 0.01:
            return

        # Entry width is handled automatically by DPI system
        # No manual scaling needed for Entry widgets
        # Update calendar if it exists
        if self.calendar and hasattr(self.calendar, "update_dpi_scaling"):
            self.calendar.update_dpi_scaling()

        # Update popup geometry if popup exists
        if not (self.popup and self.popup.winfo_exists()):
            return

        popup_geometry = self.calendar.get_popup_geometry(self)
        if self.dpi_scaling_factor <= 1.0:
            self.popup.geometry(popup_geometry)
            return

        try:
            match = re.match(r"(\d+)x(\d+)\+(\d+)\+(\d+)", popup_geometry)
            if not match:
                self.popup.geometry(popup_geometry)
                return

            width, height, x, y = map(int, match.groups())
            scaled_width = int(width * self.dpi_scaling_factor)
            scaled_height = int(height * self.dpi_scaling_factor)
            # Don't scale position coordinates (x, y) - keep them as is
            popup_geometry = f"{scaled_width}x{scaled_height}+{x}+{y}"
            self.popup.geometry(popup_geometry)
        except (ValueError, AttributeError) as e:
            self.logger.debug(
                "Failed to scale popup geometry in update_dpi_scaling: %s", e
            )
            self.popup.geometry(popup_geometry)


class DateFrame(tk.Frame, _DatePickerBase):
    @classmethod
    def create(  # pylint: disable=R0917
        cls,
        parent,
        date_format: str = "%Y-%m-%d",
        year: Optional[int] = None,
        month: Optional[int] = None,
        show_week_numbers: bool = False,
        week_start: str = "Sunday",
        day_colors: Optional[Dict[str, str]] = None,
        holidays: Optional[Dict[str, str]] = None,
        selectmode: str = "single",
        theme: str = "light",
        language: str = "en",
        today_color: str = "yellow",
        date_callback: Optional[callable] = None,
        button_text: str = "📅",
        **kwargs,
    ):
        """
        Create DateFrame widget with individual parameters
        (for backward compatibility).
        """
        config = DatePickerConfig(
            date_format=date_format,
            year=year,
            month=month,
            show_week_numbers=show_week_numbers,
            week_start=week_start,
            day_colors=day_colors,
            holidays=holidays,
            selectmode=selectmode,
            theme=theme,
            language=language,
            today_color=today_color,
            date_callback=date_callback,
        )
        return cls(parent, config=config, button_text=button_text, **kwargs)

    def __init__(  # pylint: disable=R0917
        self,
        parent,
        config: Optional[DatePickerConfig] = None,
        date_format: str = "%Y-%m-%d",
        year: Optional[int] = None,
        month: Optional[int] = None,
        show_week_numbers: bool = False,
        week_start: str = "Sunday",
        day_colors: Optional[Dict[str, str]] = None,
        holidays: Optional[Dict[str, str]] = None,
        selectmode: str = "single",
        theme: str = "light",
        language: str = "en",
        today_color: str = "yellow",
        date_callback: Optional[callable] = None,
        button_text: str = "📅",
        **kwargs,
    ):
        tk.Frame.__init__(self, parent)
        _DatePickerBase.__init__(
            self,
            parent,
            config,
            date_format,
            year,
            month,
            show_week_numbers,
            week_start,
            day_colors,
            holidays,
            selectmode,
            theme,
            language,
            today_color,
            date_callback,
            **kwargs,
        )
        # Create entry and button
        # Entry width is character units and will be handled by DPI system
        self.entry = tk.Entry(self, state="readonly", width=15)
        self.entry.pack(side="left", fill="x", expand=True)
        self.button = tk.Button(self, text=button_text, command=self.show_calendar)
        self.button.pack(side="right")
        # Update DPI scaling after widget creation
        try:
            self.update_dpi_scaling()
        except (ImportError, AttributeError, TypeError) as e:
            self.logger.debug(
                "Failed to update DPI scaling during DateFrame initialization: %s", e
            )

    def _update_entry_text(self, text: str):
        """Update the entry text."""
        self.entry.config(state="normal")
        self.entry.delete(0, tk.END)
        self.entry.insert(0, text)
        self.entry.config(state="readonly")

    def set_button_text(self, text: str):
        """Set the button text."""
        self.button.config(text=text)


class DateEntry(ttk.Entry, _DatePickerBase):
    @classmethod
    def create(  # pylint: disable=R0917
        cls,
        parent,
        date_format: str = "%Y-%m-%d",
        year: Optional[int] = None,
        month: Optional[int] = None,
        show_week_numbers: bool = False,
        week_start: str = "Sunday",
        day_colors: Optional[Dict[str, str]] = None,
        holidays: Optional[Dict[str, str]] = None,
        selectmode: str = "single",
        theme: str = "light",
        language: str = "en",
        today_color: str = "yellow",
        date_callback: Optional[callable] = None,
        button_text: str = None,
        **kwargs,
    ):
        """
        Create DateEntry widget with individual parameters
        (for backward compatibility).
        """
        config = DatePickerConfig(
            date_format=date_format,
            year=year,
            month=month,
            show_week_numbers=show_week_numbers,
            week_start=week_start,
            day_colors=day_colors,
            holidays=holidays,
            selectmode=selectmode,
            theme=theme,
            language=language,
            today_color=today_color,
            date_callback=date_callback,
        )
        return cls(parent, config=config, button_text=button_text, **kwargs)

    def __init__(  # pylint: disable=R0917
        self,
        parent,
        config: Optional[DatePickerConfig] = None,
        date_format: str = "%Y-%m-%d",
        year: Optional[int] = None,
        month: Optional[int] = None,
        show_week_numbers: bool = False,
        week_start: str = "Sunday",
        day_colors: Optional[Dict[str, str]] = None,
        holidays: Optional[Dict[str, str]] = None,
        selectmode: str = "single",
        theme: str = "light",
        language: str = "en",
        today_color: str = "yellow",
        date_callback: Optional[callable] = None,
        button_text: str = None,  # pylint: disable=unused-argument
        **kwargs,
    ):
        # Remove button_text from kwargs as it's not supported for DateEntry
        if "button_text" in kwargs:
            del kwargs["button_text"]
        # Setup style to look like a combobox
        self.style = ttk.Style(parent)
        self._setup_style()
        # Initialize ttk.Entry with combobox-like style
        ttk.Entry.__init__(self, parent, style="DateEntryCombobox", **kwargs)
        _DatePickerBase.__init__(
            self,
            parent,
            config,
            date_format,
            year,
            month,
            show_week_numbers,
            week_start,
            day_colors,
            holidays,
            selectmode,
            theme,
            language,
            today_color,
            date_callback,
            **kwargs,
        )
        # Set readonly state
        self.configure(state="readonly")
        # Bind events for combobox-like behavior
        self.bind("<ButtonPress-1>", self._on_b1_press)
        self.bind("<Key>", self._on_key)
        # Bind focus out event for calendar
        self.bind("<FocusOut>", self._on_focus_out_entry)
        # Update DPI scaling after widget creation
        try:
            self.update_dpi_scaling()
        except (ImportError, AttributeError, TypeError) as e:
            self.logger.debug(
                "Failed to update DPI scaling during DateEntry initialization: %s", e
            )

    def _setup_style(self):
        """Setup style to make DateEntry look like a Combobox."""
        self.style.layout("DateEntryCombobox", self.style.layout("TCombobox"))
        conf = self.style.configure("TCombobox")
        if conf:
            self.style.configure("DateEntryCombobox", **conf)
        maps = self.style.map("TCombobox")
        if maps:
            self.style.map("DateEntryCombobox", **maps)

    def _on_b1_press(self, event):
        """Handle button press events."""
        x = event.x
        width = self.winfo_width()
        right_area = x > width - 20
        # Check if click is in the right area (dropdown button area)
        if right_area:
            self.state(["pressed"])
            self.drop_down()
            return "break"  # Consume the event
        return None

    def drop_down(self):
        """
        Display or withdraw the drop-down calendar depending on its current
        state.
        """
        if self.popup and self.popup.winfo_ismapped():
            self.hide_calendar()
        else:
            self.show_calendar()

    def _on_focus_out_entry(self, _event):
        """Handle focus out event for the entry."""
        # Only hide if focus is not on the calendar
        if self.popup and self.popup.winfo_ismapped():
            focused_widget = self.focus_get()
            if focused_widget != self and not self._is_child_of_calendar(
                focused_widget, self.calendar
            ):
                self.hide_calendar()

    def _on_key(self, _event):  # pylint: disable=unused-argument
        """Handle key events."""
        if _event.keysym in ("Down", "space"):
            self.show_calendar()

    def _update_entry_text(self, text: str):
        """Update the entry text."""
        self.configure(state="normal")
        self.delete(0, tk.END)
        self.insert(0, text)
        self.configure(state="readonly")
