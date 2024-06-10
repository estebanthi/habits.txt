import datetime as dt
import os

import click
from dateparser import parse

import habits_txt.config as config_
import habits_txt.defaults as defaults
import habits_txt.journal as journal_
import habits_txt.style as style_


@click.group()
@click.version_option()
def cli():
    pass


def _parse_date_callback(ctx, param, value):
    try:
        return parse(value).date() if value else None
    except Exception:
        raise click.BadParameter(
            "Invalid date format. Use YYYY-MM-DD or natural language"
        )


def _parse_metadata_callback(ctx, param, value):
    if value:
        try:
            return {meta.split(":")[0]: meta.split(":")[1] for meta in value}
        except ValueError:
            raise click.BadParameter("Invalid metadata format. Use meta:value")


@cli.command()
@click.argument("file", type=click.File("r+"))
@click.option(
    "-d",
    "--date",
    default=dt.date.today().strftime(defaults.DATE_FMT),
    callback=_parse_date_callback,
    help="Date to use (defaults to today)",
)
@click.option(
    "-s",
    "--start",
    callback=_parse_date_callback,
    help="Start date",
)
@click.option(
    "-e",
    "--end",
    callback=_parse_date_callback,
    help="End date",
)
@click.option("-m", "--missing", is_flag=True, help="Fill missing records")
@click.option("-i", "--interactive", is_flag=True, help="Interactive mode")
@click.option(
    "-t",
    "--write-top",
    is_flag=True,
    help="Write output to the top of the journal file",
)
@click.option(
    "-b",
    "--write-bottom",
    is_flag=True,
    help="Write output to the bottom of the journal file",
)
@click.option(
    "-n",
    "--no-comment",
    is_flag=True,
    help="Do not add a comment to the output",
)
def fill(
    file, date, start, end, missing, interactive, write_top, write_bottom, no_comment
):
    """
    Fill habits on a given date using FILE.

    Interactive mode allows you to be prompted to fill each habit.
    If you want to skip a habit while in interactive mode, just press 's'.
    If you want to skip a habit but still append it to the journal (for manual filling later), press 'a'.
    """
    if missing:
        start = None
        end = dt.date.today()
    records = journal_.fill(
        file.name,
        date,
        start,
        end,
        interactive,
    )
    if records:
        records_str = "\n".join(
            [style_.style_habit_record(record) for record in records]
        )
        comment = f"{config_.get(
            'comment_char', 'CLI', defaults.COMMENT_CHAR
        )} Filled on {dt.datetime.now().strftime(config_.get(
            'date_fmt', 'CLI', defaults.DATE_FMT))}"
        records_str = f"{comment}\n{records_str}" if not no_comment else records_str
        if write_top or write_bottom:
            records_str = click.unstyle(records_str)
        if write_top:
            content = file.read()
            file.seek(0)
            records_str = "\n".join(reversed(records_str.split("\n")))  # reverse lines
            file.write(records_str + "\n\n" + content)
        elif write_bottom:
            file.write("\n" + records_str + "\n")
        else:
            click.echo(records_str)
    else:
        click.echo(
            f"{config_.get('comment_char', 'CLI', defaults.COMMENT_CHAR)} Nothing to fill for {date}"
        )


@cli.command()
@click.argument("file", type=click.File("r"))
@click.option(
    "-s",
    "--start",
    callback=_parse_date_callback,
    help="Start date",
)
@click.option(
    "-e",
    "--end",
    default=dt.date.today().strftime(defaults.DATE_FMT),
    callback=_parse_date_callback,
    help="End date",
)
@click.option(
    "-n",
    "--name",
    help="Filter by habit name. "
    "You can specify multiple names using multiple --name flags",
    multiple=True,
)
@click.option(
    "-m",
    "--metadata",
    help="Filter by metadata. "
    "You can specify multiple metadata using multiple --metadata flags",
    multiple=True,
    callback=_parse_metadata_callback,
)
def filter(file, start, end, name, metadata):
    """
    Filter habit records using FILE.
    """
    records = journal_.filter(file.name, start, end, name, metadata)
    if records:
        records_str = "\n".join(
            [style_.style_habit_record(record) for record in records]
        )
        click.echo(records_str)
    else:
        click.echo(
            f"{config_.get('comment_char', 'CLI', defaults.COMMENT_CHAR)} No records found"
        )


