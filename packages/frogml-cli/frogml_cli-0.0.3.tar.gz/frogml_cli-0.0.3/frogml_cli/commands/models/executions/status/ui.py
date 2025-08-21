import click
from frogml.core.exceptions import FrogmlException
from frogml.core.tools.logger.logger import get_frogml_logger

from frogml_cli.commands.models.executions.status._logic import execute_execution_status
from frogml_cli.inner.tools.cli_tools import FrogMLCommand

logger = get_frogml_logger()


@click.command(name="status", help="Get the status of an execution.", cls=FrogMLCommand)
@click.option(
    "--execution-id",
    type=str,
    help="The execution id.",
)
def execution_status(execution_id: str, **kwargs):
    try:
        job_status, success, fail_message = execute_execution_status(execution_id)
        if not success:
            raise FrogmlException(fail_message)

        logger.info(f"Status is: {job_status}.")

    except Exception as e:
        logger.error(f"Failed to cancel execution, Error: {e}")
        raise
