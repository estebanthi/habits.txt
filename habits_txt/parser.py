import datetime as dt
import logging
import re
import typing
from functools import wraps

import croniter

import habits_txt.defaults as defaults
import habits_txt.directives as directives
import habits_txt.exceptions as exceptions
import habits_txt.models as models


def parse_file(file_path: str) -> typing.Tuple[list[directives.Directive], list[str]]:
    """
    Parse a journal file and return a list of directives and a list of parse errors.

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
    If the line is a comment or empty, return None.

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
        date = _parse_date(parts)
        directive_type = _parse_directive_type(parts)
        habit_name = _parse_habit_name(parts)

        if directive_type == directives.DirectiveType.TRACK:
            frequency = _parse_frequency(parts)
            return directives.TrackDirective(date, habit_name, frequency)
        elif directive_type == directives.DirectiveType.UNTRACK:
            return directives.UntrackDirective(date, habit_name)
        elif directive_type == directives.DirectiveType.RECORD:
            value = _parse_value(parts)
            return directives.RecordDirective(date, habit_name, value)

    except IndexError:
        raise exceptions.ParseError(f"Invalid directive format: {directive_line}")

    return None


def _handle_index_error_decorator(name):
    """
    Handle IndexError exceptions in the wrapped function.

    :param func: Function to wrap.
    :param name: Name of the directive part.
    :return: Wrapped function.
    """

    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            try:
                return func(*args, **kwargs)
            except IndexError:
                raise exceptions.ParseError(
                    f"Could not parse {name}. Probably because of missing parts in"
                    f" the directive definition."
                )

        return wrapper

    return decorator


@_handle_index_error_decorator(name="date")
def _parse_date(directive_parts: list[str]) -> dt.date:
    """
    Parse the date from a list of directive parts.

    The date is ALWAYS the first part of the directive.

    :param parts: Directive parts.
    :return: Parsed date.

    Example:
    >>> directive_parts = ['2024-01-01', 'track', '"Sample', 'habit"', '*', '*', '*']
    >>> date = _parse_date(directive_parts)
    >>> print(date)
    2024-01-01
    """
    date_str = directive_parts[0]
    try:
        date = dt.datetime.strptime(date_str, defaults.DATE_FMT).date()
    except ValueError:
        raise exceptions.ParseError(f"Invalid date format: {date_str}")
    return date


@_handle_index_error_decorator(name="directive type")
def _parse_directive_type(directive_parts: list[str]) -> directives.DirectiveType:
    """
    Parse the directive type from a list of directive parts.

    The directive type is the second part of the directive. But it can be omitted and will result in
    a record directive.

    :param directive_parts: Directive parts.
    :return: Parsed directive type.

    Example:
    >>> directive_parts = ['2024-01-01', 'track', '"Sample', 'habit"', '*', '*', '*']
    >>> directive_type = _parse_directive_type(directive_parts)
    >>> print(directive_type)
    track
    """
    directive_type_str = directive_parts[1]
    try:
        # If there is no directive type, it is a record directive
        if re.match(rf'[{"".join(defaults.ALLOWED_QUOTES)}]', directive_type_str):
            return directives.DirectiveType.RECORD
        return directives.DirectiveType(directive_type_str)
    except ValueError:
        raise exceptions.ParseError(f"Invalid directive type: {directive_type_str}")


@_handle_index_error_decorator(name="habit name")
def _parse_habit_name(directive_parts: list[str]) -> str:
    """
    Parse the habit name from a list of directive parts.

    Parsing is done by joining all parts and searching for a string enclosed in quotes.

    :param directive_parts: Directive parts.
    :return: Parsed habit name.

    Example:
    >>> parts = ['2024-01-01', 'track', '"Sample', 'habit"', '*', '*', '*']
    >>> habit_name = _parse_habit_name(directive_parts)
    >>> print(habit_name)
    Sample habit
    """
    joined_parts = " ".join(directive_parts)
    habit_name = re.search(
        rf'[{"".join(defaults.ALLOWED_QUOTES)}].*[{"".join(defaults.ALLOWED_QUOTES)}]',
        joined_parts,
    )
    if habit_name is None:
        raise exceptions.ParseError(f"Invalid habit name format: {joined_parts}")
    return habit_name.group(0)[1:-1]  # [1:-1] to remove quotes


@_handle_index_error_decorator(name="frequency")
def _parse_frequency(directive_parts: list[str]) -> models.Frequency:
    """
    Parse the frequency from a list of directive parts.

    The frequency is ALWAYS the last three parts of a track directive.

    :param directive_parts: Directive parts.
    :return: Parsed frequency.

    Example:
    >>> directive_parts = ['2024-01-01', 'track', '"Sample', 'habit"', '*', '*', '*']
    >>> frequency = _parse_frequency(directive_parts)
    """
    day, month, day_of_week = directive_parts[-3:]
    cron_expression = f"0 0 {day} {month} {day_of_week}"
    try:
        croniter.croniter(cron_expression)
        return models.Frequency(day, month, day_of_week)
    except ValueError:
        raise exceptions.ParseError(f"Invalid frequency format: {cron_expression}")


@_handle_index_error_decorator(name="value")
def _parse_value(directive_parts: list[str]) -> bool | float:
    """
    Parse the value from a list of directive parts.

    The value is ALWAYS the last part of a record directive.

    :param value_str: Value string.
    :return: Parsed value.

    Example:
    >>> value_str = "yes"
    >>> value = _parse_value(value_str)
    >>> print(value)
    True
    """
    value_str = directive_parts[-1]
    return parse_value_str(value_str)


def parse_value_str(value_str: str) -> bool | float:
    """
    Parse the value from a string.

    :param value_str: Value string.
    :return: Parsed value.

    Example:
    >>> value_str = "yes"
    >>> value = parse_value_str(value_str)
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
