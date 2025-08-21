"""
Style and theme functionality for the Calendar widget.

This module provides theme loading, color processing, and appearance
customization for the Calendar widget.
"""

import configparser
import datetime
import logging
import tkinter as tk
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

from ... import lang


@dataclass
class DayColorContext:
    """Context for day color determination."""

    theme_colors: Dict[str, Any]
    selected_date: Optional[datetime.date]
    selected_range: Optional[Tuple[datetime.date, datetime.date]]
    today: datetime.date
    today_color: Optional[str]
    today_color_set: bool
    day_colors: Dict[str, str]
    holidays: Dict[str, str]
    date_obj: datetime.date
    year: int
    month: int
    day: int


@dataclass
class ColorPair:
    """Background and foreground color pair."""

    bg: str
    fg: str


def _parse_font(font_str: str) -> tuple:
    """
    Parse font string from .ini file to tuple format.

    Args:
        font_str: Font string in format "family, size, style"

    Returns:
        tuple: Font tuple (family, size, style)
    """
    parts = [part.strip() for part in font_str.split(",")]
    if len(parts) >= 2:
        family = parts[0]
        try:
            size = int(parts[1])
        except ValueError:
            size = 9
        style = parts[2] if len(parts) > 2 else "normal"
        return (family, size, style)
    return ("TkDefaultFont", 9, "normal")


def _load_theme_file(theme_name: str) -> Dict[str, Any]:
    """
    Load theme from .ini file.

    Args:
        theme_name: Name of the theme file (without .ini extension)

    Returns:
        dict: Theme definition dictionary

    Raises:
        FileNotFoundError: If theme file doesn't exist
        configparser.Error: If .ini file is malformed
    """
    # Get the directory where this module is located
    current_dir = Path(__file__).parent.parent.parent / "themes"
    theme_file = current_dir / f"{theme_name}.ini"
    if not theme_file.exists():
        raise FileNotFoundError(f"Theme file not found: {theme_file}")
    config = configparser.ConfigParser()
    config.read(theme_file)
    if theme_name not in config:
        raise configparser.Error(
            f"Theme section '{theme_name}' not found in {theme_file}"
        )
    theme_section = config[theme_name]
    theme_dict = {}
    for key, value in theme_section.items():
        # Parse font values
        if "font" in key.lower():
            theme_dict[key] = _parse_font(value)
        else:
            theme_dict[key] = value
    return theme_dict


def get_calendar_themes() -> Dict[str, Dict[str, Any]]:
    """
    Get all available calendar themes.

    Returns:
        dict: Dictionary containing all theme definitions
    """
    themes = {}
    current_dir = Path(__file__).parent.parent.parent / "themes"
    # Look for .ini files in the theme directory
    for theme_file in current_dir.glob("*.ini"):
        theme_name = theme_file.stem  # filename without extension
        try:
            themes[theme_name] = _load_theme_file(theme_name)
        except (FileNotFoundError, configparser.Error) as e:
            # Skip malformed theme files
            logger = logging.getLogger(__name__)
            logger.warning("Failed to load theme file %s: %s", theme_file, e)
            continue
    return themes


def get_calendar_theme(theme_name: str) -> Dict[str, Any]:
    """
    Get a specific calendar theme by name.

    Args:
        theme_name: Name of the theme

    Returns:
        dict: Theme definition for the specified theme name

    Raises:
        ValueError: If the theme name is not found
    """
    try:
        return _load_theme_file(theme_name)
    except FileNotFoundError as exc:
        available_themes = list(get_calendar_themes().keys())
        raise ValueError(
            f"Theme '{theme_name}' not found. Available themes: " f"{available_themes}"
        ) from exc
    except configparser.Error as e:
        raise ValueError(f"Error loading theme '{theme_name}': {e}") from e


