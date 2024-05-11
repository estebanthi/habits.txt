import datetime as dt
import logging

import src.builder as builder
import src.defaults as defaults
import src.exceptions as exceptions
import src.models as models
import src.parser as parser


def get_state_at_date(
    journal_file: str, date: dt.date
) -> (set[models.Habit], list[models.HabitRecord]):
    """
    Get the state of the habits at a given date.

    :param journal_file: Path to the journal file.
    :param date: Date to check.
    :return: Tracked habits, records.
    """
    directives, errors = parser.parse_file(journal_file)
    _log_errors(errors)
    return builder.get_state_at_date(directives, date)


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
    tracked_habits, records = get_state_at_date(journal_file, date)
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
            most_recent_and_completed_record = _get_most_recent_and_completed_record(
                habit, records
            )
            next_due_date = habit.frequency.get_next_date(
                most_recent_and_completed_record.date
            )
        if next_due_date <= date:
            if interactive:
                value_is_valid = False
                while not value_is_valid:
                    value = input(f"{habit.name} ({next_due_date}): ")
                    try:
                        parsed_value = parser._parse_value(value)
                        value_is_valid = True
                    except exceptions.ParseError as e:
                        logging.error(e)
                record = models.HabitRecord(date, habit.name, parsed_value)
            else:
                record = models.HabitRecord(date, habit.name, None)
            records_fill.append(record)

    return records_fill


def _get_most_recent_record(
    habit: models.Habit, records: list[models.HabitRecord]
) -> models.HabitRecord:
    """
    Get the most recent record for a habit.

    :param habit: Habit.
    :param records: List of records.
    :return: Most recent record.
    """
    return max(
        (record for record in records if record.habit_name == habit.name),
        key=lambda record: record.date,
    )


def _get_most_recent_and_completed_record(
    habit: models.Habit, records: list[models.HabitRecord]
) -> models.HabitRecord:
    """
    Get the most recent completed record for a habit.

    :param habit: Habit.
    :param records: List of records.
    :return: Most recent completed record.
    """
    return max(
        (
            record
            for record in records
            if record.habit_name == habit.name and record.is_complete
        ),
        key=lambda record: record.date,
    )


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
    tracked_habits, records = get_state_at_date(journal_file, end_date)
    if not start_date:
        try:
            start_date = min(record.date for record in records)
        except ValueError:
            return []
    return [
        record
        for record in records
        if start_date <= record.date <= end_date
        and (not habit_name or record.habit_name == habit_name)
    ]
