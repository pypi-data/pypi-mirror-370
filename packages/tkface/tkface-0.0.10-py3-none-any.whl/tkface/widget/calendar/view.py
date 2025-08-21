"""
View and UI functionality for the Calendar widget.

This module provides UI creation, display updates, and user interaction
handling for the Calendar widget.
"""

import calendar
import tkinter as tk

from .style import (
    bind_hover_events,
    create_grid_label,
    create_navigation_button,
    get_month_name,
    handle_mouse_enter,
    handle_mouse_leave,
    handle_year_selection_mouse_enter,
    handle_year_selection_mouse_leave,
    handle_year_view_mouse_enter,
    handle_year_view_mouse_leave,
    set_day_colors,
)


def _create_header_frame(calendar_instance, parent):
    """Create a consistent header frame structure."""
    header_frame = tk.Frame(
        parent, bg=calendar_instance.theme_colors["month_header_bg"]
    )
    header_frame.pack(fill="x", pady=(5, 0))

    nav_frame = tk.Frame(
        header_frame, bg=calendar_instance.theme_colors["month_header_bg"]
    )
    nav_frame.pack(expand=True, fill="x")

    center_frame = tk.Frame(
        nav_frame, bg=calendar_instance.theme_colors["month_header_bg"]
    )
    center_frame.pack(expand=True)

    return center_frame


def _create_grid_container(calendar_instance, parent, rows, cols):
    """Create a grid container with consistent configuration."""
    grid_frame = tk.Frame(parent, bg=calendar_instance.theme_colors["background"])
    grid_frame.pack(fill="both", expand=True, padx=2, pady=2)

    for i in range(cols):
        grid_frame.columnconfigure(i, weight=1)
    for i in range(rows):
        grid_frame.rowconfigure(i, weight=1)

    return grid_frame


def _create_container(calendar_instance):
    """Create the main container (single month or scrollable)."""
    is_single_month = calendar_instance.months == 1
    if is_single_month:
        calendar_instance.months_container = tk.Frame(
            calendar_instance,
            relief="flat",
            bd=1,
            bg=calendar_instance.theme_colors["background"],
        )
        calendar_instance.months_container.pack(
            fill="both", expand=True, padx=2, pady=2
        )
    else:
        # Create scrollable container for multiple months
        calendar_instance.canvas = tk.Canvas(
            calendar_instance, bg=calendar_instance.theme_colors["background"]
        )
        calendar_instance.scrollbar = tk.Scrollbar(
            calendar_instance,
            orient="horizontal",
            command=calendar_instance.canvas.xview,
        )
        calendar_instance.scrollable_frame = tk.Frame(
            calendar_instance.canvas, bg=calendar_instance.theme_colors["background"]
        )
        calendar_instance.scrollable_frame.bind(
            "<Configure>",
            lambda e: calendar_instance.canvas.configure(
                scrollregion=calendar_instance.canvas.bbox("all")
            ),
        )
        calendar_instance.canvas.create_window(
            (0, 0), window=calendar_instance.scrollable_frame, anchor="nw"
        )
        calendar_instance.canvas.configure(
            xscrollcommand=calendar_instance.scrollbar.set
        )
        # Pack scrollbar and canvas
        calendar_instance.scrollbar.pack(side="bottom", fill="x")
        calendar_instance.canvas.pack(side="top", fill="both", expand=True)
        # Configure grid weights for the scrollable frame
        for i in range(calendar_instance.grid_cols):
            calendar_instance.scrollable_frame.columnconfigure(i, weight=1)
        for i in range(calendar_instance.grid_rows):
            calendar_instance.scrollable_frame.rowconfigure(i, weight=1)
    return is_single_month


