import configparser
import os

import habits_txt.defaults as defaults


def setup():
    if not os.path.exists(defaults.APPDATA_PATH):
        os.makedirs(defaults.APPDATA_PATH)

    config_path = os.path.join(defaults.APPDATA_PATH, "config.ini")
    if not os.path.exists(config_path):
        sections = [
            "CLI",
        ]
        with open(config_path, "w") as f:
            f.write("\n".join([f"[{section}]\n" for section in sections]))


def validate():
    config_path = os.path.join(defaults.APPDATA_PATH, "config.ini")
    config = configparser.ConfigParser()
    config.read(config_path)
    sections = ["CLI"]
    for section in sections:
        if section not in config.sections():
            raise ValueError(f"Section {section} not found in config.ini")
        for key in config[section]:
            if not config[section][key]:
                raise ValueError(f"Key {key} in section {section} is empty")
    return True


def set(key, value, section):
    config_path = os.path.join(defaults.APPDATA_PATH, "config.ini")
    config = configparser.ConfigParser()
    config.read(config_path)
    config[section][key] = value
    with open(config_path, "w") as f:
        config.write(f)


def get(key, section):
    config_path = os.path.join(defaults.APPDATA_PATH, "config.ini")
    config = configparser.ConfigParser()
    config.read(config_path)
    try:
        return config[section][key]
    except KeyError:
        return None


def delete(key, section):
    config_path = os.path.join(defaults.APPDATA_PATH, "config.ini")
    config = configparser.ConfigParser()
    config.read(config_path)
    del config[section][key]
    with open(config_path, "w") as f:
        config.write(f)


def get_all():
    config_path = os.path.join(defaults.APPDATA_PATH, "config.ini")
    config = configparser.ConfigParser()
    config.read(config_path)
    return {section: dict(config[section]) for section in config.sections()}


def get_section(section):
    config_path = os.path.join(defaults.APPDATA_PATH, "config.ini")
    config = configparser.ConfigParser()
    config.read(config_path)
    return dict(config[section])
