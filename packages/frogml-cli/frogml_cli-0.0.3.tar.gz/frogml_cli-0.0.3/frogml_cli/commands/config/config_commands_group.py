import click

from frogml_cli.commands.config.add.ui import add_config


@click.group(name="config", help="Configure the FrogML environment")
def config_commands_group():
    pass


config_commands_group.add_command(add_config)
