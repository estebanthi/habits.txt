import datetime as dt
import logging
import typing

import habits_txt.builder as builder
import habits_txt.defaults as defaults
import habits_txt.exceptions as exceptions
import habits_txt.models as models
import habits_txt.parser as parser
import habits_txt.records_query as records_query


def get_state_at_date(journal_file: str, date: dt.date) -> typing.Tuple[
    set[models.Habit],
    list[models.HabitRecord],
    list[models.HabitRecordMatch],
]:
    """
    Get the state of the habits at a given date.

    :param journal_file: Path to the journal file.
    :param date: Date to check.
    :return: Tracked habits, records, matches between habits and records.
    """
    directives, parse_errors = parser.parse_file(journal_file)
    _log_errors(parse_errors)
    try:
        tracked_habits, records, habits_records_matches = builder.get_state_at_date(
            directives, date
        )
    except exceptions.ConsistencyError as e:
        logging.error(e)
        logging.error("Cannot continue due to consistency errors")
        exit(1)

    return tracked_habits, records, habits_records_matches


def _log_errors(errors: list[str]):
    """
    Log errors.

    :param errors: List of errors.
    """
    for error in errors:
        logging.error(error)


def fill_day(
    journal_file: str, date: dt.date, interactive: bool = False
) -> list[models.HabitRecord]:
    """
    Fill a day in the journal.

    :param journal_file: Path to the journal file.
    :param date: Date to fill.
    :param interactive: Interactive mode.
    :return: Journal file.
    """
    records_fill = []
    tracked_habits, records, habits_records_matches = get_state_at_date(
        journal_file, date
    )
    if not tracked_habits:
        logging.info(f"{defaults.COMMENT_CHAR} No habits tracked")
        return []
    for habit in tracked_habits:
        habit_records = [
            record for record in records if record.habit_name == habit.name
        ]
        if not habit_records:
            # because we can have a record directive the day we start to track a habit
            next_due_date = habit.frequency.get_next_date(date - dt.timedelta(days=1))
        else:
            most_recent_and_completed_record = (
                records_query.get_most_recent_and_completed_record(habit, habit_records)
            )
            next_due_date = habit.frequency.get_next_date(
                most_recent_and_completed_record.date
            )
        if next_due_date <= date:
            append = True
            if interactive:
                value_is_valid = False
                parsed_value = None
                while not value_is_valid:
                    value = input(f"{habit.name} ({next_due_date}): ")
                    if value == "s":
                        append = False
                        break
                    elif value == "a":
                        break
                    try:
                        parsed_value = parser.parse_value_str(value)
                        value_is_valid = True
                    except exceptions.ParseError:
                        logging.error(
                            f"Value must be a {"number" if habit.is_measurable else "boolean"}.\n"
                            f"(or 's' to skip, or 'a' to append to the journal but fill manually later)"
                        )
                record = models.HabitRecord(date, habit.name, parsed_value)
            else:
                record = models.HabitRecord(date, habit.name, None)

            if append:
                records_fill.append(record)

    return records_fill


def _filter_state(
    journal_file: str,
    start_date: dt.date | None,
    end_date: dt.date,
    habit_name: str | None,
) -> typing.Tuple[
    set[models.Habit],
    list[models.HabitRecord],
    list[models.HabitRecordMatch],
]:
    """
    Filter state.

    :param journal_file: Path to the journal file.
    :param start_date: Start date.
    :param end_date: End date.
    :param habit_name: Habit name.
    :return: Filtered state.
    """
    tracked_habits, records, habits_records_matches = get_state_at_date(
        journal_file, end_date
    )
    if not start_date:
        try:
            start_date = min(record.date for record in records)
        except ValueError:
            return set(), [], []

    filtered_tracked_habits = set(
        [
            habit
            for habit in tracked_habits
            if (not habit_name or habit.name == habit_name)
        ]
    )

    filtered_records = [
        record
        for record in records
        if start_date <= record.date <= end_date
        and (not habit_name or record.habit_name == habit_name)
    ]

    filtered_habits_records_matches = []
    for match in habits_records_matches:
        if match.tracking_start_date > end_date or (
            match.tracking_end_date and match.tracking_end_date < start_date
        ):
            continue
        if habit_name and match.habit.name != habit_name:
            continue
        match.habit_records = [
            record
            for record in match.habit_records
            if start_date <= record.date <= end_date
        ]
        filtered_habits_records_matches.append(match)

    return filtered_tracked_habits, filtered_records, filtered_habits_records_matches


def filter(
    journal_file: str,
    start_date: dt.date | None,
    end_date: dt.date,
    habit_name: str | None,
) -> list[models.HabitRecord]:
    """
    Filter records.

    :param journal_file: Path to the journal file.
    :param start_date: Start date.
    :param end_date: End date.
    :param habit_name: Habit name.
    :return: Filtered records.
    """
    return _filter_state(journal_file, start_date, end_date, habit_name)[1]


def check(journal_file: str, date: dt.date) -> bool:
    """
    Check the journal is consistent at a given date.

    :param journal_file: Path to the journal file.
    :param date: Date to check.
    :return: If it returns something, it means the journal is consistent.
    """
    get_state_at_date(journal_file, date)
    return True


def info(
    journal_file: str,
    start_date: dt.date | None,
    end_date: dt.date,
    habit_name: str | None,
) -> list[models.HabitCompletionInfo]:
    """
    Get information about the completion of habits.

    :param journal_file: Path to the journal file.
    :param start_date: Start date.
    :param end_date: End date.
    :param habit_name: Habit name.
    :return: Information about the completion of habits.
    """
    tracked_habits, records, habits_records_matches = _filter_state(
        journal_file, start_date, end_date, habit_name
    )
    completion_infos = []
    for match in habits_records_matches:
        effective_start_date = match.tracking_start_date
        if start_date and start_date > effective_start_date:
            effective_start_date = start_date

        effective_end_date = end_date
        if match.tracking_end_date and match.tracking_end_date < end_date:
            effective_end_date = match.tracking_end_date

        n_records = len(match.habit_records)
        n_records_expected = match.habit.frequency.get_n_dates(
            effective_start_date, effective_end_date
        )

        non_none_values = [
            record.value for record in match.habit_records if record.value
        ]
        sum_values = sum(float(value) for value in non_none_values)

        round_decimals = 2
        average_total = (
            round(sum_values / n_records_expected, round_decimals)
            if n_records_expected
            else 0
        )
        average_present = (
            round(sum_values / n_records, round_decimals) if n_records else 0
        )

        completion_info = models.HabitCompletionInfo(
            match.habit,
            n_records,
            n_records_expected,
            average_total,
            average_present,
            effective_start_date,
            effective_end_date,
        )
        completion_infos.append(completion_info)

    return completion_infos
