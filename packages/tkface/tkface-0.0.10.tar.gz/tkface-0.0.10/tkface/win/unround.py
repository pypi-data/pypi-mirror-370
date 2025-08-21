import logging
import sys

# Import Windows-specific modules only when needed
if sys.platform.startswith("win"):
    try:
        import ctypes
        import tkinter as tk
        from ctypes import wintypes
    except ImportError:
        ctypes = None
        wintypes = None
        tk = None
logger = logging.getLogger(__name__)
# DwmSetWindowAttribute constants
DWMWA_WINDOW_CORNER_PREFERENCE = 33
DWMWCP_DONOTROUND = 1
# Global state for auto-unround feature
_AUTO_UNROUND_ENABLED = False
_ORIGINAL_TOPLEVEL_INIT = None


def disable_window_corner_round(hwnd):
    """
    Disable window corner rounding for a specific window handle.
    Returns True if successful, False otherwise.
    """
    if not sys.platform.startswith("win") or ctypes is None or wintypes is None:
        return False
    try:
        # Load dwmapi.dll
        dwmapi = ctypes.WinDLL("dwmapi")
        preference = ctypes.c_int(DWMWCP_DONOTROUND)
        result = dwmapi.DwmSetWindowAttribute(
            wintypes.HWND(hwnd),
            ctypes.c_uint(DWMWA_WINDOW_CORNER_PREFERENCE),
            ctypes.byref(preference),
            ctypes.sizeof(preference),
        )
        return result == 0
    except (OSError, AttributeError) as e:
        logger.debug("Failed to disable window corner rounding: %s", e)
        return False


def unround(root, auto_toplevel=True):
    """
    Disable window corner rounding for all windows under the given Tk root
    (Windows 11 only).
    Does nothing on other OSes.
    Args:
        root: Tkinter root window
        auto_toplevel (bool): If True, enables automatic unrounding
            for future Toplevel windows
    Returns:
        bool: True if successful, False otherwise
    """
    if not sys.platform.startswith("win") or ctypes is None:
        return True  # Consider success on non-Windows platforms
    try:
        # Enable auto-unround for future Toplevel windows (like messageboxes)
        if auto_toplevel:
            enable_auto_unround()
        # Ensure window is fully created before applying unround
        root.update_idletasks()
        # Get the actual window handle using GetParent
        hwnd = ctypes.windll.user32.GetParent(root.winfo_id())
        success = disable_window_corner_round(hwnd)
        # Also handle existing Toplevel windows
        for w in root.winfo_children():
            if hasattr(w, "winfo_id"):
                try:
                    child_hwnd = ctypes.windll.user32.GetParent(w.winfo_id())
                    disable_window_corner_round(child_hwnd)
                except (OSError, AttributeError) as e:
                    logger.debug(
                        "Failed to disable corner rounding for child window: %s",
                        e,
                    )
        return success
    except (OSError, AttributeError) as e:
        logger.warning("Failed to unround windows: %s", e)
        return False


def _patched_toplevel_init(self, master=None, **kw):
    """Patched Toplevel.__init__ that automatically applies unround."""
    logger.debug("Creating Toplevel window with auto-unround...")
    # Call original __init__
    _ORIGINAL_TOPLEVEL_INIT(self, master, **kw)
    # Apply unround after window is created
    try:
        # Schedule multiple attempts at unround application
        self.after_idle(_apply_unround_to_toplevel, self)
        self.after(100, _apply_unround_to_toplevel, self)  # Retry after 100ms
        self.after(500, _apply_unround_to_toplevel, self)  # Retry after 500ms
        logger.debug("Scheduled multiple unround application attempts for Toplevel")
    except (OSError, AttributeError) as e:
        logger.warning("Failed to schedule unround, applying immediately: %s", e)
        # If scheduling fails, try to apply immediately
        _apply_unround_to_toplevel(self)


def _is_unround_applied(toplevel):
    """Check if unround has been applied to a Toplevel window."""
    try:
        # pylint: disable=protected-access
        return toplevel._tkface_unround_applied
    except AttributeError:
        return False


def _mark_unround_applied(toplevel):
    """Mark that unround has been applied to a Toplevel window."""
    # pylint: disable=protected-access
    toplevel._tkface_unround_applied = True


