import datetime as dt
import unittest.mock as mock

import pytest

import habits_txt.models as models
import habits_txt.parser as parser


def test_parse_file(monkeypatch):
    with mock.patch(
        "builtins.open",
        mock.mock_open(read_data="  2024-01-01 track 'Sample habit' (* * *)  "),
    ):
        monkeypatch.setattr("habits_txt.parser._parse_directive", mock.MagicMock())
        directives, errors = parser.parse_file("example.journal")
        assert len(directives) == 1
        parser._parse_directive.assert_called_once_with(
            "2024-01-01 track 'Sample habit' (* * *)",
            1,
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
    directive_line = "2024-01-01 track 'Sample habit' (* * *)"
    directive = parser._parse_directive(directive_line, 1)
    assert directive == parser.directives.TrackDirective(
        dt.date(2024, 1, 1),
        "Sample habit",
        1,
        {},
        models.Frequency("* * *"),
        False,
    )

    directive_line = (
        f"2024-01-01 track 'Sample habit' (* * *) {parser.defaults.MEASURABLE_KEYWORD}"
    )
    directive = parser._parse_directive(directive_line, 1)
    assert directive == parser.directives.TrackDirective(
        dt.date(2024, 1, 1),
        "Sample habit",
        1,
        {},
        models.Frequency("* * *"),
        True,
    )

    directive_line = "2024-01-02 'Sample habit' yes"
    directive = parser._parse_directive(directive_line, 2)
    assert directive == parser.directives.RecordDirective(
        dt.date(2024, 1, 2), "Sample habit", 2, True, {}
    )

    directive_line = "2024-01-03 untrack 'Sample habit'"
    directive = parser._parse_directive(directive_line, 3)
    assert directive == parser.directives.UntrackDirective(
        dt.date(2024, 1, 3), "Sample habit", 3, {}
    )

    directive_line = "2024-01-04 'Sample habit' 2"
    directive = parser._parse_directive(directive_line, 4)
    assert directive == parser.directives.RecordDirective(
        dt.date(2024, 1, 4), "Sample habit", 4, 2.0, {}
    )

    assert parser._parse_directive("", 5) is None
    assert parser._parse_directive(parser.defaults.COMMENT_CHAR, 6) is None

    directive_line = "2024-01-01 track 'Sample habit' (* * *) meta:test"
    directive = parser._parse_directive(directive_line, 7)
    assert directive == parser.directives.TrackDirective(
        dt.date(2024, 1, 1),
        "Sample habit",
        7,
        {"meta": "test"},
        models.Frequency("* * *"),
        False,
    )

    monkeypatch.setattr(
        "habits_txt.parser._parse_directive_type",
        mock.MagicMock(return_value="unknown"),
    )
    directive_line = "2024-01-01 unknown 'Sample habit' (* * *)"
    assert parser._parse_directive(directive_line, 7) is None


def test_parse_date():
    directive_line = "2024-01-01 track 'Sample habit' (* * *)"
    date = parser._parse_date(directive_line)
    assert date == dt.date(2024, 1, 1)

    with pytest.raises(parser.exceptions.ParseError):
        parser._parse_date("2024-01-0 track 'Sample habit' (* * *)")

    with pytest.raises(parser.exceptions.ParseError):
        parser._parse_date("0000-01-01 track 'Sample habit' (* * *)")


def test_parse_directive_type():
    directive_line = "2024-01-01 track 'Sample habit' (* * *)"
    directive_type = parser._parse_directive_type(directive_line)
    assert directive_type == parser.directives.DirectiveType.TRACK

    directive_line = "2024-01-01 untrack 'habit name'"
    directive_type = parser._parse_directive_type(directive_line)
    assert directive_type == parser.directives.DirectiveType.UNTRACK

    directive_line = "2024-01-01 'habit name' yes"
    directive_type = parser._parse_directive_type(directive_line)
    assert directive_type == parser.directives.DirectiveType.RECORD

    directive_line = "2024-01-01 'habit name' 2"
    directive_type = parser._parse_directive_type(directive_line)
    assert directive_type == parser.directives.DirectiveType.RECORD

    directive_line = "2024-01-01 invalid 5"
    with pytest.raises(parser.exceptions.ParseError):
        parser._parse_directive_type(directive_line)

    directive_line = "2024-01-01"
    with pytest.raises(parser.exceptions.ParseError):
        parser._parse_directive_type(directive_line)


def test_parse_habit_name():
    directive_line = "2024-04-01 track 'habit name' (* * *)"
    habit_name = parser._parse_habit_name(directive_line)
    assert habit_name == "habit name"

    directive_line = "2024-04-01 track 'habit name' (* * *)"
    habit_name = parser._parse_habit_name(directive_line)
    assert habit_name == "habit name"

    with pytest.raises(parser.exceptions.ParseError):
        directive_line = "2024-04-01 track habit name (* * *)"
        parser._parse_habit_name(directive_line)


def test_parse_frequency():
    directive_line = "2024-01-01 track 'Sample habit' (* * *)"
    frequency = parser._parse_frequency(directive_line)
    assert frequency == models.Frequency("* * *")

    with pytest.raises(parser.exceptions.ParseError):
        directive_line = "2024-01-01 track 'Sample habit' (* * a)"
        parser._parse_frequency(directive_line)

    with pytest.raises(parser.exceptions.ParseError):
        directive_line = "2024-01-01 track 'Sample habit' * * *"
        parser._parse_frequency(directive_line)

    with pytest.raises(parser.exceptions.ParseError):
        directive_line = "2024-01-01 track 'Sample habit' (* *)"
        parser._parse_frequency(directive_line)

    with pytest.raises(parser.exceptions.ParseError):
        directive_line = "2024-01-01 track 'Sample habit' (* * * *)"
        parser._parse_frequency(directive_line)

    directive_line = "2024-01-01 track 'Sample habit' (@daily)"
    frequency = parser._parse_frequency(directive_line)
    assert frequency == models.Frequency("@daily")

    directive_line = "2024-01-01 track 'Sample habit' (@hourly)"
    with pytest.raises(parser.exceptions.ParseError):
        parser._parse_frequency(directive_line)


def test_parse_value():
    directive_line = "2024-01-01 'habit name' 10"
    value = parser.parse_value(directive_line)
    assert value == 10.0

    directive_line = "2024-01-01 'habit name' a"
    with pytest.raises(parser.exceptions.ParseError):
        parser.parse_value(directive_line)

    directive_line = f"2024-01-01 'habit name' {parser.defaults.BOOLEAN_TRUE}"
    value = parser.parse_value(directive_line)
    assert value is True

    directive_line = f"2024-01-01 'habit name' {parser.defaults.BOOLEAN_FALSE}"
    value = parser.parse_value(directive_line)
    assert value is False


def test_parse_value_str():
    value = parser._parse_value_str("yes")
    assert value is True

    value = parser._parse_value_str("no")
    assert value is False

    value = parser._parse_value_str("10")
    assert value == 10.0

    with pytest.raises(parser.exceptions.ParseError):
        parser._parse_value_str("a")


def test_handle_index_error_decorator():
    @parser._handle_index_error_decorator(name="value")
    def _parse_value(directive_parts: list[str]):
        return directive_parts[100]

    with pytest.raises(parser.exceptions.ParseError):
        _parse_value(["2024-01-01", "'habit name'", "10"])
