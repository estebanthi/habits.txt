import datetime as dt

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


@cli.group()
def config():
    config_.setup()


@config.group()
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
    config_.set("journal", path, "CLI")
    click.echo(f"Journal file path set to {path}")


@config.command()
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


@config.command()
def edit():
    """
    Edit configuration settings.
    """
    click.edit(filename=defaults.APPDATA_PATH + "/config.ini")
