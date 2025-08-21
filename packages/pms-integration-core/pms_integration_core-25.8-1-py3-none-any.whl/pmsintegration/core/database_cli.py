import typer


app = typer.Typer(
    pretty_exceptions_show_locals=False,
)


@app.command()
def check():
    """Check the database connection.

    """
    from pmsintegration.core.cli_commands import pmsdb
    pmsdb.run_check(typer.secho)


@app.callback()
def main(ctx: typer.Context):  # noqa
    """Database Tools

    To automate the repeated tasks which related with middleware database.
    """


@app.command()
def migrate():
    """Migrate the database scripts

    To automate the schema migration
    """
    from pmsintegration.core.cli_commands import pmsdb
    pmsdb.run_migrate(typer.secho)


def register(parent: typer.Typer):
    parent.add_typer(app, name="database")


if __name__ == '__main__':
    app()
