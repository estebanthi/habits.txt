import datetime as dt


def build_dates_between_dates(first_date: dt.date, last_date: dt.date) -> list[dt.date]:
    """
    Build a list of dates between two dates.

    :param first_date: First date.
    :param last_date: Last date.
    :return: List of dates.

    Example:
    >>> dates = build_dates_between_dates(dt.date(2024, 1, 1), dt.date(2024, 1, 3))
    >>> print(dates)
    [datetime.date(2024, 1, 1), datetime.date(2024, 1, 2), datetime.date(2024, 1, 3)]
    """
    return [
        first_date + dt.timedelta(days=i)
        for i in range((last_date - first_date).days + 1)
    ]
