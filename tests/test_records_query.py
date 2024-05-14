import datetime as dt

import habits_txt.records_query as records_query


def test_get_most_recent_record():
    frequency = records_query.models.Frequency("*", "*", "*")
    habit1 = records_query.models.Habit("Habit 1", frequency)
    habit2 = records_query.models.Habit("Habit 2", frequency)
    record1 = records_query.models.HabitRecord(dt.date(2024, 1, 1), habit1.name, False)
    record2 = records_query.models.HabitRecord(dt.date(2024, 1, 2), habit1.name, True)
    record3 = records_query.models.HabitRecord(dt.date(2024, 1, 3), habit2.name, False)
    record4 = records_query.models.HabitRecord(dt.date(2024, 1, 4), habit2.name, True)
    records = [record1, record2, record3, record4]

    most_recent_record = records_query.get_most_recent_record(habit1, records)
    assert most_recent_record == record2

    most_recent_record = records_query.get_most_recent_record(habit2, records)
    assert most_recent_record == record4

    records = [record4, record3, record2, record1]
    most_recent_record = records_query.get_most_recent_record(habit1, records)
    assert most_recent_record == record2

    most_recent_record = records_query.get_most_recent_record(habit2, records)
    assert most_recent_record == record4


def test_get_most_recent_and_completed_record():
    frequency = records_query.models.Frequency("*", "*", "*")
    habit1 = records_query.models.Habit("Habit 1", frequency)
    record1 = records_query.models.HabitRecord(dt.date(2024, 1, 1), habit1.name, False)
    record2 = records_query.models.HabitRecord(dt.date(2024, 1, 2), habit1.name, True)
    record3 = records_query.models.HabitRecord(dt.date(2024, 1, 3), habit1.name, False)

    records = [record1, record2, record3]
    most_recent_and_completed_record = (
        records_query.get_most_recent_and_completed_record(habit1, records)
    )
    assert most_recent_and_completed_record == record2
