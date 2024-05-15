import unittest.mock as mock

import pytest

import habits_txt.config as config


def test_setup(monkeypatch):
    monkeypatch.setattr(config.os.path, "exists", lambda x: False)
    monkeypatch.setattr(config.os, "makedirs", mock.MagicMock())

    with mock.patch("builtins.open", mock.mock_open()) as m:
        config.setup()
        m.assert_called_once_with(config.defaults.APPDATA_PATH + "/config.ini", "w")
        m().write.assert_called_once_with("[CLI]\n")


def test_validate(monkeypatch):
    monkeypatch.setattr(config.configparser.ConfigParser, "sections", lambda x: ["CLI"])
    monkeypatch.setattr(
        config.configparser.ConfigParser, "__getitem__", lambda x, y: {"key": "value"}
    )
    config.validate()

    monkeypatch.setattr(
        config.configparser.ConfigParser, "__getitem__", lambda x, y: {"key": ""}
    )
    with pytest.raises(ValueError):
        config.validate()

    monkeypatch.setattr(
        config.configparser.ConfigParser, "sections", lambda x: ["INVALID"]
    )
    with pytest.raises(ValueError):
        config.validate()


def test_set(monkeypatch):
    with mock.patch("builtins.open", mock.mock_open()) as m:
        monkeypatch.setattr(
            config.configparser.ConfigParser, "__setitem__", mock.MagicMock()
        )
        monkeypatch.setattr(
            config.configparser.ConfigParser,
            "__getitem__",
            lambda x, y: {"key": "value"},
        )
        config.set("key", "value", "CLI")
        m.assert_called_with(config.defaults.APPDATA_PATH + "/config.ini", "w")


def test_get(monkeypatch):
    with mock.patch("builtins.open", mock.mock_open()) as m:
        monkeypatch.setattr(
            config.configparser.ConfigParser,
            "__getitem__",
            lambda x, y: {"key": "value"},
        )
        assert config.get("key", "CLI") == "value"
        m.assert_called_with(
            config.defaults.APPDATA_PATH + "/config.ini", encoding="locale"
        )

        monkeypatch.setattr(
            config.configparser.ConfigParser,
            "__getitem__",
            lambda x, y: {"unknown": ""},
        )
        assert config.get("key", "CLI") is None


def test_delete(monkeypatch):
    with mock.patch("builtins.open", mock.mock_open()) as m:
        monkeypatch.setattr(
            config.configparser.ConfigParser,
            "__getitem__",
            lambda x, y: {"key": "value"},
        )
        monkeypatch.setattr(
            config.configparser.ConfigParser, "__delitem__", mock.MagicMock()
        )
        config.delete("key", "CLI")
        m.assert_called_with(config.defaults.APPDATA_PATH + "/config.ini", "w")


def test_get_all(monkeypatch):
    monkeypatch.setattr(config.configparser.ConfigParser, "sections", lambda x: ["CLI"])
    monkeypatch.setattr(
        config.configparser.ConfigParser, "__getitem__", lambda x, y: {"key": "value"}
    )
    assert config.get_all() == {"CLI": {"key": "value"}}


def test_get_section(monkeypatch):
    def mock_getitem(x, y):
        if y == "CLI":
            return {"key": "value"}
        return {}

    monkeypatch.setattr(config.configparser.ConfigParser, "__getitem__", mock_getitem)
    assert config.get_section("CLI") == {"key": "value"}

    assert config.get_section("INVALID") == {}