def _hide_normal_calendar_views(calendar_instance):
    """Hide normal month views (single or scrollable) when showing overlays."""
    # Hide single-month container
    if (
        hasattr(calendar_instance, "months_container")
        and calendar_instance.months_container
    ):
        try:
            calendar_instance.months_container.pack_forget()
        except Exception:  # pylint: disable=broad-except
            pass
    # Hide scrollable views if present
    if hasattr(calendar_instance, "canvas") and calendar_instance.canvas:
        try:
            calendar_instance.canvas.pack_forget()
        except Exception:  # pylint: disable=broad-except
            pass
    if hasattr(calendar_instance, "scrollbar") and calendar_instance.scrollbar:
        try:
            calendar_instance.scrollbar.pack_forget()
        except Exception:  # pylint: disable=broad-except
            pass


def _ensure_year_container(calendar_instance):
    """Ensure overlay container exists and is packed to fill the calendar area."""
    _hide_normal_calendar_views(calendar_instance)
    if (
        not hasattr(calendar_instance, "year_container")
        or calendar_instance.year_container is None
    ):
        calendar_instance.year_container = tk.Frame(
            calendar_instance,
            relief="flat",
            bd=1,
            bg=calendar_instance.theme_colors["background"],
        )
        calendar_instance.year_container.pack(fill="both", expand=True, padx=2, pady=2)
    else:
        # If exists but not visible, ensure it's packed
        try:
            calendar_instance.year_container.pack(
                fill="both", expand=True, padx=2, pady=2
            )
        except Exception:  # pylint: disable=broad-except
            pass


def _clear_year_container_children(calendar_instance):
    """Remove all widgets inside the overlay container."""
    if (
        hasattr(calendar_instance, "year_container")
        and calendar_instance.year_container
    ):
        for child in list(calendar_instance.year_container.winfo_children()):
            try:
                child.destroy()
            except Exception:  # pylint: disable=broad-except
                pass


def _destroy_year_container(calendar_instance):  # pylint: disable=W0212
    """Destroy overlay container and restore normal month views."""
    if (
        hasattr(calendar_instance, "year_container")
        and calendar_instance.year_container
    ):
        try:
            calendar_instance.year_container.destroy()
        except Exception:  # pylint: disable=broad-except
            pass
        calendar_instance.year_container = None
    # Restore normal views
    if (
        hasattr(calendar_instance, "months_container")
        and calendar_instance.months_container
    ):
        try:
            calendar_instance.months_container.pack(
                fill="both", expand=True, padx=2, pady=2
            )
        except Exception:  # pylint: disable=broad-except
            pass
    if hasattr(calendar_instance, "canvas") and calendar_instance.canvas:
        try:
            calendar_instance.canvas.pack(side="top", fill="both", expand=True)
        except Exception:  # pylint: disable=broad-except
            pass
    if hasattr(calendar_instance, "scrollbar") and calendar_instance.scrollbar:
        try:
            calendar_instance.scrollbar.pack(side="bottom", fill="x")
        except Exception:  # pylint: disable=broad-except
            pass


def _create_navigation_buttons(calendar_instance, center_frame, month_index):
    """Create navigation buttons for a month."""
    year_first = calendar_instance._is_year_first_in_format()  # pylint: disable=W0212
    # Define navigation items in order based on date format
    nav_items = (
        [
            (
                "year",
                "<<",
                ">>",
                calendar_instance._on_prev_year,  # pylint: disable=W0212
                calendar_instance._on_next_year,  # pylint: disable=W0212
            ),
            (
                "month",
                "<",
                ">",
                calendar_instance._on_prev_month,  # pylint: disable=W0212
                calendar_instance._on_next_month,  # pylint: disable=W0212
            ),
        ]
        if year_first
        else [
            (
                "month",
                "<",
                ">",
                calendar_instance._on_prev_month,  # pylint: disable=W0212
                calendar_instance._on_next_month,  # pylint: disable=W0212
            ),
            (
                "year",
                "<<",
                ">>",
                calendar_instance._on_prev_year,  # pylint: disable=W0212
                calendar_instance._on_next_year,  # pylint: disable=W0212
            ),
        ]
    )

    for (
        item_type,
        prev_text,
        next_text,
        prev_cmd,
        next_cmd,
    ) in nav_items:
        _create_navigation_item(
            calendar_instance,
            center_frame,
            month_index,
            item_type,
            prev_text,
            next_text,
            prev_cmd,
            next_cmd,
            year_first,
        )


