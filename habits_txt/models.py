import datetime as dt
from dataclasses import dataclass

import croniter

import habits_txt.defaults as defaults


@dataclass
class Frequency:
    """
    Frequency of a habit, following a simplified cron-like syntax.

    Example - every weekday:
      day: *
      month: *
      day_of_week: 1-5
    """

    day: str
    month: str
    day_of_week: str

    def get_next_date(self, date: dt.date) -> dt.date:
        """
        Get the next date based on the frequency.

        :param date: Current date.
        :return: Next date.
        """
        cron_str = f"0 0 {self.day} {self.month} {self.day_of_week}"
        cron = croniter.croniter(cron_str, dt.datetime.combine(date, dt.time()))
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

    def __repr__(self) -> str:
        return f"{self.day} {self.month} {self.day_of_week}"


@dataclass
class Habit:
    """
    Habit tracked by the user.

    Example:
      name: "Sample habit"
      frequency: Frequency("*", "*", "*")
      is_measurable: False
    """

    name: str
    frequency: Frequency
    is_measurable: bool = False

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

    @property
    def is_complete(self) -> bool:
        return self.value is not None

    def __str__(self) -> str:
        return (
            f"{dt.datetime.strftime(self.date, defaults.DATE_FMT)} "
            f'"{self.habit_name}" {self._str_value()}'
        )

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
    average_total: float
    average_present: float
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
