import datetime as dt
import unittest.mock as mock

import pytest
from freezegun import freeze_time

import habits_txt.journal as journal
import habits_txt.models as models


def test_get_state_at_date(monkeypatch):
    mock_directive = mock.MagicMock()
    mock_habit = mock.MagicMock()
    mock_record = mock.MagicMock()
    mock_habits_records_matches = mock.MagicMock()
    monkeypatch.setattr(journal.parser, "parse_file", lambda x: ([mock_directive], []))
    monkeypatch.setattr(
        journal.builder,
        "get_state_at_date",
        lambda x, y: ([mock_habit], [mock_record], mock_habits_records_matches),
    )
    assert journal.get_state_at_date("journal_file", dt.date(2021, 1, 1)) == (
        [mock_habit],
        [mock_record],
        mock_habits_records_matches,
    )

    monkeypatch.setattr(
        journal.parser, "parse_file", lambda x: ([mock_directive], ["error"])
    )
    monkeypatch.setattr(journal, "_log_errors", mock.MagicMock())
    assert journal.get_state_at_date("journal_file", dt.date(2021, 1, 1)) == (
        [mock_habit],
        [mock_record],
        mock_habits_records_matches,
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
    monkeypatch.setattr(journal, "get_state_at_date", lambda x, y: ([], [], []))
    assert journal._fill_day("journal_file", dt.date(2021, 1, 1)) == ([], False)

    habits = [models.Habit("habit1", models.Frequency("* * *"))]
    records = []
    habits_records_matches = []
    monkeypatch.setattr(
        journal,
        "get_state_at_date",
        lambda x, y: (habits, records, habits_records_matches),
    )
    assert journal._fill_day("journal_file", dt.date(2021, 1, 1)) == (
        [models.HabitRecord(dt.date(2021, 1, 1), "habit1", None)],
        False,
    )

    with mock.patch("click.prompt", side_effect=["yes"]) as mock_input:
        assert journal._fill_day("journal_file", dt.date(2021, 1, 1), True) == (
            [models.HabitRecord(dt.date(2021, 1, 1), "habit1", True)],
            False,
        )
        mock_input.assert_called_once()
        mock_input.reset_mock()
        mock_input.side_effect = ["False", "no"]
        assert journal._fill_day("journal_file", dt.date(2021, 1, 1), True) == (
            [models.HabitRecord(dt.date(2021, 1, 1), "habit1", False)],
            False,
        )
        assert mock_input.call_count == 2

    with mock.patch("click.prompt", side_effect=["s"]) as mock_input:
        assert journal._fill_day("journal_file", dt.date(2021, 1, 1), True) == (
            [],
            False,
        )
        mock_input.assert_called_once()
        mock_input.reset_mock()

    with mock.patch("click.prompt", side_effect=["a"]) as mock_input:
        assert journal._fill_day("journal_file", dt.date(2021, 1, 1), True) == (
            [models.HabitRecord(dt.date(2021, 1, 1), "habit1", None)],
            False,
        )
        mock_input.assert_called_once()
        mock_input.reset_mock()

    records = [models.HabitRecord(dt.date(2021, 1, 1), "habit1", True)]
    monkeypatch.setattr(
        journal,
        "get_state_at_date",
        lambda x, y: (habits, records, habits_records_matches),
    )
    assert journal._fill_day("journal_file", dt.date(2021, 1, 1)) == ([], False)

    records = [models.HabitRecord(dt.date(2021, 1, 1), "habit1", False)]
    monkeypatch.setattr(
        journal,
        "get_state_at_date",
        lambda x, y: (habits, records, habits_records_matches),
    )
    assert journal._fill_day("journal_file", dt.date(2021, 1, 1)) == ([], False)


@freeze_time("2021-01-02")
def test_fill_range(monkeypatch):
    mock_fill_day = mock.MagicMock()
    mock_fill_day.side_effect = [
        (["record1"], False),
        (["record2"], False),
        (["record3"], False),
    ]
    monkeypatch.setattr(journal, "_fill_day", mock_fill_day)
    assert journal._fill_range(
        "journal_file", dt.date(2021, 1, 1), dt.date(2021, 1, 3)
    ) == [
        "record1",
        "record2",
        "record3",
    ]
    journal._fill_day.assert_has_calls(
        [
            mock.call("journal_file", dt.date(2021, 1, 1), False),
            mock.call("journal_file", dt.date(2021, 1, 2), False),
            mock.call("journal_file", dt.date(2021, 1, 3), False),
        ]
    )

    mock_fill_day.reset_mock()
    mock_fill_day.side_effect = [
        (["record1"], False),
        (["record2"], False),
        (["record3"], False),
    ]
    monkeypatch.setattr(journal, "_get_first_date", lambda x: dt.date(2021, 1, 2))
    assert journal._fill_range("journal_file", None, dt.date(2021, 1, 3)) == [
        "record1",
        "record2",
    ]
    journal._fill_day.assert_has_calls(
        [
            mock.call("journal_file", dt.date(2021, 1, 2), False),
            mock.call("journal_file", dt.date(2021, 1, 3), False),
        ]
    )

    mock_fill_day.reset_mock()
    mock_fill_day.side_effect = [
        (["record1"], False),
        (["record2"], False),
        (["record3"], False),
    ]
    assert journal._fill_range("journal_file", dt.date(2021, 1, 1), None) == [
        "record1",
        "record2",
    ]
    journal._fill_day.assert_has_calls(
        [
            mock.call("journal_file", dt.date(2021, 1, 1), False),
            mock.call("journal_file", dt.date(2021, 1, 2), False),
        ]
    )

    mock_fill_day.reset_mock()
    mock_fill_day.side_effect = [
        (["record1"], False),
        (["record2"], False),
        (["record3"], False),
    ]
    assert journal._fill_range("journal_file", None, None) == []
    journal._fill_day.assert_not_called()

    mock_fill_day.reset_mock()
    mock_fill_day.side_effect = [
        (["record1"], False),
        (["record2"], True),
        (["record3"], False),
    ]
    assert journal._fill_range(
        "journal_file", dt.date(2021, 1, 1), dt.date(2021, 1, 3)
    ) == [
        "record1",
        "record2",
    ]
    journal._fill_day.assert_has_calls(
        [
            mock.call("journal_file", dt.date(2021, 1, 1), False),
            mock.call("journal_file", dt.date(2021, 1, 2), False),
        ]
    )


def test_fill(monkeypatch):
    monkeypatch.setattr(journal, "_fill_day", lambda x, y, z: (["record"], False))
    assert journal.fill("journal_file", dt.date(2021, 1, 1), None, None) == ["record"]

    monkeypatch.setattr(journal, "_fill_range", lambda x, y, z, a: ["record"])
    assert journal.fill(
        "journal_file", None, dt.date(2021, 1, 1), dt.date(2021, 1, 3)
    ) == ["record"]


def test_get_first_date(monkeypatch):
    records = [
        models.HabitRecord(dt.date(2021, 1, 1), "habit1", True),
        models.HabitRecord(dt.date(2021, 1, 2), "habit1", True),
    ]
    monkeypatch.setattr(journal, "get_state_at_date", lambda x, y: ([], records, []))
    assert journal._get_first_date("journal_file") == dt.date(2021, 1, 1)

    records = [
        models.HabitRecord(dt.date(2021, 1, 2), "habit1", True),
        models.HabitRecord(dt.date(2021, 1, 1), "habit1", True),
    ]
    monkeypatch.setattr(journal, "get_state_at_date", lambda x, y: ([], records, []))
    assert journal._get_first_date("journal_file") == dt.date(2021, 1, 1)


def test_filter_state(monkeypatch):
    monkeypatch.setattr(journal, "get_state_at_date", lambda x, y: ([], [], []))
    assert journal._filter_state("journal_file", None, dt.date(2021, 1, 1), None) == (
        set(),
        [],
        [],
    )

    tracked_habits = [
        models.Habit("habit1", models.Frequency("* * *")),
        models.Habit("habit2", models.Frequency("* * *")),
    ]
    records = [
        models.HabitRecord(dt.date(2021, 1, 1), "habit1", True),
        models.HabitRecord(dt.date(2021, 1, 1), "habit2", True),
        models.HabitRecord(dt.date(2022, 1, 1), "habit1", True),
        models.HabitRecord(dt.date(2022, 1, 1), "habit2", True),
    ]
    habits_records_matches = [
        models.HabitRecordMatch(
            models.Habit("habit1", models.Frequency("* * *")),
            [
                models.HabitRecord(dt.date(2021, 1, 1), "habit1", True),
                models.HabitRecord(dt.date(2022, 1, 1), "habit1", True),
            ],
            dt.date(2021, 1, 1),
            None,
        ),
        models.HabitRecordMatch(
            models.Habit("habit2", models.Frequency("* * *")),
            [
                models.HabitRecord(dt.date(2021, 1, 1), "habit2", True),
                models.HabitRecord(dt.date(2022, 1, 1), "habit2", True),
            ],
            dt.date(2021, 1, 1),
            None,
        ),
    ]
    monkeypatch.setattr(
        journal,
        "get_state_at_date",
        lambda x, y: (tracked_habits, records, habits_records_matches),
    )
    assert journal._filter_state("journal_file", None, dt.date(2024, 1, 1), None) == (
        set(tracked_habits),
        records,
        habits_records_matches,
    )

    assert journal._filter_state(
        "journal_file", None, dt.date(2024, 1, 1), "habit1"
    ) == (
        {models.Habit("habit1", models.Frequency("* * *"))},
        [
            models.HabitRecord(dt.date(2021, 1, 1), "habit1", True),
            models.HabitRecord(dt.date(2022, 1, 1), "habit1", True),
        ],
        [
            models.HabitRecordMatch(
                models.Habit("habit1", models.Frequency("* * *")),
                [
                    models.HabitRecord(dt.date(2021, 1, 1), "habit1", True),
                    models.HabitRecord(dt.date(2022, 1, 1), "habit1", True),
                ],
                dt.date(2021, 1, 1),
                None,
            )
        ],
    )

    assert journal._filter_state(
        "journal_file", dt.date(2020, 12, 31), dt.date(2021, 2, 1), None
    ) == (
        {
            models.Habit("habit1", models.Frequency("* * *")),
            models.Habit("habit2", models.Frequency("* * *")),
        },
        [
            models.HabitRecord(dt.date(2021, 1, 1), "habit1", True),
            models.HabitRecord(dt.date(2021, 1, 1), "habit2", True),
        ],
        [
            models.HabitRecordMatch(
                models.Habit("habit1", models.Frequency("* * *")),
                [
                    models.HabitRecord(dt.date(2021, 1, 1), "habit1", True),
                ],
                dt.date(2021, 1, 1),
                None,
            ),
            models.HabitRecordMatch(
                models.Habit("habit2", models.Frequency("* * *")),
                [
                    models.HabitRecord(dt.date(2021, 1, 1), "habit2", True),
                ],
                dt.date(2021, 1, 1),
                None,
            ),
        ],
    )


def test_filter(monkeypatch):
    monkeypatch.setattr(journal, "get_state_at_date", lambda x, y: ([], [], []))
    assert journal.filter("journal_file", None, dt.date(2021, 1, 1), None) == []

    records = [models.HabitRecord(dt.date(2021, 1, 1), "habit1", True)]
    monkeypatch.setattr(journal, "get_state_at_date", lambda x, y: ([], records, []))
    assert journal.filter("journal_file", None, dt.date(2021, 1, 1), None) == records

    records = [models.HabitRecord(dt.date(2021, 1, 1), "habit1", True)]
    monkeypatch.setattr(journal, "get_state_at_date", lambda x, y: ([], records, []))
    assert (
        journal.filter("journal_file", None, dt.date(2021, 1, 1), "habit1") == records
    )

    records = [models.HabitRecord(dt.date(2021, 1, 1), "habit1", True)]
    monkeypatch.setattr(journal, "get_state_at_date", lambda x, y: ([], records, []))
    assert (
        journal.filter(
            "journal_file", dt.date(2021, 1, 1), dt.date(2021, 1, 1), "habit1"
        )
        == records
    )

    records = [models.HabitRecord(dt.date(2021, 1, 1), "habit1", True)]
    monkeypatch.setattr(journal, "get_state_at_date", lambda x, y: ([], records, []))
    assert (
        journal.filter(
            "journal_file", dt.date(2021, 1, 2), dt.date(2021, 1, 2), "habit1"
        )
        == []
    )

    records = [models.HabitRecord(dt.date(2021, 1, 1), "habit1", True)]
    monkeypatch.setattr(journal, "get_state_at_date", lambda x, y: ([], records, []))
    assert (
        journal.filter(
            "journal_file", dt.date(2021, 1, 1), dt.date(2021, 1, 1), "habit2"
        )
        == []
    )


def test_check(monkeypatch):
    monkeypatch.setattr(journal, "get_state_at_date", lambda x, y: ([], [], []))
    assert journal.check("journal_file", dt.date(2021, 1, 1)) is True


def test_info(monkeypatch):
    habit1 = models.Habit("habit1", models.Frequency("* * *"))
    record11 = models.HabitRecord(dt.date(2021, 1, 1), "habit1", True)
    record12 = models.HabitRecord(dt.date(2021, 1, 2), "habit1", True)
    tracking_start_date1 = dt.date(2021, 1, 1)
    tracking_end_date1 = dt.date(2021, 1, 3)

    habit_record_matches1 = models.HabitRecordMatch(
        habit1, [record11, record12], tracking_start_date1, tracking_end_date1
    )
    monkeypatch.setattr(
        journal,
        "get_state_at_date",
        lambda x, y: ([habit1], [record11, record12], [habit_record_matches1]),
    )

    info = journal.info("journal_file", None, dt.date(2021, 1, 3), None)

    assert info[0].habit == habit1
    assert info[0].n_records == 2
    assert info[0].n_records_expected == 3
    assert info[0].average_total == 0.67
    assert info[0].average_present == 1.0
    assert info[0].longest_streak == 2
    assert info[0].latest_streak == 0
    assert info[0].start_date == tracking_start_date1
    assert info[0].end_date == tracking_end_date1

    habit2 = models.Habit("habit2", models.Frequency("* * *"))
    record21 = models.HabitRecord(dt.date(2021, 1, 1), "habit2", True)
    record22 = models.HabitRecord(dt.date(2021, 1, 2), "habit2", True)
    record24 = models.HabitRecord(dt.date(2021, 1, 4), "habit2", True)
    tracking_start_date2 = dt.date(2021, 1, 1)
    tracking_end_date2 = dt.date(2021, 1, 4)

    habit_record_matches2 = models.HabitRecordMatch(
        habit2, [record21, record22, record24], tracking_start_date2, tracking_end_date2
    )
    monkeypatch.setattr(
        journal,
        "get_state_at_date",
        lambda x, y: (
            [habit2],
            [record21, record22, record24],
            [habit_record_matches2],
        ),
    )

    info = journal.info("journal_file", None, dt.date(2021, 1, 4), None)

    assert info[0].habit == habit2
    assert info[0].longest_streak == 2
    assert info[0].latest_streak == 1

    habit3 = models.Habit("habit3", models.Frequency("* * *"), is_measurable=True)
    record31 = models.HabitRecord(dt.date(2021, 1, 1), "habit3", 5)
    record32 = models.HabitRecord(dt.date(2021, 1, 2), "habit3", 10)
    record34 = models.HabitRecord(dt.date(2021, 1, 4), "habit3", 20)
    tracking_start_date3 = dt.date(2021, 1, 1)
    tracking_end_date3 = dt.date(2021, 1, 4)

    habit_record_matches3 = models.HabitRecordMatch(
        habit3, [record31, record32, record34], tracking_start_date3, tracking_end_date3
    )

    monkeypatch.setattr(
        journal,
        "get_state_at_date",
        lambda x, y: (
            [habit3],
            [record31, record32, record34],
            [habit_record_matches3],
        ),
    )

    info = journal.info("journal_file", None, dt.date(2021, 1, 4), None)

    assert info[0].habit == habit3
    assert info[0].longest_streak == 2
    assert info[0].latest_streak == 1
