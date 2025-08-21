import click
from frogml.core.clients.feature_store import FeatureRegistryClient
from frogml.core.exceptions import FrogmlException

from frogml_cli.inner.tools.cli_tools import FrogMLCommand
from frogml_cli.tools.colors import Color


@click.command("resume", cls=FrogMLCommand, help="Resume a paused feature set")
@click.argument("name")
def resume_feature_set(name, **kwargs):
    try:
        FeatureRegistryClient().resume_feature_set(feature_set_name=name)
    except Exception as e:
        print(f"{Color.RED} Failed to resume feature set {name} {Color.END}")
        raise FrogmlException(f"Failed to resume feature set {name}") from e

    print(f"{Color.GREEN}Successfully resume feature set {Color.YELLOW}{name}")