def _create_navigation_item(  # pylint: disable=R0917,W0212
    calendar_instance,
    center_frame,
    month_index,
    item_type,
    prev_text,
    next_text,
    prev_cmd,
    next_cmd,
    year_first,
):
    """Create a single navigation item (prev button, label, next button)."""
    # Previous button
    create_navigation_button(
        calendar_instance,
        center_frame,
        prev_text,
        lambda m=month_index, cmd=prev_cmd: cmd(m),
        padx=(5, 0),
    )

    # Label
    is_year = item_type == "year"
    label = tk.Label(
        center_frame,
        font=calendar_instance._get_scaled_font(  # pylint: disable=W0212
            ("TkDefaultFont", 9, "bold")
        ),
        relief="flat",
        bd=0,
        bg=calendar_instance.theme_colors["month_header_bg"],
        fg=calendar_instance.theme_colors["month_header_fg"],
        cursor="hand2" if not is_year else "",
    )

    if not is_year:
        # Ensure month header is clickable
        label.bind(
            "<Button-1>",
            lambda e, m=month_index: (
                calendar_instance._on_month_header_click(m)  # pylint: disable=W0212
            ),
        )
        label.bind(
            "<Enter>",
            lambda e, lbl=label: lbl.config(
                bg=calendar_instance.theme_colors["navigation_hover_bg"],
                fg=calendar_instance.theme_colors["navigation_hover_fg"],
            ),
        )
        label.bind(
            "<Leave>",
            lambda e, lbl=label: lbl.config(
                bg=calendar_instance.theme_colors["month_header_bg"],
                fg=calendar_instance.theme_colors["month_header_fg"],
            ),
        )
        calendar_instance.month_headers.append(label)
    else:
        # Bind click event for year selection
        label.bind(
            "<Button-1>",
            lambda e: calendar_instance._on_year_header_click(),  # noqa: E501
        )
        label.config(cursor="hand2")
        calendar_instance.year_labels.append(label)
    label.pack(side="left", padx=2)

    # Next button
    if item_type == ("year" if year_first else "month"):
        next_padx = (0, 10)
    else:
        next_padx = (0, 5)
    create_navigation_button(
        calendar_instance,
        center_frame,
        next_text,
        lambda m=month_index, cmd=next_cmd: cmd(m),
        padx=next_padx,
    )


def _create_month_header(calendar_instance, month_frame, month_index):
    """Create month header with navigation."""
    if not calendar_instance.show_month_headers:
        return

    center_frame = _create_header_frame(calendar_instance, month_frame)
    _create_navigation_buttons(calendar_instance, center_frame, month_index)


def _create_widgets(calendar_instance):  # pylint: disable=W0212
    """Create the calendar widget structure."""
    # Set main frame background color
    calendar_instance.configure(bg=calendar_instance.theme_colors["background"])

    # Create container
    is_single_month = _create_container(calendar_instance)

    # Initialize label lists
    calendar_instance.year_labels = []
    calendar_instance.month_headers = []

    # Create month frames in grid layout
    for i in range(calendar_instance.months):
        row = i // calendar_instance.grid_cols
        col = i % calendar_instance.grid_cols

        if is_single_month:
            month_frame = tk.Frame(
                calendar_instance.months_container,
                relief="flat",
                bd=1,
                bg=calendar_instance.theme_colors["background"],
            )
            month_frame.pack(fill="both", expand=True, padx=2, pady=2)
        else:
            month_frame = tk.Frame(
                calendar_instance.scrollable_frame,
                relief="flat",
                bd=1,
                bg=calendar_instance.theme_colors["background"],
            )
            month_frame.grid(row=row, column=col, padx=2, pady=2, sticky="nsew")

        calendar_instance.month_frames.append(month_frame)

        # Create month header
        _create_month_header(calendar_instance, month_frame, i)

        # Calendar grid (including header)
        _create_calendar_grid(calendar_instance, month_frame, i)