@cli.command()
@click.argument("file", type=click.File("r"))
@click.option(
    "-s",
    "--start",
    callback=_parse_date_callback,
    help="Start date",
)
@click.option(
    "-e",
    "--end",
    default=dt.date.today().strftime(defaults.DATE_FMT),
    callback=_parse_date_callback,
    help="End date",
)
@click.option(
    "-n",
    "--name",
    help="Filter by habit name. "
    "You can specify multiple names using multiple --name flags",
    multiple=True,
)
@click.option(
    "-m",
    "--metadata",
    help="Filter by metadata. "
    "You can specify multiple metadata using multiple --metadata flags",
    multiple=True,
    callback=_parse_metadata_callback,
)
@click.option(
    "--ignore-missing",
    is_flag=True,
    help="Ignore missing records when computing stats",
)
def info(file, start, end, name, metadata, ignore_missing):
    """
    Get information about habit records using FILE.
    """
    habit_completion_infos = journal_.info(
        file.name, start, end, name, metadata, ignore_missing
    )
    if habit_completion_infos:
        for habit_completion_info in habit_completion_infos:
            click.echo(style_.style_completion_info(habit_completion_info))
            click.echo()
    else:
        click.echo(
            f"{config_.get('comment_char', 'CLI', defaults.COMMENT_CHAR)} No records found"
        )


@cli.command()
@click.argument("file", type=click.File("r"))
@click.option(
    "-i", "--interval", type=click.Choice(["weekly", "monthly"]), default="weekly"
)
@click.option(
    "-s",
    "--start",
    callback=_parse_date_callback,
    help="Start date",
)
@click.option(
    "-e",
    "--end",
    default=dt.date.today().strftime(defaults.DATE_FMT),
    callback=_parse_date_callback,
    help="End date",
)
@click.option(
    "-n",
    "--name",
    help="Filter by habit name. "
    "You can specify multiple names using multiple --name flags",
    multiple=True,
)
@click.option(
    "-m",
    "--metadata",
    help="Filter by metadata. "
    "You can specify multiple metadata using multiple --metadata flags",
    multiple=True,
    callback=_parse_metadata_callback,
)
@click.option(
    "--ignore-missing",
    is_flag=True,
    help="Ignore missing records when computing stats",
)
def chart(file, interval, start, end, name, metadata, ignore_missing):
    """
    Generate a chart of habit records using FILE.
    """
    journal_.chart(file.name, interval, start, end, name, metadata, ignore_missing)


""" tracked command to list the tracked habits at the given date"""


@cli.command()
@click.argument("file", type=click.File("r"))
@click.option(
    "-d",
    "--date",
    default=dt.date.today().strftime(defaults.DATE_FMT),
    callback=_parse_date_callback,
    help="Date to use (defaults to today)",
)
def tracked(file, date):
    """
    List the tracked habits at the given date.
    """
    tracked_habits = journal_.tracked(file.name, date)
    if tracked_habits:
        for habit, tracking_start_date in tracked_habits:
            click.echo(style_.style_tracked_habit(habit, tracking_start_date))
    else:
        click.echo(
            f"{config_.get('comment_char', 'CLI', defaults.COMMENT_CHAR)} No habits found"
        )


@cli.command()
@click.argument("file", type=click.File("r"))
def edit(file):
    """
    Edit FILE.
    """
    click.edit(filename=file.name)


@cli.group(help="Configuration settings")
def config():
    config_.setup()


@config.group(help="Set configuration settings")
def set():
    try:
        config_.validate()
    except ValueError as e:
        click.echo(e)
        raise click.Abort()


@set.command()
@click.argument("path", type=click.Path())
def journal(path):
    """
    Set the journal file path.
    """
    config_.set("journal", os.path.abspath(path), "CLI")
    click.echo(f"Journal file path set to {path}")


@set.command()
@click.argument("date_fmt")
def date_fmt(date_fmt):
    """
    Set the date format used in the journal file.
    """
    config_.set("date_fmt", date_fmt, "CLI")
    click.echo(f"Date format set to {date_fmt}")


@set.command()
@click.argument("comment_char")
def comment_char(comment_char):
    """
    Set the comment character used in the journal file.
    """
    config_.set("comment_char", comment_char, "CLI")
    click.echo(f"Comment character set to {comment_char}")


@config.command(help="Get configuration settings")
def get():
    """
    Get all configuration settings.
    """
    try:
        config_.validate()
    except ValueError as e:
        click.echo(e)
        raise click.Abort()
    with open(defaults.APPDATA_PATH + "/config.ini") as f:
        click.echo(f.read())


@config.command(name="edit", help="Edit configuration settings with default editor")
def config_edit():
    """
    Edit configuration settings.
    """
    click.edit(filename=defaults.APPDATA_PATH + "/config.ini")


@cli.command(help="Check the journal file is consistent at a given date")
@click.argument("file", type=click.File("r"))
@click.option(
    "-d",
    "--date",
    default=dt.date.today().strftime(defaults.DATE_FMT),
    callback=_parse_date_callback,
)
def check(file, date):
    """
    Check the journal file is valid.
    """
    is_valid = journal_.check(file.name, date)
    click.echo(
        click.style(
            (
                "The journal file is consistent"
                if is_valid
                else "The journal file is not consistent"
            ),
            fg="green" if is_valid else "red",
        )
    )
