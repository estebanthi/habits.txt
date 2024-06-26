import datetime as dt
from dataclasses import dataclass

import croniter

import habits_txt.config as config
import habits_txt.defaults as defaults


class Frequency:
    """
    Frequency of a habit. Intraday frequencies are not supported.
    """

    def __init__(self, cron_str: str):
        self.cron_str = cron_str
        self._process_cron_str()
        self._validate_cron_str()

    def _process_cron_str(self):
        if len(self.cron_str.split()) == 3:
            self.cron_str = f"0 0 {self.cron_str}"

    def _validate_cron_str(self):
        today = dt.date.today()
        try:
            cron = croniter.croniter(
                self.cron_str, dt.datetime(today.year, today.month, today.day)
            )
        except ValueError:
            raise ValueError(f"Invalid cron string: {self.cron_str}")
        if cron.get_next(dt.datetime) < dt.datetime(
            today.year, today.month, today.day, 23, 59, 59, 999999
        ):
            raise ValueError("Intraday frequencies are not supported.")

    def get_next_date(self, date: dt.date) -> dt.date:
        """
        Get the next date based on the frequency.

        :param date: Current date.
        :return: Next date.
        """
        cron = croniter.croniter(self.cron_str, dt.datetime.combine(date, dt.time()))
        return cron.get_next(dt.datetime).date()

    def get_n_dates(self, start_date: dt.date, end_date: dt.date) -> int:
        """
        Get the number of dates between two dates based on the frequency.

        :param start_date: Start date.
        :param end_date: End date.
        :return: Number of dates.
        """
        n_dates = 1
        date = start_date
        while date <= end_date:
            date = self.get_next_date(date)
            if date <= end_date:
                n_dates += 1
        return n_dates

    def __repr__(self):
        if self.cron_str.startswith("0 0"):
            return self.cron_str[4:]
        return self.cron_str

    def __eq__(self, other):
        return self.cron_str == other.cron_str


@dataclass
class Habit:
    """
    Habit tracked by the user.

    Example:
      name: "Sample habit"
      frequency: Frequency("* * *")
      is_measurable: False
    """

    name: str
    frequency: Frequency
    is_measurable: bool = False
    metadata: dict | None = None

    def __post_init__(self):
        if self.metadata is None:
            self.metadata = {}

    def __hash__(self):
        return hash(self.name)


@dataclass
class HabitRecord:
    """
    Record of a habit on a specific date.

    Example:
        date: dt.date(2024, 1, 1)
        habit_name: "Sample habit"
        value: 2.0
    """

    date: dt.date
    habit_name: str
    value: bool | float | None
    metadata: dict | None = None

    def __post_init__(self):
        if self.metadata is None:
            self.metadata = {}

    @property
    def is_complete(self) -> bool:
        return self.value is not None

    def __str__(self) -> str:
        return (
            f"{dt.datetime.strftime(self.date, config.get("date_fmt", "CLI", defaults.DATE_FMT))} "
            f'"{self.habit_name}"{" " + self._str_meta() if self._str_meta() else ""} {self._str_value()}'
        )

    def _str_meta(self) -> str:
        meta = []
        if not self.metadata:
            return ""
        for key, value in self.metadata.items():
            meta.append(f"{key}:{value}")
        return " ".join(meta)

    def _str_value(self) -> str:
        if self.value is True:
            return defaults.BOOLEAN_TRUE
        elif self.value is False:
            return defaults.BOOLEAN_FALSE
        elif self.value is None:
            return ""
        return str(self.value)


@dataclass
class HabitCompletionInfo:
    """
    Information about the completion of a habit.
    """

    habit: Habit
    n_records: int
    n_records_expected: int
    average_value: float
    longest_streak: int
    latest_streak: int
    start_date: dt.date
    end_date: dt.date | None


@dataclass
class HabitRecordMatch:
    """
    Match between a habit and its records.
    """

    habit: Habit
    habit_records: list[HabitRecord]
    tracking_start_date: dt.date
    tracking_end_date: dt.date | None
