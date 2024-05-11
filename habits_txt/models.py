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


@dataclass
class Habit:
    """
    Habit tracked by the user.

    Example:
      name: "Sample habit"
      frequency: Frequency("*", "*", "*")
    """

    name: str
    frequency: Frequency

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
        return bool(self.value)

    def __str__(self) -> str:
        return (f'{dt.datetime.strftime(self.date, defaults.DATE_FMT)} '
                f'"{self.habit_name}" {self.value if self.value is not None else ""}')
