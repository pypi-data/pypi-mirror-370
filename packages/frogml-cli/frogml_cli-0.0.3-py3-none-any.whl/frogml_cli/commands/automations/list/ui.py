import click

from frogml_cli.commands.automations.list._logic import (
    execute_list_automations,
    execute_list_json_automations,
)
from frogml_cli.inner.tools.cli_tools import FrogMLCommand


@click.command(
    "list",
    help="List all automations",
    cls=FrogMLCommand,
)
@click.option("--json-format", is_flag=True, type=bool)
def list_automations(json_format: bool, **kwargs):
    if json_format:
        click.echo(execute_list_json_automations())

    else:
        click.echo(execute_list_automations())
