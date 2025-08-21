import logging
import tkinter as tk
from dataclasses import dataclass
from typing import Any, Dict, List, Optional, Tuple

from tkface import lang, win
from tkface.dialog import _get_or_create_root, _position_window, _setup_dialog_base


@dataclass
class MessageBoxConfig:
    """Configuration for message box dialogs."""

    title: Optional[str] = "Message"
    message: str = ""
    icon: Optional[str] = None
    button_set: Optional[str] = "ok"
    buttons: Optional[List[Tuple[str, Any]]] = None
    default: Optional[Any] = None
    cancel: Optional[Any] = None
    language: Optional[str] = None
    custom_translations: Optional[Dict[str, Dict[str, str]]] = None
    bell: bool = False


@dataclass
class WindowPosition:
    """Window positioning configuration."""

    x: Optional[int] = None
    y: Optional[int] = None
    x_offset: int = 0
    y_offset: int = 0


# Icon configuration - unified structure for all icon-related data
ICON_CONFIG = {
    "info": {"title": "Info", "tk_icon": "::tk::icons::information"},
    "warning": {"title": "Warning", "tk_icon": "::tk::icons::warning"},
    "error": {"title": "Error", "tk_icon": "::tk::icons::error"},
    "question": {"title": "Question", "tk_icon": "::tk::icons::question"},
}
# Icon type constants (for backward compatibility and convenience)
INFO = "info"
WARNING = "warning"
ERROR = "error"
QUESTION = "question"
# Convenience functions for accessing icon configuration


def get_icon_title(icon_type: str) -> str:
    """Get the default title for an icon type."""
    return ICON_CONFIG.get(icon_type, {}).get("title", "Message")


def get_tk_icon(icon_type: str) -> str:
    """Get the Tkinter icon name for an icon type."""
    return ICON_CONFIG.get(icon_type, {}).get("tk_icon", f"::tk::icons::{icon_type}")


def _get_button_labels(button_set="ok", root=None, language=None):
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
    button_sets = {
        "ok": ["ok"],
        "okcancel": ["ok", "cancel"],
        "retrycancel": ["retry", "cancel"],
        "yesno": ["yes", "no"],
        "yesnocancel": ["yes", "no", "cancel"],
        "abortretryignore": ["abort", "retry", "ignore"],
    }
    keys = button_sets.get(button_set, ["ok"])
    # Return which is default/cancel button
    default_map = {
        "ok": "ok",
        "okcancel": "ok",
        "retrycancel": "retry",
        "yesno": "yes",
        "yesnocancel": "yes",
        "abortretryignore": "abort",
    }
    cancel_map = {
        "okcancel": "cancel",
        "retrycancel": "cancel",
        "yesnocancel": "cancel",
        "abortretryignore": "cancel",
    }
    default_key = default_map.get(button_set, keys[0])
    cancel_key = cancel_map.get(button_set)
    return [
        (
            lang.get(key.lower(), root, language=language),
            key,
            key == default_key,
            key == cancel_key,
        )
        for key in keys
    ]


