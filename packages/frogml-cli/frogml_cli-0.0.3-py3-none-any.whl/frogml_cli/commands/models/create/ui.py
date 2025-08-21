import click

from frogml_cli.commands.models.create._logic import execute_model_create
from frogml_cli.commands.ui_tools import output_as_json
from frogml_cli.inner.tools.cli_tools import FrogMLCommand
from frogml_cli.tools.colors import Color


@click.command("create", cls=FrogMLCommand)
@click.argument("name", metavar="name", required=True)
@click.option(
    "--project-key",
    metavar="ID",
    required=False,
    help="An existing jfrog project key (3-44 characters)",
)
@click.option(
    "--description",
    metavar="DESCRIPTION",
    required=False,
    help="Model description",
)
@click.option(
    "--format",
    default="text",
    show_default=True,
    type=click.Choice(["text", "json"], case_sensitive=True),
    metavar="FORMAT",
    required=False,
    help="The formatting style for commands output (choose from text, json)",
)
def model_create(
    name,
    project_key: str,
    description,
    format,
    **kwargs,
):
    try:
        response = execute_model_create(name, description, project_key)
        if format == "json":
            output_as_json(response)
        else:
            print(f"Model created\nmodel id : {response.model_id}")
    except Exception as e:
        print(f"{Color.RED}Error creating model: {e}{Color.RED}")