def _create_calendar_grid(calendar_instance, month_frame, month_index):
    """Create the calendar grid for a specific month."""
    grid_frame = tk.Frame(month_frame, bg=calendar_instance.theme_colors["background"])
    grid_frame.pack(fill="both", expand=True, padx=2, pady=2)
    # Configure grid weights
    if calendar_instance.show_week_numbers:
        grid_frame.columnconfigure(0, weight=1)
        for i in range(7):
            grid_frame.columnconfigure(i + 1, weight=1)
    else:
        for i in range(7):
            grid_frame.columnconfigure(i, weight=1)
    # Configure row weights (header row + 6 week rows)
    grid_frame.rowconfigure(0, weight=0)  # Header row (no expansion)
    for week in range(6):  # Maximum 6 weeks
        grid_frame.rowconfigure(week + 1, weight=1)
    # Create day name headers (row 0)
    day_names = calendar_instance._get_day_names_for_headers()  # pylint: disable=W0212
    if calendar_instance.show_week_numbers:
        # Empty header for week number column
        empty_header = tk.Label(
            grid_frame,
            text="",
            font=calendar_instance._get_scaled_font(  # pylint: disable=W0212
                ("TkDefaultFont", 8)
            ),
            relief="flat",
            bd=0,
            bg=calendar_instance.theme_colors["day_header_bg"],
            fg=calendar_instance.theme_colors["day_header_fg"],
        )
        empty_header.grid(row=0, column=0, sticky="nsew", padx=1, pady=1)
    for day, day_name in enumerate(day_names):
        day_header = tk.Label(
            grid_frame,
            text=day_name,
            font=calendar_instance._get_scaled_font(  # pylint: disable=W0212
                calendar_instance.theme_colors["day_header_font"]
            ),
            relief="flat",
            bd=0,
            bg=calendar_instance.theme_colors["day_header_bg"],
            fg=calendar_instance.theme_colors["day_header_fg"],
        )
        col = day + 1 if calendar_instance.show_week_numbers else day
        day_header.grid(row=0, column=col, sticky="nsew", padx=1, pady=1)
    # Create labels for each week and day
    for week in range(6):  # Maximum 6 weeks
        # Week number label
        if calendar_instance.show_week_numbers:
            week_label = tk.Label(
                grid_frame,
                font=calendar_instance._get_scaled_font(  # pylint: disable=W0212
                    calendar_instance.theme_colors["week_number_font"]
                ),
                relief="flat",
                bd=0,
                bg=calendar_instance.theme_colors["week_number_bg"],
                fg=calendar_instance.theme_colors["week_number_fg"],
            )
            week_label.grid(row=week + 1, column=0, sticky="nsew", padx=1, pady=1)
            calendar_instance.week_labels.append(week_label)
        # Day labels (clickable)
        for day in range(7):
            day_label = tk.Label(
                grid_frame,
                font=calendar_instance._get_scaled_font(  # pylint: disable=W0212
                    calendar_instance.theme_colors["day_font"]
                ),
                relief="flat",
                bd=0,
                anchor="center",
                bg=calendar_instance.theme_colors["day_bg"],
                fg=calendar_instance.theme_colors["day_fg"],
                cursor="hand2",
            )
            col = day + 1 if calendar_instance.show_week_numbers else day
            day_label.grid(row=week + 1, column=col, sticky="nsew", padx=1, pady=1)
            # Store original colors for this label
            calendar_instance.original_colors[day_label] = {
                "bg": calendar_instance.theme_colors["day_bg"],
                "fg": calendar_instance.theme_colors["day_fg"],
            }
            # Bind click events
            day_label.bind(
                "<Button-1>",
                lambda e, m=month_index, w=week, d=day: (
                    calendar_instance._on_date_click(m, w, d)  # pylint: disable=W0212
                ),
            )
            day_label.bind(
                "<Enter>",
                lambda e, label=day_label: handle_mouse_enter(calendar_instance, label),
            )
            day_label.bind(
                "<Leave>",
                lambda e, label=day_label: handle_mouse_leave(calendar_instance, label),
            )
            calendar_instance.day_labels.append((month_index, week, day, day_label))


