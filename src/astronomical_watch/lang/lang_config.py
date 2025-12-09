import os
import configparser

CONFIG_FILENAME = os.path.expanduser("~/.astronomical_watch_config.ini")
CONFIG_SECTION = "General"
CONFIG_KEY = "language"
DEFAULT_LANGUAGE = "English"

def save_language(lang_code):
    config = configparser.ConfigParser()
    config.read(CONFIG_FILENAME)
    if not config.has_section(CONFIG_SECTION):
        config.add_section(CONFIG_SECTION)
    config.set(CONFIG_SECTION, CONFIG_KEY, lang_code)
    with open(CONFIG_FILENAME, "w") as f:
        config.write(f)

def load_language():
    config = configparser.ConfigParser()
    config.read(CONFIG_FILENAME)
    if config.has_section(CONFIG_SECTION) and config.has_option(CONFIG_SECTION, CONFIG_KEY):
        return config.get(CONFIG_SECTION, CONFIG_KEY)
    return DEFAULT_LANGUAGE