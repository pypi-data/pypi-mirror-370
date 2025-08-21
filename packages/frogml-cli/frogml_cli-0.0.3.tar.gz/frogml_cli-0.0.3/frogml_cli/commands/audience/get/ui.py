import click

from frogml_cli.commands.audience.audience_api_dump import (
    audience_to_json,
    audience_to_pretty_string,
)
from frogml_cli.commands.audience.get.logic import get_audience
from frogml_cli.exceptions import FrogmlCommandException, FrogmlResourceNotFound
from frogml_cli.inner.tools.cli_tools import FrogMLCommand


@click.command("get", cls=FrogMLCommand)
@click.option("--audience-id", type=str)
@click.option("--json-format", is_flag=True, type=bool)
def get_audience_command(audience_id: str, json_format: bool, **kwargs):
    click.echo(f"Getting audience {audience_id}")
    try:
        audience = get_audience(audience_id)
        if json_format:
            click.echo(audience_to_json(audience))
        else:
            click.echo(audience_to_pretty_string(audience_id, audience))
    except (FrogmlCommandException, FrogmlResourceNotFound) as e:
        click.echo(f"Failed to get audience, Error: {e}")
        exit(1)
