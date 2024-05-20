import datetime as dt

import pytest

import habits_txt.builder as builder


def test_sort_directives():
    directive1 = builder.directives.RecordDirective(
        dt.datetime(2024, 1, 1), "Habit 1", 1, False
    )
    directive2 = builder.directives.RecordDirective(
        dt.datetime(2024, 1, 2), "Habit 2", 1, True
    )

    sorted_directives = builder._sort_directives([directive2, directive1])
    assert sorted_directives == [directive1, directive2]


def test_get_tracked_habits_at_date():
    directive1 = builder.directives.TrackDirective(
        dt.datetime(2024, 1, 1),
        "Habit 1",
        1,
        "0 0 * * *",
        False,
    )
    directive2 = builder.directives.TrackDirective(
        dt.datetime(2024, 1, 2),
        "Habit 2",
        2,
        "0 0 * * *",
        False,
    )
    directive3 = builder.directives.TrackDirective(
        dt.datetime(2024, 1, 3),
        "Habit 3",
        3,
        "0 0 * * *",
        False,
    )

    tracked_habits = builder._get_tracked_habits_at_date(
        [directive1, directive2, directive3], dt.datetime(2024, 1, 2)
    )
    assert tracked_habits == {
        builder.models.Habit("Habit 1", "0 0 * * *", False),
        builder.models.Habit("Habit 2", "0 0 * * *", False),
    }

    directive4 = builder.directives.UntrackDirective(
        dt.datetime(2024, 1, 4), "Habit 2", 2
    )
    tracked_habits = builder._get_tracked_habits_at_date(
        [directive1, directive2, directive3, directive4], dt.datetime(2024, 1, 4)
    )
    assert tracked_habits == {
        builder.models.Habit("Habit 1", "0 0 * * *", False),
        builder.models.Habit("Habit 3", "0 0 * * *", False),
    }


def test_check_track_directive_is_valid():
    directive = builder.directives.TrackDirective(
        dt.datetime(2024, 1, 1),
        "Habit 1",
        1,
        "0 0 * * *",
        False,
    )
    current_state = {builder.models.Habit("Habit 2", "0 0 * * *")}
    builder._check_track_directive_is_valid(directive, current_state)

    directive = builder.directives.TrackDirective(
        dt.datetime(2024, 1, 1),
        "Habit 1",
        1,
        "0 0 * * *",
        False,
    )
    current_state = {builder.models.Habit("Habit 1", "0 0 * * *")}
    with pytest.raises(builder.exceptions.ConsistencyError):
        builder._check_track_directive_is_valid(directive, current_state)


def test_check_untrack_directive_is_valid():
    directive = builder.directives.UntrackDirective(
        dt.datetime(2024, 1, 1), "Habit 1", 1
    )
    current_state = {builder.models.Habit("Habit 1", "0 0 * * *")}
    builder._check_untrack_directive_is_valid(directive, current_state)

    directive = builder.directives.UntrackDirective(
        dt.datetime(2024, 1, 1), "Habit 1", 1
    )
    current_state = {builder.models.Habit("Habit 2", "0 0 * * *")}
    with pytest.raises(builder.exceptions.ConsistencyError):
        builder._check_untrack_directive_is_valid(directive, current_state)


def test_remove_habit_from_state():
    habit1 = builder.models.Habit("Habit 1", "0 0 * * *")
    habit2 = builder.models.Habit("Habit 2", "0 0 * * *")
    habit3 = builder.models.Habit("Habit 3", "0 0 * * *")
    current_state = {habit1, habit2, habit3}

    new_state = builder._remove_habit_from_state("Habit 2", current_state)
    assert new_state == {habit1, habit3}

    new_state = builder._remove_habit_from_state("Habit 4", current_state)
    assert new_state == {habit1, habit2, habit3}


def test_build_habit_from_track_directive():
    directive = builder.directives.TrackDirective(
        dt.datetime(2024, 1, 1),
        "Habit 1",
        1,
        "0 0 * * *",
        False,
    )
    habit = builder._build_habit_from_track_directive(directive)
    assert habit == builder.models.Habit("Habit 1", "0 0 * * *")

    directive = builder.directives.TrackDirective(
        dt.datetime(2024, 1, 1),
        "Habit 1",
        1,
        "0 0 * * *",
        True,
    )
    habit = builder._build_habit_from_track_directive(directive)
    assert habit == builder.models.Habit("Habit 1", "0 0 * * *", True)


