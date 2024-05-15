import datetime as dt
import typing

import habits_txt.directives as directives
import habits_txt.exceptions as exceptions
import habits_txt.models as models


def _sort_directives(
    directives_: list[directives.Directive],
) -> list[directives.Directive]:
    """
    Sort the directives by date.

    :param directives_: List of directives.
    :return: Sorted list of directives.

    Example:
    >>> directive1 = directives.RecordDirective(dt.datetime(2024, 1, 1), "Habit 1", False)
    >>> directive2 = directives.RecordDirective(dt.datetime(2024, 1, 2), "Habit 2", True)
    >>> sorted_directives = _sort_directives([directive2, directive1])
    >>> print(sorted_directives)
    [directive1, directive2]
    """
    return sorted(directives_, key=lambda directive_: directive_.date)


def _get_tracked_habits_at_date(
    directives_: list[directives.Directive], date: dt.date
) -> set[models.Habit]:
    """
    Get the tracked habits at a given date.

    :param directives_: List of directives.
    :param date: Date to check.
    :return: List of tracked habits.

    Example:
    >>> directive1 = directives.TrackDirective(dt.datetime(2024, 1, 1), "Habit 1", models.Frequency("*", "*", "*"))
    >>> directive2 = directives.TrackDirective(dt.datetime(2024, 1, 2), "Habit 2", models.Frequency("*", "*", "*"))
    >>> directive3 = directives.TrackDirective(dt.datetime(2024, 1, 3), "Habit 3", models.Frequency("*", "*", "*"))
    >>> tracked_habits = _get_tracked_habits_at_date([directive1, directive2, directive3], dt.datetime(2024, 1, 2))
    >>> print(tracked_habits)
    [Habit 1, Habit 2]
    """
    directives_before_date = [
        directive for directive in directives_ if directive.date <= date
    ]
    sorted_directives = _sort_directives(directives_before_date)

    current_state: set[models.Habit] = set()
    for directive in sorted_directives:
        if isinstance(directive, directives.TrackDirective):
            _check_track_directive_is_valid(directive, current_state)
            current_state.add(_build_habit_from_track_directive(directive))
        elif isinstance(directive, directives.UntrackDirective):
            _check_untrack_directive_is_valid(directive, current_state)
            current_state = _remove_habit_from_state(
                directive.habit_name, current_state
            )

    return current_state


def _check_track_directive_is_valid(
    directive: directives.TrackDirective, tracked_habits: set[models.Habit]
):
    """
    Check if a track directive is valid.

    :param directive: Track directive.
    :param tracked_habits: Tracked habits.

    Example:
    >>> directive1 = directives.TrackDirective(dt.datetime(2024, 1, 1), "Habit 1", models.Frequency("*", "*", "*"))
    >>> directive2 = directives.TrackDirective(dt.datetime(2024, 1, 2), "Habit 2", models.Frequency("*", "*", "*"))
    >>> tracked_habits = {models.Habit("Habit 1", models.Frequency("*", "*", "*"))}
    >>> _check_track_directive_is_valid(directive2, tracked_habits)
    """
    if directive.habit_name in {habit.name for habit in tracked_habits}:
        raise exceptions.ConsistencyError(
            f"Several tracked habits with the same name: {directive.habit_name}",
            directive,
        )


def _check_untrack_directive_is_valid(
    directive: directives.UntrackDirective, tracked_habits: set[models.Habit]
):
    """
    Check if an untrack directive is valid.

    :param directive: Untrack directive.
    :param tracked_habits: Tracked habits.

    Example:
    >>> directive = directives.UntrackDirective(dt.datetime(2024, 1, 1), "Habit 1")
    >>> tracked_habits = {models.Habit("Habit 1", models.Frequency("*", "*", "*"))}
    >>> _check_untrack_directive_is_valid(directive, tracked_habits)
    """
    if directive.habit_name not in {habit.name for habit in tracked_habits}:
        raise exceptions.ConsistencyError(
            f"Untracked habit without a corresponding track directive: {directive.habit_name}",
            directive,
        )


def _remove_habit_from_state(
    habit_name: str, tracked_habits: set[models.Habit]
) -> set[models.Habit]:
    """
    Remove a habit from the state.

    :param habit_name: Name of the habit to remove.
    :param tracked_habits: Tracked habits.
    :return: Updated tracked habits.

    Example:
    >>> habit_name = "Habit 1"
    >>> tracked_habits = {models.Habit("Habit 1", models.Frequency("*", "*", "*"))}
    >>> updated_tracked_habits = _remove_habit_from_state(habit_name, tracked_habits)
    >>> print(updated_tracked_habits)
    []
    """
    return {habit for habit in tracked_habits if habit.name != habit_name}


