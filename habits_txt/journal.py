import datetime as dt
import logging
import typing

import habits_txt.builder as builder
import habits_txt.defaults as defaults
import habits_txt.exceptions as exceptions
import habits_txt.models as models
import habits_txt.parser as parser
import habits_txt.records_query as records_query


def get_state_at_date(
    journal_file: str, date: dt.date
) -> typing.Tuple[set[models.Habit], list[models.HabitRecord]]:
    """
    Get the state of the habits at a given date.

    :param journal_file: Path to the journal file.
    :param date: Date to check.
    :return: Tracked habits, records.
    """
    directives, parse_errors = parser.parse_file(journal_file)
    _log_errors(parse_errors)
    try:
        tracked_habits, records = builder.get_state_at_date(directives, date)
    except exceptions.ConsistencyError as e:
        logging.error(e)
        logging.error("Cannot continue due to consistency errors")
        exit(1)

    return tracked_habits, records


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
            most_recent_and_completed_record = (
                records_query.get_most_recent_and_completed_record(habit, habit_records)
            )
            next_due_date = habit.frequency.get_next_date(
                most_recent_and_completed_record.date
            )
        if next_due_date <= date:
            if interactive:
                value_is_valid = False
                parsed_value = None
                while not value_is_valid:
                    value = input(f"{habit.name} ({next_due_date}): ")
                    try:
                        parsed_value = parser.parse_value_str(value)
                        value_is_valid = True
                    except exceptions.ParseError as e:
                        logging.error(e)
                record = models.HabitRecord(date, habit.name, parsed_value)
            else:
                record = models.HabitRecord(date, habit.name, None)
            records_fill.append(record)

    return records_fill


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
