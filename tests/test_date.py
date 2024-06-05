import datetime as dt

import pytest

import habits_txt.date as date_


def test_get_date_range():
    start = dt.date(2021, 1, 1)
    end = dt.date(2021, 1, 3)
    step = dt.timedelta(days=1)
    assert date_.get_date_range(start, end, step) == [
        dt.date(2021, 1, 1),
        dt.date(2021, 1, 2),
        dt.date(2021, 1, 3),
    ]

    start = dt.date(2021, 1, 1)
    end = dt.date(2021, 1, 3)
    step = dt.timedelta(days=2)
    assert date_.get_date_range(start, end, step) == [
        dt.date(2021, 1, 1),
        dt.date(2021, 1, 3),
    ]

    start = dt.date(2021, 1, 1)
    end = dt.date(2021, 1, 3)
    step = dt.timedelta(days=3)
    assert date_.get_date_range(start, end, step) == [dt.date(2021, 1, 1)]

    start = dt.date(2021, 1, 1)
    end = dt.date(2021, 1, 3)
    step = dt.timedelta(days=1)
    assert date_.get_date_range(start, end, step, inclusive=False) == [
        dt.date(2021, 1, 1),
        dt.date(2021, 1, 2),
    ]

    with pytest.raises(ValueError):
        start = dt.date(2021, 1, 1)
        end = dt.date(2021, 1, 3)
        step = dt.timedelta(minutes=60)
        assert date_.get_date_range(start, end, step) == [dt.date(2021, 1, 1)]

    with pytest.raises(ValueError):
        start = dt.date(2021, 1, 3)
        end = dt.date(2021, 1, 1)
        step = dt.timedelta(days=1)
        assert date_.get_date_range(start, end, step) == [dt.date(2021, 1, 1)]
