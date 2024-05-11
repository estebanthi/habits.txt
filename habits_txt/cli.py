import argparse
import datetime as dt
import logging

import habits_txt.defaults as defaults
import habits_txt.journal as journal


def parse_args(args: list[str]) -> argparse.Namespace:
    """
    Parse arguments.

    :param args: List of arguments.
    :return: Parsed arguments.
    """
    parser = argparse.ArgumentParser()

    command_subparsers = parser.add_subparsers(dest="command")

    fill_parser = command_subparsers.add_parser(
        "fill",
        help="Fill habits on a given date",
        description="Fill habits on a given date",
    )
    fill_parser.add_argument(
        "--date",
        help="Date to use (defaults to today)",
        default=dt.date.today().strftime(defaults.DATE_FMT),
    )
    fill_parser.add_argument(
        "--interactive", help="Interactive mode", action="store_true"
    )
    fill_parser.add_argument(
        "--write-top",
        help="Write output to the top of the journal file",
        action="store_true",
    )
    fill_parser.add_argument(
        "--write-bottom",
        help="Write output to the bottom of the journal file",
        action="store_true",
    )

    filter_parser = command_subparsers.add_parser(
        "filter", help="Filter habit records", description="Filter habit records"
    )
    filter_parser.add_argument("--start", help="Start date", default=None)
    filter_parser.add_argument(
        "--end", help="End date", default=dt.date.today().strftime(defaults.DATE_FMT)
    )
    filter_parser.add_argument("--habit", help="Habit to filter", default=None)

    parser.add_argument("file", help="Journal file to read")
    return parser.parse_args(args)


def run_command(args: argparse.Namespace):
    """
    Run a command.

    :param args: Parsed arguments.
    """

    def run_fill():
        records = journal.fill_day(
            args.file,
            dt.datetime.strptime(args.date, defaults.DATE_FMT).date(),
            args.interactive,
        )
        if records:
            records_str = (
                "\n".join([str(record) for record in records]) if records else ""
            )
            output(args.file, records_str, args.write_top, args.write_bottom)

    if not args.command:
        run_fill()
    if args.command == "fill":
        run_fill()
    if args.command == "filter":
        start_date = (
            dt.datetime.strptime(args.start, defaults.DATE_FMT).date()
            if args.start
            else None
        )
        end_date = dt.datetime.strptime(args.end, defaults.DATE_FMT).date()
        records = journal.filter(args.file, start_date, end_date, args.habit)
        if records:
            records_str = "\n".join([str(record) for record in records])
            logging.info(records_str)
        else:
            logging.info("No records found")


def output(file: str, string: str, write_top: bool, write_bottom: bool):
    """
    Output a string to the console or a file.

    :param file: File to write to.
    :param string: String to write.
    :param write_top: Write to the top of the file.
    :param write_bottom: Write to the bottom of the file.
    """
    if write_top:
        with open(file, "r") as f:
            content = f.read()
        with open(file, "w") as f:
            f.write(string + "\n\n" + content)
    elif write_bottom:
        with open(file, "a") as f:
            f.write("\n" + string + "\n")
    else:
        print(string)
