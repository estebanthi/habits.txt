import datetime as dt

import habits_txt.directives as directives
import habits_txt.exceptions as exceptions


def test_parse_error():
    error = exceptions.ParseError("Error message")
    assert error.message == "Error message"


def test_consistency_error():
    directive = directives.Directive(dt.date(2024, 1, 1), "Sample habit", 1)
    error = exceptions.ConsistencyError("Error message", directive)
    assert str(error) == "Consistency error in line 1: Error message"
    assert error.message == "Consistency error in line 1: Error message"
