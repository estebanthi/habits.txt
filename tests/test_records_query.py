import datetime as dt

import habits_txt.models as models
import habits_txt.records_query as records_query


def test_get_most_recent_record():
    frequency = models.Frequency("* * *")
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
    frequency = models.Frequency("* * *")
    habit1 = records_query.models.Habit("Habit 1", frequency)
    record1 = records_query.models.HabitRecord(dt.date(2024, 1, 1), habit1.name, False)
    record2 = records_query.models.HabitRecord(dt.date(2024, 1, 2), habit1.name, True)
    record3 = records_query.models.HabitRecord(dt.date(2024, 1, 3), habit1.name, False)
    record4 = records_query.models.HabitRecord(dt.date(2024, 1, 4), habit1.name, None)

    records = [record1, record2, record3, record4]
    most_recent_and_completed_record = (
        records_query.get_most_recent_and_completed_record(habit1, records)
    )
    assert most_recent_and_completed_record == record3


def test_get_longest_streak():
    frequency = models.Frequency("* * *")
    habit1 = records_query.models.Habit("Habit 1", frequency)
    record1 = records_query.models.HabitRecord(dt.date(2024, 1, 1), habit1.name, False)
    record2 = records_query.models.HabitRecord(dt.date(2024, 1, 2), habit1.name, True)
    record3 = records_query.models.HabitRecord(dt.date(2024, 1, 3), habit1.name, False)
    longest_streak = records_query.get_longest_streak(
        habit1, [record1, record2, record3]
    )
    assert longest_streak == 1

    record4 = records_query.models.HabitRecord(dt.date(2024, 1, 4), habit1.name, True)
    record5 = records_query.models.HabitRecord(dt.date(2024, 1, 5), habit1.name, True)
    record6 = records_query.models.HabitRecord(dt.date(2024, 1, 6), habit1.name, False)
    longest_streak = records_query.get_longest_streak(
        habit1, [record1, record2, record3, record4, record5, record6]
    )
    assert longest_streak == 2

    record7 = records_query.models.HabitRecord(dt.date(2024, 1, 7), habit1.name, True)
    record8 = records_query.models.HabitRecord(dt.date(2024, 1, 8), habit1.name, True)
    record9 = records_query.models.HabitRecord(dt.date(2024, 1, 9), habit1.name, True)
    longest_streak = records_query.get_longest_streak(
        habit1,
        [
            record1,
            record2,
            record3,
            record4,
            record5,
            record6,
            record7,
            record8,
            record9,
        ],
    )
    assert longest_streak == 3

    record10 = records_query.models.HabitRecord(dt.date(2024, 1, 12), habit1.name, True)
    longest_streak = records_query.get_longest_streak(
        habit1,
        [
            record1,
            record2,
            record3,
            record4,
            record5,
            record6,
            record7,
            record8,
            record9,
            record10,
        ],
    )
    assert longest_streak == 4


def test_get_current_streak():
    frequency = models.Frequency("* * *")
    habit1 = records_query.models.Habit("Habit 1", frequency)
    record1 = records_query.models.HabitRecord(dt.date(2024, 1, 1), habit1.name, False)
    record2 = records_query.models.HabitRecord(dt.date(2024, 1, 2), habit1.name, True)
    record3 = records_query.models.HabitRecord(dt.date(2024, 1, 3), habit1.name, False)
    latest_streak = records_query.get_latest_streak(habit1, [record1, record2, record3])
    assert latest_streak == 0

    record4 = records_query.models.HabitRecord(dt.date(2024, 1, 4), habit1.name, True)
    record5 = records_query.models.HabitRecord(dt.date(2024, 1, 5), habit1.name, True)
    record6 = records_query.models.HabitRecord(dt.date(2024, 1, 6), habit1.name, False)
    latest_streak = records_query.get_latest_streak(
        habit1, [record1, record2, record3, record4, record5, record6]
    )
    assert latest_streak == 0

    record7 = records_query.models.HabitRecord(dt.date(2024, 1, 7), habit1.name, True)
    record8 = records_query.models.HabitRecord(dt.date(2024, 1, 8), habit1.name, True)
    record9 = records_query.models.HabitRecord(dt.date(2024, 1, 9), habit1.name, True)
    latest_streak = records_query.get_latest_streak(
        habit1,
        [
            record1,
            record2,
            record3,
            record4,
            record5,
            record6,
            record7,
            record8,
            record9,
        ],
    )
    assert latest_streak == 3

    record10 = records_query.models.HabitRecord(dt.date(2024, 1, 12), habit1.name, True)
    latest_streak = records_query.get_latest_streak(
        habit1,
        [
            record1,
            record2,
            record3,
            record4,
            record5,
            record6,
            record7,
            record8,
            record9,
            record10,
        ],
    )
    assert latest_streak == 4
