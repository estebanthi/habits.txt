import datetime as dt

import habits_txt.models as models


def test_frequency_next_date():
    frequency = models.Frequency("*", "*", "*")
    date = dt.date(2024, 1, 1)
    next_date = frequency.get_next_date(date)
    assert next_date == dt.date(2024, 1, 2)

    frequency = models.Frequency("1", "*", "*")
    date = dt.date(2024, 1, 1)
    next_date = frequency.get_next_date(date)
    assert next_date == dt.date(2024, 2, 1)

    frequency = models.Frequency("*", "2", "*")
    date = dt.date(2024, 1, 1)
    next_date = frequency.get_next_date(date)
    assert next_date == dt.date(2024, 2, 1)


def test_str_frequency():
    frequency = models.Frequency("*", "*", "*")
    assert str(frequency) == "* * *"


def test_habit_hash():
    habit1 = models.Habit("habit1", models.Frequency("*", "*", "*"))
    habit2 = models.Habit("habit2", models.Frequency("*", "*", "*"))
    habit3 = models.Habit("habit1", models.Frequency("*", "*", "*/5"))
    assert habit1.__hash__() != habit2.__hash__()
    assert habit1.__hash__() == habit1.__hash__()
    assert habit1.__hash__() == habit3.__hash__()


def test_habit_record():
    record = models.HabitRecord(dt.date(2024, 1, 1), "habit1", 2.0)
    assert record.date == dt.date(2024, 1, 1)
    assert record.habit_name == "habit1"
    assert record.value == 2.0
    assert record.is_complete
    assert record._str_value() == "2.0"

    record = models.HabitRecord(dt.date(2024, 1, 1), "habit1", None)
    assert not record.is_complete
    assert record._str_value() == ""

    record = models.HabitRecord(dt.date(2024, 1, 1), "habit1", False)
    assert record.is_complete
    assert record._str_value() == models.defaults.BOOLEAN_FALSE

    record = models.HabitRecord(dt.date(2024, 1, 1), "habit1", True)
    assert record.is_complete
    assert record._str_value() == models.defaults.BOOLEAN_TRUE


def test_str_habit_record(monkeypatch):
    monkeypatch.setattr(models.HabitRecord, "_str_value", lambda self: "2.0")
    record = models.HabitRecord(dt.date(2024, 1, 1), "habit1", 2.0)
    assert str(record) == '2024-01-01 "habit1" 2.0'
