import ctypes
import logging
import re
import sys
import tkinter as tk
import tkinter.font as tkfont
from ctypes import pointer, wintypes


def is_windows():
    """Check if running on Windows platform."""
    return sys.platform == "win32"


class DPIManager:
    """DPI management class for Windows applications."""

    def __init__(self):
        self._dpi_awareness_set = False
        self.logger = logging.getLogger(__name__)

    def _get_hwnd_dpi(self, window_handle):
        """Get DPI information for a window handle."""
        if not is_windows():
            return 96, 96, 1.0
        try:
            try:
                ctypes.windll.shcore.SetProcessDpiAwareness(1)
            except Exception as e:  # pylint: disable=W0718  # pylint: disable=W0718
                self.logger.debug("Failed to set process DPI awareness: %s", e)
            dpi_100pc = 96
            dpi_type = 0
            win_h = wintypes.HWND(window_handle)
            monitor_handle = ctypes.windll.user32.MonitorFromWindow(
                win_h, wintypes.DWORD(2)
            )
            x_dpi = wintypes.UINT()
            y_dpi = wintypes.UINT()
            try:
                ctypes.windll.shcore.GetDpiForMonitor(
                    monitor_handle,
                    dpi_type,
                    pointer(x_dpi),
                    pointer(y_dpi),
                )
                try:
                    scale_factor = ctypes.windll.shcore.GetScaleFactorForDevice(0)
                    windows_scale = scale_factor / 100.0
                except Exception as e:  # pylint: disable=W0718  # pylint: disable=W0718
                    self.logger.debug("Failed to get Windows scale factor: %s", e)
                    windows_scale = None
                dpi_scaling = (x_dpi.value + y_dpi.value) / (2 * dpi_100pc)
                if windows_scale and windows_scale > dpi_scaling:
                    scaling_factor = windows_scale
                    self.logger.info(
                        "DPI: Using Windows scale factor %s instead of DPI-based %s",
                        windows_scale,
                        dpi_scaling,
                    )
                else:
                    scaling_factor = dpi_scaling
                return x_dpi.value, y_dpi.value, scaling_factor
            except Exception as e:  # pylint: disable=W0718  # pylint: disable=W0718
                self.logger.debug("Failed to get DPI for monitor: %s", e)
                return 96, 96, 1.0
        except Exception as e:  # pylint: disable=W0718  # pylint: disable=W0718
            self.logger.debug("Failed to get DPI information: %s", e)
            return 96, 96, 1.0

    def _scale_geometry_string(self, geometry_string, scale_func):
        """Scale geometry string based on DPI scaling."""
        if not geometry_string:
            return geometry_string
        try:
            pattern = r"(?P<W>\d+)x(?P<H>\d+)\+(?P<X>\d+)\+(?P<Y>\d+)"
            match = re.search(pattern, geometry_string)
            if match:
                w = scale_func(int(match.group("W")))
                h = scale_func(int(match.group("H")))
                x = scale_func(int(match.group("X")))
                y = scale_func(int(match.group("Y")))
                return f"{w}x{h}+{x}+{y}"
            pattern = r"(?P<W>\d+)x(?P<H>\d+)"
            match = re.search(pattern, geometry_string)
            if match:
                w = scale_func(int(match.group("W")))
                h = scale_func(int(match.group("H")))
                return f"{w}x{h}"
        except Exception as e:  # pylint: disable=W0718  # pylint: disable=W0718
            self.logger.debug("Failed to scale geometry string: %s", e)
        return geometry_string

    def _fix_scaling(self, root):
        """Scale fonts on high DPI displays."""
        if not root:
            return
        try:
            scaling = float(root.tk.call("tk", "scaling"))
            if scaling != 1.0:
                for name in tkfont.names(root):
                    font = tkfont.Font(root=root, name=name, exists=True)
                    size = int(font["size"])
                    if size < 0:
                        font["size"] = round(size * scaling)
        except Exception as e:  # pylint: disable=W0718  # pylint: disable=W0718
            self.logger.debug("Failed to fix scaling: %s", e)

    def _patch_widget_methods(self, root):
        """Patch widget methods to handle pad/padding scaling."""
        if not root or not hasattr(root, "DPI_scaling"):
            return

        scaling_factor = self._get_scaling_factor_for_patching(root)

        # Patch layout methods
        self._patch_layout_methods(scaling_factor)

        # Patch widget constructors
        self._patch_widget_constructors(scaling_factor)

    def _get_scaling_factor_for_patching(self, root):
        """Get scaling factor for patching widget methods."""
        try:
            return float(root.tk.call("tk", "scaling"))
        except Exception as e:  # pylint: disable=W0718
            self.logger.debug("Failed to get tk scaling: %s", e)
            return root.DPI_scaling

    def _patch_layout_methods(self, scaling_factor):
        """Patch layout methods (pack, grid, place)."""
        self._patch_pack_method(scaling_factor)
        self._patch_grid_method(scaling_factor)
        self._patch_place_method(scaling_factor)

    def _patch_pack_method(self, scaling_factor):
        """Patch the pack method with scaling."""
        original_pack = tk.Widget.pack

        def _scale_padding_kwargs_global(kwargs, scaling_factor):
            """Scale padding arguments in kwargs."""
            scaled_kwargs = kwargs.copy()

            if "padx" in scaled_kwargs:
                scaled_kwargs["padx"] = _scale_padding_value_global(
                    scaled_kwargs["padx"], scaling_factor
                )

            if "pady" in scaled_kwargs:
                scaled_kwargs["pady"] = _scale_padding_value_global(
                    scaled_kwargs["pady"], scaling_factor
                )

            return scaled_kwargs

        def _scale_padding_value_global(value, scaling_factor):
            """Scale a single padding value."""
            if isinstance(value, (int, float)):
                if 0 <= abs(value) <= 50:
                    return int(value * scaling_factor)
            elif isinstance(value, (list, tuple)) and len(value) == 2:
                if all(0 <= abs(val) <= 50 for val in value):
                    return (
                        int(value[0] * scaling_factor),
                        int(value[1] * scaling_factor),
                    )
            return value

        def scaled_pack(self, **kwargs):
            scaled_kwargs = _scale_padding_kwargs_global(kwargs, scaling_factor)
            return original_pack(self, **scaled_kwargs)

        tk.Widget.pack = scaled_pack

    def _patch_grid_method(self, scaling_factor):
        """Patch the grid method with scaling."""
        original_grid = tk.Widget.grid

        def _scale_padding_kwargs_global(kwargs, scaling_factor):
            """Scale padding arguments in kwargs."""
            scaled_kwargs = kwargs.copy()

            if "padx" in scaled_kwargs:
                scaled_kwargs["padx"] = _scale_padding_value_global(
                    scaled_kwargs["padx"], scaling_factor
                )

            if "pady" in scaled_kwargs:
                scaled_kwargs["pady"] = _scale_padding_value_global(
                    scaled_kwargs["pady"], scaling_factor
                )

            return scaled_kwargs

        def _scale_padding_value_global(value, scaling_factor):
            """Scale a single padding value."""
            if isinstance(value, (int, float)):
                if 0 <= abs(value) <= 50:
                    return int(value * scaling_factor)
            elif isinstance(value, (list, tuple)) and len(value) == 2:
                if all(0 <= abs(val) <= 50 for val in value):
                    return (
                        int(value[0] * scaling_factor),
                        int(value[1] * scaling_factor),
                    )
            return value

        def scaled_grid(self, **kwargs):
            scaled_kwargs = _scale_padding_kwargs_global(kwargs, scaling_factor)
            return original_grid(self, **scaled_kwargs)

        tk.Widget.grid = scaled_grid

    def _patch_place_method(self, scaling_factor):
        """Patch the place method with scaling."""
        original_place = tk.Widget.place

        def scaled_place(self, **kwargs):
            scaled_kwargs = kwargs.copy()
            if "x" in scaled_kwargs:
                scaled_kwargs["x"] = int(scaled_kwargs["x"] * scaling_factor)
            if "y" in scaled_kwargs:
                scaled_kwargs["y"] = int(scaled_kwargs["y"] * scaling_factor)
            return original_place(self, **scaled_kwargs)

        tk.Widget.place = scaled_place

    def _scale_padding_kwargs(self, kwargs, scaling_factor):
        """Scale padding arguments in kwargs."""
        scaled_kwargs = kwargs.copy()

        if "padx" in scaled_kwargs:
            scaled_kwargs["padx"] = self._scale_padding_value(
                scaled_kwargs["padx"], scaling_factor
            )

        if "pady" in scaled_kwargs:
            scaled_kwargs["pady"] = self._scale_padding_value(
                scaled_kwargs["pady"], scaling_factor
            )

        return scaled_kwargs

    def _scale_padding_value(self, value, scaling_factor):
        """Scale a single padding value."""
        if isinstance(value, (int, float)):
            if 0 <= abs(value) <= 50:
                return int(value * scaling_factor)
        elif isinstance(value, (list, tuple)) and len(value) == 2:
            if all(0 <= abs(val) <= 50 for val in value):
                return (
                    int(value[0] * scaling_factor),
                    int(value[1] * scaling_factor),
                )
        return value

    def _patch_widget_constructors(self, scaling_factor):
        """Patch widget constructors with scaling."""
        self._patch_label_frame_constructor(scaling_factor)
        self._patch_frame_constructor(scaling_factor)
        self._patch_button_constructor(scaling_factor)
        self._patch_entry_constructor(scaling_factor)
        self._patch_label_constructor(scaling_factor)
        self._patch_text_constructor(scaling_factor)
        self._patch_checkbutton_constructor(scaling_factor)
        self._patch_radiobutton_constructor(scaling_factor)
        self._patch_listbox_constructor(scaling_factor)
        self._patch_spinbox_constructor(scaling_factor)
        self._patch_scale_constructor(scaling_factor)
        self._patch_scrollbar_constructor(scaling_factor)
        self._patch_canvas_constructor(scaling_factor)
        self._patch_menu_constructor(scaling_factor)
        self._patch_menubutton_constructor(scaling_factor)

    def _patch_label_frame_constructor(self, scaling_factor):
        """Patch the LabelFrame constructor with scaling."""
        original_label_frame = tk.LabelFrame.__init__

        def scaled_label_frame_init(self, parent=None, **kwargs):
            scaled_kwargs = kwargs.copy()
            if "padx" in scaled_kwargs:
                scaled_kwargs["padx"] = int(scaled_kwargs["padx"] * scaling_factor)
                if (
                    isinstance(scaled_kwargs["padx"], (list, tuple))
                    and len(scaled_kwargs["padx"]) == 2
                ):
                    scaled_kwargs["padx"] = (
                        int(scaled_kwargs["padx"][0] * scaling_factor),
                        int(scaled_kwargs["padx"][1] * scaling_factor),
                    )
            if "pady" in scaled_kwargs:
                scaled_kwargs["pady"] = int(scaled_kwargs["pady"] * scaling_factor)
                if (
                    isinstance(scaled_kwargs["pady"], (list, tuple))
                    and len(scaled_kwargs["pady"]) == 2
                ):
                    scaled_kwargs["pady"] = (
                        int(scaled_kwargs["pady"][0] * scaling_factor),
                        int(scaled_kwargs["pady"][1] * scaling_factor),
                    )
            return original_label_frame(self, parent, **scaled_kwargs)

        tk.LabelFrame.__init__ = scaled_label_frame_init

    def _patch_frame_constructor(self, scaling_factor):
        """Patch the Frame constructor with scaling."""
        original_frame = tk.Frame.__init__

        def scaled_frame_init(self, parent=None, **kwargs):
            scaled_kwargs = kwargs.copy()
            if "padx" in scaled_kwargs:
                scaled_kwargs["padx"] = int(scaled_kwargs["padx"] * scaling_factor)
                if (
                    isinstance(scaled_kwargs["padx"], (list, tuple))
                    and len(scaled_kwargs["padx"]) == 2
                ):
                    scaled_kwargs["padx"] = (
                        int(scaled_kwargs["padx"][0] * scaling_factor),
                        int(scaled_kwargs["padx"][1] * scaling_factor),
                    )
            if "pady" in scaled_kwargs:
                scaled_kwargs["pady"] = int(scaled_kwargs["pady"] * scaling_factor)
                if (
                    isinstance(scaled_kwargs["pady"], (list, tuple))
                    and len(scaled_kwargs["pady"]) == 2
                ):
                    scaled_kwargs["pady"] = (
                        int(scaled_kwargs["pady"][0] * scaling_factor),
                        int(scaled_kwargs["pady"][1] * scaling_factor),
                    )
            return original_frame(self, parent, **scaled_kwargs)

        tk.Frame.__init__ = scaled_frame_init

    def _patch_button_constructor(self, scaling_factor):
        """Patch the Button constructor with scaling."""
        original_button = tk.Button.__init__

        def scaled_button_init(self, parent=None, **kwargs):
            scaled_kwargs = kwargs.copy()
            if "bd" in scaled_kwargs:
                scaled_kwargs["bd"] = int(scaled_kwargs["bd"] * scaling_factor)
            return original_button(self, parent, **scaled_kwargs)

        tk.Button.__init__ = scaled_button_init

    def _patch_entry_constructor(self, scaling_factor):
        """Patch the Entry constructor with scaling."""
        original_entry = tk.Entry.__init__

        def scaled_entry_init(self, parent=None, **kwargs):
            scaled_kwargs = kwargs.copy()
            if "bd" in scaled_kwargs:
                scaled_kwargs["bd"] = int(scaled_kwargs["bd"] * scaling_factor)
            return original_entry(self, parent, **scaled_kwargs)

        tk.Entry.__init__ = scaled_entry_init

    def _patch_label_constructor(self, scaling_factor):
        """Patch the Label constructor with scaling."""
        original_label = tk.Label.__init__

        def scaled_label_init(self, parent=None, **kwargs):
            scaled_kwargs = kwargs.copy()
            if "bd" in scaled_kwargs:
                scaled_kwargs["bd"] = int(scaled_kwargs["bd"] * scaling_factor)
            if "wraplength" in scaled_kwargs:
                scaled_kwargs["wraplength"] = int(
                    scaled_kwargs["wraplength"] * scaling_factor
                )
            return original_label(self, parent, **scaled_kwargs)

        tk.Label.__init__ = scaled_label_init

    def _patch_text_constructor(self, scaling_factor):
        """Patch the Text constructor with scaling."""
        original_text = tk.Text.__init__

        def scaled_text_init(self, parent=None, **kwargs):
            scaled_kwargs = kwargs.copy()
            if "bd" in scaled_kwargs:
                scaled_kwargs["bd"] = int(scaled_kwargs["bd"] * scaling_factor)
            return original_text(self, parent, **scaled_kwargs)

        tk.Text.__init__ = scaled_text_init

    def _patch_checkbutton_constructor(self, scaling_factor):
        """Patch the Checkbutton constructor with scaling."""
        original_checkbutton = tk.Checkbutton.__init__

        def scaled_checkbutton_init(self, parent=None, **kwargs):
            scaled_kwargs = kwargs.copy()
            if "bd" in scaled_kwargs:
                scaled_kwargs["bd"] = int(scaled_kwargs["bd"] * scaling_factor)
            return original_checkbutton(self, parent, **scaled_kwargs)

        tk.Checkbutton.__init__ = scaled_checkbutton_init

    def _patch_radiobutton_constructor(self, scaling_factor):
        """Patch the Radiobutton constructor with scaling."""
        original_radiobutton = tk.Radiobutton.__init__

        def scaled_radiobutton_init(self, parent=None, **kwargs):
            scaled_kwargs = kwargs.copy()
            if "bd" in scaled_kwargs:
                scaled_kwargs["bd"] = int(scaled_kwargs["bd"] * scaling_factor)
            return original_radiobutton(self, parent, **scaled_kwargs)

        tk.Radiobutton.__init__ = scaled_radiobutton_init

    def _patch_listbox_constructor(self, scaling_factor):
        """Patch the Listbox constructor with scaling."""
        original_listbox = tk.Listbox.__init__

        def scaled_listbox_init(self, parent=None, **kwargs):
            scaled_kwargs = kwargs.copy()
            if "bd" in scaled_kwargs:
                scaled_kwargs["bd"] = int(scaled_kwargs["bd"] * scaling_factor)
            return original_listbox(self, parent, **scaled_kwargs)

        tk.Listbox.__init__ = scaled_listbox_init

    def _patch_spinbox_constructor(self, scaling_factor):
        """Patch the Spinbox constructor with scaling."""
        original_spinbox = tk.Spinbox.__init__

        def scaled_spinbox_init(self, parent=None, **kwargs):
            scaled_kwargs = kwargs.copy()
            if "bd" in scaled_kwargs:
                scaled_kwargs["bd"] = int(scaled_kwargs["bd"] * scaling_factor)
            return original_spinbox(self, parent, **scaled_kwargs)

        tk.Spinbox.__init__ = scaled_spinbox_init

    def _patch_scale_constructor(self, scaling_factor):
        """Patch the Scale constructor with scaling."""
        original_scale = tk.Scale.__init__

        def scaled_scale_init(self, parent=None, **kwargs):
            scaled_kwargs = kwargs.copy()
            if "bd" in scaled_kwargs:
                scaled_kwargs["bd"] = int(scaled_kwargs["bd"] * scaling_factor)
            return original_scale(self, parent, **scaled_kwargs)

        tk.Scale.__init__ = scaled_scale_init

    def _patch_scrollbar_constructor(self, scaling_factor):
        """Patch the Scrollbar constructor with scaling."""
        original_scrollbar = tk.Scrollbar.__init__

        def scaled_scrollbar_init(self, parent=None, **kwargs):
            scaled_kwargs = kwargs.copy()
            if "bd" in scaled_kwargs:
                scaled_kwargs["bd"] = int(scaled_kwargs["bd"] * scaling_factor)
            return original_scrollbar(self, parent, **scaled_kwargs)

        tk.Scrollbar.__init__ = scaled_scrollbar_init

    def _patch_canvas_constructor(self, scaling_factor):
        """Patch the Canvas constructor with scaling."""
        original_canvas = tk.Canvas.__init__

        def scaled_canvas_init(self, parent=None, **kwargs):
            scaled_kwargs = kwargs.copy()
            if "width" in scaled_kwargs:
                scaled_kwargs["width"] = int(scaled_kwargs["width"] * scaling_factor)
            if "height" in scaled_kwargs:
                scaled_kwargs["height"] = int(scaled_kwargs["height"] * scaling_factor)
            if "bd" in scaled_kwargs:
                scaled_kwargs["bd"] = int(scaled_kwargs["bd"] * scaling_factor)
            return original_canvas(self, parent, **scaled_kwargs)

        tk.Canvas.__init__ = scaled_canvas_init

    def _patch_menu_constructor(self, scaling_factor):
        """Patch the Menu constructor with scaling."""
        original_menu = tk.Menu.__init__

        def scaled_menu_init(self, parent=None, **kwargs):
            scaled_kwargs = kwargs.copy()
            if "bd" in scaled_kwargs:
                scaled_kwargs["bd"] = int(scaled_kwargs["bd"] * scaling_factor)
            return original_menu(self, parent, **scaled_kwargs)

        tk.Menu.__init__ = scaled_menu_init

    def _patch_menubutton_constructor(self, scaling_factor):
        """Patch the Menubutton constructor with scaling."""
        original_menubutton = tk.Menubutton.__init__

        def scaled_menubutton_init(self, parent=None, **kwargs):
            scaled_kwargs = kwargs.copy()
            if "bd" in scaled_kwargs:
                scaled_kwargs["bd"] = int(scaled_kwargs["bd"] * scaling_factor)
            return original_menubutton(self, parent, **scaled_kwargs)

        tk.Menubutton.__init__ = scaled_menubutton_init

    def fix_dpi(self, root):
        """Adjust scaling for high DPI displays on Windows."""
        if not is_windows():
            root.DPI_X, root.DPI_Y, root.DPI_scaling = self._get_hwnd_dpi(
                root.winfo_id()
            )
            return

        try:
            dpi_awareness_result = self._enable_dpi_awareness()
            if dpi_awareness_result["shcore"]:
                self._apply_shcore_dpi_scaling(root)
            else:
                root.DPI_X, root.DPI_Y, root.DPI_scaling = self._get_hwnd_dpi(
                    root.winfo_id()
                )
        except Exception as e:  # pylint: disable=W0718
            self.logger.warning("Failed to fix DPI: %s, using fallback", e)
            root.DPI_X, root.DPI_Y, root.DPI_scaling = self._get_hwnd_dpi(
                root.winfo_id()
            )

        self._fix_scaling(root)

    def _enable_dpi_awareness(self):
        """Enable DPI awareness and return the method used."""
        try:
            ctypes.windll.shcore.SetProcessDpiAwareness(2)
            scale_factor = ctypes.windll.shcore.GetScaleFactorForDevice(0)
            return {"shcore": True, "scale_factor": scale_factor}
        except Exception as e:  # pylint: disable=W0718
            self.logger.debug("Failed to set process DPI awareness (shcore): %s", e)
            try:
                ctypes.windll.user32.SetProcessDPIAware()
                return {"shcore": False, "scale_factor": None}
            except Exception as e2:  # pylint: disable=W0718
                self.logger.debug(
                    "Failed to set process DPI awareness (user32): %s", e2
                )
                raise

    def _apply_shcore_dpi_scaling(self, root):
        """Apply DPI scaling using shcore method."""
        # Get initial scale factor
        scale_factor = ctypes.windll.shcore.GetScaleFactorForDevice(0)

        # Apply initial Tk scaling
        tk_scaling = (scale_factor / 100) * (96 / 72)
        root.tk.call("tk", "scaling", tk_scaling)

        # Adjust scaling based on Windows scale factor
        self._adjust_tk_scaling(root, tk_scaling)

        # Get DPI information
        self._set_dpi_information(root)

    def _adjust_tk_scaling(
        self, root, initial_tk_scaling
    ):  # pylint: disable=unused-argument
        """Adjust Tk scaling based on Windows scale factor."""
        try:
            windows_scale_factor = ctypes.windll.shcore.GetScaleFactorForDevice(0)
            windows_scale = windows_scale_factor / 100.0
            if windows_scale > (windows_scale_factor / 100):
                tk_scaling = windows_scale * (96 / 72)
                root.tk.call("tk", "scaling", tk_scaling)
                self.logger.info(
                    "DPI: Adjusted Tk scaling to %s based on Windows scale %s",
                    tk_scaling,
                    windows_scale,
                )
        except Exception as e:  # pylint: disable=W0718
            self.logger.debug(
                "Failed to get Windows scale factor for verification: %s", e
            )

    def _set_dpi_information(self, root):
        """Set DPI information on the root window."""
        win_handle = wintypes.HWND(root.winfo_id())
        monitor_handle = ctypes.windll.user32.MonitorFromWindow(win_handle, 2)
        x_dpi = wintypes.UINT()
        y_dpi = wintypes.UINT()

        ctypes.windll.shcore.GetDpiForMonitor(
            monitor_handle, 0, pointer(x_dpi), pointer(y_dpi)
        )

        root.DPI_X = x_dpi.value
        root.DPI_Y = y_dpi.value
        dpi_scaling = (x_dpi.value + y_dpi.value) / (2 * 96)

        # Use Windows scale factor if available and higher
        try:
            windows_scale_factor = ctypes.windll.shcore.GetScaleFactorForDevice(0)
            windows_scale = windows_scale_factor / 100.0
            if windows_scale > dpi_scaling:
                root.DPI_scaling = windows_scale
                self.logger.info(
                    "DPI: Using Windows scale %s instead of DPI-based %s",
                    windows_scale,
                    dpi_scaling,
                )
            else:
                root.DPI_scaling = dpi_scaling
        except Exception as e:  # pylint: disable=W0718
            self.logger.debug(
                "Failed to get Windows scale factor for DPI scaling: %s", e
            )
            root.DPI_scaling = dpi_scaling

    def apply_dpi(self, root, *, enable=True):
        """Enable DPI awareness and apply scaling to a Tkinter root window."""
        result = self._create_initial_result(enable)

        if not self._should_apply_dpi(enable, root):
            return result

        try:
            self._apply_dpi_to_root(root, result)
        except Exception as e:  # pylint: disable=W0718
            result["error"] = str(e)

        return result

    def _create_initial_result(self, enable):
        """Create initial result dictionary."""
        return {
            "enabled": enable,
            "platform": "windows" if is_windows() else "non-windows",
            "dpi_awareness_set": False,
            "effective_dpi": 96,
            "scaling_factor": 1.0,
            "tk_scaling": 1.0,
            "hwnd": None,
            "applied_to_windows": [],
        }

    def _should_apply_dpi(self, enable, root):
        """Check if DPI should be applied."""
        return enable and is_windows() and root is not None

    def _apply_dpi_to_root(self, root, result):
        """Apply DPI settings to the root window."""
        self.fix_dpi(root)

        # Update result with DPI information
        self._update_result_with_dpi_info(root, result)

        # Apply scaling methods
        self._apply_scaling_methods(root)

        # Update tasks and finalize
        root.update_idletasks()
        result["applied_to_windows"].append(result["hwnd"])

    def _update_result_with_dpi_info(self, root, result):
        """Update result dictionary with DPI information."""
        result["dpi_awareness_set"] = True
        result["effective_dpi"] = (root.DPI_X + root.DPI_Y) / 2
        result["scaling_factor"] = root.DPI_scaling
        result["hwnd"] = root.winfo_id()
        result["tk_scaling"] = float(root.tk.call("tk", "scaling"))

    def _apply_scaling_methods(self, root):
        """Apply scaling methods to the root window."""
        # Add TkScale method
        root.TkScale = lambda v: int(float(v) * root.DPI_scaling)

        # Override geometry method
        self._override_geometry_method(root)

        # Patch widget methods
        self._patch_widget_methods(root)

    def _override_geometry_method(self, root):
        """Override the geometry method with scaling."""
        original_geometry = root.wm_geometry

        def scaled_geometry(geometry_string=None):
            if geometry_string is None:
                return original_geometry()
            scaled = self._scale_geometry_string(geometry_string, root.TkScale)
            return original_geometry(scaled)

        root.geometry = scaled_geometry

    def enable_dpi_awareness(self):
        """Enable DPI awareness for the current process."""
        if not is_windows():
            return False
        try:
            try:
                ctypes.windll.shcore.SetProcessDpiAwareness(2)
                return True
            except (AttributeError, OSError):
                pass
            try:
                ctypes.windll.user32.SetProcessDPIAware()
                return True
            except (AttributeError, OSError):
                pass
        except Exception as e:  # pylint: disable=W0718
            self.logger.debug("Failed to enable DPI awareness: %s", e)
        return False

    def get_scaling_factor(self, root):
        """Get DPI scaling factor for a root window."""
        if not is_windows() or root is None:
            return 1.0
        try:
            if hasattr(root, "DPI_scaling"):
                return root.DPI_scaling
            _, _, scaling_factor = self._get_hwnd_dpi(root.winfo_id())
            return scaling_factor
        except Exception as e:  # pylint: disable=W0718
            self.logger.debug("Failed to get scaling factor: %s", e)
            return 1.0

    def get_effective_dpi(self, root):
        """Get effective DPI for a root window."""
        if not is_windows() or root is None:
            return 96
        try:
            if hasattr(root, "DPI_X") and hasattr(root, "DPI_Y"):
                return (root.DPI_X + root.DPI_Y) / 2
            dpi_x, dpi_y, _ = self._get_hwnd_dpi(root.winfo_id())
            return (dpi_x + dpi_y) / 2
        except Exception as e:  # pylint: disable=W0718
            self.logger.debug("Failed to get effective DPI: %s", e)
            return 96

    def logical_to_physical(self, value, *, root=None, scaling_factor=None):
        """Convert logical pixel value to physical pixels."""
        if not is_windows() or not isinstance(value, (int, float)):
            return value
        try:
            if scaling_factor is None:
                if root is None:
                    return value
                if hasattr(root, "DPI_scaling"):
                    scaling_factor = root.DPI_scaling
                else:
                    _, _, scaling_factor = self._get_hwnd_dpi(root.winfo_id())
            return type(value)(round(float(value) * float(scaling_factor)))
        except Exception as e:  # pylint: disable=W0718
            self.logger.debug("Failed to convert logical to physical pixels: %s", e)
            return value

    def physical_to_logical(self, value, *, root=None, scaling_factor=None):
        """Convert physical pixel value to logical pixels."""
        if not is_windows() or not isinstance(value, (int, float)):
            return value
        try:
            if scaling_factor is None:
                if root is None:
                    return value
                if hasattr(root, "DPI_scaling"):
                    scaling_factor = root.DPI_scaling
                else:
                    _, _, scaling_factor = self._get_hwnd_dpi(root.winfo_id())
            if scaling_factor == 0:
                return value
            return type(value)(round(float(value) / float(scaling_factor)))
        except Exception as e:  # pylint: disable=W0718
            self.logger.debug("Failed to convert physical to logical pixels: %s", e)
            return value

    def scale_font_size(self, original_size, root=None, *, scaling_factor=None):
        """Scale a font size based on DPI scaling factor."""
        if not is_windows():
            return original_size
        try:
            if scaling_factor is None:
                if root is None:
                    return original_size
                try:
                    scaling_factor = float(root.tk.call("tk", "scaling"))
                except Exception as e:  # pylint: disable=W0718
                    self.logger.debug("Failed to get tk scaling for font: %s", e)
                    if hasattr(root, "DPI_scaling"):
                        scaling_factor = root.DPI_scaling
                    else:
                        _, _, scaling_factor = self._get_hwnd_dpi(root.winfo_id())
            if original_size < 0:
                return round(original_size * scaling_factor)
            return round(original_size * scaling_factor)
        except Exception as e:  # pylint: disable=W0718
            self.logger.debug("Failed to scale font size: %s", e)
            return original_size

    def get_actual_window_size(self, root):
        """Get actual window size information."""
        if not is_windows() or root is None:
            return {
                "platform": ("non-windows" if not is_windows() else "no-root"),
                "logical_size": None,
                "physical_size": None,
            }
        try:
            geometry = root.geometry()
            match = re.match(r"(\d+)x(\d+)", geometry)
            logical_width = int(match.group(1)) if match else None
            logical_height = int(match.group(2)) if match else None
            if hasattr(root, "DPI_scaling"):
                scaling_factor = root.DPI_scaling
            else:
                _, _, scaling_factor = self._get_hwnd_dpi(root.winfo_id())
            physical_width = (
                int(logical_width * scaling_factor) if logical_width else None
            )
            physical_height = (
                int(logical_height * scaling_factor) if logical_height else None
            )
            return {
                "hwnd": root.winfo_id(),
                "logical_size": {
                    "width": logical_width,
                    "height": logical_height,
                    "geometry": geometry,
                },
                "physical_size": {
                    "width": physical_width,
                    "height": physical_height,
                },
                "scaling_factor": scaling_factor,
            }
        except Exception as e:  # pylint: disable=W0718
            return {
                "error": f"Failed to get window size: {str(e)}",
                "logical_size": None,
                "physical_size": None,
            }

    def calculate_dpi_sizes(self, base_sizes, root=None, max_scale=None):
        """Calculate DPI-aware sizes for various UI elements."""
        if not is_windows() or not isinstance(base_sizes, dict):
            return base_sizes
        try:
            if root and hasattr(root, "DPI_scaling"):
                scaling_factor = root.DPI_scaling
            elif root:
                _, _, scaling_factor = self._get_hwnd_dpi(root.winfo_id())
            else:
                scaling_factor = 1.0
            if max_scale and scaling_factor > max_scale:
                scaling_factor = max_scale
            return {
                key: int(value * scaling_factor) for key, value in base_sizes.items()
            }
        except Exception as e:  # pylint: disable=W0718
            logger = logging.getLogger(__name__)
            logger.debug("Failed to calculate DPI sizes: %s", e)
            return base_sizes


