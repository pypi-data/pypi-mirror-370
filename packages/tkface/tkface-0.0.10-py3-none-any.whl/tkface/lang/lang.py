# lang/lang.py
import logging
import os
import tkinter as tk
from tkinter import TclError


class LanguageManager:
    def __init__(self):
        self.user_dicts = {}
        self.current_lang = "en"
        self.msgcat_loaded = set()
        self.logger = logging.getLogger(__name__)

    def register(self, lang_code, dictionary, root):
        if lang_code not in self.user_dicts:
            self.user_dicts[lang_code] = {}
        self.user_dicts[lang_code].update(dictionary)
        for key, value in dictionary.items():
            root.tk.call("msgcat::mcset", lang_code, key, value)

    def _determine_language(self, lang_code, root):
        """Determine the actual language code, handling 'auto' case."""
        if lang_code == "auto":
            try:
                lang_code_full = root.tk.call("msgcat::mclocale").replace("-", "_")
                lang_code = lang_code_full
            except TclError as e:
                self.logger.warning(
                    "Could not determine locale: %s, using 'en' as fallback",
                    e,
                )
                lang_code = "en"
        return lang_code

    def _load_tk_msgcat(self, lang_code, root):
        """Load tk standard msgcat file if available."""
        try:
            tk_library = str(root.tk.globalgetvar("tk_library"))
            msg_path_full = os.path.join(tk_library, "msgs", f"{lang_code}.msg")
            msg_path_short = os.path.join(
                tk_library, "msgs", f'{lang_code.split("_")[0]}.msg'
            )
            loaded = False
            if os.path.exists(msg_path_full):
                root.tk.call("msgcat::mcload", msg_path_full)
                loaded = True
            elif os.path.exists(msg_path_short):
                root.tk.call("msgcat::mcload", msg_path_short)
                loaded = True
            if loaded:
                root.tk.call("msgcat::mclocale", lang_code)
                self.msgcat_loaded.add(lang_code)
        except TclError as e:
            self.logger.debug("Failed to load tk msgcat file for %s: %s", lang_code, e)

    def _parse_msg_file(self, file_path, lang_code, root):
        """Parse a .msg file and load translations."""
        if lang_code not in self.user_dicts:
            self.user_dicts[lang_code] = {}
        with open(file_path, encoding="utf-8") as f:
            for line in f:
                line = line.strip()
                if not line or line.startswith("#"):
                    continue
                if "{" in line and "}" in line:
                    key, val = line.split("{", 1)
                    key = key.strip()
                    val = val.rsplit("}", 1)[0].strip()
                    # Store in user_dicts
                    self.user_dicts[lang_code][key] = val
                    # Also set in msgcat
                    root.tk.call("msgcat::mcset", lang_code, key, val)

    def _load_custom_msgcat(self, lang_code, root):
        """Load custom msgcat files from locales directory."""
        try:
            assets_path_full = os.path.join(
                os.path.dirname(__file__),
                "..",
                "locales",
                f"{lang_code}.msg",
            )
            assets_path_short = os.path.join(
                os.path.dirname(__file__),
                "..",
                "locales",
                f'{lang_code.split("_")[0]}.msg',
            )
            if os.path.exists(assets_path_full):
                self._parse_msg_file(assets_path_full, lang_code, root)
                root.tk.call("msgcat::mclocale", lang_code)
                self.msgcat_loaded.add(lang_code)
            elif os.path.exists(assets_path_short):
                short_lang = lang_code.split("_")[0]
                self._parse_msg_file(assets_path_short, short_lang, root)
                root.tk.call("msgcat::mclocale", short_lang)
                self.msgcat_loaded.add(short_lang)
        except (TclError, OSError) as e:
            self.logger.warning(
                "Failed to load custom msgcat file for %s: %s",
                lang_code,
                e,
            )

    def _set_final_locale(self, lang_code, root):
        """Set the final locale for the language."""
        try:
            root.tk.call("msgcat::mclocale", lang_code)
        except TclError as e:
            self.logger.debug("Failed to set locale to %s: %s", lang_code, e)

    def set(self, lang_code, root):
        """Set the language for the application."""
        lang_code = self._determine_language(lang_code, root)
        self.current_lang = lang_code
        # Load tk standard msgcat file (optional, but keep for fallback)
        self._load_tk_msgcat(lang_code, root)
        # Load custom msgcat files
        self._load_custom_msgcat(lang_code, root)
        # Set final locale
        self._set_final_locale(lang_code, root)

    def get(self, key, root=None, language=None):
        if root is None:
            root = getattr(tk, "_default_root", None)
            if root is None:
                raise RuntimeError(
                    "No Tk root window found. Please create a Tk instance "
                    "or pass root explicitly."
                )
        lang_code = language or self.current_lang
        if lang_code in self.user_dicts and key in self.user_dicts[lang_code]:
            result = self.user_dicts[lang_code][key]
            return result
        try:
            orig_locale = root.tk.call("msgcat::mclocale")
            root.tk.call("msgcat::mclocale", lang_code)
            translated = root.tk.call("::msgcat::mc", key)
            root.tk.call("msgcat::mclocale", orig_locale)
            if translated != key:
                return translated
        except TclError as e:
            self.logger.debug(
                "Failed to get translation for '%s' in %s: %s",
                key,
                lang_code,
                e,
            )
            # Fallback to English or return key
        try:
            root.tk.call("msgcat::mclocale", "en")
            translated = root.tk.call("::msgcat::mc", key)
            if translated != key:
                return translated
        except TclError as e:
            self.logger.debug("Failed to get English translation for '%s': %s", key, e)
            # Return key as final fallback
        return key

    mc = get  # alias

    def available(self):
        """
        Return a sorted list of available language codes (user, msgcat, and
        'en').
        """
        langs = set()
        if self.user_dicts:
            langs.update(self.user_dicts.keys())
        if self.msgcat_loaded:
            langs.update(self.msgcat_loaded)
        langs.add("en")
        return sorted(langs)

    def load_msg(self, lang_code, msg_path, root):
        """
        Load a .msg file into msgcat for the specified language code.
        """
        try:
            root.tk.call("msgcat::mcload", os.path.abspath(msg_path))
            self.msgcat_loaded.add(lang_code)
        except TclError as e:
            self.logger.warning(
                "Failed to load msg file %s for %s: %s",
                msg_path,
                lang_code,
                e,
            )
            return False
        return True

    def clear(self, lang_code):
        """
        Remove the user dictionary for the specified language code.
        """
        if lang_code in self.user_dicts:
            del self.user_dicts[lang_code]

    def current(self):
        """
        Return the current language code in use.
        """
        return self.current_lang

    def get_dict(self, lang_code):
        """
        Return the user dictionary for the specified language code.
        """
        return self.user_dicts.get(lang_code, {})


__all__ = ["LanguageManager"]
