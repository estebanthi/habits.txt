import datetime as dt
import unittest.mock as mock

import pytest

import src.parser as parser


def test_parse_file(monkeypatch):
    with mock.patch(
        "builtins.open",
        mock.mock_open(read_data="  2024-01-01 track 'Sample habit' * * *  "),
    ):
        monkeypatch.setattr("src.parser._parse_directive", mock.MagicMock())
        directives, errors = parser.parse_file("example.journal")
        assert len(directives) == 1
        parser._parse_directive.assert_called_once_with(
            "2024-01-01 track 'Sample habit' * * *"
        )
        assert len(errors) == 0

        monkeypatch.setattr(
            "src.parser._parse_directive",
            mock.MagicMock(side_effect=parser.exceptions.ParseError("Error")),
        )
        directives, errors = parser.parse_file("example.journal")
        assert len(directives) == 0
        assert len(errors) == 1


def test_parse_directive(monkeypatch):
    directive_line = "2024-01-01 track 'Sample habit' * * *"
    directive = parser._parse_directive(directive_line)
    assert directive == parser.directives.TrackDirective(
        dt.date(2024, 1, 1), "Sample habit", parser.models.Frequency("*", "*", "*")
    )

    directive_line = "2024-01-02 'Sample habit' yes"
    directive = parser._parse_directive(directive_line)
    assert directive == parser.directives.RecordDirective(
        dt.date(2024, 1, 2), "Sample habit", True
    )

    directive_line = "2024-01-03 untrack 'Sample habit'"
    directive = parser._parse_directive(directive_line)
    assert directive == parser.directives.UntrackDirective(
        dt.date(2024, 1, 3), "Sample habit"
    )

    directive_line = "2024-01-04 'Sample habit' 2"
    directive = parser._parse_directive(directive_line)
    assert directive == parser.directives.RecordDirective(
        dt.date(2024, 1, 4), "Sample habit", 2.0
    )

    assert parser._parse_directive("") is None
    assert parser._parse_directive(parser.defaults.COMMENT_CHAR) is None


def test_parse_date():
    date = parser._parse_date("2024-01-01")
    assert date == dt.date(2024, 1, 1)

    with pytest.raises(parser.exceptions.ParseError):
        parser._parse_date("2024-01-32")


def test_parse_directive_type():
    directive_type = parser._parse_directive_type("track")
    assert directive_type == parser.directives.DirectiveType.TRACK

    directive_type = parser._parse_directive_type("untrack")
    assert directive_type == parser.directives.DirectiveType.UNTRACK

    directive_type = parser._parse_directive_type("record")
    assert directive_type == parser.directives.DirectiveType.RECORD

    directive_type = parser._parse_directive_type("'habit name'")
    assert directive_type == parser.directives.DirectiveType.RECORD

    with pytest.raises(parser.exceptions.ParseError):
        parser._parse_directive_type("invalid")


def test_parse_habit_name():
    habit_name = parser._parse_habit_name(["2024-04-01", "track", "'habit name'"])
    assert habit_name == "habit name"

    habit_name = parser._parse_habit_name(
        ["2024-04-01", "track", "'habit name'", "*", "*", "*"]
    )
    assert habit_name == "habit name"

    with pytest.raises(parser.exceptions.ParseError):
        parser._parse_habit_name(["2024-04-01", "track", "habit name"])


def test_parse_frequency():
    frequency = parser._parse_frequency(["*", "*", "*"])
    assert frequency == parser.models.Frequency("*", "*", "*")

    with pytest.raises(parser.exceptions.ParseError):
        parser._parse_frequency(["*", "*", "a"])


def test_parse_value():
    value = parser._parse_value("10")
    assert value == 10.0

    with pytest.raises(parser.exceptions.ParseError):
        parser._parse_value("a")

    value = parser._parse_value(parser.defaults.BOOLEAN_TRUE)
    assert value is True

    value = parser._parse_value(parser.defaults.BOOLEAN_FALSE)
    assert value is False