def test_build_habit_record_from_record_directive():
    directive = builder.directives.RecordDirective(
        dt.datetime(2024, 1, 1), "Habit 1", 1, 2.0
    )
    habit_record = builder._build_habit_record_from_record_directive(directive)
    assert habit_record == builder.models.HabitRecord(
        dt.datetime(2024, 1, 1), "Habit 1", 2.0
    )


def test_get_records_up_to_date():
    track_directive = builder.directives.TrackDirective(
        dt.datetime(2024, 1, 1),
        "Habit 1",
        1,
        "0 0 * * *",
        True,
    )
    directive1 = builder.directives.RecordDirective(
        dt.datetime(2024, 1, 1), "Habit 1", 1, 2.0
    )
    directive2 = builder.directives.RecordDirective(
        dt.datetime(2024, 1, 2), "Habit 1", 1, 3.0
    )
    directive3 = builder.directives.RecordDirective(
        dt.datetime(2024, 1, 3), "Habit 1", 1, 4.0
    )

    records = builder._get_records_up_to_date(
        [track_directive, directive1, directive2, directive3], dt.datetime(2024, 1, 2)
    )
    assert records == [
        builder.models.HabitRecord(dt.datetime(2024, 1, 1), "Habit 1", 2.0),
        builder.models.HabitRecord(dt.datetime(2024, 1, 2), "Habit 1", 3.0),
    ]


def test_check_record_directive_is_valid():
    directive = builder.directives.RecordDirective(
        dt.datetime(2024, 1, 1), "Habit 1", 1, 2.0
    )
    tracked_habits = {builder.models.Habit("Habit 1", "0 0 * * *", True)}
    current_records = []
    builder._check_record_directive_is_valid(directive, tracked_habits, current_records)

    with pytest.raises(builder.exceptions.ConsistencyError):
        builder._check_record_directive_is_valid(directive, set(), current_records)

    with pytest.raises(builder.exceptions.ConsistencyError):
        current_records = [
            builder.models.HabitRecord(dt.datetime(2024, 1, 1), "Habit 1", 2.0)
        ]
        builder._check_record_directive_is_valid(
            directive, tracked_habits, current_records
        )

    with pytest.raises(builder.exceptions.ConsistencyError):
        tracked_habits = {builder.models.Habit("Habit 2", "0 0 * * *", False)}
        builder._check_record_directive_is_valid(
            directive, tracked_habits, current_records
        )

    with pytest.raises(builder.exceptions.ConsistencyError):
        tracked_habits = {builder.models.Habit("Habit 1", "0 0 * * *", True)}
        record_directive = builder.directives.RecordDirective(
            dt.datetime(2024, 1, 1), "Habit 1", 1, True
        )
        builder._check_record_directive_is_valid(
            record_directive, tracked_habits, current_records
        )

    with pytest.raises(builder.exceptions.ConsistencyError):
        tracked_habits = {builder.models.Habit("Habit 1", "0 0 * * *", True)}
        record_directive = builder.directives.RecordDirective(
            dt.datetime(2024, 1, 1), "Habit 1", 1, True
        )

        current_records = []

        builder._check_record_directive_is_valid(
            record_directive, tracked_habits, current_records
        )

    with pytest.raises(builder.exceptions.ConsistencyError):
        tracked_habits = {builder.models.Habit("Habit 1", "0 0 * * *", False)}
        record_directive = builder.directives.RecordDirective(
            dt.datetime(2024, 1, 1), "Habit 1", 1, 10.0
        )

        current_records = []

        builder._check_record_directive_is_valid(
            record_directive, tracked_habits, current_records
        )


