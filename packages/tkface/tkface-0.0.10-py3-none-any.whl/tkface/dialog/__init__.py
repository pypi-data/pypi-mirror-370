"""Dialog module for tkface."""

import tkinter as tk

from ..lang import lang as lang_module

__all__ = ["messagebox", "simpledialog"]


def _get_or_create_root():
    """
    Get existing root window or create a new one.
    Returns:
        tuple: (root_window, created_flag)
    """
    root = getattr(tk, "_default_root", None)
    created = False
    if root is None:
        root = tk.Tk()
        root.withdraw()
        created = True
    return root, created


def _get_button_labels(  # pylint: disable=unused-argument
    button_set="ok", root=None, language=None
):
    """
    Get button labels for the specified button set with proper translations.
    Args:
        button_set (str): The type of button set ("ok", "okcancel",
            "retrycancel", etc.)
        root: Tkinter root window
        language (str): Language code for translations
    Returns:
        list: List of tuples (translated_text, button_value,
            is_default, is_cancel)
    """
    if language and root:
        lang_module.set(language, root)  # pylint: disable=no-member

    # This is a placeholder - actual implementation would be in the specific
    # dialog classes
    return []


def _position_window(  # pylint: disable=R0917
    window, master, x=None, y=None, x_offset=0, y_offset=0
):
    """
    Position a window relative to its master window.
    Args:
        window: The window to position
        master: The master window
        x: X coordinate (None for center)
        y: Y coordinate (None for center)
        x_offset: X offset from calculated position
        y_offset: Y offset from calculated position
    """
    window.update_idletasks()
    width = window.winfo_reqwidth()
    height = window.winfo_reqheight()
    if x is None or y is None:
        parent_x = master.winfo_rootx()
        parent_y = master.winfo_rooty()
        parent_width = master.winfo_width()
        parent_height = master.winfo_height()
        x = parent_x + (parent_width - width) // 2
        y = parent_y + (parent_height - height) // 2
    x += x_offset
    y += y_offset
    window.geometry(f"{width}x{height}+{x}+{y}")


def _setup_dialog_base(master, language):
    """
    Setup common dialog base functionality.
    Args:
        master: Parent window
        language: Language code
    Returns:
        tuple: (root_window, created_flag, language)
    """
    if master is None:
        master = getattr(tk, "_default_root", None)
        if master is None:
            raise RuntimeError(
                "No Tk root window found. Please create a Tk instance "
                "or pass master explicitly."
            )
    return master, False, language
