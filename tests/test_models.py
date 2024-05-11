import datetime as dt

import src.models as models


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
