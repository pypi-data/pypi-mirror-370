from .lang import LanguageManager

_lang_instance = LanguageManager()
set = _lang_instance.set  # pylint: disable=redefined-builtin
get = _lang_instance.get
register = _lang_instance.register
available = _lang_instance.available
load_msg = _lang_instance.load_msg
clear = _lang_instance.clear
current = _lang_instance.current
get_dict = _lang_instance.get_dict
mc = _lang_instance.get  # alias
