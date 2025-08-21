# Tkface
[![License: MIT](https://img.shields.io/pypi/l/tkface)](https://opensource.org/licenses/MIT)
[![PyPI - Python Version](https://img.shields.io/pypi/pyversions/tkface)](https://pypi.org/project/tkface)
[![GitHub Release](https://img.shields.io/github/release/mashu3/tkface?color=orange)](https://github.com/mashu3/tkface/releases)
[![PyPi Version](https://img.shields.io/pypi/v/tkface?color=yellow)](https://pypi.org/project/tkface/)
[![Downloads](https://static.pepy.tech/badge/tkface)](https://pepy.tech/project/tkface)

**Restore the "face" to your Tkinter!**

A multilingual GUI extension library for Tkinter (tkinter) - bringing back the "face" (interface) that Tkinter left behind. **Built with zero external dependencies, using only Python's standard library.**

---

## 📖 Overview

Tkface is a Python library designed to restore and enhance the "face" (user interface) of Tkinter. While Tkinter is a powerful toolkit, its dialogs and user-facing components are minimal and lack friendly interfaces. Tkface fills this gap with multilingual dialogs, advanced message boxes, and Windows-specific features. **The library is built entirely with Python's standard library, requiring no external dependencies.**

- **Completing the Interface**: Tkinter stands for "Tk **inter**face," providing a powerful core for building GUIs. Tk**face** is designed to complement it by providing the user-facing components—the "**face**"—that are essential for a polished user experience but not built into the standard library. It extends Tkinter with ready-to-use, multilingual dialogs and widgets, letting you build sophisticated, user-friendly applications with less effort.
- **Vibe Coding**: Developed with a "Vibe Coding" approach-prioritizing developer joy, rapid prototyping, and a sense of fun. The codebase is hackable, readable, and easy to extend—and so is this document.

---

## 🔧 Requirements

- Python 3.7+
- Tkinter (included with Python)
- **Zero external dependencies** - Uses only Python standard library

---

## 📦 Installation

Install the latest version from PyPI:

```bash
pip install tkface
```

Or install from the GitHub repository for the latest changes:

```bash
pip install git+https://github.com/mashu3/tkface.git
```

---

## 🚀 Usage

### Message Boxes

```python
import tkface

# Simple information dialog
tkface.messagebox.showinfo("Operation completed successfully!")

# Multilingual support
tkface.messagebox.showerror("An error has occurred!", language="ja")

# With system sound (Windows only)
tkface.messagebox.showerror("An error has occurred!", bell=True)

# Confirmation dialog
if tkface.messagebox.askyesno("Do you want to save?"):
    # Handle save operation
    tkface.messagebox.showinfo("File saved successfully!")
```

### Screenshots

| Dialog Type | Windows | macOS |
|-------------|---------|-------|
| **Warning** | <img src="https://raw.githubusercontent.com/mashu3/tkface/main/examples/images/tkface_messagebox_warning_windows.png" width="200px" alt="Warning Dialog"> | <img src="https://raw.githubusercontent.com/mashu3/tkface/main/examples/images/tkface_messagebox_warning_mac.png" width="200px" alt="Warning Dialog"> |
| **Error** | <img src="https://raw.githubusercontent.com/mashu3/tkface/main/examples/images/tkface_messagebox_error_windows.png" width="200px" alt="Error Dialog"> | <img src="https://raw.githubusercontent.com/mashu3/tkface/main/examples/images/tkface_messagebox_error_mac.png" width="200px" alt="Error Dialog"> |
| **Information** | <img src="https://raw.githubusercontent.com/mashu3/tkface/main/examples/images/tkface_messagebox_info_windows.png" width="200px" alt="Info Dialog"> | <img src="https://raw.githubusercontent.com/mashu3/tkface/main/examples/images/tkface_messagebox_info_mac.png" width="200px" alt="Info Dialog"> |
| **Question** | <img src="https://raw.githubusercontent.com/mashu3/tkface/main/examples/images/tkface_messagebox_question_windows.png" width="200px" alt="Question Dialog"> | <img src="https://raw.githubusercontent.com/mashu3/tkface/main/examples/images/tkface_messagebox_question_mac.png" width="200px" alt="Question Dialog"> |

### Input Dialogs

```python
import tkface

# String input
name = tkface.simpledialog.askstring("Enter your name:")

# Integer input with validation
age = tkface.simpledialog.askinteger("Enter your age:", minvalue=0, maxvalue=120)

# List selection dialog
color = tkface.simpledialog.askfromlistbox("Choose a color:", choices=["Red", "Green", "Blue"])

# Multiple selection dialog
colors = tkface.simpledialog.askfromlistbox("Choose colors:", choices=["Red", "Green", "Blue"], multiple=True)
```

### DatePicker Widgets

#### Screenshots

| Widget Type | Windows | macOS |
|-------------|---------|-------|
| **DateFrame** | <img src="https://raw.githubusercontent.com/mashu3/tkface/main/examples/images/tkface_calendar_dateframe_windows.png" width="200px" alt="DateFrame Widget"> | <img src="https://raw.githubusercontent.com/mashu3/tkface/main/examples/images/tkface_calendar_dateframe_mac.png" width="200px" alt="DateFrame Widget"> |

#### Usage Examples

**Initial Date Behavior**: When no `year` and `month` parameters are specified, both `DateEntry` and `DateFrame` automatically use the current date as the initial value. You can also explicitly set the initial date using the `year` and `month` parameters.

**Navigation Features**: The calendar widgets include intuitive navigation features:
- Click on the year/month header to switch to year selection mode (3x4 month grid)
- Click on a month in year selection mode to switch to that month
- Use arrow buttons to navigate between months/years
- All navigation maintains the selected date and theme settings

```python
import tkinter as tk
import tkface

root = tk.Tk()
root.title("DateEntry Demo")

# Basic DateEntry (uses current date by default)
date_entry = tkface.DateEntry(root)
date_entry.pack(padx=10, pady=10)

# DateFrame with custom button text
date_frame = tkface.DateFrame(root, button_text="📅")
date_frame.pack(padx=10, pady=10)

# Advanced DateEntry with features
date_entry = tkface.DateEntry(
    root,
    show_week_numbers=True,      # Show week numbers
    week_start="Monday",         # Start week on Monday
    day_colors={                 # Color weekends
        "Sunday": "lightcoral",
        "Saturday": "lightblue"
    },
    holidays={                   # Highlight holidays
        "2025-08-15": "red",     # Custom holiday
        "2025-08-30": "blue"     # Another holiday
    },
    theme="light",               # Light theme
    language="ja"                # Japanese language
)

# DateEntry with specific initial date
date_entry_with_date = tkface.DateEntry(
    root,
    year=2025,                   # Set initial year
    month=8,                     # Set initial month
    date_format="%Y年%m月%d日"    # Japanese date format
)
date_entry_with_date.pack(padx=10, pady=10)

# Get selected date
selected_date = date_entry.get_date()
# Process the selected date as needed
if selected_date:
    # Handle the selected date
    pass

# Get selected date from specific date entry
selected_date_with_date = date_entry_with_date.get_date()

root.mainloop()
```

#### Key Parameters

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `year` | `int` | `None` (current year) | Initial year to display |
| `month` | `int` | `None` (current month) | Initial month to display |
| `date_format` | `str` | `"%Y-%m-%d"` | Date format string |
| `button_text` | `str` | `"📅"` | Button text (DateFrame only) |
| `theme` | `str` | `"light"` | Theme: "light" or "dark" |
| `language` | `str` | `"en"` | Language: "en" or "ja" |

#### DateFrame vs DateEntry

- **DateFrame**: Customizable button text, more flexible layout
- **DateEntry**: Combobox-style appearance, standard system look

### Windows-Specific Features

Tkface provides Windows-specific enhancements that automatically detect the platform and gracefully degrade on non-Windows systems. These features include DPI awareness, Windows 11 corner rounding control, and system sound integration.

#### DPI Awareness and Scaling

```python
import tkinter as tk
import tkface

root = tk.Tk()

# Enable DPI awareness and automatic scaling
tkface.win.dpi(root)  # Enable DPI awareness

# Window geometry is automatically adjusted for DPI
root.geometry("600x400")  # Will be scaled appropriately

# UI elements are automatically scaled
button = tkface.Button(root, text="Scaled Button")
button.pack()

root.mainloop()
```

#### Other Windows Features

```python
import tkinter as tk
import tkface

root = tk.Tk()
root.title("Windows Features Demo")

# Enable DPI awareness and automatic scaling
tkface.win.dpi(root)         # Enable DPI awareness (Windows only)

# Set window geometry
root.geometry("600x400")

# Create your widgets here
def on_button_click():
    tkface.messagebox.showinfo("Info", "Button clicked!")

button = tkface.Button(root, text="Flat Button", command=on_button_click)  # Flat styling on Windows
button.pack()

# Disable corner rounding (Windows 11 only) - call after all widgets are created
tkface.win.unround(root)     # Disable corner rounding (Windows 11 only)

# Play Windows system sound (Windows only)
tkface.win.bell("error")     # Play Windows system sound (Windows only)

root.mainloop()
```

**Important**: Call `tkface.win.unround(root)` after creating all widgets but before `mainloop()` to ensure the window is fully initialized.

> **Note**: All Windows-specific features gracefully degrade on non-Windows platforms.

### Language Management

```python
import tkface
import tkinter as tk

root = tk.Tk()
tkface.lang.set("ja", root)  # Set language manually
tkface.lang.set("auto", root)  # Auto-detect system language

# Register custom translations
custom_translations = {
    "ja": {
        "Choose an option:": "オプションを選択:",
        "Option 1": "オプション1",
        "Option 2": "オプション2", 
        "Option 3": "オプション3"
    }
}
tkface.simpledialog.askfromlistbox(
    "Choose an option:",
    choices=["Option 1", "Option 2", "Option 3"],
    custom_translations=custom_translations,
    language="ja"
)
```

---

## 🧩 Features

- **Zero Dependencies**: Built entirely with Python's standard library - no external packages required
- **Multilingual Support**: Automatic language detection, English/Japanese built-in, custom dictionaries
- **Enhanced Message Boxes**: All standard and advanced dialogs, custom positioning, keyboard shortcuts, tab navigation
- **Enhanced Input Dialogs**: String/integer/float input, validation, password input, list selection, custom positioning
- **Calendar Widget**: Multi-month display, week numbers, holiday highlighting, customizable colors, language support
- **Windows Features**: 
  - **DPI Awareness**: Automatic scaling for high-resolution displays
  - **Windows 11 Corner Rounding Control**: Modern UI appearance
  - **Windows System Sounds**: Platform-specific audio feedback
  - **Flat Button Styling**: Modern appearance without shadows
  - All features gracefully degrade on other OS

---

## 📁 Examples

See the `examples/` directory for complete working examples:

- `demo_messagebox.py` - Message box demonstrations
- `demo_simpledialog.py` - Input dialog demonstrations
- `demo_calendar.py` - Calendar widget demonstrations
- `demo_windows_features.py` - Windows-specific features demonstrations

> **Note**: Test files are not included in the public release. For testing, see the development repository.

---

## 🌐 Supported Languages

- **English (en)**: Default, comprehensive translations
- **Japanese (ja)**: Complete Japanese translations

You can add support for any language by providing translation dictionaries:

```python
custom_translations = {
    "fr": {
        "ok": "OK",
        "cancel": "Annuler",
        "yes": "Oui",
        "no": "Non",
        "Error": "Erreur",
        "Warning": "Avertissement"
    }
}
```

---

## 📝 License

This project is licensed under the MIT License. See the LICENSE file for details.

---

## 👨‍💻 Author
[mashu3](https://github.com/mashu3)

[![Authors](https://contrib.rocks/image?repo=mashu3/tkface)](https://github.com/mashu3/tkface/graphs/contributors)