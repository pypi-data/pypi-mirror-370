import click

from frogml_cli.commands.audience.delete.logic import delete_audience
from frogml_cli.exceptions import FrogmlCommandException, FrogmlResourceNotFound
from frogml_cli.inner.tools.cli_tools import FrogMLCommand


@click.command("delete", cls=FrogMLCommand)
@click.option("--audience-id", type=str)
def delete_audience_command(audience_id: str, **kwargs):
    click.echo(f"Deleting audience ID {audience_id}")
    try:
        delete_audience(audience_id)
        click.echo(f"Audience ID {audience_id} deleted successfully")
    except (FrogmlCommandException, FrogmlResourceNotFound) as e:
        click.echo(f"Failed to delete audience, Error: {e}")
        exit(1)
