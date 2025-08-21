import ctypes
import sys
from typing import Literal, Union


def is_windows():
    """Check if running on Windows platform."""
    return sys.platform == "win32"


# Windows MessageBeep sound types
MB_ICONASTERISK = 0x00000040  # Information sound
MB_ICONEXCLAMATION = 0x00000030  # Warning sound
MB_ICONHAND = 0x00000010  # Error sound
MB_ICONQUESTION = 0x00000020  # Question sound
MB_OK = 0x00000000  # Default sound
# Type definitions for better type checking
SoundType = Literal["error", "warning", "info", "question", "default"]


def bell(sound_type: Union[str, SoundType] = "default") -> bool:
    """
    Play a Windows system sound based on the type.
    Args:
        sound_type: Type of sound to play
            - "error": Error sound (MB_ICONHAND)
            - "warning": Warning sound (MB_ICONEXCLAMATION)
            - "info": Information sound (MB_ICONASTERISK)
            - "question": Question sound (MB_ICONQUESTION)
            - "default": Default sound (MB_OK)
    Returns:
        bool: True if sound was played successfully, False otherwise
    Note:
        This function only works on Windows platforms. On other platforms,
        it returns False without playing any sound.
    """
    if not is_windows():
        return False
    try:
        # Map sound types to Windows constants
        sound_map = {
            "error": MB_ICONHAND,
            "warning": MB_ICONEXCLAMATION,
            "info": MB_ICONASTERISK,
            "question": MB_ICONQUESTION,
            "default": MB_OK,
        }
        # Get the Windows constant for the sound type
        win_sound = sound_map.get(sound_type.lower(), MB_OK)
        # Call Windows MessageBeep API
        result = ctypes.windll.user32.MessageBeep(win_sound)
        return result != 0
    except (AttributeError, OSError):
        # Handle cases where windll is not available or MessageBeep fails
        try:
            ctypes.windll.user32.MessageBeep(MB_OK)
            return True
        except (AttributeError, OSError):
            return False
