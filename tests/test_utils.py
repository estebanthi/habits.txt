import datetime as dt

import habits_txt.utils as utils


def test_build_dates_between_dates():
    date_start = dt.date(2024, 1, 1)
    date_end = dt.date(2024, 1, 3)

    dates = utils.build_dates_between_dates(date_start, date_end)
    assert dates == [dt.date(2024, 1, 1), dt.date(2024, 1, 2), dt.date(2024, 1, 3)]
