import click

from frogml_cli.inner.tools.cli_tools import FrogMLCommand
from frogml_cli.tools.colors import Color
from frogml_cli.tools.log_handling import FrogmlLogHandling


@click.command("logs", cls=FrogMLCommand)
@click.option("-f", "--follow", is_flag=True, default=False, help="Follow log tail")
@click.option(
    "-d",
    "--deployment-id",
    required=False,
    help="Runtime model Deployment ID to show logs of",
)
@click.option(
    "-b",
    "--build-id",
    required=False,
    help="Runtime model Build ID to show logs of",
)
@click.option(
    "-s",
    "--since",
    required=False,
    metavar="X [TYPE] ago",
    help=f"Get logs from X1 [type] X2 [type]... Xn [type] ago. "
    f"(x = INT; type = {FrogmlLogHandling.TIME_UNITS}) i.e. [1 day 2 hours ago]",
)
@click.option(
    "-n",
    "--number-of-results",
    required=False,
    type=int,
    help="Maximum number of results per query",
)
@click.option(
    "-g", "--grep", required=False, help="Filter by log content contains [expression]"
)
def runtime_logs(
    follow=True,
    deployment_id=None,
    build_id=None,
    since=None,
    number_of_results=None,
    grep=None,
    **kwargs,
):
    if not deployment_id and not build_id:
        print(
            f"{Color.YELLOW}Please provide either a Deployment or a Build ID{Color.END}"
        )
        return

    frogml_log_handling = FrogmlLogHandling()
    frogml_log_handling.get_logs(
        follow,
        since,
        number_of_results,
        grep,
        {"build_id": build_id, "deployment_id": deployment_id},
        "runtime_model",
    )