_dpi_manager = DPIManager()


def dpi(root, *, enable=True):
    """Backward compatibility function for dpi()."""
    return _dpi_manager.apply_dpi(root, enable=enable)


def enable_dpi_awareness():
    """Backward compatibility function for enable_dpi_awareness()."""
    return _dpi_manager.enable_dpi_awareness()


def enable_dpi_geometry(root):
    """Enable DPI-aware geometry for backward compatibility."""
    return dpi(root)


def get_scaling_factor(root):
    """Backward compatibility function for get_scaling_factor()."""
    return _dpi_manager.get_scaling_factor(root)


def get_effective_dpi(root):
    """Backward compatibility function for get_effective_dpi()."""
    return _dpi_manager.get_effective_dpi(root)


def logical_to_physical(value, *, root=None, scaling_factor=None):
    """Backward compatibility function for logical_to_physical()."""
    return _dpi_manager.logical_to_physical(
        value, root=root, scaling_factor=scaling_factor
    )


def physical_to_logical(value, *, root=None, scaling_factor=None):
    """Backward compatibility function for physical_to_logical()."""
    return _dpi_manager.physical_to_logical(
        value, root=root, scaling_factor=scaling_factor
    )


def scale_font_size(original_size, root=None, *, scaling_factor=None):
    """Backward compatibility function for scale_font_size()."""
    return _dpi_manager.scale_font_size(
        original_size, root=root, scaling_factor=scaling_factor
    )


