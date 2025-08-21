import logging
import tkinter as tk
from dataclasses import dataclass
from typing import Callable, Dict, List, Optional

from tkface import lang
from tkface.dialog import _position_window, _setup_dialog_base, messagebox


@dataclass
class SimpleDialogConfig:
    """Configuration for simple dialog dialogs."""

    title: Optional[str] = "Input"
    message: str = ""
    initialvalue: Optional[str] = None
    show: Optional[str] = None
    ok_label: Optional[str] = None
    cancel_label: Optional[str] = None
    language: Optional[str] = None
    custom_translations: Optional[Dict[str, Dict[str, str]]] = None
    validate_func: Optional[Callable[[str], bool]] = None
    choices: Optional[List[str]] = None
    multiple: bool = False
    initial_selection: Optional[List[int]] = None


@dataclass
class WindowPosition:
    """Window positioning configuration."""

    x: Optional[int] = None
    y: Optional[int] = None
    x_offset: int = 0
    y_offset: int = 0


class CustomSimpleDialog:
    """
    A customizable simple dialog for user input with
    internationalization support.
    This class provides a modal dialog with an entry field and
    OK/Cancel buttons, similar to tkinter's simpledialog but with
    enhanced features like internationalization, custom positioning,
    and validation.
    """

    def __init__(
        self,
        master=None,
        config: Optional[SimpleDialogConfig] = None,
        position: Optional[WindowPosition] = None,
    ):
        """
        Initialize the CustomSimpleDialog.
        Args:
            master: Parent window. If None, uses default root or
                creates one.
            config: SimpleDialogConfig object containing dialog configuration
            position: WindowPosition object containing window positioning
        """
        # Set default values
        if config is None:
            config = SimpleDialogConfig()
        if position is None:
            position = WindowPosition()

        master, _, self.language = _setup_dialog_base(master, config.language)
        self.logger = logging.getLogger(__name__)
        self.validate_func = config.validate_func
        self.choices = config.choices
        self.multiple = config.multiple
        self.initial_selection = config.initial_selection or []
        # Initialize attributes that will be set in _create_content
        self.listbox = None
        self.window = tk.Toplevel(master)
        self.window.title(lang.get(config.title, self.window, language=config.language))
        self.window.transient(master)
        self.window.grab_set()
        if config.custom_translations:
            for lang_code, dictionary in config.custom_translations.items():
                lang.register(lang_code, dictionary, self.window)
        self.result = None
        # Create body frame
        body = tk.Frame(self.window)
        self.initial_focus = self._create_content(
            body, config.message, config.initialvalue, config.show
        )
        body.pack(padx=5, pady=5)
        self._create_buttons(config.ok_label, config.cancel_label)
        self._set_window_position(
            master, position.x, position.y, position.x_offset, position.y_offset
        )
        self.window.lift()
        # Set focus to entry
        if self.initial_focus is None:
            self.initial_focus = self.window
        self.initial_focus.focus_set()
        self.window.wait_window()

    def _create_content(self, master, message, initialvalue, show):
        """
        Create the content area with message label and entry field or
        selection list.
        Args:
            master: Parent widget for the content.
            message: Text to display above the entry field.
            initialvalue: Initial value for the entry
            field.
            show: Character to show for password input.
        Returns:
            tk.Entry or tk.Listbox: The widget that should receive focus.
        """
        if message:
            # Translate the message
            translated_message = lang.get(message, master, language=self.language)
            message_label = tk.Label(master, text=translated_message, justify="left")
            message_label.grid(row=0, padx=5, sticky="w")
        # If choices are provided, create a selection list instead of entry
        # field
        if self.choices:
            return self._create_selection_list(master)
        self.entry_var = tk.StringVar(
            value=initialvalue if initialvalue is not None else ""
        )
        entry = tk.Entry(master, textvariable=self.entry_var, show=show)
        entry.grid(row=1, padx=5, sticky="ew")
        self.entry = entry
        entry.bind("<Return>", lambda e: self._on_ok())
        entry.bind("<Escape>", lambda e: self._on_cancel())
        return entry

    def _create_selection_list(self, parent):
        """
        Create a selection list (Listbox) for choices.
        Args:
            parent: Parent widget for the list
        Returns:
            tk.Listbox: The listbox widget that should receive focus
        """
        # Create frame for listbox and scrollbar
        list_frame = tk.Frame(parent)
        list_frame.grid(row=1, padx=5, sticky="ew")
        # Create scrollbar
        scrollbar = tk.Scrollbar(list_frame)
        scrollbar.pack(side="right", fill="y")
        # Create listbox
        self.listbox = tk.Listbox(
            list_frame,
            selectmode=tk.MULTIPLE if self.multiple else tk.SINGLE,
            yscrollcommand=scrollbar.set,
            height=min(len(self.choices), 10),  # Max 10 items visible
        )
        self.listbox.pack(side="left", fill="both", expand=True)
        scrollbar.config(command=self.listbox.yview)
        # Add choices to listbox
        for choice in self.choices:
            self.listbox.insert(tk.END, choice)
        # Set initial selection
        if self.initial_selection:
            for index in self.initial_selection:
                if 0 <= index < len(self.choices):
                    self.listbox.selection_set(index)
        # Bind double-click for single selection mode
        if not self.multiple:
            self.listbox.bind("<Double-Button-1>", self._on_double_click)
        # Bind keyboard shortcuts
        self.listbox.bind("<Return>", lambda e: self._on_ok())
        self.listbox.bind("<Escape>", lambda e: self._on_cancel())
        return self.listbox

    def _on_double_click(self, event):  # pylint: disable=unused-argument
        """
        Handle double-click on listbox item for single selection mode.
        Args:
            event: Double-click event
        """
        selection = self.listbox.curselection()
        if selection:
            self.set_result(self.choices[selection[0]])

    def _get_selection_result(self):
        """
        Get the current selection result.
        Returns:
            Selected value(s) based on selection mode
        """
        if not hasattr(self, "listbox") or self.listbox is None:
            return None
        selection = self.listbox.curselection()
        if not selection:
            return None
        if self.multiple:
            # Return list of selected values
            return [self.choices[i] for i in selection]
        # Return single selected value
        return self.choices[selection[0]]

    def _create_buttons(self, ok_label, cancel_label):
        """
        Create OK and Cancel buttons with proper layout and bindings.
        Args:
            ok_label: Custom text for OK button.
            cancel_label: Custom text for Cancel button.
        """
        button_frame = tk.Frame(self.window)
        button_frame.pack()
        ok_text = ok_label or lang.get("ok", self.window, language=self.language)
        cancel_text = cancel_label or lang.get(
            "cancel", self.window, language=self.language
        )
        ok_btn = tk.Button(
            button_frame,
            text=ok_text,
            width=10,
            command=self._on_ok,
            default="active",
        )
        ok_btn.pack(side="left", padx=5, pady=5)
        cancel_btn = tk.Button(
            button_frame,
            text=cancel_text,
            width=10,
            command=self._on_cancel,
        )
        cancel_btn.pack(side="left", padx=5, pady=5)
        self.ok_btn = ok_btn
        self.cancel_btn = cancel_btn
        # Tab navigation
        ok_btn.bind("<Tab>", lambda e: cancel_btn.focus_set())
        cancel_btn.bind("<Tab>", lambda e: ok_btn.focus_set())
        # Enter/Esc
        self.window.bind("<Return>", lambda e: ok_btn.invoke())
        self.window.bind("<Escape>", lambda e: cancel_btn.invoke())
        ok_btn.focus_set()

    def _set_window_position(  # pylint: disable=R0917
        self, master, x=None, y=None, x_offset=0, y_offset=0
    ):
        """
        Set the window position relative to the parent window.
        Args:
            master: Parent window for positioning reference.
            x, y: Absolute position (if specified).
            x_offset, y_offset: Offset from parent window center.
        """
        _position_window(self.window, master, x, y, x_offset, y_offset)

    def _on_ok(self):
        """Handle OK button click with validation if specified."""
        # For selection dialogs, get the selection result
        if hasattr(self, "listbox") and self.listbox is not None:
            self.result = self._get_selection_result()
            self.close()
            return
        # For regular entry dialogs, validate and get entry value
        if self.validate_func:
            result = self.entry_var.get()
            if not self.validate_func(result):
                # Show error message
                err_msg = lang.get("Invalid input.", None, language=self.language)
                try_again_msg = lang.get(
                    "Please try again.", None, language=self.language
                )
                illegal_value_msg = lang.get(
                    "Illegal value", None, language=self.language
                )
                messagebox.showwarning(
                    master=self.window,
                    message=err_msg + "\n" + try_again_msg,
                    title=illegal_value_msg,
                    language=self.language,
                )
                return  # Don't close dialog
        self.result = self.entry_var.get()
        self.close()

    def _on_cancel(self):
        """Handle Cancel button click."""
        self.result = None
        self.close()

    def set_result(self, value):
        """
        Set the dialog result and close the window.
        Args:
            value: The result value to return
        """
        self.result = value
        self.close()

    def close(self):
        """Close the dialog window."""
        self.window.destroy()

    @classmethod
    def show(
        cls,
        master=None,
        config: Optional[SimpleDialogConfig] = None,
        position: Optional[WindowPosition] = None,
    ):
        """
        Show the dialog and return the result.
        This is a convenience method that creates and shows the dialog,
        handling root window creation/destruction automatically.
        Args:
            master: Parent window.
            config: SimpleDialogConfig object containing dialog configuration
            position: WindowPosition object containing window positioning
        Returns:
            str or None: The entered value or None if cancelled.
        """
        if config is None:
            config = SimpleDialogConfig()
        if position is None:
            position = WindowPosition()

        master, created, _ = _setup_dialog_base(master, config.language)
        lang.set(config.language or "auto", master)
        result = cls(
            master=master,
            config=config,
            position=position,
        ).result
        if created:
            master.destroy()
        return result


