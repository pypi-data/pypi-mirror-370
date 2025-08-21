from pathlib import Path

import click

from frogml_cli.commands.alerts.register._logic import execute_register_channel
from frogml_cli.inner.tools.cli_tools import FrogMLCommand


@click.command(
    "register",
    cls=FrogMLCommand,
    help="Register all alerts system objects under the given path.",
)
@click.option(
    "--path",
    "-p",
    type=click.Path(exists=True),
    metavar="PATH",
    help="Directory / module where frogml alerts system objects are stored",
)
@click.option(
    "--force",
    "-f",
    default=False,
    is_flag=True,
    metavar="FLAG",
    help="Force register all found frogml alerts system objects",
)
def register_channel(path: Path, force: bool, **kwargs):
    execute_register_channel(path, force)
