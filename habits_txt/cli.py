import datetime as dt
import os

import click

import habits_txt.config as config_
import habits_txt.defaults as defaults
import habits_txt.journal as journal_
import habits_txt.models as models_


@click.group()
def cli():
    pass


@cli.command()
@click.argument("file", type=click.File("r+"))
@click.option(
    "-d",
    "--date",
    type=click.DateTime(formats=["%Y-%m-%d"]),
    default=dt.date.today().strftime(defaults.DATE_FMT),
    callback=lambda ctx, param, value: value.date(),
    help="Date to use (defaults to today)",
)
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
def fill(file, date, interactive, write_top, write_bottom):
    """
    Fill habits on a given date using FILE.

    Interactive mode allows you to be prompted to fill each habit.
    If you want to skip a habit while in interactive mode, just press 's'.
    If you want to skip a habit but still append it to the journal (for manual filling later), press 'a'.
    """
    records = journal_.fill_day(
        file.name,
        date,
        interactive,
    )
    if records:
        records_str = "\n".join([_style_record(record) for record in records])
        if write_top or write_bottom:
            records_str = click.unstyle(records_str)
        if write_top:
            content = file.read()
            file.seek(0)
            file.write(records_str + "\n\n" + content)
        elif write_bottom:
            file.write("\n" + records_str + "\n")
        else:
            click.echo(records_str)
    else:
        click.echo(f"{defaults.COMMENT_CHAR} Nothing to fill for {date}")


@cli.command()
@click.argument("file", type=click.File("r"))
@click.option(
    "-s",
    "--start",
    type=click.DateTime(formats=["%Y-%m-%d"]),
    callback=lambda ctx, param, value: value.date() if value else None,
    help="Start date",
)
@click.option(
    "-e",
    "--end",
    type=click.DateTime(formats=["%Y-%m-%d"]),
    default=dt.date.today().strftime(defaults.DATE_FMT),
    callback=lambda ctx, param, value: value.date(),
    help="End date",
)
@click.option("-n", "--name", help="Filter by habit name")
def filter(file, start, end, name):
    """
    Filter habit records using FILE.
    """
    records = journal_.filter(file.name, start, end, name)
    if records:
        records_str = "\n".join([_style_record(record) for record in records])
        click.echo(records_str)
    else:
        click.echo(f"{defaults.COMMENT_CHAR} No records found")


@cli.command()
@click.argument("file", type=click.File("r"))
@click.option(
    "-s",
    "--start",
    type=click.DateTime(formats=["%Y-%m-%d"]),
    callback=lambda ctx, param, value: value.date() if value else None,
    help="Start date",
)
@click.option(
    "-e",
    "--end",
    type=click.DateTime(formats=["%Y-%m-%d"]),
    default=dt.date.today().strftime(defaults.DATE_FMT),
    callback=lambda ctx, param, value: value.date(),
    help="End date",
)
@click.option("-n", "--name", help="Filter by habit name")
def info(file, start, end, name):
    """
    Get information about habit records using FILE.
    """
    habit_completion_infos = journal_.info(file.name, start, end, name)
    if habit_completion_infos:
        for habit_completion_info in habit_completion_infos:
            click.echo(_style_completion_info(habit_completion_info))
            click.echo()
    else:
        click.echo(f"{defaults.COMMENT_CHAR} No records found")


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
    type=click.DateTime(formats=["%Y-%m-%d"]),
    default=dt.date.today().strftime(defaults.DATE_FMT),
    callback=lambda ctx, param, value: value.date(),
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


def _style_record(record: models_.HabitRecord) -> str:
    return " ".join(
        [
            click.style(
                dt.datetime.strftime(record.date, defaults.DATE_FMT), fg="blue"
            ),
            f'"{click.style(record.habit_name, fg="green")}"',
            click.style(record._str_value(), fg="yellow"),
        ]
    )


def _style_completion_info(habit_completion_info: models_.HabitCompletionInfo) -> str:
    def process_average(x):
        return (
            round(x, 2)
            if habit_completion_info.habit.is_measurable
            else str(x * 100) + "%"
        )

    value_str = (
        "Average value"
        if habit_completion_info.habit.is_measurable
        else "Completion rate"
    )

    string = "\n".join(
        [
            click.style(habit_completion_info.habit.name, fg="green")
            + " ("
            + click.style(
                f"{habit_completion_info.start_date} - {habit_completion_info.end_date}",
                fg="blue",
            )
            + "):",
            click.style(
                "  Total records in journal:",
                fg="cyan",
            )
            + click.style(
                f" {habit_completion_info.n_records}",
                fg="bright_cyan",
            ),
            click.style(
                "  Total records expected:",
                fg="cyan",
            )
            + click.style(
                f" {habit_completion_info.n_records_expected}",
                fg="bright_cyan",
            ),
            click.style(
                "  Missing records:",
                fg="red",
            )
            + click.style(
                f" {habit_completion_info.n_records_expected - habit_completion_info.n_records}",
                fg="bright_red",
            ),
            click.style(
                f"  {value_str} (among expected records):",
                fg="magenta",
            )
            + click.style(
                f" {process_average(habit_completion_info.average_total)}",
                fg="bright_magenta",
            ),
            click.style(
                f"  {value_str} (among written records):",
                fg="magenta",
            )
            + click.style(
                f" {process_average(habit_completion_info.average_present)}",
                fg="bright_magenta",
            ),
        ]
    )
    return string
