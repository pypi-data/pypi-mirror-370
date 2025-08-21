import click

from frogml_cli.commands.auto_scalling.attach._logic import attach_autoscaling
from frogml_cli.exceptions import FrogmlCommandException
from frogml_cli.inner.tools.cli_tools import FrogMLCommand


@click.command("attach", cls=FrogMLCommand)
@click.option("-m", "--model-id", required=False, help="Model named ID")
@click.option("-v", "--variation-name", required=False, help="Model variation name")
@click.option("-f", "--file", required=True, type=click.Path(exists=True))
def attach(model_id: str, variation_name: str, file: str, **kwargs):
    click.echo("Attaching autoscaling configuration")
    try:
        response = attach_autoscaling(model_id, variation_name, file)
        click.echo(
            f"Successfully configured autoscaling. model: {response['model_id']}, variation: {response['variation_name']}"
        )
    except FrogmlCommandException as e:
        click.echo(f"Failed to attach autoscaling, Error: {e}")
        exit(1)
