import click
from frogml.core.tools.logger.logger import get_frogml_logger

from frogml_cli.commands.models.builds.cancel._logic import execute_cancel_build
from frogml_cli.inner.tools.cli_tools import FrogMLCommand

logger = get_frogml_logger()


@click.command("cancel", cls=FrogMLCommand)
@click.argument("build_id")
def cancel_build(build_id, **kwargs):
    logger.info(f"Attempting to cancel remote build with build id [{build_id}]")
    execute_cancel_build(build_id=build_id)
    logger.info("Successfully canceled remote build")
