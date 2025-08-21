import click

from frogml_cli.commands.automations.executions.list._logic import (
    execute_list_executions,
)
from frogml_cli.inner.tools.cli_tools import FrogMLCommand

DELIMITER = "----------------------------------------"


@click.command(
    "list",
    help="List all executions for a specific automation",
    cls=FrogMLCommand,
)
@click.option(
    "--automation-id",
    type=str,
    metavar="ID",
    required=True,
    help="The automation id to list its executions",
)
def list_executions(automation_id: str, **kwargs):
    executions_list = execute_list_executions(automation_id)
    for execution in executions_list:
        print(execution)
        print(DELIMITER)
