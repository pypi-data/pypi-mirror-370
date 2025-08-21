import json

import click
from frogml._proto.qwak.builds.builds_pb2 import BuildStatus
from frogml.core.tools.logger.logger import get_frogml_logger

from frogml_cli.commands.models.builds.status._logic import execute_get_build_status
from frogml_cli.inner.tools.cli_tools import FrogMLCommand

logger = get_frogml_logger()


@click.command("status", cls=FrogMLCommand)
@click.argument("build_id")
@click.option(
    "--format",
    default="text",
    show_default=True,
    type=click.Choice(["text", "json"], case_sensitive=True),
    metavar="FORMAT",
    required=False,
    help="The formatting style for commands output (choose from text, json)",
)
def get_build_status(build_id, format, **kwargs):
    if format == "text":
        logger.info(f"Getting build status for build id [{build_id}]")
    build_status = execute_get_build_status(build_id)
    if format == "text":
        logger.info(f"Build status: {BuildStatus.Name(build_status)}")
    elif format == "json":
        print(
            json.dumps(
                {
                    "build_id": build_id,
                    "build_status": BuildStatus.Name(build_status),
                }
            )
        )
    return BuildStatus.Name(build_status)