def _update_display(calendar_instance):  # pylint: disable=W0212
    """Update the calendar display."""
    if not calendar_instance.winfo_exists():
        return
    # Check if in month selection mode
    if calendar_instance.month_selection_mode:
        _update_year_view(calendar_instance)
        return
    # Check if in year selection mode
    if calendar_instance.year_selection_mode:
        return
    week_label_index = 0
    for month_offset in range(calendar_instance.months):
        # Get display date using existing helper
        display_date = calendar_instance._get_display_date(  # pylint: disable=W0212
            month_offset
        )
        display_year = display_date.year
        display_month = display_date.month
        # Update year and month headers
        if calendar_instance.show_month_headers:
            _update_month_headers(
                calendar_instance, month_offset, display_year, display_month
            )
        # Update day name headers
        children = calendar_instance.month_frames[month_offset].winfo_children()
        if calendar_instance.show_month_headers and len(children) > 1:
            days_frame = children[1]
        else:
            days_frame = children[0]
        _update_day_name_headers(calendar_instance, days_frame)
        # Get calendar data from core helper
        _, _last_day = calendar.monthrange(display_year, display_month)
        month_days = calendar_instance._get_month_days_list(  # pylint: disable=W0212
            display_year, display_month
        )
        # Update week numbers
        if calendar_instance.show_week_numbers:
            week_label_index = _update_week_numbers(
                calendar_instance, display_year, display_month, week_label_index
            )
        # Update day labels
        _update_day_labels(
            calendar_instance, month_offset, display_year, display_month, month_days
        )
        # Update week label index for next month
        if calendar_instance.show_week_numbers:
            week_label_index += 6


def _update_month_headers(
    calendar_instance, month_offset: int, display_year: int, display_month: int
):
    """Update year and month headers."""
    year_text, month_text = (
        calendar_instance._get_month_header_texts(  # pylint: disable=W0212
            display_year, display_month
        )
    )
    if hasattr(calendar_instance, "year_labels") and month_offset < len(
        calendar_instance.year_labels
    ):
        year_label = calendar_instance.year_labels[month_offset]
        year_label.config(text=year_text)
    if hasattr(calendar_instance, "month_headers") and month_offset < len(
        calendar_instance.month_headers
    ):
        month_label = calendar_instance.month_headers[month_offset]
        month_label.config(text=month_text)


def _update_day_name_headers(calendar_instance, days_frame):
    """Update day name headers."""
    day_names = calendar_instance._get_day_names_for_headers()  # pylint: disable=W0212
    # Find day header labels and update them
    day_header_index = 0
    for child in days_frame.winfo_children():
        if isinstance(child, tk.Label) and child.cget("text") == "":
            # Skip empty header (week number column)
            continue
        if isinstance(child, tk.Label):
            # This is a day header
            if day_header_index < len(day_names):
                child.config(text=day_names[day_header_index])
                day_header_index += 1


def _update_day_labels(
    calendar_instance,
    month_offset: int,
    display_year: int,
    display_month: int,
    month_days,
):
    """Update day labels for a specific month."""
    for week in range(6):
        for day in range(7):
            day_index = week * 7 + day
            # Find the corresponding label
            for m, w, d, label in calendar_instance.day_labels:
                if m == month_offset and w == week and d == day:
                    _update_single_day_label(
                        calendar_instance,
                        label,
                        display_year,
                        display_month,
                        week,
                        day,
                        day_index,
                        month_days,
                    )
                    break


