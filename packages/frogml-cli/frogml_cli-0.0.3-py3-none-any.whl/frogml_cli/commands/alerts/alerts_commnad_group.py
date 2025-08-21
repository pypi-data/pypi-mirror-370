import click

from frogml_cli.commands.alerts.delete.ui import delete_channel
from frogml_cli.commands.alerts.list.ui import list_channels
from frogml_cli.commands.alerts.register.ui import register_channel


@click.group(
    name="alerts",
    help="Commands for interacting with the Qwak alerts System",
)
def alerts_commands_group():
    pass


alerts_commands_group.add_command(register_channel)
alerts_commands_group.add_command(list_channels)
alerts_commands_group.add_command(delete_channel)
