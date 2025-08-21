import click

from frogml_cli.commands.automations.delete._logic import delete_automation
from frogml_cli.inner.tools.cli_tools import FrogMLCommand


@click.command(
    "delete",
    help="Delete an automation object",
    cls=FrogMLCommand,
)
@click.option(
    "--automation-id",
    type=str,
    metavar="ID",
    help="The automation id to delete",
)
def delete(automation_id: str, **kwargs):
    deleted = delete_automation(automation_id=automation_id)
    if deleted:
        print(f"Automation {automation_id} deleted successfully")
    else:
        print(f"Automation {automation_id} was not found")
