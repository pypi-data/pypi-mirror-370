import click
from frogml.core.tools.logger.logger import get_frogml_logger

from frogml_cli.commands.models.executions.cancel.ui import execution_cancel
from frogml_cli.commands.models.executions.report.ui import execution_report
from frogml_cli.commands.models.executions.start.ui import execution_start
from frogml_cli.commands.models.executions.status.ui import execution_status

logger = get_frogml_logger()


@click.group(
    name="execution",
    help="Executions of a batch job on deployed model.",
)
def execution_commands_group():
    # Click commands group injection
    pass


execution_commands_group.add_command(execution_cancel)
execution_commands_group.add_command(execution_report)
execution_commands_group.add_command(execution_start)
execution_commands_group.add_command(execution_status)
