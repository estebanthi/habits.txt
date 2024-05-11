import datetime as dt
from enum import Enum

import habits_txt.models as models


class DirectiveType(Enum):
    TRACK = "track"
    UNTRACK = "untrack"
    RECORD = "record"


class Directive:

    directive_type: DirectiveType

    def __init__(self, date: dt.date, habit_name: str):
        self.date = date
        self.habit_name = habit_name

    def __eq__(self, other):
        return self.date == other.date and self.habit_name == other.habit_name

    def __repr__(self):
        return f"{self.directive_type} {self.date} {self.habit_name}"


class TrackDirective(Directive):

    directive_type = DirectiveType.TRACK

    def __init__(self, date: dt.date, habit_name: str, frequency: models.Frequency):
        super().__init__(date, habit_name)
        self.frequency = frequency

    def __eq__(self, other):
        return super().__eq__(other) and self.frequency == other.frequency

    def __repr__(self):
        return super().__repr__() + f" {self.frequency}"


class UntrackDirective(Directive):

    directive_type = DirectiveType.UNTRACK

    def __init__(self, date: dt.date, habit_name: str):
        super().__init__(date, habit_name)


class RecordDirective(Directive):

    directive_type = DirectiveType.RECORD

    def __init__(self, date: dt.date, habit_name: str, value: bool | float):
        super().__init__(date, habit_name)
        self.value = value

    def __eq__(self, other):
        return super().__eq__(other) and self.value == other.value

    def __repr__(self):
        return super().__repr__() + f" {self.value}"