def _update_single_day_label(  # pylint: disable=R0917,W0212
    calendar_instance,
    label,
    display_year: int,
    display_month: int,
    week: int,
    day: int,
    day_index: int,
    month_days,
):
    """Update a single day label."""
    use_adjacent, day_num = calendar_instance._get_day_cell_value(
        display_year,
        display_month,
        day_index,
        month_days,
    )
    if use_adjacent:
        calendar_instance._set_adjacent_month_day(
            label, display_year, display_month, week, day
        )
    else:
        label.config(text=str(day_num))
        set_day_colors(
            calendar_instance, label, display_year, display_month, int(day_num)
        )


def _update_week_numbers(
    calendar_instance, display_year: int, display_month: int, week_label_index: int
) -> int:
    """Update week numbers for a specific month."""
    week_numbers = calendar_instance._compute_week_numbers(  # pylint: disable=W0212
        display_year, display_month
    )
    for week in range(6):
        if week_label_index + week < len(calendar_instance.week_labels):
            week_label = calendar_instance.week_labels[week_label_index + week]
            week_label.config(text=week_numbers[week])
    return week_label_index


def _create_year_view_content(calendar_instance):  # pylint: disable=W0212
    """Create month selection content with 3x4 month grid as overlay."""
    # Ensure overlay container
    _ensure_year_container(calendar_instance)
    _clear_year_container_children(calendar_instance)

    # Header
    if calendar_instance.show_navigation:
        center_frame = _create_header_frame(
            calendar_instance, calendar_instance.year_container
        )
        _create_year_view_navigation(calendar_instance, center_frame)

    # Grid frame
    month_grid_frame = _create_grid_container(
        calendar_instance, calendar_instance.year_container, 3, 4
    )

    # Month labels
    calendar_instance.year_view_labels = []
    for month in range(1, 13):
        row = (month - 1) // 4
        col = (month - 1) % 4
        month_name = get_month_name(calendar_instance, month, short=True)

        def _on_month_label_click(_event, m=month):  # noqa: ANN001
            calendar_instance._on_year_view_month_click(m)  # pylint: disable=W0212
            return "break"

        month_label = create_grid_label(
            calendar_instance,
            month_grid_frame,
            month_name,
            command=_on_month_label_click,
            is_selected=(month == calendar_instance.month),
            row=row,
            col=col,
        )

        bind_hover_events(
            calendar_instance,
            month_label,
            handle_year_view_mouse_enter,
            handle_year_view_mouse_leave,
        )

        calendar_instance.year_view_labels.append((month, month_label))

    # Bring overlay to front and force redraw
    try:
        if (
            hasattr(calendar_instance, "year_container")
            and calendar_instance.year_container
        ):
            calendar_instance.year_container.lift()
        calendar_instance.update_idletasks()
    except Exception:  # pylint: disable=broad-except
        pass


def _create_year_selection_content(calendar_instance):  # pylint: disable=W0212
    """Create year selection content with 3x4 year grid as overlay."""
    _ensure_year_container(calendar_instance)
    _clear_year_container_children(calendar_instance)

    center_frame = _create_header_frame(
        calendar_instance, calendar_instance.year_container
    )
    _create_year_selection_navigation(calendar_instance, center_frame)

    year_grid_frame = _create_grid_container(
        calendar_instance, calendar_instance.year_container, 3, 4
    )

    calendar_instance.year_selection_labels = []
    for year in range(
        calendar_instance.year_range_start, calendar_instance.year_range_end + 1
    ):
        row = (year - calendar_instance.year_range_start) // 4
        col = (year - calendar_instance.year_range_start) % 4

        def _on_year_label_click(_event, y=year):  # noqa: ANN001
            calendar_instance._on_year_selection_year_click(y)  # pylint: disable=W0212
            return "break"

        year_label = create_grid_label(
            calendar_instance,
            year_grid_frame,
            str(year),
            command=_on_year_label_click,
            is_selected=(year == calendar_instance.year),
            row=row,
            col=col,
        )

        bind_hover_events(
            calendar_instance,
            year_label,
            handle_year_selection_mouse_enter,
            handle_year_selection_mouse_leave,
        )

        calendar_instance.year_selection_labels.append((year, year_label))

    # Bring overlay to front and force redraw
    try:
        if (
            hasattr(calendar_instance, "year_container")
            and calendar_instance.year_container
        ):
            calendar_instance.year_container.lift()
        calendar_instance.update_idletasks()
    except Exception:  # pylint: disable=broad-except
        pass


