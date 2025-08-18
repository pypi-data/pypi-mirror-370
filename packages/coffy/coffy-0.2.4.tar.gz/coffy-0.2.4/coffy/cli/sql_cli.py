# coffy/cli/sql_cli.py
# author: nsarathy

import click
from coffy import sql


@click.group()
def sql_cli():
    """
    CLI for Coffy SQL engine.
    """
    pass


@sql_cli.command()
@click.option(
    "--db",
    type=click.Path(),
    default=None,
    help="Path to SQLite database (default: in-memory).",
)
def init(db):
    """
    Initialize SQL engine.
    db -- Path to SQLite database file. If not provided, uses an in-memory database.
    """
    sql.init(db)
    click.echo(f"Initialized SQL engine (db: {db or 'in-memory'})")


@sql_cli.command()
@click.argument("query")
def run(query):
    """
    Run a SQL query and print results.
    query -- SQL query to run.
    """
    result = sql.query(query)
    if hasattr(result, "view"):  # SELECT
        click.echo(result)
    else:
        click.echo(result)


@sql_cli.command()
@click.argument("query")
def view(query):
    """
    Run a SQL SELECT query and open results in browser.
    query -- SQL SELECT query to run.
    """
    result = sql.query(query)
    if hasattr(result, "view"):
        result.view()
        click.echo("Opened query results in browser.")
    else:
        click.echo("Not a SELECT query.")


@sql_cli.command()
def close():
    """
    Close SQL engine connection.
    """
    sql.close()
    click.echo("Closed SQL engine connection.")
