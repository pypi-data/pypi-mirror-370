import click
from packaging import version

from frogml_cli import __version__ as sdk_version
from frogml_cli.commands.alerts.alerts_commnad_group import alerts_commands_group
from frogml_cli.commands.audience.audience_commands_group import audience_commands_group
from frogml_cli.commands.automations.automations_commands_group import (
    automations_commands_group,
)
from frogml_cli.commands.config.config_commands_group import config_commands_group
from frogml_cli.commands.feature_store.feature_store_command_group import (
    feature_store_commands_group,
)
from frogml_cli.commands.models.models_command_group import models_command_group
from frogml_cli.commands.secrets.secrets_commands_group import secrets_commands_group
from frogml_cli.inner.tools.logger import setup_frogml_logger

version_option_kwargs = {}
if version.parse(click.__version__) >= version.parse("8.0.0"):
    version_option_kwargs["package_name"] = "frogml_cli"
    version_option_kwargs["version"] = sdk_version


def create_frogml_cli():
    setup_frogml_logger()

    @click.group()
    @click.version_option(**version_option_kwargs)
    def frogml_cli():
        # This class is intentionally empty
        pass

    frogml_cli.add_command(config_commands_group)
    frogml_cli.add_command(models_command_group)
    frogml_cli.add_command(secrets_commands_group)
    frogml_cli.add_command(automations_commands_group)
    frogml_cli.add_command(feature_store_commands_group)
    frogml_cli.add_command(audience_commands_group)
    frogml_cli.add_command(alerts_commands_group)
    return frogml_cli
