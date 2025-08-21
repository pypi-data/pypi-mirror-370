import click
from frogml.core.exceptions import FrogmlException

from frogml_cli.commands.models.runtime.update._logic import execute_runtime_update
from frogml_cli.inner.tools.cli_tools import FrogMLCommand


@click.command("update", cls=FrogMLCommand)
@click.option("-l", "--log-level", required=True, help="Log level to set.")
@click.option("-m", "--model-id", required=True, help="Model named ID")
def runtime_update(model_id, log_level, **kwargs):
    try:
        execute_runtime_update(model_id, log_level=log_level)
    except Exception as e:
        raise FrogmlException(
            f'Failed to update runtime configurations. Error is "{e}"'
        )
