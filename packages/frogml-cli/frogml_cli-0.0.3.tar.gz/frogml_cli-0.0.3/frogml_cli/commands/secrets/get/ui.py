import click
from frogml.core.exceptions import FrogmlNotFoundException

from frogml_cli.commands.secrets.get._logic import execute_get_secret
from frogml_cli.inner.tools.cli_tools import FrogMLCommand


@click.command("get", cls=FrogMLCommand)
@click.option("--name", metavar="TEXT", required=True, help="the secret name")
def get_secret(name, **kwargs):
    try:
        value = execute_get_secret(name)
        print(value)
    except FrogmlNotFoundException:
        print(f"Secret '{name}' does not exists")
    except Exception as e:
        print(f"Error getting secret. Error is {e}")