def _build_habit_from_track_directive(
    directive: directives.TrackDirective,
) -> models.Habit:
    """
    Build a habit from a track directive.

    :param directive: Track directive.
    :return: Built habit.

    Example:
    >>> directive = directives.TrackDirective(dt.datetime(2024, 1, 1), "Habit 1", models.Frequency("*", "*", "*"))
    >>> habit = _build_habit_from_track_directive(directive)
    >>> print(habit)
    Habit 1
    """
    return models.Habit(
        directive.habit_name, directive.frequency, directive.is_measurable
    )


def _build_habit_record_from_record_directive(
    directive: directives.RecordDirective,
) -> models.HabitRecord:
    """
    Build a habit record from a record directive.

    :param directive: Record directive.
    :return: Built habit record.

    Example:
    >>> directive = directives.RecordDirective(dt.datetime(2024, 1, 1), "Habit 1", False)
    >>> habit_record = _build_habit_record_from_record_directive(directive)
    >>> print(habit_record)
    HabitRecord(2024-01-01, Habit 1, False)
    """
    return models.HabitRecord(directive.date, directive.habit_name, directive.value)


def _get_records_up_to_date(
    directives_: list[directives.Directive], date: dt.date
) -> list[models.HabitRecord]:
    """
    Get the records up to a given date.

    :param directives_: List of directives.
    :param date: Date to check.
    :return: List of records.

    Example:
    >>> directive1 = directives.RecordDirective(dt.datetime(2024, 1, 1), "Habit 1", False)
    >>> directive2 = directives.RecordDirective(dt.datetime(2024, 1, 2), "Habit 2", True)
    >>> directive3 = directives.RecordDirective(dt.datetime(2024, 1, 3), "Habit 3", False)
    >>> records = _get_records_up_to_date([directive1, directive2, directive3], dt.datetime(2024, 1, 2))
    >>> print(records)
    [HabitRecord(Habit 1, False), HabitRecord(Habit 2, True)]
    """
    directives_before_date = [
        directive for directive in directives_ if directive.date <= date
    ]
    sorted_directives = _sort_directives(directives_before_date)

    records: list[models.HabitRecord] = []
    for directive in sorted_directives:
        if isinstance(directive, directives.RecordDirective):
            tracked_habits_at_date = _get_tracked_habits_at_date(
                directives_, directive.date
            )
            _check_record_directive_is_valid(directive, tracked_habits_at_date, records)
            records.append(_build_habit_record_from_record_directive(directive))

    return records


def _check_record_directive_is_valid(
    directive: directives.RecordDirective,
    tracked_habits: set[models.Habit],
    records: list[models.HabitRecord],
):
    """
    Check if a record directive is valid.

    :param directive: Record directive.
    :param tracked_habits: Tracked habits.
    :param records: List of records.

    Example:
    >>> directive = directives.RecordDirective(dt.datetime(2024, 1, 1), "Habit 1", False)
    >>> tracked_habits = {models.Habit("Habit 1", models.Frequency("*", "*", "*"))}
    >>> records = [models.HabitRecord(dt.datetime(2024, 1, 1), "Habit 2", True)]
    >>> _check_record_directive_is_valid(directive, tracked_habits, records)
    """
    if directive.habit_name not in {habit.name for habit in tracked_habits}:
        raise exceptions.ConsistencyError(
            f"Recorded habit without a corresponding track directive: {directive.habit_name}",
            directive,
        )

    if any(
        record.date == directive.date and record.habit_name == directive.habit_name
        for record in records
    ):
        raise exceptions.ConsistencyError(
            f"Several records of the same habit on the same day: {directive.habit_name}",
            directive,
        )

    for habit in tracked_habits:
        if habit.name == directive.habit_name:
            if habit.is_measurable and not isinstance(directive.value, float):
                raise exceptions.ConsistencyError(
                    f"Measurable habit with a non-float value: {directive.habit_name}",
                    directive,
                )
            if not habit.is_measurable and not isinstance(directive.value, bool):
                raise exceptions.ConsistencyError(
                    f"Non-measurable habit with a non-bool value: {directive.habit_name}",
                    directive,
                )


