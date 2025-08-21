import sys
import tkinter as tk


def is_windows():
    """Check if running on Windows platform."""
    return sys.platform == "win32"


def configure_button_for_windows(button):
    """
    Configure button appearance for Windows (disable shadow but keep border).
    Args:
        button: Tkinter Button widget
    """
    if is_windows() and button is not None:
        button.configure(relief="solid", bd=1)


def get_button_label_with_shortcut(button_value, translated_text):
    """
    Get button label with keyboard shortcut for Windows.
    Args:
        button_value (str): Button value (e.g., "yes", "no", "ok")
        translated_text (str): Translated button text
    Returns:
        str: Button text with shortcut (e.g., "はい(Y)" for Windows,
            original text for others
        )
    """
    # Handle None inputs
    if button_value is None or translated_text is None:
        return translated_text if translated_text is not None else ""
    if not is_windows():
        return translated_text
    # Map button values to keyboard shortcuts
    shortcuts = {
        "yes": "Y",
        "no": "N",
        "retry": "R",
        "abort": "A",
        "ignore": "I",
    }
    shortcut = shortcuts.get(button_value.lower())
    if shortcut:
        return f"{translated_text}({shortcut})"
    return translated_text


class FlatButton(tk.Button):
    """
    A Button widget with Windows-specific flat styling.
    This class automatically applies Windows-specific styling when used on
    Windows,
    while maintaining normal appearance on other platforms.
    """

    def __init__(self, master=None, **kwargs):
        super().__init__(master, **kwargs)
        configure_button_for_windows(self)


def create_flat_button(master, text, command=None, **kwargs):
    """
    Create a button with Windows-specific flat styling.
    Args:
        master: Parent widget
        text (str): Button text
        command: Command to execute when button is clicked
        **kwargs: Additional button configuration options
    Returns:
        FlatButton: Configured button widget
    """
    return FlatButton(master, text=text, command=command, **kwargs)
