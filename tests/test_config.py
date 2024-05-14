import unittest.mock as mock

import habits_txt.config as config


def test_setup(monkeypatch):
    monkeypatch.setattr(config.os.path, "exists", lambda x: False)
    monkeypatch.setattr(config.os, "makedirs", mock.MagicMock())

    with mock.patch("builtins.open", mock.mock_open()) as m:
        config.setup()
        m.assert_called_once_with(config.defaults.APPDATA_PATH + "/config.ini", "w")
        m().write.assert_called_once_with("[CLI]\n")
