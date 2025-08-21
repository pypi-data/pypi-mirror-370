"""Widget module for tkface."""

# Import DPI functions for scaling support
try:
    from ..win.dpi import get_scaling_factor, scale_font_size
except ImportError:
    # Fallback functions if DPI module is not available
    def get_scaling_factor(root):  # pylint: disable=unused-argument
        """Get DPI scaling factor for the given root window."""
        return 1.0

    def scale_font_size(  # pylint: disable=unused-argument
        original_size, root=None, scaling_factor=None
    ):
        """Scale font size based on DPI scaling factor."""
        return original_size


# Default popup dimensions
DEFAULT_POPUP_WIDTH = 235
DEFAULT_POPUP_HEIGHT = 175
WEEK_NUMBERS_WIDTH_OFFSET = 20

# Import classes lazily to avoid circular imports
# These will be imported when needed to avoid circular imports
__all__ = ["Calendar"]
