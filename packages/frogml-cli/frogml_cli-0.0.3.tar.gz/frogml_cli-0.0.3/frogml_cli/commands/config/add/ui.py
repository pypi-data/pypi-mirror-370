from typing import Optional

import click
from frogml.core.inner.di_configuration import UserAccountConfiguration
from frogml.core.inner.di_configuration.account import UserAccount

from frogml_cli.inner.tools.cli_tools import FrogMLCommand


@click.command("add", cls=FrogMLCommand, help="Adds a server configuration.")
@click.option("--url", metavar="BASE_URL", required=False, help="Artifactory base url")
@click.option(
    "--username", metavar="USERNAME", required=False, help="The user's username"
)
@click.option(
    "--password", metavar="PASSWORD", required=False, help="The user's password"
)
@click.option(
    "--access-token",
    metavar="ACCESS_TOKEN",
    required=False,
    help="Access token to authenticate",
)
@click.option(
    "--interactive",
    metavar="INTERACTIVE",
    required=False,
    help="Login with interactive flow",
    default=False,
)
@click.option(
    "--server-id",
    metavar="SERVER_ID",
    required=False,
    help="The server id, if not provided, the server id will be auto generated as uuid.",
)
def add_config(
    url: Optional[str],
    username: Optional[str],
    password: Optional[str],
    access_token: Optional[str],
    server_id: Optional[str],
    interactive: Optional[bool],
    **_,
):
    if url is None and not interactive:
        raise click.BadOptionUsage(
            option_name="config add",
            message="One of --interactive or --url must be provided",
        )
    account_config = UserAccountConfiguration()
    account_config.configure_user(
        UserAccount(
            url=url,
            username=username,
            password=password,
            token=access_token,
            anonymous=False,
            is_interactive=interactive,
            server_id=server_id,
        )
    )
