import datetime as dt
import logging
import typing

import click
from plotly import express as px

import habits_txt.builder as builder
import habits_txt.config as config
import habits_txt.defaults as defaults
import habits_txt.exceptions as exceptions
import habits_txt.models as models
import habits_txt.parser as parser
import habits_txt.records_query as records_query
from habits_txt.date import get_date_range
from habits_txt.style import style_habit_input


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


def fill(
    journal_file: str,
    date: dt.date,
    start_date: dt.date | None,
    end_date: dt.date | None,
    interactive: bool = False,
) -> list[models.HabitRecord]:
    """
    Fill a day in the journal.

    :param journal_file: Path to the journal file.
    :param date: Date to fill.
    :param start_date: Start date to fill from.
    :param end_date: End date to fill to.
    :param interactive: Interactive mode.
    :return: Journal file.
    """
    if start_date or end_date:
        return _fill_range(journal_file, start_date, end_date, interactive)
    return _fill_day(journal_file, date, interactive)[0]


def _fill_range(
    journal_file: str,
    start_date: dt.date | None,
    end_date: dt.date | None,
    interactive: bool = False,
) -> list[models.HabitRecord]:
    if start_date and not end_date:
        end_date = dt.date.today()
    if end_date and not start_date:
        start_date = _get_first_date(journal_file)
    if not start_date or not end_date:
        return []
    records_fill = []
    for date in get_date_range(start_date, end_date, dt.timedelta(days=1)):
        records, stop = _fill_day(journal_file, date, interactive)
        records_fill.extend(records)
        if stop:
            break
    return records_fill


def _get_first_date(journal_file: str) -> dt.date:
    _, records, _ = get_state_at_date(journal_file, dt.date.today())
    return min(record.date for record in records)


def _fill_day(
    journal_file: str,
    date: dt.date,
    interactive: bool = False,
) -> typing.Tuple[list[models.HabitRecord], bool]:
    records_fill: list[models.HabitRecord] = []
    tracked_habits, records, habits_records_matches = get_state_at_date(
        journal_file, date
    )
    if not tracked_habits:
        logging.info(
            f"{config.get('comment_char', 'CLI', defaults.COMMENT_CHAR)} No habits tracked"
        )
        return [], False
    for habit in sorted(tracked_habits, key=lambda habit_: habit_.name):
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
                parsed_metadata = {}
                while not value_is_valid:
                    value = click.prompt(
                        style_habit_input(date, habit.name),
                        default="",
                        show_default=False,
                        show_choices=False,
                    )
                    if value == "s":
                        append = False
                        break
                    elif value == "a":
                        break
                    elif value == "save":
                        return records_fill, True
                    value_is_valid = True
                    try:
                        parsed_metadata = parser.parse_metadata(value)
                    except exceptions.ParseError as e:
                        logging.error(e)
                        value_is_valid = False
                        continue
                    try:
                        parsed_value = parser.parse_value(value)
                    except exceptions.ParseError:
                        logging.error(
                            f"Value must be a {"number" if habit.is_measurable else "boolean"}.\n"
                            "(or 's' to skip, 'a' to append to the journal but fill manually later, and "
                            "'save' to save and exit)"
                        )
                        value_is_valid = False
                record = models.HabitRecord(
                    date, habit.name, parsed_value, parsed_metadata
                )
            else:
                record = models.HabitRecord(date, habit.name, None, {})

            if append:
                records_fill.append(record)

    return records_fill, False


def _filter_state(
    journal_file: str,
    start_date: dt.date | None,
    end_date: dt.date,
    habit_name: typing.Tuple[str, ...] | None,
    metadata: dict[str, str] | None,
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
    :param metadata: Metadata.
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
            if (not habit_name or habit.name in habit_name)
        ]
    )

    filtered_records = [
        record
        for record in records
        if start_date <= record.date <= end_date
        and (not habit_name or record.habit_name in habit_name)
        and (
            not metadata
            or (
                record.metadata
                and all(record.metadata.get(k) == v for k, v in metadata.items())
            )
        )
    ]

    filtered_habits_records_matches = []
    for match in habits_records_matches:
        if match.tracking_start_date > end_date or (
            match.tracking_end_date and match.tracking_end_date < start_date
        ):
            continue
        if habit_name and match.habit.name not in habit_name:
            continue
        match.habit_records = [
            record
            for record in match.habit_records
            if start_date <= record.date <= end_date
            and (
                not metadata
                or (
                    record.metadata
                    and all(record.metadata.get(k) == v for k, v in metadata.items())
                )
            )
        ]
        filtered_habits_records_matches.append(match)

    return filtered_tracked_habits, filtered_records, filtered_habits_records_matches


