import os
from pathlib import Path

import typer

from pmsintegration.core import database_cli
from pmsintegration.core.app import AppContext
from pmsintegration.core.cli_commands import addepar_field_mappings
from pmsintegration.core.custom_fields import SOURCE_FILE_PATH
from pmsintegration.platform import utils

app = typer.Typer(
    pretty_exceptions_show_locals=False,
)


@app.command()
def generate_addepar_field_mappings(
        output: str = typer.Option(
            help="Path to the output file where the field mapping will be saved",
            default=SOURCE_FILE_PATH
        )
):
    """Generate yml file having the addepar custom fields.

    ```yml
    __note__: Generated
    addepar_custom_fields:
        field_name:
         id:
         category:
    ```
    """
    addepar_field_mappings.run(output, typer.secho)


@app.command()
def info():
    """Show generic information which may amaze you.

    """
    typer.echo("This command is an informative tool")


@app.callback()
def main(ctx: typer.Context):  # noqa
    """Core Tools

    To automate the repeated tasks which are core to the middleware.
    """


@app.command()
def sf_platform_events_consume(
        listeners: list[str] = typer.Option(
            [], "--listener", "-l",
            min=1,
            help="Specify the listeners configuration names. ALL (for all known configuration)",
        )
):
    """A near real-time streaming service that consumes Salesforce Platform Events and
     sinks them into a PMS database table for further processing.

     :param: listeners - list the configuration. See defaults.yml#listeners.salesforce.* keys

    Deployment Note:- It may be theoretically possible to run all the listeners in a single process. However,
    it may have the stability issues due to usage of GRPC, GIL and K8s.

    It is recommended to run a single listeners per process.
    """
    from pmsintegration.core.app import AppContext
    from pmsintegration.core.salesforce.sf_event_listener import run
    run(AppContext.global_context(), set(listeners))


@app.command()
def sf_platform_events_process(
        listeners: list[str] = typer.Option(
            [], "--listener", "-l",
            min=1,
            help="Specify the listeners configuration names.",
        )
):
    """A near real-time streaming service that process the ingested Salesforce Platform Events and sync
     data into Addepar.

     :param: listeners - list the configuration. See defaults.yml#listeners.salesforce.* keys

    It is recommended to run a single processor per process.
    """
    from pmsintegration.core.app import AppContext
    from pmsintegration.core.salesforce.sf_event_processor import run

    run(AppContext.global_context(), set(listeners))


@app.command()
def write_databricks_dbt_profile(
        project: str = typer.Option("pms_integration_data", help="DBT project name", envvar="DBT_PROJECT"),
        schema: str = typer.Option("recon", help="Schema name", envvar="DBT_SCHEMA"),
):
    ctx = AppContext.global_context()
    target = ctx.env.get("app.databricks_env_name")
    data = ctx.databricks.config().as_dbt_profile(
        project, target, schema
    )
    typer.secho(f"Generating profiles.yml for {project=}, {target=}")
    dbt_profiles_dir = os.path.expanduser(os.environ.get("DBT_PROFILES_DIR", "~/.dbt"))
    os.makedirs(dbt_profiles_dir, exist_ok=True)
    output_file = Path(dbt_profiles_dir).joinpath("profiles.yml")
    utils.write_text_to(
        output_file,
        utils.to_yaml_str(data)
    )
    typer.secho(f"File '{output_file}' generated")


def register(parent: typer.Typer):
    parent.add_typer(app, name="core")
    # The core has database component as its core; lets add it along with the core
    database_cli.register(parent)


if __name__ == '__main__':
    app()
