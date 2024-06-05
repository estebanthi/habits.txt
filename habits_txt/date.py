import datetime as dt


def get_date_range(
    start: dt.date, end: dt.date, step: dt.timedelta, inclusive: bool = True
) -> list[dt.date]:
    """
    Get a list of dates between two dates.

    :param start: Start date.
    :param end: End date.
    :param step: Step.
    :param inclusive: Include the end date.
    :return: List of dates.
    """
    if start > end:
        raise ValueError("Start date must be before end date")
    if step.total_seconds() < 60 * 60 * 24:
        raise ValueError("Step must be greater than one day")
    dates = []
    date = start
    while date <= end:
        dates.append(date)
        date += step
    if not inclusive and dates[-1] == end:
        dates.pop()
    return dates