def _apply_unround_to_toplevel(toplevel):
    """Apply unround to a Toplevel window."""
    if not sys.platform.startswith("win") or ctypes is None:
        return
    # Avoid duplicate applications
    if _is_unround_applied(toplevel):
        return
    try:
        # Ensure window is fully created
        toplevel.update_idletasks()
        # Get window handle - try multiple methods
        hwnd = None
        # Method 1: Direct winfo_id (for Toplevel windows)
        try:
            hwnd = toplevel.winfo_id()
            if hwnd and hwnd != 0:
                logger.debug("Got Toplevel hwnd via winfo_id: %s", hwnd)
            else:
                hwnd = None
        except (OSError, AttributeError) as e:
            logger.debug("Failed to get Toplevel hwnd via winfo_id: %s", e)
            hwnd = None
        # Method 2: GetParent (for embedded windows)
        if hwnd is None or hwnd == 0:
            try:
                hwnd = ctypes.windll.user32.GetParent(toplevel.winfo_id())
                if hwnd and hwnd != 0:
                    logger.debug("Got Toplevel hwnd via GetParent: %s", hwnd)
                else:
                    hwnd = None
            except (OSError, AttributeError) as e:
                logger.debug("Failed to get Toplevel hwnd via GetParent: %s", e)
                hwnd = None
        # Method 3: FindWindow by title (last resort)
        if hwnd is None or hwnd == 0:
            try:
                title = toplevel.title()
                if title:
                    hwnd = ctypes.windll.user32.FindWindowW(None, title)
                    if hwnd and hwnd != 0:
                        logger.debug("Got Toplevel hwnd via FindWindow: %s", hwnd)
                    else:
                        hwnd = None
            except (OSError, AttributeError) as e:
                logger.debug("Failed to get Toplevel hwnd via FindWindow: %s", e)
                hwnd = None
        if hwnd and hwnd != 0:
            result = disable_window_corner_round(hwnd)
            logger.debug("Applied unround to Toplevel (hwnd: %s): %s", hwnd, result)
            if result:
                # Mark as successfully applied to avoid duplicate attempts
                _mark_unround_applied(toplevel)
        else:
            logger.warning("Failed to get valid hwnd for Toplevel window")
    except (OSError, AttributeError) as e:
        logger.warning("Failed to apply unround to Toplevel: %s", e)


def enable_auto_unround():
    """
    Enable automatic unrounding for all future Toplevel windows.
    This affects messageboxes, dialogs, and other popup windows.
    Returns:
        bool: True if auto-unround was enabled, False otherwise
    """
    global _AUTO_UNROUND_ENABLED, _ORIGINAL_TOPLEVEL_INIT  # noqa: E501 pylint: disable=global-statement
    if not sys.platform.startswith("win") or ctypes is None or tk is None:
        logger.info("Auto-unround: Not on Windows or missing dependencies")
        return False
    if _AUTO_UNROUND_ENABLED:
        logger.debug("Auto-unround: Already enabled")
        return True  # Already enabled
    try:
        # Store original Toplevel.__init__
        _ORIGINAL_TOPLEVEL_INIT = tk.Toplevel.__init__
        # Replace with patched version
        tk.Toplevel.__init__ = _patched_toplevel_init
        _AUTO_UNROUND_ENABLED = True
        logger.info("Auto-unround: Successfully enabled, Toplevel.__init__ patched")
        return True
    except (OSError, AttributeError) as e:
        logger.warning("Auto-unround: Failed to enable: %s", e)
        return False


def disable_auto_unround():
    """
    Disable automatic unrounding for Toplevel windows.
    Returns:
        bool: True if auto-unround was disabled, False otherwise
    """
    global _AUTO_UNROUND_ENABLED, _ORIGINAL_TOPLEVEL_INIT  # noqa: E501 pylint: disable=global-statement
    if not _AUTO_UNROUND_ENABLED or _ORIGINAL_TOPLEVEL_INIT is None:
        return True  # Already disabled or never enabled
    try:
        # Restore original Toplevel.__init__
        if tk is not None:
            tk.Toplevel.__init__ = _ORIGINAL_TOPLEVEL_INIT
        _AUTO_UNROUND_ENABLED = False
        _ORIGINAL_TOPLEVEL_INIT = None
        return True
    except (OSError, AttributeError) as e:
        logger.warning("Auto-unround: Failed to disable: %s", e)
        return False


def is_auto_unround_enabled():
    """
    Check if automatic unrounding is enabled.
    Returns:
        bool: True if auto-unround is enabled, False otherwise
    """
    return _AUTO_UNROUND_ENABLED