def _determine_day_colors(context: DayColorContext) -> ColorPair:
    """
    Determine background and foreground colors for a day.

    Args:
        context: DayColorContext containing all necessary information

    Returns:
        ColorPair: Background and foreground colors
    """
    # Default colors
    bg_color = context.theme_colors["day_bg"]
    fg_color = context.theme_colors["day_fg"]

    # Check selection colors first (highest priority)
    colors = _get_selection_colors(
        context.theme_colors,
        context.selected_date,
        context.selected_range,
        context.date_obj,
        bg_color,
        fg_color,
    )
    bg_color, fg_color = colors.bg, colors.fg

    # If not selected, check other conditions
    if bg_color == context.theme_colors["day_bg"]:
        # Check today colors
        colors = _get_today_colors(
            context.theme_colors,
            context.today,
            context.today_color,
            context.today_color_set,
            context.year,
            context.month,
            context.day,
            bg_color,
            fg_color,
        )
        bg_color, fg_color = colors.bg, colors.fg

        # Check holiday colors
        if bg_color == context.theme_colors["day_bg"]:
            bg_color = _get_holiday_color(
                context.holidays, context.year, context.month, context.day, bg_color
            )

        # Check day of week colors
        if bg_color == context.theme_colors["day_bg"]:
            colors = _get_day_of_week_colors(
                context.theme_colors,
                context.day_colors,
                context.date_obj,
                bg_color,
                fg_color,
            )
            bg_color, fg_color = colors.bg, colors.fg

    return ColorPair(bg=bg_color, fg=fg_color)


def _get_selection_colors(  # pylint: disable=R0917
    theme_colors, selected_date, selected_range, date_obj, bg_color, fg_color
) -> ColorPair:
    """
    Get colors for selected dates.

    Args:
        theme_colors: Theme color dictionary
        selected_date: Currently selected date
        selected_range: Currently selected date range
        date_obj: Date object for comparison
        bg_color: Current background color
        fg_color: Current foreground color

    Returns:
        ColorPair: Background and foreground colors
    """
    if selected_date == date_obj:
        return ColorPair(bg=theme_colors["selected_bg"], fg=theme_colors["selected_fg"])
    if selected_range:
        start_date, end_date = selected_range
        if start_date <= date_obj <= end_date:
            if date_obj in (start_date, end_date):
                return ColorPair(
                    bg=theme_colors["selected_bg"], fg=theme_colors["selected_fg"]
                )
            return ColorPair(bg=theme_colors["range_bg"], fg=theme_colors["range_fg"])
    return ColorPair(bg=bg_color, fg=fg_color)


def _get_today_colors(  # pylint: disable=R0917
    theme_colors,
    today,
    today_color,
    today_color_set,
    year,
    month,
    day,
    bg_color,
    fg_color,
) -> ColorPair:
    """
    Get colors for today's date.

    Args:
        theme_colors: Theme color dictionary
        today: Today's date
        today_color: Custom today color
        today_color_set: Whether today color is set
        year: Year
        month: Month
        day: Day
        bg_color: Current background color
        fg_color: Current foreground color

    Returns:
        ColorPair: Background and foreground colors
    """
    if year == today.year and month == today.month and day == today.day:
        if today_color is not None:
            return ColorPair(
                bg=today_color, fg="black"
            )  # Default foreground for custom today color
        if today_color is None and not today_color_set:
            # Skip today color if explicitly set to "none"
            return ColorPair(bg=bg_color, fg=fg_color)
        return ColorPair(bg=theme_colors["today_bg"], fg=theme_colors["today_fg"])
    return ColorPair(bg=bg_color, fg=fg_color)


def _get_holiday_color(holidays, year, month, day, bg_color):
    """
    Get holiday color for a date.

    Args:
        holidays: Holiday colors dictionary
        year: Year
        month: Month
        day: Day
        bg_color: Current background color

    Returns:
        str: Background color for holiday
    """
    date_str = f"{year:04d}-{month:02d}-{day:02d}"
    if date_str in holidays:
        return holidays[date_str]
    return bg_color


def _get_day_of_week_colors(  # pylint: disable=R0917
    theme_colors, day_colors, date_obj, bg_color, fg_color
) -> ColorPair:
    """
    Get colors based on day of week.

    Args:
        theme_colors: Theme color dictionary
        day_colors: Day of week colors dictionary
        date_obj: Date object
        bg_color: Current background color
        fg_color: Current foreground color

    Returns:
        ColorPair: Background and foreground colors
    """
    day_name = date_obj.strftime("%A")
    if day_name in day_colors:
        return ColorPair(bg=day_colors[day_name], fg=fg_color)
    # Apply default weekend colors for Saturday and Sunday if no custom colors set
    if day_name in ["Saturday", "Sunday"]:
        return ColorPair(bg=theme_colors["weekend_bg"], fg=theme_colors["weekend_fg"])
    return ColorPair(bg=bg_color, fg=fg_color)