def get_state_at_date(
    directives_: list[directives.Directive], date: dt.date
) -> typing.Tuple[
    set[models.Habit],
    list[models.HabitRecord],
    list[models.HabitRecordMatch],
]:
    """
    Get the state of the habits at a given date.

    :param directives_: List of directives.
    :param date: Date to check.
    :return: List of tracked habits, list of records, list of matches.

    Example:
    >>> directive1 = directives.TrackDirective(dt.datetime(2024, 1, 1), "Habit 1", models.Frequency("*", "*", "*"))
    >>> directive2 = directives.TrackDirective(dt.datetime(2024, 1, 2), "Habit 2", models.Frequency("*", "*", "*"))
    >>> directive3 = directives.RecordDirective(dt.datetime(2024, 1, 1), "Habit 1", False)
    >>> tracked_habits, records, habits_records_matches = \
    get_state_at_date([directive1, directive2, directive3], dt.datetime(2024, 1, 1))
    >>> print(tracked_habits)
    [Habit 1]
    >>> print(records)
    [HabitRecord(Habit 1, False)]
    >>> print(habits_records_matches)
    [(Habit 1, [HabitRecord(Habit 1, False)], 2024-01-01, None)]
    """
    tracked_habits = _get_tracked_habits_at_date(directives_, date)
    records = _get_records_up_to_date(directives_, date)

    track_untrack_record_matches = get_track_untrack_record_matches_at_date(
        directives_, date
    )
    habits_records_matches = [
        models.HabitRecordMatch(
            habit=_build_habit_from_track_directive(track_directive),
            habit_records=[
                _build_habit_record_from_record_directive(record_directive)
                for record_directive in record_directives
            ],
            tracking_start_date=track_directive.date,
            tracking_end_date=(
                untrack_directive.date if untrack_directive is not None else None
            ),
        )
        for track_directive, untrack_directive, record_directives in track_untrack_record_matches
    ]

    return tracked_habits, records, habits_records_matches


def get_track_untrack_record_matches_at_date(
    directives_: list[directives.Directive], date: dt.date
) -> list[
    typing.Tuple[
        directives.TrackDirective,
        directives.UntrackDirective | None,
        list[directives.RecordDirective],
    ]
]:
    """
    Get the matches of track, untrack, and record directives at a given date.

    :param directives_: List of directives.
    :param date: Date to check.
    :return: List of matches.

    Example:
    >>> directive1 = directives.TrackDirective(dt.datetime(2024, 1, 1), "Habit 1", models.Frequency("*", "*", "*"))
    >>> directive2 = directives.UntrackDirective(dt.datetime(2024, 1, 2), "Habit 1")
    >>> directive3 = directives.TrackDirective(dt.datetime(2024, 1, 2), "Habit 2", models.Frequency("*", "*", "*"))
    >>> directive4 = directives.RecordDirective(dt.datetime(2024, 1, 1), "Habit 1", False)
    >>> matches = get_track_untrack_record_matches_at_date(\
    [directive1, directive2, directive3, directive4], dt.datetime(2024, 2, 1))
    >>> print(matches)
    [(directive1, directive2, [directive4]), (directive3, None, [])]
    """
    directives_before_date = [
        directive for directive in directives_ if directive.date <= date
    ]
    sorted_directives = _sort_directives(directives_before_date)

    track_directives: list[directives.TrackDirective] = []
    untrack_directives: list[directives.UntrackDirective] = []
    matches: list[
        typing.Tuple[directives.TrackDirective, directives.UntrackDirective | None]
    ] = []
    for directive in sorted_directives:
        if isinstance(directive, directives.TrackDirective):
            track_directives.append(directive)
        elif isinstance(directive, directives.UntrackDirective):
            untrack_directives.append(directive)

    for track_directive in track_directives:
        match = next(
            (
                untrack_directive
                for untrack_directive in untrack_directives
                if untrack_directive.habit_name == track_directive.habit_name
            ),
            None,
        )
        matches.append((track_directive, match))

    all_matches: list[
        typing.Tuple[
            directives.TrackDirective,
            directives.UntrackDirective | None,
            list[directives.RecordDirective],
        ]
    ] = []
    for track_directive, untrack_directive in matches:
        start_date = track_directive.date
        end_date = untrack_directive.date if untrack_directive is not None else date
        record_directives = [
            directive
            for directive in directives_
            if isinstance(directive, directives.RecordDirective)
            and directive.habit_name == track_directive.habit_name
            and start_date <= directive.date <= end_date
        ]
        all_matches.append((track_directive, untrack_directive, record_directives))
    return all_matches