def get_actual_window_size(root):
    """Backward compatibility function for get_actual_window_size()."""
    return _dpi_manager.get_actual_window_size(root)


def calculate_dpi_sizes(base_sizes, root=None, max_scale=None):
    """Backward compatibility function for calculate_dpi_sizes()."""
    return _dpi_manager.calculate_dpi_sizes(base_sizes, root=root, max_scale=max_scale)


def scale_icon(  # pylint: disable=unused-argument
    icon_name, parent, base_size=24, max_scale=3.0
):
    """Create a scaled version of a Tkinter icon for DPI-aware sizing."""
    if not is_windows():
        return icon_name
    try:
        scaling = get_scaling_factor(parent)
        if scaling > 1.0:
            icon_mapping = {
                "error": "::tk::icons::error",
                "info": "::tk::icons::information",
                "warning": "::tk::icons::warning",
                "question": "::tk::icons::question",
            }
            original_icon = icon_mapping.get(icon_name, f"::tk::icons::{icon_name}")
            scaled_icon = f"scaled_{icon_name}_large"
            if scaling >= 1.25:
                scale_factor = min(scaling, max_scale)
            else:
                scale_factor = 1.0
            parent.tk.call("image", "create", "photo", scaled_icon)
            parent.tk.call(
                scaled_icon,
                "copy",
                original_icon,
                "-zoom",
                int(scale_factor),
                int(scale_factor),
            )
            return scaled_icon
    except Exception as e:  # pylint: disable=W0718
        logger = logging.getLogger(__name__)
        logger.debug("Failed to scale icon %s: %s", icon_name, e)
    return icon_name