def get_day_names(calendar_instance, short: bool = False) -> List[str]:
    """Get localized day names."""
    # Define base day names
    full_days = [
        "Monday",
        "Tuesday",
        "Wednesday",
        "Thursday",
        "Friday",
        "Saturday",
        "Sunday",
    ]
    short_days = ["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"]
    # Choose day list based on short parameter
    days = short_days if short else full_days
    # Shift days based on week_start
    if calendar_instance.week_start == "Sunday":
        # Move Sunday to the beginning
        days = days[-1:] + days[:-1]
    elif calendar_instance.week_start == "Saturday":
        # Move Saturday to the beginning
        days = days[-2:] + days[:-2]
    # Get translations and handle short names
    day_names = []
    for day in days:
        if short:
            # For short names, get full name translation first, then truncate
            full_name = full_days[short_days.index(day)]
            full_translated = lang.get(full_name, calendar_instance.winfo_toplevel())
            translated = (
                full_translated[:3] if len(full_translated) >= 3 else full_translated
            )
        else:
            translated = lang.get(day, calendar_instance.winfo_toplevel())
        day_names.append(translated)
    return day_names


def get_month_name(calendar_instance, month: int, short: bool = False) -> str:
    """Get localized month name."""
    # Define base month names
    full_months = [
        "January",
        "February",
        "March",
        "April",
        "May",
        "June",
        "July",
        "August",
        "September",
        "October",
        "November",
        "December",
    ]
    # Get the month name based on short parameter
    if short:
        # For short names, get full name translation first, then truncate
        full_name = full_months[month - 1]
        full_translated = lang.get(full_name, calendar_instance.winfo_toplevel())
        return full_translated[:3] if len(full_translated) >= 3 else full_translated
    month_name = full_months[month - 1]
    return lang.get(month_name, calendar_instance.winfo_toplevel())


def handle_mouse_enter(calendar_instance, label):
    """Handle mouse enter event."""
    # Only highlight if not already selected
    current_bg = label.cget("bg")
    if current_bg not in [
        calendar_instance.theme_colors["selected_bg"],
        calendar_instance.theme_colors["range_bg"],
    ]:
        # Store current colors before changing to hover
        if label not in calendar_instance.original_colors:
            calendar_instance.original_colors[label] = {
                "bg": current_bg,
                "fg": label.cget("fg"),
            }
        label.config(
            bg=calendar_instance.theme_colors["hover_bg"],
            fg=calendar_instance.theme_colors["hover_fg"],
        )


def handle_mouse_leave(calendar_instance, label):
    """Handle mouse leave event."""
    # Only restore if not selected
    current_bg = label.cget("bg")
    if current_bg == calendar_instance.theme_colors["hover_bg"]:
        # Restore original colors
        if label in calendar_instance.original_colors:
            original = calendar_instance.original_colors[label]
            label.config(bg=original["bg"], fg=original["fg"])
        else:
            # Fallback to default colors
            label.config(
                bg=calendar_instance.theme_colors["day_bg"],
                fg=calendar_instance.theme_colors["day_fg"],
            )


def handle_year_view_mouse_enter(calendar_instance, label):
    """Handle mouse enter event in month selection."""
    current_bg = label.cget("bg")
    if current_bg != calendar_instance.theme_colors["selected_bg"]:
        label.config(
            bg=calendar_instance.theme_colors["hover_bg"],
            fg=calendar_instance.theme_colors["hover_fg"],
        )


def handle_year_view_mouse_leave(calendar_instance, label):
    """Handle mouse leave event in month selection."""
    current_bg = label.cget("bg")
    if current_bg == calendar_instance.theme_colors["hover_bg"]:
        # Check if this is the current month
        for month, month_label in calendar_instance.year_view_labels:
            if month_label == label:
                if month == calendar_instance.month:
                    label.config(
                        bg=calendar_instance.theme_colors["selected_bg"],
                        fg=calendar_instance.theme_colors["selected_fg"],
                    )
                else:
                    label.config(
                        bg=calendar_instance.theme_colors["day_bg"],
                        fg=calendar_instance.theme_colors["day_fg"],
                    )
                break


def handle_year_selection_mouse_enter(calendar_instance, label):
    """Handle mouse enter event in year selection."""
    current_bg = label.cget("bg")
    if current_bg != calendar_instance.theme_colors["selected_bg"]:
        label.config(
            bg=calendar_instance.theme_colors["hover_bg"],
            fg=calendar_instance.theme_colors["hover_fg"],
        )