def askstring(  # pylint: disable=R0917
    master=None,
    message: str = "",
    title: Optional[str] = None,
    initialvalue: Optional[str] = None,
    show: Optional[str] = None,
    ok_label: Optional[str] = None,
    cancel_label: Optional[str] = None,
    language: Optional[str] = None,
    custom_translations: Optional[Dict[str, Dict[str, str]]] = None,
    x: Optional[int] = None,
    y: Optional[int] = None,
    x_offset: int = 0,
    y_offset: int = 0,
):
    """
    Display a string input dialog and return the entered value.
    This function provides a simple way to get string input from the
    user,
    similar to tkinter.simpledialog.askstring but with
    internationalization support.
    Args:
        master: Parent window.
        message: Message text to display.
        title: Dialog title.
        initialvalue: Initial value for the entry
            field.
        show: Character to show for password input
            (e.g., "*").
        ok_label: Custom text for OK button.
        cancel_label: Custom text for Cancel button.
        language: Language code for internationalization.
        custom_translations: Custom translation
            dictionary.
        x, y: Absolute position for the dialog.
        x_offset, y_offset: Offset from parent window center.
    Returns:
        str or None: The entered string or None if cancelled.
    Example:
        >>> name = askstring(
        ...     message="Enter your name:", language="ja"
        ... )
        >>> password = askstring(
        ...     message="Enter password:", show="*", language="en"
        ... )
    """
    config = SimpleDialogConfig(
        message=message,
        title=title or "Input",
        initialvalue=initialvalue,
        show=show,
        ok_label=ok_label,
        cancel_label=cancel_label,
        language=language,
        custom_translations=custom_translations,
    )
    position = WindowPosition(x=x, y=y, x_offset=x_offset, y_offset=y_offset)
    return CustomSimpleDialog.show(
        master=master,
        config=config,
        position=position,
    )