def test_get_state_at_date():
    directive1 = builder.directives.TrackDirective(
        dt.date(2024, 1, 1),
        "Habit 1",
        1,
        "0 0 * * *",
        False,
    )
    directive2 = builder.directives.TrackDirective(
        dt.date(2024, 1, 2),
        "Habit 2",
        2,
        "0 0 * * *",
        False,
    )
    directive3 = builder.directives.TrackDirective(
        dt.date(2024, 1, 3),
        "Habit 3",
        3,
        "0 0 * * *",
        False,
    )
    directive4 = builder.directives.UntrackDirective(dt.date(2024, 1, 4), "Habit 2", 2)
    directive5 = builder.directives.RecordDirective(
        dt.date(2024, 1, 1), "Habit 1", 1, False
    )

    directives = [directive1, directive2, directive3, directive4, directive5]
    tracked_habits, records, habits_records_matches = builder.get_state_at_date(
        directives, dt.date(2024, 1, 2)
    )
    assert tracked_habits == {
        builder.models.Habit("Habit 1", "0 0 * * *", False),
        builder.models.Habit("Habit 2", "0 0 * * *", False),
    }
    assert records == [
        builder.models.HabitRecord(dt.date(2024, 1, 1), "Habit 1", False)
    ]
    assert habits_records_matches == [
        builder.models.HabitRecordMatch(
            builder.models.Habit("Habit 1", "0 0 * * *"),
            [builder.models.HabitRecord(dt.date(2024, 1, 1), "Habit 1", False)],
            dt.date(2024, 1, 1),
            None,
        ),
        builder.models.HabitRecordMatch(
            builder.models.Habit("Habit 2", "0 0 * * *"),
            [],
            dt.date(2024, 1, 2),
            None,
        ),
    ]

    tracked_habits, records, track_untrack_matches = builder.get_state_at_date(
        directives, dt.date(2024, 1, 4)
    )
    assert tracked_habits == {
        builder.models.Habit("Habit 1", "0 0 * * *", False),
        builder.models.Habit("Habit 3", "0 0 * * *", False),
    }
    assert records == [
        builder.models.HabitRecord(dt.date(2024, 1, 1), "Habit 1", False)
    ]
    assert track_untrack_matches == [
        builder.models.HabitRecordMatch(
            builder.models.Habit("Habit 1", "0 0 * * *"),
            [builder.models.HabitRecord(dt.date(2024, 1, 1), "Habit 1", False)],
            dt.date(2024, 1, 1),
            None,
        ),
        builder.models.HabitRecordMatch(
            builder.models.Habit("Habit 2", "0 0 * * *"),
            [],
            dt.date(2024, 1, 2),
            dt.date(2024, 1, 4),
        ),
        builder.models.HabitRecordMatch(
            builder.models.Habit("Habit 3", "0 0 * * *"),
            [],
            dt.date(2024, 1, 3),
            None,
        ),
    ]


def test_get_track_untrack_record_matches_at_date():
    directive1 = builder.directives.TrackDirective(
        dt.datetime(2024, 1, 1),
        "Habit 1",
        1,
        "0 0 * * *",
        False,
    )
    directive2 = builder.directives.TrackDirective(
        dt.datetime(2024, 1, 2),
        "Habit 2",
        2,
        "0 0 * * *",
        False,
    )
    directive3 = builder.directives.UntrackDirective(
        dt.datetime(2024, 1, 3),
        "Habit 2",
        2,
    )
    directive4 = builder.directives.TrackDirective(
        dt.datetime(2024, 1, 4),
        "Habit 3",
        3,
        "0 0 * * *",
        False,
    )
    directive_5 = builder.directives.RecordDirective(
        dt.datetime(2024, 1, 2), "Habit 1", 1, 2.0
    )
    directive_6 = builder.directives.RecordDirective(
        dt.datetime(2024, 1, 3), "Habit 1", 1, 3.0
    )
    directive_7 = builder.directives.RecordDirective(
        dt.datetime(2024, 1, 4), "Habit 1", 1, 4.0
    )

    assert builder.get_track_untrack_record_matches_at_date(
        [
            directive1,
            directive2,
            directive3,
            directive4,
            directive_5,
            directive_6,
            directive_7,
        ],
        dt.datetime(2024, 1, 3),
    ) == [(directive1, None, [directive_5, directive_6]), (directive2, directive3, [])]