def handle_year_selection_mouse_leave(calendar_instance, label):
    """Handle mouse leave event in year selection."""
    current_bg = label.cget("bg")
    if current_bg == calendar_instance.theme_colors["hover_bg"]:
        # Check if this is the current year
        for year, year_label in calendar_instance.year_selection_labels:
            if year_label == label:
                if year == calendar_instance.year:
                    label.config(
                        bg=calendar_instance.theme_colors["selected_bg"],
                        fg=calendar_instance.theme_colors["selected_fg"],
                    )
                else:
                    label.config(
                        bg=calendar_instance.theme_colors["day_bg"],
                        fg=calendar_instance.theme_colors["day_fg"],
                    )
                break


def create_navigation_button(calendar_instance, parent, text, command, padx=(0, 0)):
    """Create a navigation button with consistent styling and events."""
    btn = tk.Label(
        parent,
        text=text,
        font=calendar_instance._get_scaled_font(  # pylint: disable=W0212
            calendar_instance.theme_colors["navigation_font"]
        ),
        bg=calendar_instance.theme_colors["navigation_bg"],
        fg=calendar_instance.theme_colors["navigation_fg"],
        cursor="hand2",
    )
    btn.pack(side="left", padx=padx)
    btn.bind("<Button-1>", lambda e, cmd=command: cmd())
    btn.bind(
        "<Enter>",
        lambda e, button=btn: button.config(
            bg=calendar_instance.theme_colors["navigation_hover_bg"],
            fg=calendar_instance.theme_colors["navigation_hover_fg"],
        ),
    )
    btn.bind(
        "<Leave>",
        lambda e, button=btn: button.config(
            bg=calendar_instance.theme_colors["navigation_bg"],
            fg=calendar_instance.theme_colors["navigation_fg"],
        ),
    )
    return btn

# UI helper functions for calendar widgets.
# Note: create_clickable_label was removed as it is not used anywhere.


def create_grid_label(  # pylint: disable=too-many-positional-arguments
    calendar_instance,
    parent,
    text,
    command=None,
    is_selected=False,
    row=0,
    col=0,
    sticky="nsew",
    padx=1,
    pady=1,
):
    """Create a grid label with consistent styling and events."""
    label = tk.Label(
        parent,
        text=text,
        font=calendar_instance._get_scaled_font(  # pylint: disable=W0212
            ("TkDefaultFont", 10, "bold")
        ),
        relief="flat",
        bd=0,
        anchor="center",
        bg=calendar_instance.theme_colors["day_bg"],
        fg=calendar_instance.theme_colors["day_fg"],
        cursor="hand2",
    )
    label.grid(row=row, column=col, sticky=sticky, padx=padx, pady=pady)

    if is_selected:
        label.config(
            bg=calendar_instance.theme_colors["selected_bg"],
            fg=calendar_instance.theme_colors["selected_fg"],
        )

    if command:
        # Pass through Tkinter event to callback if it expects it
        label.bind("<Button-1>", lambda event, cmd=command: cmd(event))

    return label


def bind_hover_events(
    calendar_instance, label, hover_enter_func=None, hover_leave_func=None
):
    """Bind hover events to a label with optional custom handlers."""
    if hover_enter_func:
        label.bind(
            "<Enter>", lambda e, lbl=label: hover_enter_func(calendar_instance, lbl)
        )
    if hover_leave_func:
        label.bind(
            "<Leave>", lambda e, lbl=label: hover_leave_func(calendar_instance, lbl)
        )


def set_day_colors(
    calendar_instance, label, year: int, month: int, day: int
):  # pylint: disable=W0212
    """Set colors for a specific day."""
    # Create context for color determination
    context = DayColorContext(
        theme_colors=calendar_instance.theme_colors,
        selected_date=calendar_instance.selected_date,
        selected_range=calendar_instance.selected_range,
        today=datetime.date.today(),
        today_color=calendar_instance.today_color,
        today_color_set=calendar_instance.today_color_set,
        day_colors=calendar_instance.day_colors,
        holidays=calendar_instance.holidays,
        date_obj=datetime.date(year, month, day),
        year=year,
        month=month,
        day=day,
    )

    # Get colors based on various conditions
    colors = _determine_day_colors(context)

    # Apply colors
    label.config(bg=colors.bg, fg=colors.fg)
    # Update original colors for hover effect restoration
    if label in calendar_instance.original_colors:
        calendar_instance.original_colors[label] = {"bg": colors.bg, "fg": colors.fg}