def filter(
    journal_file: str,
    start_date: dt.date | None,
    end_date: dt.date,
    habit_name: typing.Tuple[str, ...] | None,
    metadata: dict[str, str] | None,
) -> list[models.HabitRecord]:
    """
    Filter records.

    :param journal_file: Path to the journal file.
    :param start_date: Start date.
    :param end_date: End date.
    :param habit_name: Habit name.
    :param metadata: Metadata.
    :return: Filtered records.
    """
    return _filter_state(journal_file, start_date, end_date, habit_name, metadata)[1]


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
    habit_name: typing.Tuple[str, ...] | None,
    metadata: dict[str, str] | None,
    ignore_missing: bool = False,
) -> list[models.HabitCompletionInfo]:
    """
    Get information about the completion of habits.

    :param journal_file: Path to the journal file.
    :param start_date: Start date.
    :param end_date: End date.
    :param habit_name: Habit name.
    :param metadata: Metadata.
    :param ignore_missing: Ignore missing records when computing stats.
    :return: Information about the completion of habits.
    """
    tracked_habits, records, habits_records_matches = _filter_state(
        journal_file, start_date, end_date, habit_name, metadata
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

        # add missing records
        sorted_records = sorted(match.habit_records, key=lambda record: record.date)
        all_records = []
        next_expected_date = None
        for record in sorted_records:
            if next_expected_date:
                while next_expected_date < record.date:
                    all_records.append(
                        models.HabitRecord(next_expected_date, match.habit.name, None)
                    )
                    next_expected_date = match.habit.frequency.get_next_date(
                        next_expected_date
                    )
            all_records.append(record)
            next_expected_date = match.habit.frequency.get_next_date(record.date)

        if next_expected_date and next_expected_date <= effective_end_date:
            while next_expected_date <= effective_end_date:
                all_records.append(
                    models.HabitRecord(next_expected_date, match.habit.name, None)
                )
                next_expected_date = match.habit.frequency.get_next_date(
                    next_expected_date
                )

        longest_streak_total = records_query.get_longest_streak(
            match.habit, all_records
        )
        latest_streak_total = records_query.get_latest_streak(match.habit, all_records)

        longest_streak = records_query.get_longest_streak(
            match.habit, match.habit_records
        )
        latest_streak = records_query.get_latest_streak(
            match.habit, match.habit_records
        )

        completion_info = models.HabitCompletionInfo(
            match.habit,
            n_records,
            n_records_expected,
            average_present if ignore_missing else average_total,
            longest_streak if ignore_missing else longest_streak_total,
            latest_streak if ignore_missing else latest_streak_total,
            effective_start_date,
            effective_end_date,
        )
        completion_infos.append(completion_info)

    return completion_infos


def chart(
    journal_file: str,
    interval: str,
    start_date: dt.date | None,
    end_date: dt.date,
    habit_name: typing.Tuple[str, ...] | None,
    metadata: dict[str, str] | None,
    ignore_missing: bool = False,
) -> None:
    """
    Get information about the completion of habits in a chart.

    :param journal_file: Path to the journal file.
    :param interval: Interval (weekly or monthly).
    :param start_date: Start date.
    :param end_date: End date.
    :param habit_name: Habit name.
    :param metadata: Metadata.
    :param ignore_missing: Ignore missing records when computing stats.
    """
    if interval == "weekly":
        interval_td = dt.timedelta(weeks=1)
    elif interval == "monthly":
        interval_td = dt.timedelta(weeks=4)
    else:
        raise ValueError(f"Invalid interval: {interval}")

    tracked_habits, records, habits_records_matches = _filter_state(
        journal_file, start_date, end_date, habit_name, metadata
    )

    if not records:
        logging.info(
            f"{config.get('comment_char', 'CLI', defaults.COMMENT_CHAR)} No records to plot"
        )
        return

    if not start_date:
        start_date = min(record.date for record in records)

    records_by_interval: dict[dt.date, list[models.HabitRecord]] = {}
    for record in records:
        interval_start = record.date - (record.date - start_date) % interval_td
        if interval_start not in records_by_interval:
            records_by_interval[interval_start] = []
        records_by_interval[interval_start].append(record)

    if len(records_by_interval) < 2:
        logging.info(
            f"{config.get('comment_char', 'CLI', defaults.COMMENT_CHAR)} Not enough data to plot"
        )
        return

    completion_infos = []
    for interval_start, interval_records in records_by_interval.items():
        interval_end = interval_start + interval_td - dt.timedelta(days=1)
        interval_completion_infos = info(
            journal_file,
            interval_start,
            interval_end,
            habit_name,
            metadata,
            ignore_missing,
        )
        completion_infos.extend(interval_completion_infos)

    if not completion_infos:
        logging.info(
            f"{config.get('comment_char', 'CLI', defaults.COMMENT_CHAR)} No data to plot"
        )
        return

    habit_names = [info_.habit.name for info_ in completion_infos]
    interval_starts = [info_.start_date for info_ in completion_infos]
    average_value = [info_.average_value for info_ in completion_infos]

    fig = px.line(
        x=interval_starts,
        y=average_value,
        color=habit_names,
        labels={"x": "Date", "y": "Average completion"},
        title="Average completion by habit",
    )
    fig.show()


def tracked(
    journal_file: str, date: dt.date
) -> list[typing.Tuple[models.Habit, dt.date]]:
    """
    Get the tracked habits at a given date.

    :param journal_file: Path to the journal file.
    :param date: Date to use.
    :return: Tracked habits and their tracking start date.
    """
    _, _, matches = get_state_at_date(journal_file, date)
    return [
        (match.habit, match.tracking_start_date)
        for match in matches
        if match.tracking_end_date is None
    ]
