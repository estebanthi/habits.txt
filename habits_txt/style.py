import datetime as dt
from enum import Enum

import click

import habits_txt.config as config
import habits_txt.defaults as defaults
import habits_txt.models as models_


class Colors(Enum):
    HABIT_NAME_fg = "green"
    HABIT_NAME_bg = None
    HABIT_NAME_bold = False

    DATE_fg = "blue"
    DATE_bg = None
    DATE_bold = False

    VALUE_fg = "yellow"
    VALUE_bg = None
    VALUE_bold = False

    TOTAL_RECORDS_fg = "cyan"
    TOTAL_RECORDS_bg = None
    TOTAL_RECORDS_bold = False

    TOTAL_RECORDS_EXPECTED_fg = "cyan"
    TOTAL_RECORDS_EXPECTED_bg = None
    TOTAL_RECORDS_EXPECTED_bold = False

    N_RECORDS_fg = "bright_cyan"
    N_RECORDS_bg = None
    N_RECORDS_bold = False

    N_RECORDS_MISSING_fg = "bright_red"
    N_RECORDS_MISSING_bg = None
    N_RECORDS_MISSING_bold = False

    MISSING_RECORDS_fg = "red"
    MISSING_RECORDS_bg = None
    MISSING_RECORDS_bold = False

    AVERAGE_fg = "magenta"
    AVERAGE_bg = None
    AVERAGE_bold = False

    AVERAGE_VALUE_fg = "bright_magenta"
    AVERAGE_VALUE_bg = None
    AVERAGE_VALUE_bold = True

    FREQUENCY_fg = "bright_yellow"
    FREQUENCY_bg = None
    FREQUENCY_bold = False

    LONGEST_STREAK_fg = "bright_green"
    LONGEST_STREAK_bg = None
    LONGEST_STREAK_bold = False

    LONGEST_STREAK_VALUE_fg = "green"
    LONGEST_STREAK_VALUE_bg = None
    LONGEST_STREAK_VALUE_bold = False

    LATEST_STREAK_fg = "bright_green"
    LATEST_STREAK_bg = None
    LATEST_STREAK_bold = False

    LATEST_STREAK_VALUE_fg = "green"
    LATEST_STREAK_VALUE_bg = None
    LATEST_STREAK_VALUE_bold = False

    META_fg = "cyan"
    META_bg = None
    META_bold = False


def _style_str(s: str, key: str) -> str:
    return click.style(
        s,
        fg=Colors[key + "_fg"].value,
        bg=Colors[key + "_bg"].value,
        bold=Colors[key + "_bold"].value,
    )


def style_habit_record(record: models_.HabitRecord) -> str:
    return " ".join(
        [
            _style_str(
                dt.datetime.strftime(
                    record.date, config.get("date_fmt", "CLI", defaults.DATE_FMT)
                ),
                "DATE",
            ),
            f'"{_style_str(record.habit_name, "HABIT_NAME")}"',
            _style_str(record._str_meta(), "META"),
            _style_str(record._str_value(), "VALUE"),
        ]
    )


def style_habit_input(date: dt.date, habit_name: str) -> str:
    return f"{_style_str(date.strftime(config.get(
        "date_fmt", "CLI", defaults.DATE_FMT)), "DATE")} - {_style_str(habit_name, "HABIT_NAME")}: "


def style_completion_info(habit_completion_info: models_.HabitCompletionInfo) -> str:
    def process_average(x):
        return (
            round(x, 2)
            if habit_completion_info.habit.is_measurable
            else str(round(x * 100, 2)) + "%"
        )

    value_str = (
        "Average value"
        if habit_completion_info.habit.is_measurable
        else "Completion rate"
    )

    string = "\n".join(
        [
            _style_str(habit_completion_info.habit.name, "HABIT_NAME")
            + " ("
            + _style_str(
                f"{habit_completion_info.start_date} - {habit_completion_info.end_date}",
                "DATE",
            )
            + "):",
            _style_str("  Total records in journal:", "TOTAL_RECORDS")
            + _style_str(f" {habit_completion_info.n_records}", "N_RECORDS"),
            _style_str("  Total records expected:", "TOTAL_RECORDS_EXPECTED")
            + _style_str(f" {habit_completion_info.n_records_expected}", "N_RECORDS"),
            _style_str("  Missing records:", "MISSING_RECORDS")
            + _style_str(
                f" {habit_completion_info.n_records_expected - habit_completion_info.n_records}",
                "N_RECORDS_MISSING",
            ),
            _style_str(f"  {value_str}:", "AVERAGE")
            + _style_str(
                f" {process_average(habit_completion_info.average_value)}",
                "AVERAGE_VALUE",
            ),
            _style_str("  Longest streak:", "LONGEST_STREAK")
            + _style_str(
                f" {habit_completion_info.longest_streak}", "LONGEST_STREAK_VALUE"
            ),
            _style_str("  Latest streak:", "LATEST_STREAK")
            + _style_str(
                f" {habit_completion_info.latest_streak}", "LATEST_STREAK_VALUE"
            ),
        ]
    )
    return string


def style_tracked_habit(habit: models_.Habit, tracking_start_date: dt.date) -> str:
    return (
        "Since "
        + _style_str(
            dt.datetime.strftime(
                tracking_start_date, config.get("date_fmt", "CLI", defaults.DATE_FMT)
            ),
            "DATE",
        )
        + ": "
        + _style_str(habit.name, "HABIT_NAME")
        + " "
        + _style_str(
            f"({habit.frequency})",
            "FREQUENCY",
        )
        + " "
        + (
            _style_str(
                "[measurable]",
                "VALUE",
            )
            if habit.is_measurable
            else ""
        )
    )
