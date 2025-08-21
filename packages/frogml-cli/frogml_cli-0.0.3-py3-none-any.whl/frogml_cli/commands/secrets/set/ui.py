import click

from frogml_cli.commands.secrets.set._logic import execute_set_secret
from frogml_cli.inner.tools.cli_tools import FrogMLCommand


@click.command("set", cls=FrogMLCommand)
@click.option("--name", metavar="TEXT", required=True, help="the secret name")
@click.option("--value", hide_input=True, confirmation_prompt=False, prompt=True)
def set_secret(name, value, **kwargs):
    print(f"Creating secret named '{name}' with value length of {len(value)}...")
    try:
        execute_set_secret(name, value)
        print("Created!")
    except Exception as e:
        print(f"Error setting secret. Error is {e}")