class CustomMessageBox:
    """
    A custom message box dialog with multilingual support and enhanced
    features.
    This class provides a fully customizable message box that supports multiple
    languages, custom positioning, and various button configurations.
    Attributes:
        window: The Toplevel window instance
        result: The result value returned when the dialog is closed
        language: The language code used for translations
    """

    def __init__(
        self,
        master=None,
        config: Optional[MessageBoxConfig] = None,
        position: Optional[WindowPosition] = None,
    ):
        """
        Initialize a custom message box.
        Args:
            master: Parent window (defaults to tk._default_root)
            config: MessageBoxConfig object containing dialog configuration
            position: WindowPosition object containing window positioning
        """
        # Set default values
        if config is None:
            config = MessageBoxConfig()
        if position is None:
            position = WindowPosition()

        master, _, self.language = _setup_dialog_base(master, config.language)
        self.logger = logging.getLogger(__name__)
        self.window = tk.Toplevel(master)
        self.window.title(lang.get(config.title, self.window, language=config.language))
        self.window.transient(master)
        self.window.grab_set()
        # Hide window initially to prevent flickering
        self.window.withdraw()
        # Cache DPI scaling calculations for performance
        # Use different padding based on DPI scaling: 10 when DPI is effective,
        # 20 otherwise
        base_padding = 10 if win.get_scaling_factor(self.window) > 1.0 else 20
        self._scaled_sizes = win.calculate_dpi_sizes(
            {
                "padding": base_padding,
                "wraplength": 300,
                "button_width": 10,
                "button_padding": 5,
                "button_area_padding": 10,
            },
            self.window,
            max_scale=1.5,
        )
        if config.custom_translations:
            for lang_code, dictionary in config.custom_translations.items():
                lang.register(lang_code, dictionary, self.window)
        self._create_content(config.message, config.icon)
        self.result = None
        self._create_buttons(
            config.button_set, config.buttons, config.default, config.cancel
        )
        self._set_window_position(
            master, position.x, position.y, position.x_offset, position.y_offset
        )
        # Show window after position is set to prevent flickering
        self.window.deiconify()
        self.window.lift()
        self.window.focus_set()
        if config.bell:
            self._ring_bell(config.icon)
        self.window.wait_window()

    def _create_content(self, message, icon):
        """
        Create the main content area with message and icon.
        Args:
            message (str): Message text to display
            icon (str): Icon identifier or file path
        """
        # Use cached DPI scaling calculations
        base_padding = self._scaled_sizes["padding"]
        base_wraplength = self._scaled_sizes["wraplength"]
        frame = tk.Frame(self.window, padx=base_padding, pady=base_padding)
        frame.pack(fill="both", expand=True)
        # Create a horizontal container for icon and content with proper
        # alignment
        content_container = tk.Frame(frame)
        content_container.pack(fill="both", expand=True)
        # Icon frame with vertical centering
        if icon:
            icon_frame = tk.Frame(content_container)
            icon_frame.pack(side="left", padx=(0, 5), fill="y")
            icon_label = self._get_icon_label(icon, icon_frame)
            if icon_label:
                icon_label.pack(expand=True, anchor="center")
        # Main content area
        content_frame = tk.Frame(content_container)
        content_frame.pack(side="left", fill="both", expand=True)
        if message:
            # Translate the message
            translated_message = lang.get(message, self.window, language=self.language)
            message_label = tk.Label(
                content_frame,
                text=translated_message,
                wraplength=base_wraplength,
                justify="left",
            )
            message_label.pack(fill="both", expand=True, anchor="center")

    def _get_icon_label(self, icon, parent):
        """
        Create an icon label widget.
        Args:
            icon (str): Icon identifier or file path
            parent: Parent widget
        Returns:
            tk.Label: Icon label widget or None if icon cannot be loaded
        """
        if icon in ICON_CONFIG:
            # Use Windows-specific icon scaling
            scaled_icon_name = win.scale_icon(icon, parent, max_scale=3.0)
            # Use the scaled icon name if it's different from original,
            # otherwise use original
            icon_to_use = (
                scaled_icon_name
                if scaled_icon_name != icon
                else ICON_CONFIG[icon]["tk_icon"]
            )
            icon_label = tk.Label(parent, image=icon_to_use)
            return icon_label
        try:
            icon_image = tk.PhotoImage(file=icon)
            return tk.Label(parent, image=icon_image)
        except (OSError, tk.TclError) as e:
            self.logger.debug("Failed to load icon from file %s: %s", icon, e)
            return None

    def _create_buttons(self, button_set, buttons, default, cancel):
        """
        Create and configure button widgets.
        Args:
            button_set (str): Predefined button set
            buttons (list): Custom button list
            default: Default button value
            cancel: Cancel button value
        """
        # Use cached DPI scaling calculations
        base_button_width = self._scaled_sizes["button_width"]
        base_button_padding = self._scaled_sizes["button_padding"]
        base_button_area_padding = self._scaled_sizes["button_area_padding"]
        button_frame = tk.Frame(self.window)
        button_frame.pack(
            pady=(base_button_area_padding // 3, base_button_area_padding)
        )
        self.button_widgets = []
        default_btn = None
        cancel_btn = None
        if buttons:
            for label, value in buttons:
                btn = tk.Button(
                    button_frame,
                    text=label,
                    width=base_button_width,
                    command=lambda v=value: self.set_result(v),
                )
                # Configure button appearance for Windows
                win.configure_button_for_windows(btn)
                btn.pack(side="left", padx=base_button_padding)
                self.button_widgets.append((btn, value))
                if value == default:
                    default_btn = btn
                if value == cancel:
                    cancel_btn = btn
            # If default/cancel not specified, use first/last
            if not default_btn and self.button_widgets:
                default_btn = self.button_widgets[0][0]
            if not cancel_btn and self.button_widgets:
                cancel_btn = self.button_widgets[-1][0]
        else:
            for text, value, is_default, is_cancel in _get_button_labels(
                button_set, self.window, language=self.language
            ):
                # Add keyboard shortcut to button text for Windows
                button_text = win.get_button_label_with_shortcut(value, text)
                btn = tk.Button(
                    button_frame,
                    text=button_text,
                    width=base_button_width,
                    command=lambda v=value: self.set_result(v),
                )
                # Configure button appearance for Windows
                win.configure_button_for_windows(btn)
                btn.pack(side="left", padx=base_button_padding)
                self.button_widgets.append((btn, value))
                if is_default:
                    default_btn = btn
                    # Set as default button (this gives the blue appearance on
                    # most systems)
                    btn.configure(default=tk.ACTIVE)
                if is_cancel:
                    cancel_btn = btn
        # Add left/right padding to button frame for window edge spacing
        button_frame.configure(padx=base_button_area_padding)
        # Set consistent button spacing
        for btn, _ in self.button_widgets:
            btn.pack_configure(padx=base_button_padding)
        # Focus only on default button
        if default_btn:
            default_btn.focus_set()
        # Enter triggers default button
        if default_btn:
            self.window.bind("<Return>", lambda e: default_btn.invoke())
        # Esc triggers cancel button
        if cancel_btn:
            self.window.bind("<Escape>", lambda e: cancel_btn.invoke())
        # Add keyboard shortcuts for common buttons
        self._add_keyboard_shortcuts()
        # Tab navigation
        for i, (btn, _) in enumerate(self.button_widgets):
            btn.bind("<Tab>", lambda e, idx=i: self._focus_next(idx))

    def _focus_next(self, idx):
        """
        Move focus to the next button in the tab order.
        Args:
            idx (int): Current button index
        """
        next_idx = (idx + 1) % len(self.button_widgets)
        self.button_widgets[next_idx][0].focus_set()

    def _add_keyboard_shortcuts(self):
        """
        Add keyboard shortcuts for common button actions.
        """
        # Map button values to keyboard shortcuts
        shortcuts = {
            "yes": ["y", "Y"],
            "no": ["n", "N"],
            "retry": ["r", "R"],
            "abort": ["a", "A"],
            "ignore": ["i", "I"],
        }
        # Add shortcuts for each button
        for btn, value in self.button_widgets:
            if value.lower() in shortcuts:
                for key in shortcuts[value.lower()]:
                    self.window.bind(
                        f"<Key-{key}>",
                        lambda e, button=btn: button.invoke(),
                    )
                    self.window.bind(
                        f"<Key-{key}>",
                        lambda e, button=btn: button.invoke(),
                        add="+",
                    )

    def _set_window_position(  # pylint: disable=R0917
        self, master, x=None, y=None, x_offset=0, y_offset=0
    ):
        """
        Set the window position relative to the master window.
        Args:
            master: Parent window
            x (int): X coordinate (None for center)
            y (int): Y coordinate (None for center)
            x_offset (int): X offset from calculated position
            y_offset (int): Y offset from calculated position
        """
        _position_window(self.window, master, x, y, x_offset, y_offset)

    def set_result(self, value):
        """
        Set the dialog result and close the window.
        Args:
            value: The result value to return
        """
        self.result = value
        self.close()

    def _ring_bell(self, icon):
        """
        Ring the bell based on the icon type.
        Args:
            icon: Icon identifier ("error", "warning", "info", "question")
        """
        # Use Windows-specific bell sounds or fallback to standard bell
        try:
            win.bell(icon)
        except (OSError, AttributeError) as e:
            self.logger.debug("Failed to use Windows bell sound: %s", e)
            # Fallback to standard bell with some variation
            if icon == ERROR:
                # Error: Multiple bells for urgent attention
                self.window.bell()
                self.window.after(100, self.window.bell)
            else:
                # Warning/Info/Question: Standard bell
                self.window.bell()

    def close(self):
        """Close the dialog window."""
        self.window.destroy()

    @classmethod
    def show(
        cls,
        master=None,
        config: Optional[MessageBoxConfig] = None,
        position: Optional[WindowPosition] = None,
    ):
        """
        Show a message box dialog and return the result.
        This is the main class method for displaying message boxes. It handles
        root window creation/destruction and returns the user's choice.
        Args:
            master: Parent window
            config: MessageBoxConfig object containing dialog configuration
            position: WindowPosition object containing window positioning
        Returns:
            The value corresponding to the button that was clicked, or
            selected choice(s)
        """
        root, created = _get_or_create_root() if master is None else (master, False)
        if config is None:
            config = MessageBoxConfig()
        if position is None:
            position = WindowPosition()

        lang.set(config.language or "auto", root)
        result = cls(
            master=root,
            config=config,
            position=position,
        ).result
        if created:
            root.destroy()
        return result


def showinfo(  # pylint: disable=R0917
    master=None,
    message="",
    title=None,
    language=None,
    bell=False,
    x=None,
    y=None,
    x_offset=0,
    y_offset=0,
):
    """
    Show an information message box.
    Args:
        master: Parent window
        message (str): Information message to display
        title (str): Window title (defaults to "Info")
        language (str): Language code for translations
        **kwargs: Additional arguments passed to CustomMessageBox.show
    Returns:
        The button value that was clicked (usually "ok")
    Example:
        >>> showinfo("Operation completed successfully!", language="ja")
    """
    config = MessageBoxConfig(
        message=message,
        title=title or get_icon_title(INFO),
        icon=INFO,
        button_set="ok",
        language=language,
        bell=bell,
    )
    position = WindowPosition(x=x, y=y, x_offset=x_offset, y_offset=y_offset)
    return CustomMessageBox.show(
        master=master,
        config=config,
        position=position,
    )


def showerror(  # pylint: disable=R0917
    master=None,
    message="",
    title=None,
    language=None,
    bell=False,
    x=None,
    y=None,
    x_offset=0,
    y_offset=0,
):
    """
    Show an error message box.
    Args:
        master: Parent window
        message (str): Error message to display
        title (str): Window title (defaults to "Error")
        language (str): Language code for translations
        **kwargs: Additional arguments passed to CustomMessageBox.show
    Returns:
        The button value that was clicked (usually "ok")
    Example:
        >>> showerror("An error has occurred!", language="ja")
    """
    config = MessageBoxConfig(
        message=message,
        title=title or get_icon_title(ERROR),
        icon=ERROR,
        button_set="ok",
        language=language,
        bell=bell,
    )
    position = WindowPosition(x=x, y=y, x_offset=x_offset, y_offset=y_offset)
    return CustomMessageBox.show(
        master=master,
        config=config,
        position=position,
    )


def showwarning(  # pylint: disable=R0917
    master=None,
    message="",
    title=None,
    language=None,
    bell=False,
    x=None,
    y=None,
    x_offset=0,
    y_offset=0,
):
    """
    Show a warning message box.
    Args:
        master: Parent window
        message (str): Warning message to display
        title (str): Window title (defaults to "Warning")
        language (str): Language code for translations
        **kwargs: Additional arguments passed to CustomMessageBox.show
    Returns:
        The button value that was clicked (usually "ok")
    Example:
        >>> showwarning("This is a warning message.", language="ja")
    """
    config = MessageBoxConfig(
        message=message,
        title=title or get_icon_title(WARNING),
        icon=WARNING,
        button_set="ok",
        language=language,
        bell=bell,
    )
    position = WindowPosition(x=x, y=y, x_offset=x_offset, y_offset=y_offset)
    return CustomMessageBox.show(
        master=master,
        config=config,
        position=position,
    )


def askquestion(  # pylint: disable=R0917
    master=None,
    message="",
    title=None,
    language=None,
    bell=False,
    x=None,
    y=None,
    x_offset=0,
    y_offset=0,
):
    """
    Show a question dialog with Yes/No buttons.
    Args:
        master: Parent window
        message (str): Question message to display
        title (str): Window title (defaults to "Question")
        language (str): Language code for translations
        **kwargs: Additional arguments passed to CustomMessageBox.show
    Returns:
        "yes" or "no" depending on which button was clicked
    Example:
        >>> result = askquestion("Do you want to proceed?", language="ja")
        >>> if result == "yes":
        ...     # User chose yes - handle accordingly
        ...     pass
    """
    config = MessageBoxConfig(
        message=message,
        title=title or get_icon_title(QUESTION),
        icon=QUESTION,
        button_set="yesno",
        language=language,
        bell=bell,
    )
    position = WindowPosition(x=x, y=y, x_offset=x_offset, y_offset=y_offset)
    return CustomMessageBox.show(
        master=master,
        config=config,
        position=position,
    )


def askyesno(  # pylint: disable=R0917
    master=None,
    message="",
    title=None,
    language=None,
    bell=False,
    x=None,
    y=None,
    x_offset=0,
    y_offset=0,
):
    """
    Show a question dialog with Yes/No buttons.
    This function is identical to askquestion() but returns boolean values
    instead of strings for better integration with conditional statements.
    Args:
        master: Parent window
        message (str): Question message to display
        title (str): Window title (defaults to "Question")
        language (str): Language code for translations
        **kwargs: Additional arguments passed to CustomMessageBox.show
    Returns:
        True for "yes", False for "no"
    Example:
        >>> if askyesno("Do you want to save?", language="ja"):
        ...     save_file()
    """
    config = MessageBoxConfig(
        message=message,
        title=title or get_icon_title(QUESTION),
        icon=QUESTION,
        button_set="yesno",
        language=language,
        bell=bell,
    )
    position = WindowPosition(x=x, y=y, x_offset=x_offset, y_offset=y_offset)
    result = CustomMessageBox.show(
        master=master,
        config=config,
        position=position,
    )
    return result == "yes"


def askokcancel(  # pylint: disable=R0917
    master=None,
    message="",
    title=None,
    language=None,
    bell=False,
    x=None,
    y=None,
    x_offset=0,
    y_offset=0,
):
    """
    Show a confirmation dialog with OK and Cancel buttons.
    Args:
        master: Parent window
        message (str): Confirmation message to display
        title (str): Window title (defaults to "Confirm")
        language (str): Language code for translations
        **kwargs: Additional arguments passed to CustomMessageBox.show
    Returns:
        True if OK was clicked, False if Cancel was clicked
    Example:
        >>> if askokcancel("Do you want to save?"):
        ...     save_file()
    """
    config = MessageBoxConfig(
        message=message,
        title=title or "Confirm",
        icon=QUESTION,
        button_set="okcancel",
        language=language,
        bell=bell,
    )
    position = WindowPosition(x=x, y=y, x_offset=x_offset, y_offset=y_offset)
    result = CustomMessageBox.show(
        master=master,
        config=config,
        position=position,
    )
    return result == "ok"


def askretrycancel(  # pylint: disable=R0917
    master=None,
    message="",
    title=None,
    language=None,
    bell=False,
    x=None,
    y=None,
    x_offset=0,
    y_offset=0,
):
    """
    Show a retry dialog with Retry and Cancel buttons.
    Args:
        master: Parent window
        message (str): Retry message to display
        title (str): Window title (defaults to "Retry")
        language (str): Language code for translations
        **kwargs: Additional arguments passed to CustomMessageBox.show
    Returns:
        True if Retry was clicked, False if Cancel was clicked
    Example:
        >>> if askretrycancel("Failed to save. Retry?"):
        ...     retry_save()
    """
    config = MessageBoxConfig(
        message=message,
        title=title or "Retry",
        icon=WARNING,
        button_set="retrycancel",
        language=language,
        bell=bell,
    )
    position = WindowPosition(x=x, y=y, x_offset=x_offset, y_offset=y_offset)
    result = CustomMessageBox.show(
        master=master,
        config=config,
        position=position,
    )
    return result == "retry"


def askyesnocancel(  # pylint: disable=R0917
    master=None,
    message="",
    title=None,
    language=None,
    bell=False,
    x=None,
    y=None,
    x_offset=0,
    y_offset=0,
):
    """
    Show a question dialog with Yes/No/Cancel buttons.
    Args:
        master: Parent window
        message (str): Question message to display
        title (str): Window title (defaults to "Question")
        language (str): Language code for translations
        **kwargs: Additional arguments passed to CustomMessageBox.show
    Returns:
        "yes", "no", or "cancel" depending on which button was clicked
    Example:
        >>> result = askyesnocancel("Save changes?", language="ja")
        >>> if result == "yes":
        ...     save_file()
        >>> elif result == "no":
        ...     discard_changes()
        >>> # else: cancel - do nothing
    """
    config = MessageBoxConfig(
        message=message,
        title=title or get_icon_title(QUESTION),
        icon=QUESTION,
        button_set="yesnocancel",
        language=language,
        bell=bell,
    )
    position = WindowPosition(x=x, y=y, x_offset=x_offset, y_offset=y_offset)
    result = CustomMessageBox.show(
        master=master,
        config=config,
        position=position,
    )
    if result == "yes":
        return True
    if result == "no":
        return False
    return None


def askabortretryignore(  # pylint: disable=R0917
    master=None,
    message="",
    title=None,
    language=None,
    bell=False,
    x=None,
    y=None,
    x_offset=0,
    y_offset=0,
):
    """
    Show an abort/retry/ignore dialog.
    Args:
        master: Parent window
        message (str): Message to display
        title (str): Window title (defaults to "Error")
        language (str): Language code for translations
        **kwargs: Additional arguments passed to CustomMessageBox.show
    Returns:
        "abort", "retry", or "ignore" depending on which button was clicked
    Example:
        >>> result = askabortretryignore("File access failed.")
        >>> if result == "retry":
        ...     retry_operation()
        >>> elif result == "ignore":
        ...     continue_operation()
    """
    config = MessageBoxConfig(
        message=message,
        title=title or "Error",
        icon=ERROR,
        button_set="abortretryignore",
        language=language,
        bell=bell,
    )
    position = WindowPosition(x=x, y=y, x_offset=x_offset, y_offset=y_offset)
    return CustomMessageBox.show(
        master=master,
        config=config,
        position=position,
    )
