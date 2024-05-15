import datetime as dt
from enum import Enum

import habits_txt.defaults as defaults
import habits_txt.models as models


class DirectiveType(Enum):
    TRACK = "track"
    UNTRACK = "untrack"
    RECORD = "record"


class Directive:

    directive_type: DirectiveType

    def __init__(self, date: dt.date, habit_name: str, lineno: int):
        self.date = date
        self.habit_name = habit_name
        self.lineno = lineno

    def __eq__(self, other):
        return self.date == other.date and self.habit_name == other.habit_name

    def __repr__(self):
        return f'{self.date} {self.directive_type.value} "{self.habit_name}"'


class TrackDirective(Directive):

    directive_type = DirectiveType.TRACK

    def __init__(
        self,
        date: dt.date,
        habit_name: str,
        lineno: int,
        frequency: models.Frequency,
        is_measurable: bool,
    ):
        super().__init__(date, habit_name, lineno)
        self.frequency = frequency
        self.is_measurable = is_measurable

    def __eq__(self, other):
        return (
            super().__eq__(other)
            and self.frequency == other.frequency
            and self.is_measurable == other.is_measurable
        )

    def __repr__(self):
        return (
            super().__repr__()
            + f" {self.frequency} {defaults.MEASURABLE_KEYWORD if self.is_measurable else ''}"
        )


class UntrackDirective(Directive):

    directive_type = DirectiveType.UNTRACK

    def __init__(self, date: dt.date, habit_name: str, lineno: int):
        super().__init__(date, habit_name, lineno)


class RecordDirective(Directive):

    directive_type = DirectiveType.RECORD

    def __init__(
        self, date: dt.date, habit_name: str, lineno: int, value: bool | float
    ):
        super().__init__(date, habit_name, lineno)
        self.value = value

    def __eq__(self, other):
        return super().__eq__(other) and self.value == other.value

    def __repr__(self):
        return (super().__repr__() + f" {self._str_value()}").strip()

    def _str_value(self) -> str:
        if self.value is True:
            return defaults.BOOLEAN_TRUE
        elif self.value is False:
            return defaults.BOOLEAN_FALSE
        elif self.value is None:
            return ""
        return str(self.value)
