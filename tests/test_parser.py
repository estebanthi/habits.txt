import datetime as dt
import unittest.mock as mock

import pytest

import habits_txt.parser as parser


def test_parse_file(monkeypatch):
    with mock.patch(
        "builtins.open",
        mock.mock_open(read_data="  2024-01-01 track 'Sample habit' * * *  "),
    ):
        monkeypatch.setattr("habits_txt.parser._parse_directive", mock.MagicMock())
        directives, errors = parser.parse_file("example.journal")
        assert len(directives) == 1
        parser._parse_directive.assert_called_once_with(
            "2024-01-01 track 'Sample habit' * * *"
        )
        assert len(errors) == 0

        monkeypatch.setattr(
            "habits_txt.parser._parse_directive",
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
    parts = ["2024-01-01", "track", "'habit name'", "*", "*", "*"]
    date = parser._parse_date(parts)
    assert date == dt.date(2024, 1, 1)

    with pytest.raises(parser.exceptions.ParseError):
        parser._parse_date(["2024", "01", "a", "track", "'habit name'", "*", "*", "*"])


def test_parse_directive_type():
    parts = ["2024-01-01", "track", "'habit name'", "*", "*", "*"]
    directive_type = parser._parse_directive_type(parts)
    assert directive_type == parser.directives.DirectiveType.TRACK

    parts = ["2024-01-01", "untrack", "'habit name'"]
    directive_type = parser._parse_directive_type(parts)
    assert directive_type == parser.directives.DirectiveType.UNTRACK

    parts = ["2024-01-01", "'habit name'", "yes"]
    directive_type = parser._parse_directive_type(parts)
    assert directive_type == parser.directives.DirectiveType.RECORD

    parts = ["2024-01-01", "'habit name'", "2"]
    directive_type = parser._parse_directive_type(parts)
    assert directive_type == parser.directives.DirectiveType.RECORD

    parts = ["2024-01-01", "invalid", "5"]
    with pytest.raises(parser.exceptions.ParseError):
        parser._parse_directive_type(parts)


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
    parts = ["2024-01-01", "'habit name'", "10"]
    value = parser._parse_value(parts)
    assert value == 10.0

    parts = ["2024-01-01", "'habit name'", "a"]
    with pytest.raises(parser.exceptions.ParseError):
        parser._parse_value(parts)

    parts = ["2024-01-01", "'habit name'", parser.defaults.BOOLEAN_TRUE]
    value = parser._parse_value(parts)
    assert value is True

    parts = ["2024-01-01", "'habit name'", parser.defaults.BOOLEAN_FALSE]
    value = parser._parse_value(parts)
    assert value is False


def test_parse_value_str():
    value = parser.parse_value_str("yes")
    assert value is True

    value = parser.parse_value_str("no")
    assert value is False

    value = parser.parse_value_str("10")
    assert value == 10.0

    with pytest.raises(parser.exceptions.ParseError):
        parser.parse_value_str("a")


def test_handle_index_error_decorator():
    @parser._handle_index_error_decorator(name="value")
    def _parse_value(directive_parts: list[str]) -> bool | float:
        return directive_parts[100]

    with pytest.raises(parser.exceptions.ParseError):
        _parse_value(["2024-01-01", "'habit name'", "10"])