def askinteger(  # pylint: disable=R0917
    master=None,
    message: str = "",
    title: Optional[str] = None,
    initialvalue: Optional[str] = None,
    minvalue: Optional[int] = None,
    maxvalue: Optional[int] = None,
    ok_label: Optional[str] = None,
    cancel_label: Optional[str] = None,
    language: Optional[str] = None,
    custom_translations: Optional[Dict[str, Dict[str, str]]] = None,
    x: Optional[int] = None,
    y: Optional[int] = None,
    x_offset: int = 0,
    y_offset: int = 0,
):
    """
    Display an integer input dialog with validation.
    This function shows a dialog for integer input with optional range
    validation.
    If the input is invalid, an error message is shown and the
    dialog remains open.
    Args:
        master: Parent window.
        message: Message text to display.
        title: Dialog title.
        initialvalue: Initial value for the entry
            field.
        minvalue: Minimum allowed value (inclusive).
        maxvalue: Maximum allowed value (inclusive).
        ok_label: Custom text for OK button.
        cancel_label: Custom text for Cancel button.
        language: Language code for internationalization.
        custom_translations: Custom translation
            dictionary.
        x, y: Absolute position for the dialog.
        x_offset, y_offset: Offset from parent window center.
    Returns:
        int or None: The entered integer or None if cancelled.
    Example:
        >>> age = askinteger(
        ...     message="Enter your age:", minvalue=0, maxvalue=120,
        ...     language="ja"
        ... )
        >>> count = askinteger(
        ...     message="Enter count:", minvalue=1, language="en"
        ... )
    """

    def validate(val):
        try:
            ival = int(val)
            if minvalue is not None and ival < minvalue:
                return False
            if maxvalue is not None and ival > maxvalue:
                return False
            return True
        except (ValueError, TypeError) as e:
            logger = logging.getLogger(__name__)
            logger.debug("Failed to validate integer input '%s': %s", val, e)
            return False

    config = SimpleDialogConfig(
        message=message,
        title=title or "Input",
        initialvalue=initialvalue,
        show=None,
        ok_label=ok_label,
        cancel_label=cancel_label,
        language=language,
        custom_translations=custom_translations,
        validate_func=validate,
    )
    position = WindowPosition(x=x, y=y, x_offset=x_offset, y_offset=y_offset)
    result = CustomSimpleDialog.show(
        master=master,
        config=config,
        position=position,
    )
    if result is None:
        return None
    return int(result)


