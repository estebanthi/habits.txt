import datetime as dt

import habits_txt.defaults as defaults
import habits_txt.directives as directives
import habits_txt.models as models


def test_directive():
    directive1 = directives.Directive(dt.date(2021, 1, 1), "habit1", 1)
    directive2 = directives.Directive(dt.date(2021, 1, 1), "habit1", 2)
    directive1.directive_type = directives.DirectiveType.TRACK

    assert directive1 == directive2
    assert str(directive1) == '2021-01-01 track "habit1"'


def test_track_directive():
    directive1 = directives.TrackDirective(
        dt.date(2021, 1, 1),
        "habit1",
        1,
        models.Frequency("* * *"),
        True,
    )
    directive2 = directives.TrackDirective(
        dt.date(2021, 1, 1),
        "habit1",
        2,
        models.Frequency("* * *"),
        True,
    )

    assert directive1 == directive2
    assert (
        str(directive1)
        == f'2021-01-01 track "habit1" (* * *) {defaults.MEASURABLE_KEYWORD}'
    )


def test_untrack_directive():
    directive1 = directives.UntrackDirective(dt.date(2021, 1, 1), "habit1", 1)
    directive2 = directives.UntrackDirective(dt.date(2021, 1, 1), "habit1", 2)

    assert directive1 == directive2
    assert str(directive1) == '2021-01-01 untrack "habit1"'


def test_record_directive():
    directive1 = directives.RecordDirective(dt.date(2021, 1, 1), "habit1", 1, 1)
    directive2 = directives.RecordDirective(dt.date(2021, 1, 1), "habit1", 2, 1)

    assert directive1 == directive2
    assert str(directive1) == '2021-01-01 record "habit1" 1'

    directive3 = directives.RecordDirective(dt.date(2021, 1, 1), "habit1", 1, True)
    directive4 = directives.RecordDirective(dt.date(2021, 1, 1), "habit1", 2, False)

    assert str(directive3) == f'2021-01-01 record "habit1" {defaults.BOOLEAN_TRUE}'
    assert str(directive4) == f'2021-01-01 record "habit1" {defaults.BOOLEAN_FALSE}'

    directive5 = directives.RecordDirective(dt.date(2021, 1, 1), "habit1", 1, None)
    assert str(directive5) == '2021-01-01 record "habit1"'
