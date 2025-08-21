from pathlib import Path

import click

from frogml_cli.commands.audience.create.logic import create_audience
from frogml_cli.exceptions import FrogmlCommandException, FrogmlResourceNotFound
from frogml_cli.inner.tools.cli_tools import FrogMLCommand


@click.command("create", cls=FrogMLCommand)
@click.option("--name", type=str)
@click.option("--description", type=str)
@click.option("-f", "--file", type=click.Path(exists=True))
def create_audience_command(name: str, description: str, file: Path, **kwargs):
    click.echo("Creating audience")
    try:
        audience_id = create_audience(name=name, description=description, file=file)
        click.echo(f"Audience ID {audience_id} created successfully")
    except (FrogmlCommandException, FrogmlResourceNotFound) as e:
        click.echo(f"Failed to create audience, Error: {e}")
        exit(1)
