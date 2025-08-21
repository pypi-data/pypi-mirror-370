from pathlib import Path

import click

from frogml_cli.commands.audience.update.logic import update_audience
from frogml_cli.exceptions import FrogmlCommandException, FrogmlResourceNotFound
from frogml_cli.inner.tools.cli_tools import FrogMLCommand


@click.command("update", cls=FrogMLCommand)
@click.option("--audience-id", type=str)
@click.option("--name", type=str)
@click.option("--description", type=str)
@click.option("-f", "--file", type=click.Path(exists=True))
def update_audience_command(
    audience_id: str, name: str, description: str, file: Path, **kwargs
):
    click.echo(f"Updating audience ID {audience_id}")
    try:
        update_audience(
            audience_id=audience_id, name=name, description=description, file=file
        )
        click.echo(f"Audience ID {audience_id} updated successfully")
    except (FrogmlCommandException, FrogmlResourceNotFound) as e:
        click.echo(f"Failed to update audience, Error: {e}")
        exit(1)