def askfloat(  # pylint: disable=R0917
    master=None,
    message: str = "",
    title: Optional[str] = None,
    initialvalue: Optional[str] = None,
    minvalue: Optional[float] = None,
    maxvalue: Optional[float] = None,
    ok_label: Optional[str] = None,
    cancel_label: Optional[str] = None,
    language: Optional[str] = None,
    custom_translations: Optional[Dict[str, Dict[str, str]]] = None,
    x: Optional[int] = None,
    y: Optional[int] = None,
    x_offset: int = 0,
    y_offset: int = 0,
):
    """
    Display a float input dialog with validation.
    This function shows a dialog for floating-point input with optional
    range validation.
    If the input is invalid, an error message is shown and the
    dialog remains open.
    Args:
        master: Parent window.
        message: Message text to display.
        title: Dialog title.
        initialvalue: Initial value for the entry
            field.
        minvalue: Minimum allowed value (inclusive).
        maxvalue: Maximum allowed value (inclusive).
        ok_label: Custom text for OK button.
        cancel_label: Custom text for Cancel button.
        language: Language code for internationalization.
        custom_translations: Custom translation
            dictionary.
        x, y: Absolute position for the dialog.
        x_offset, y_offset: Offset from parent window center.
    Returns:
        float or None: The entered float or None if cancelled.
    Example:
        >>> height = askfloat(
        ...     message="Enter height (m):", minvalue=0.0, maxvalue=3.0,
        ...     language="ja"
        ... )
        >>> price = askfloatfloat(
        ...     message="Enter price:", minvalue=0.0, language="en"
        ... )
    """

    def validate(val):
        try:
            fval = float(val)
            if minvalue is not None and fval < minvalue:
                return False
            if maxvalue is not None and fval > maxvalue:
                return False
            return True
        except (ValueError, TypeError) as e:
            logger = logging.getLogger(__name__)
            logger.debug("Failed to validate float input '%s': %s", val, e)
            return False

    config = SimpleDialogConfig(
        message=message,
        title=title or "Input",
        initialvalue=initialvalue,
        show=None,
        ok_label=ok_label,
        cancel_label=cancel_label,
        language=language,
        custom_translations=custom_translations,
        validate_func=validate,
    )
    position = WindowPosition(x=x, y=y, x_offset=x_offset, y_offset=y_offset)
    result = CustomSimpleDialog.show(
        master=master,
        config=config,
        position=position,
    )
    if result is None:
        return None
    return float(result)


def askfromlistbox(  # pylint: disable=R0917
    master=None,
    message: str = "",
    title: Optional[str] = None,
    choices: Optional[List[str]] = None,
    multiple: bool = False,
    initial_selection: Optional[List[int]] = None,
    ok_label: Optional[str] = None,
    cancel_label: Optional[str] = None,
    language: Optional[str] = None,
    custom_translations: Optional[Dict[str, Dict[str, str]]] = None,
    x: Optional[int] = None,
    y: Optional[int] = None,
    x_offset: int = 0,
    y_offset: int = 0,
):
    """
    Show a list selection dialog.
    Args:
        master: Parent window
        message (str): Message to display above the list
        title (str): Window title (defaults to "Select")
        choices (list): List of choices to display
        multiple (bool): Allow multiple selection if True
        initial_selection (list): Initial selection indices for multiple
            selection
        ok_label: Custom text for OK button
        cancel_label: Custom text for Cancel button
        language (str): Language code for translations
        custom_translations: Custom translation dictionary
        x, y: Absolute position for the dialog
        x_offset, y_offset: Offset from parent window center
    Returns:
        Selected choice(s) or None if cancelled
    Example:
        >>> choice = askfromlistbox(
        ...     "Choose a color:", choices=["Red", "Green", "Blue"]
        ... )
        >>> choices = askfromlistbox(
        ...     "Choose colors:", choices=["Red", "Green", "Blue"],
        ...     multiple=True
        ... )
    """
    if not choices:
        raise ValueError("choices parameter is required")
    config = SimpleDialogConfig(
        message=message,
        title=title or "Select",
        ok_label=ok_label,
        cancel_label=cancel_label,
        language=language,
        custom_translations=custom_translations,
        choices=choices,
        multiple=multiple,
        initial_selection=initial_selection,
    )
    position = WindowPosition(x=x, y=y, x_offset=x_offset, y_offset=y_offset)
    return CustomSimpleDialog.show(
        master=master,
        config=config,
        position=position,
    )
