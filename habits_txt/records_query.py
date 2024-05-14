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
