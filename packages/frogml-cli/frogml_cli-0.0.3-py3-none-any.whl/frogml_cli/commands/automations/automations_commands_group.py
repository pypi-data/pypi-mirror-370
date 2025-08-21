import logging

import click

from frogml_cli.commands.automations.delete.ui import delete
from frogml_cli.commands.automations.executions.executions_commands_group import (
    executions_command_group,
)
from frogml_cli.commands.automations.list.ui import list_automations
from frogml_cli.commands.automations.register.ui import register

logger = logging.getLogger(__name__)
DELIMITER = "----------------------------------------"

AUTOMATION = "automation"


@click.group(
    name="automations",
    help="Commands for interacting with the Qwak Automations",
)
def automations_commands_group():
    # Click commands group injection
    pass


automations_commands_group.add_command(delete)
automations_commands_group.add_command(list_automations)
automations_commands_group.add_command(register)
automations_commands_group.add_command(executions_command_group)
