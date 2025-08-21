import click
from frogml.core.exceptions import FrogmlException
from frogml.core.tools.logger.logger import get_frogml_logger

from frogml_cli.commands.models.executions.cancel._logic import execute_execution_cancel
from frogml_cli.inner.tools.cli_tools import FrogMLCommand

logger = get_frogml_logger()


@click.command(name="cancel", help="Cancel a running execution.", cls=FrogMLCommand)
@click.option(
    "--execution-id",
    type=str,
    help="The execution id.",
)
def execution_cancel(execution_id: str, **kwargs):
    try:
        success, fail_message = execute_execution_cancel(execution_id)
        if not success:
            raise FrogmlException(fail_message)

        logger.info(f"Execution {execution_id} cancelled successfully.")

    except Exception as e:
        logger.error(f"Failed to cancel execution, Error: {e}")
        raise
