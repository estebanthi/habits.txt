import datetime as dt
import unittest.mock as mock

import pytest

import habits_txt.journal as journal
import habits_txt.models as models


def test_get_state_at_date(monkeypatch):
    mock_directive = mock.MagicMock()
    mock_habit = mock.MagicMock()
    mock_record = mock.MagicMock()
    monkeypatch.setattr(journal.parser, "parse_file", lambda x: ([mock_directive], []))
    monkeypatch.setattr(
        journal.builder, "get_state_at_date", lambda x, y: ([mock_habit], [mock_record])
    )
    assert journal.get_state_at_date("journal_file", dt.date(2021, 1, 1)) == (
        [mock_habit],
        [mock_record],
    )

    monkeypatch.setattr(
        journal.parser, "parse_file", lambda x: ([mock_directive], ["error"])
    )
    monkeypatch.setattr(journal, "_log_errors", mock.MagicMock())
    assert journal.get_state_at_date("journal_file", dt.date(2021, 1, 1)) == (
        [mock_habit],
        [mock_record],
    )
    journal._log_errors.assert_called_with(["error"])

    def raise_error(*args):
        raise journal.exceptions.ConsistencyError("error", mock.MagicMock())

    monkeypatch.setattr(journal.builder, "get_state_at_date", raise_error)

    with pytest.raises(SystemExit):
        journal.get_state_at_date("journal_file", dt.date(2021, 1, 1))


def test_log_errors(caplog):
    journal._log_errors(["error1", "error2"])
    assert caplog.records[0].levelname == "ERROR"
    assert caplog.records[0].message == "error1"
    assert caplog.records[1].levelname == "ERROR"
    assert caplog.records[1].message == "error2"


def test_fill_day(monkeypatch):
    monkeypatch.setattr(journal, "get_state_at_date", lambda x, y: ([], []))
    assert journal.fill_day("journal_file", dt.date(2021, 1, 1)) == []

    habits = [models.Habit("habit1", models.Frequency("*", "*", "*"))]
    records = []
    monkeypatch.setattr(journal, "get_state_at_date", lambda x, y: (habits, records))
    assert journal.fill_day("journal_file", dt.date(2021, 1, 1)) == [
        models.HabitRecord(dt.date(2021, 1, 1), "habit1", None)
    ]

    with mock.patch("builtins.input", side_effect=["yes"]) as mock_input:
        assert journal.fill_day("journal_file", dt.date(2021, 1, 1), True) == [
            models.HabitRecord(dt.date(2021, 1, 1), "habit1", True)
        ]
        mock_input.assert_called_once()
        mock_input.reset_mock()
        mock_input.side_effect = ["False", "no"]
        assert journal.fill_day("journal_file", dt.date(2021, 1, 1), True) == [
            models.HabitRecord(dt.date(2021, 1, 1), "habit1", False)
        ]
        assert mock_input.call_count == 2

    records = [models.HabitRecord(dt.date(2021, 1, 1), "habit1", True)]
    monkeypatch.setattr(journal, "get_state_at_date", lambda x, y: (habits, records))
    assert journal.fill_day("journal_file", dt.date(2021, 1, 1)) == []

    records = [models.HabitRecord(dt.date(2021, 1, 1), "habit1", False)]
    monkeypatch.setattr(journal, "get_state_at_date", lambda x, y: (habits, records))
    assert journal.fill_day("journal_file", dt.date(2021, 1, 1)) == []


def test_filter(monkeypatch):
    monkeypatch.setattr(journal, "get_state_at_date", lambda x, y: ([], []))
    assert journal.filter("journal_file", None, dt.date(2021, 1, 1), None) == []

    records = [models.HabitRecord(dt.date(2021, 1, 1), "habit1", True)]
    monkeypatch.setattr(journal, "get_state_at_date", lambda x, y: ([], records))
    assert journal.filter("journal_file", None, dt.date(2021, 1, 1), None) == records

    records = [models.HabitRecord(dt.date(2021, 1, 1), "habit1", True)]
    monkeypatch.setattr(journal, "get_state_at_date", lambda x, y: ([], records))
    assert (
        journal.filter("journal_file", None, dt.date(2021, 1, 1), "habit1") == records
    )

    records = [models.HabitRecord(dt.date(2021, 1, 1), "habit1", True)]
    monkeypatch.setattr(journal, "get_state_at_date", lambda x, y: ([], records))
    assert (
        journal.filter(
            "journal_file", dt.date(2021, 1, 1), dt.date(2021, 1, 1), "habit1"
        )
        == records
    )

    records = [models.HabitRecord(dt.date(2021, 1, 1), "habit1", True)]
    monkeypatch.setattr(journal, "get_state_at_date", lambda x, y: ([], records))
    assert (
        journal.filter(
            "journal_file", dt.date(2021, 1, 2), dt.date(2021, 1, 2), "habit1"
        )
        == []
    )

    records = [models.HabitRecord(dt.date(2021, 1, 1), "habit1", True)]
    monkeypatch.setattr(journal, "get_state_at_date", lambda x, y: ([], records))
    assert (
        journal.filter(
            "journal_file", dt.date(2021, 1, 1), dt.date(2021, 1, 1), "habit2"
        )
        == []
    )


def test_check(monkeypatch):
    monkeypatch.setattr(journal, "get_state_at_date", lambda x, y: ([], []))
    assert journal.check("journal_file", dt.date(2021, 1, 1)) is True
