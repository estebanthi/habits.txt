import datetime as dt
import logging
import re

import croniter

import habits_txt.defaults as defaults
import habits_txt.directives as directives
import habits_txt.exceptions as exceptions
import habits_txt.models as models


def parse_file(file_path: str) -> (list[directives.Directive], list[str]):
    """
    Parse a journal file and return a list of directives.

    :param file_path: Path to the journal file.
    :return: List of parsed directives and list of errors.

    Example:
    # example.journal
    2024-01-01 track "Sample habit boolean" * * *  ; start tracking a habit
    2024-01-02 "Sample habit" yes
    2024-01-03 untrack "Sample habit"  ; stop tracking a habit
    2024-01-03 track "Sample habit numerical" * * *  ; start tracking a habit
    2024-01-04 "Sample habit" 2
    >>> directives, errors = parse_file("example.journal")
    """
    logging.debug(f"Parsing file: {file_path}")

    with open(file_path, "r") as file:
        lines = file.readlines()
        lines = [line.strip() for line in lines]

    parsed_directives = []
    errors = []
    for lineno, line in enumerate(lines):
        lineno += 1

        logging.debug(f"Parsing line {lineno}: {line}")

        try:
            parsed_directive = _parse_directive(line)
            if parsed_directive:
                parsed_directives.append(parsed_directive)
        except exceptions.ParseError as e:
            errors.append(f"Error parsing line {lineno}: {e.message}")

    logging.debug(f"Got {len(parsed_directives)} directives")
    return parsed_directives, errors


def _parse_directive(directive_line: str) -> directives.Directive | None:
    """
    Parse a single directive line.

    :param directive_line: Directive line.
    :return: Parsed directive or None if not a directive.

    Example:
    >>> directive_line = '2024-01-01 track "Sample habit" * * *'
    >>> parsed_directive = _parse_directive(directive_line)
    """
    if not directive_line or directive_line.startswith(defaults.COMMENT_CHAR):
        return None
    directive_line = re.sub(r"\s+", " ", directive_line)  # Remove extra spaces

    parts = directive_line.split(" ")
    try:
        date = _parse_date(parts[0])
        directive_type = _parse_directive_type(parts[1])
        habit_name = _parse_habit_name(parts)

        if directive_type == directives.DirectiveType.TRACK:
            frequency = _parse_frequency(parts[-3:])
            return directives.TrackDirective(date, habit_name, frequency)
        elif directive_type == directives.DirectiveType.UNTRACK:
            return directives.UntrackDirective(date, habit_name)
        elif directive_type == directives.DirectiveType.RECORD:
            value = _parse_value(parts[-1])
            return directives.RecordDirective(date, habit_name, value)

    except IndexError:
        raise exceptions.ParseError(f"Invalid directive format: {directive_line}")


def _parse_date(date_str: str) -> dt.date:
    """
    Parse a date string.

    :param date_str: Date string.
    :return: Parsed date.

    Example:
    >>> date_str = "2024-01-01"
    >>> date = _parse_date(date_str)
    >>> print(date)
    2024-01-01
    """
    try:
        date = dt.datetime.strptime(date_str, defaults.DATE_FMT).date()
    except ValueError:
        raise exceptions.ParseError(f"Invalid date format: {date_str}")
    return date


def _parse_directive_type(directive_type_str: str) -> directives.DirectiveType:
    """
    Parse a directive type string.

    :param directive_type_str: Directive type string.
    :return: Parsed directive type.

    Example:
    >>> directive_type_str = "track"
    >>> directive_type = _parse_directive_type(directive_type_str)
    >>> print(directive_type)
    track
    """
    try:
        if re.match(rf'[{"".join(defaults.ALLOWED_QUOTES)}]', directive_type_str):
            return directives.DirectiveType.RECORD
        return directives.DirectiveType(directive_type_str)
    except ValueError:
        raise exceptions.ParseError(f"Invalid directive type: {directive_type_str}")


def _parse_habit_name(parts: list[str]) -> str:
    """
    Parse a habit name string.

    :param parts: Directive parts.
    :return: Parsed habit name.

    Example:
    >>> parts = ['2024-01-01', 'track', '"Sample', 'habit"', '*', '*', '*']
    >>> habit_name = _parse_habit_name(parts)
    >>> print(habit_name)
    Sample habit
    """
    joined_parts = " ".join(parts)
    habit_name = re.search(
        rf'[{"".join(defaults.ALLOWED_QUOTES)}].*[{"".join(defaults.ALLOWED_QUOTES)}]',
        joined_parts,
    )
    if habit_name is None:
        raise exceptions.ParseError(f"Invalid habit name format: {joined_parts}")
    return habit_name.group(0)[1:-1]


def _parse_frequency(frequency_parts: list[str]) -> models.Frequency:
    """
    Parse a frequency string.

    :param frequency_parts: Frequency parts.
    :return: Parsed frequency.

    Example:
    >>> frequency_parts = ['*', '*', '*']
    >>> frequency = _parse_frequency(frequency_parts)
    """
    minute, hour = 0, 0
    day, month, day_of_week = frequency_parts
    cron_expression = f"{minute} {hour} {day} {month} {day_of_week}"
    try:
        croniter.croniter(cron_expression)
        return models.Frequency(day, month, day_of_week)
    except ValueError:
        raise exceptions.ParseError(f"Invalid frequency format: {cron_expression}")


def _parse_value(value_str: str) -> bool | float:
    """
    Parse a value string.

    :param value_str: Value string.
    :return: Parsed value.

    Example:
    >>> value_str = "yes"
    >>> value = _parse_value(value_str)
    >>> print(value)
    True
    """
    if value_str == defaults.BOOLEAN_TRUE:
        return True
    elif value_str == defaults.BOOLEAN_FALSE:
        return False
    try:
        return float(value_str)
    except ValueError:
        raise exceptions.ParseError(f"Value must be a boolean or a number: {value_str}")
