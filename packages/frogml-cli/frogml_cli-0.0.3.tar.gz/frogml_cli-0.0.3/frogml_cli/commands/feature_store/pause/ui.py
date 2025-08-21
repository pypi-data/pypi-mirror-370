import click
from frogml.core.clients.feature_store import FeatureRegistryClient
from frogml.core.exceptions import FrogmlException

from frogml_cli.inner.tools.cli_tools import FrogMLCommand
from frogml_cli.tools.colors import Color


@click.command("pause", cls=FrogMLCommand, help="Pause a running feature set")
@click.argument("name")
def pause_feature_set(name, **kwargs):
    try:
        FeatureRegistryClient().pause_feature_set(feature_set_name=name)
    except Exception as e:
        print(f"{Color.RED} Failed to pause feature set {name} {Color.END}")
        raise FrogmlException(f"Failed to pause feature set {name}") from e

    print(f"{Color.GREEN}Successfully paused feature set {Color.YELLOW}{name}")
