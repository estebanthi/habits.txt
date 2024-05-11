import datetime as dt

import pytest

import src.builder as builder


def test_sort_directives():
    directive1 = builder.directives.RecordDirective(
        dt.datetime(2024, 1, 1), "Habit 1", False
    )
    directive2 = builder.directives.RecordDirective(
        dt.datetime(2024, 1, 2), "Habit 2", True
    )

    sorted_directives = builder._sort_directives([directive2, directive1])
    assert sorted_directives == [directive1, directive2]


def test_get_tracked_habits_at_date():
    directive1 = builder.directives.TrackDirective(
        dt.datetime(2024, 1, 1), "Habit 1", builder.models.Frequency("*", "*", "*")
    )
    directive2 = builder.directives.TrackDirective(
        dt.datetime(2024, 1, 2), "Habit 2", builder.models.Frequency("*", "*", "*")
    )
    directive3 = builder.directives.TrackDirective(
        dt.datetime(2024, 1, 3), "Habit 3", builder.models.Frequency("*", "*", "*")
    )

    tracked_habits = builder._get_tracked_habits_at_date(
        [directive1, directive2, directive3], dt.datetime(2024, 1, 2)
    )
    assert tracked_habits == {
        builder.models.Habit("Habit 1", builder.models.Frequency("*", "*", "*")),
        builder.models.Habit("Habit 2", builder.models.Frequency("*", "*", "*")),
    }


def test_check_track_directive_is_valid():
    directive = builder.directives.TrackDirective(
        dt.datetime(2024, 1, 1), "Habit 1", builder.models.Frequency("*", "*", "*")
    )
    current_state = {
        builder.models.Habit("Habit 2", builder.models.Frequency("*", "*", "*"))
    }
    builder._check_track_directive_is_valid(directive, current_state)

    directive = builder.directives.TrackDirective(
        dt.datetime(2024, 1, 1), "Habit 1", builder.models.Frequency("*", "*", "*")
    )
    current_state = {
        builder.models.Habit("Habit 1", builder.models.Frequency("*", "*", "*"))
    }
    with pytest.raises(builder.exceptions.ConsistencyError):
        builder._check_track_directive_is_valid(directive, current_state)


def test_check_untrack_directive_is_valid():
    directive = builder.directives.UntrackDirective(dt.datetime(2024, 1, 1), "Habit 1")
    current_state = {
        builder.models.Habit("Habit 1", builder.models.Frequency("*", "*", "*"))
    }
    builder._check_untrack_directive_is_valid(directive, current_state)

    directive = builder.directives.UntrackDirective(dt.datetime(2024, 1, 1), "Habit 1")
    current_state = {
        builder.models.Habit("Habit 2", builder.models.Frequency("*", "*", "*"))
    }
    with pytest.raises(builder.exceptions.ConsistencyError):
        builder._check_untrack_directive_is_valid(directive, current_state)


def test_remove_habit_from_state():
    habit1 = builder.models.Habit("Habit 1", builder.models.Frequency("*", "*", "*"))
    habit2 = builder.models.Habit("Habit 2", builder.models.Frequency("*", "*", "*"))
    habit3 = builder.models.Habit("Habit 3", builder.models.Frequency("*", "*", "*"))
    current_state = {habit1, habit2, habit3}

    new_state = builder._remove_habit_from_state("Habit 2", current_state)
    assert new_state == {habit1, habit3}

    new_state = builder._remove_habit_from_state("Habit 4", current_state)
    assert new_state == {habit1, habit2, habit3}


def test_build_habit_from_track_directive():
    directive = builder.directives.TrackDirective(
        dt.datetime(2024, 1, 1), "Habit 1", builder.models.Frequency("*", "*", "*")
    )
    habit = builder._build_habit_from_track_directive(directive)
    assert habit == builder.models.Habit(
        "Habit 1", builder.models.Frequency("*", "*", "*")
    )


def test_build_habit_record_from_record_directive():
    directive = builder.directives.RecordDirective(
        dt.datetime(2024, 1, 1), "Habit 1", 2.0
    )
    habit_record = builder._build_habit_record_from_record_directive(directive)
    assert habit_record == builder.models.HabitRecord(
        dt.datetime(2024, 1, 1), "Habit 1", 2.0
    )


def test_get_records_up_to_date():
    track_directive = builder.directives.TrackDirective(
        dt.datetime(2024, 1, 1), "Habit 1", builder.models.Frequency("*", "*", "*")
    )
    directive1 = builder.directives.RecordDirective(
        dt.datetime(2024, 1, 1), "Habit 1", 2.0
    )
    directive2 = builder.directives.RecordDirective(
        dt.datetime(2024, 1, 2), "Habit 1", 3.0
    )
    directive3 = builder.directives.RecordDirective(
        dt.datetime(2024, 1, 3), "Habit 1", 4.0
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
        dt.datetime(2024, 1, 1), "Habit 1", 2.0
    )
    tracked_habits = {
        builder.models.Habit("Habit 1", builder.models.Frequency("*", "*", "*"))
    }
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
