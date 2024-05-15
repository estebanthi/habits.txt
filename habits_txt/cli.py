import datetime as dt
import os

import click

import habits_txt.config as config_
import habits_txt.defaults as defaults
import habits_txt.journal as journal_


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
    """
    records = journal_.fill_day(
        file.name,
        date,
        interactive,
    )
    if records:
        records_str = "\n".join([str(record) for record in records]) if records else ""
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
        records_str = "\n".join([str(record) for record in records])
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
            click.echo(
                f"{habit_completion_info.habit.name} ({habit_completion_info.start_date} - "
                f"{habit_completion_info.end_date}):"
            )
            click.echo(f"  Total records in journal: {habit_completion_info.n_records}")
            click.echo(
                f"  Total records expected: {habit_completion_info.n_records_expected}"
            )
            click.echo(
                f"  Missing records: "
                f"{habit_completion_info.n_records_expected - habit_completion_info.n_records}"
            )
            value_str = (
                "Average value"
                if habit_completion_info.habit.is_measurable
                else "Completion rate"
            )

            def process_average(x):
                return (
                    round(x, 2)
                    if habit_completion_info.habit.is_measurable
                    else str(x * 100) + "%"
                )

            click.echo(
                f"  {value_str} (among all records): {process_average(habit_completion_info.average_total)}"
            )
            click.echo(
                f"  {value_str} (among present records): "
                f"{process_average(habit_completion_info.average_present)}"
            )
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
        "Journal file is consistent" if is_valid else "Journal file is inconsistent"
    )
