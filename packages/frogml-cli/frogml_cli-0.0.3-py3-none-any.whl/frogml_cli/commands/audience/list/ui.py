import click

from frogml_cli.commands._logic.tools import list_of_messages_to_json_str
from frogml_cli.commands.audience.audience_api_dump import (
    audience_entries_to_pretty_string,
)
from frogml_cli.commands.audience.list.logic import list_audience
from frogml_cli.exceptions import FrogmlCommandException, FrogmlResourceNotFound
from frogml_cli.inner.tools.cli_tools import FrogMLCommand


@click.command("list", cls=FrogMLCommand)
@click.option("--json-format", is_flag=True, type=bool)
def list_audience_command(json_format: bool, **kwargs):
    try:
        audience_entries = list_audience()
        if json_format:
            click.echo(list_of_messages_to_json_str(audience_entries))
        else:
            click.echo("Getting audiences")
            click.echo(
                audience_entries_to_pretty_string(audience_entries=audience_entries)
            )
    except (FrogmlCommandException, FrogmlResourceNotFound) as e:
        click.echo(f"Failed to list audiences, Error: {e}")
        exit(1)
