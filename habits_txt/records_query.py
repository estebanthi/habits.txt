import habits_txt.models as models


def get_most_recent_record(
    habit: models.Habit, records: list[models.HabitRecord]
) -> models.HabitRecord:
    """
    Get the most recent record for a habit.

    :param habit: Habit.
    :param records: List of records.
    :return: Most recent record.
    """
    return max(
        (record for record in records if record.habit_name == habit.name),
        key=lambda record: record.date,
    )


def get_most_recent_and_completed_record(
    habit: models.Habit, records: list[models.HabitRecord]
) -> models.HabitRecord:
    """
    Get the most recent completed record for a habit.

    :param habit: Habit.
    :param records: List of records.
    :return: Most recent completed record.
    """
    return max(
        (
            record
            for record in records
            if record.habit_name == habit.name and record.is_complete
        ),
        key=lambda record: record.date,
    )


def get_longest_streak(habit: models.Habit, records: list[models.HabitRecord]) -> int:
    """
    Get the longest streak for a habit.

    :param habit: Habit.
    :param records: List of records.
    :return: Longest streak.
    """
    streak = 0
    longest_streak = 0
    for record in records:
        if record.habit_name != habit.name:
            continue
        if record.value:
            streak += 1
        else:
            longest_streak = max(streak, longest_streak)
            streak = 0
    return max(streak, longest_streak)


def get_latest_streak(habit: models.Habit, records: list[models.HabitRecord]) -> int:
    """
    Get the latest streak for a habit.

    :param habit: Habit.
    :param records: List of records.
    :return: Current streak.
    """
    streak = 0
    for record in reversed(records):
        if record.habit_name != habit.name:
            continue
        if record.value:
            streak += 1
        else:
            break
    return streak