def enable_auto_dpi_scaling(  # pylint: disable=unused-argument
    root, *, interval_ms=500, adjust_fonts=True
):
    """Placeholder for auto DPI scaling (not implemented in simplified version)."""
    return False


def disable_auto_dpi_scaling(root):  # pylint: disable=unused-argument
    """Placeholder for disabling auto DPI scaling."""
    return False


def is_auto_dpi_scaling_enabled(root):  # pylint: disable=unused-argument
    """Placeholder for checking auto DPI scaling status."""
    return False


def scale_widget_dimensions(  # pylint: disable=unused-argument
    widget, root=None, *, scaling_factor=None, exclude_properties=None
):
    """Placeholder for widget dimension scaling (not implemented)."""
    return {
        "scaled_properties": [],
        "errors": ["Not implemented in simplified version"],
    }


def scale_widget_tree(  # pylint: disable=unused-argument
    root_widget, *, scaling_factor=None, exclude_properties=None, widget_filter=None
):
    """Placeholder for widget tree scaling (not implemented in simplified version)."""
    return {
        "total_widgets": 0,
        "scaled_widgets": 0,
        "widget_results": [],
        "errors": ["Not implemented in simplified version"],
    }


def get_scalable_properties():
    """Placeholder for getting scalable properties."""
    return set()


def add_scalable_property(property_name):  # pylint: disable=unused-argument
    """Placeholder for adding scalable property."""


def remove_scalable_property(property_name):  # pylint: disable=unused-argument
    """Placeholder for removing scalable property."""
