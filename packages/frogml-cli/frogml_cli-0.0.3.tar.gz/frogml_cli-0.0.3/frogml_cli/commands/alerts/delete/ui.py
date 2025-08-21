import click

from frogml_cli.commands.alerts.delete._logic import execute_delete_channel
from frogml_cli.inner.tools.cli_tools import FrogMLCommand


@click.command("delete", cls=FrogMLCommand, help="Delete a Channel by name")
@click.argument("name")
def delete_channel(name, **kwargs):
    execute_delete_channel(name)