# pylint: disable=W0212
def _update_year_selection_display(calendar_instance):
    """Update year selection display."""
    # Update year range label
    if hasattr(calendar_instance, "year_selection_header_label"):
        calendar_instance.year_selection_header_label.config(
            text=calendar_instance._get_year_range_text()
        )

    # Update year labels (texts, bindings, and highlight) to reflect new range
    if (
        hasattr(calendar_instance, "year_selection_labels")
        and calendar_instance.year_selection_labels
    ):
        updated_labels = []
        for idx, (_old_year, label) in enumerate(
            calendar_instance.year_selection_labels
        ):
            new_year = calendar_instance.year_range_start + idx
            # Update text
            label.config(
                text=str(new_year),
                bg=calendar_instance.theme_colors["day_bg"],
                fg=calendar_instance.theme_colors["day_fg"],
            )
            # Rebind click with the new year value
            label.bind(
                "<Button-1>",
                lambda e, y=new_year: (
                    calendar_instance._on_year_selection_year_click(y)
                ),
            )
            # Apply highlight for the currently selected year
            if new_year == calendar_instance.year:
                label.config(
                    bg=calendar_instance.theme_colors["selected_bg"],
                    fg=calendar_instance.theme_colors["selected_fg"],
                )
            updated_labels.append((new_year, label))
        # Replace with updated (year, label) pairs
        calendar_instance.year_selection_labels = updated_labels


def _update_year_view(calendar_instance):  # pylint: disable=W0212
    """Update month selection display."""
    # Update year label
    if hasattr(calendar_instance, "year_view_year_label"):
        calendar_instance.year_view_year_label.config(text=str(calendar_instance.year))

    # Update month labels
    if hasattr(calendar_instance, "year_view_labels"):
        for month, label in calendar_instance.year_view_labels:
            # Reset to default colors
            label.config(
                bg=calendar_instance.theme_colors["day_bg"],
                fg=calendar_instance.theme_colors["day_fg"],
            )
            # Highlight current month
            if month == calendar_instance.month:
                label.config(
                    bg=calendar_instance.theme_colors["selected_bg"],
                    fg=calendar_instance.theme_colors["selected_fg"],
                )


def _recreate_widgets(calendar_instance):  # pylint: disable=W0212
    """Recreate all widgets while preserving current settings."""
    # Store current settings
    current_day_colors = calendar_instance.day_colors.copy()
    current_holidays = calendar_instance.holidays.copy()
    current_show_week_numbers = calendar_instance.show_week_numbers
    current_month_selection_mode = calendar_instance.month_selection_mode
    current_year_selection_mode = calendar_instance.year_selection_mode
    # Destroy all existing widgets completely
    if hasattr(calendar_instance, "canvas"):
        calendar_instance.canvas.destroy()
    if hasattr(calendar_instance, "scrollbar"):
        calendar_instance.scrollbar.destroy()
    if hasattr(calendar_instance, "year_container"):
        calendar_instance.year_container.destroy()
    # Clear all lists
    calendar_instance.month_frames.clear()
    calendar_instance.day_labels.clear()
    calendar_instance.week_labels.clear()
    calendar_instance.original_colors.clear()
    calendar_instance.year_view_labels.clear()
    calendar_instance.year_selection_labels.clear()
    # Restore settings
    calendar_instance.day_colors = current_day_colors
    calendar_instance.holidays = current_holidays
    calendar_instance.show_week_numbers = current_show_week_numbers
    calendar_instance.month_selection_mode = current_month_selection_mode
    calendar_instance.year_selection_mode = current_year_selection_mode
    # Recreate everything
    if calendar_instance.year_selection_mode:
        _create_year_selection_content(calendar_instance)
    elif calendar_instance.month_selection_mode:
        _create_year_view_content(calendar_instance)
    else:
        _create_widgets(calendar_instance)
        _update_display(calendar_instance)
    # Update DPI scaling after recreation
    try:
        calendar_instance.update_dpi_scaling()
    except (OSError, ValueError, AttributeError) as e:
        calendar_instance.logger.debug(
            "Failed to update DPI scaling during recreation: %s", e
        )


# pylint: disable=W0108
def _create_year_view_navigation(calendar_instance, center_frame):
    """Create navigation buttons for year view."""
    # Previous year button
    create_navigation_button(
        calendar_instance,
        center_frame,
        "<<",
        lambda: calendar_instance._on_prev_year_view(),  # pylint: disable=W0212
        padx=(5, 0),
    )

    # Year label
    calendar_instance.year_view_year_label = tk.Label(
        center_frame,
        text=str(calendar_instance.year),
        font=calendar_instance._get_scaled_font(  # pylint: disable=W0212
            ("TkDefaultFont", 12, "bold")
        ),
        relief="flat",
        bd=0,
        bg=calendar_instance.theme_colors["month_header_bg"],
        fg=calendar_instance.theme_colors["month_header_fg"],
    )
    calendar_instance.year_view_year_label.pack(side="left", padx=10)
    calendar_instance.year_view_year_label.config(cursor="hand2")
    # Bind click event for year selection
    calendar_instance.year_view_year_label.bind(
        "<Button-1>",
        lambda _e: calendar_instance._on_year_header_click(),  # pylint: disable=W0212
    )
    # Add hover effects for year label
    calendar_instance.year_view_year_label.bind(
        "<Enter>",
        lambda e, lbl=calendar_instance.year_view_year_label: lbl.config(
            bg=calendar_instance.theme_colors["navigation_hover_bg"],
            fg=calendar_instance.theme_colors["navigation_hover_fg"],
        ),
    )
    calendar_instance.year_view_year_label.bind(
        "<Leave>",
        lambda e, lbl=calendar_instance.year_view_year_label: lbl.config(
            bg=calendar_instance.theme_colors["month_header_bg"],
            fg=calendar_instance.theme_colors["month_header_fg"],
        ),
    )

    # Next year button
    create_navigation_button(
        calendar_instance,
        center_frame,
        ">>",
        lambda: calendar_instance._on_next_year_view(),  # pylint: disable=W0212
        padx=(0, 10),
    )


# pylint: disable=W0108
def _create_year_selection_navigation(calendar_instance, center_frame):
    """Create navigation buttons for year selection."""
    # Previous year range button
    create_navigation_button(
        calendar_instance,
        center_frame,
        "<<",
        lambda: calendar_instance._on_prev_year_range(),  # pylint: disable=W0212
        padx=(5, 0),
    )

    # Year range label
    calendar_instance.year_selection_header_label = tk.Label(
        center_frame,
        text=(
            f"{calendar_instance.year_range_start} - "
            f"{calendar_instance.year_range_end}"
        ),
        font=calendar_instance._get_scaled_font(  # pylint: disable=W0212
            ("TkDefaultFont", 12, "bold")
        ),
        relief="flat",
        bd=0,
        bg=calendar_instance.theme_colors["month_header_bg"],
        fg=calendar_instance.theme_colors["month_header_fg"],
    )
    calendar_instance.year_selection_header_label.pack(side="left", padx=10)

    # Next year range button
    create_navigation_button(
        calendar_instance,
        center_frame,
        ">>",
        lambda: calendar_instance._on_next_year_range(),  # pylint: disable=W0212
        padx=(0, 10),
    )
