import os
from pathlib import Path

import click

from frogml_cli.commands.automations.register._logic import register_automations
from frogml_cli.inner.file_registry import list_qwak_python_files
from frogml_cli.inner.tools.cli_tools import FrogMLCommand
from frogml_cli.tools.utils import frogml_spinner


@click.command(
    "register",
    help="Register all automations object under the given path. Registered "
    "automations will be visible on the Frogml management platform after registration",
    cls=FrogMLCommand,
)
@click.option(
    "--path",
    "-p",
    type=click.Path(exists=True),
    metavar="PATH",
    help="Directory / module where frogml automations objects are stored",
)
@click.option(
    "--force",
    "-f",
    default=False,
    is_flag=True,
    metavar="FLAG",
    help="Force register all found frogml automations Store objects",
)
def register(path: Path, force: bool, **kwargs):
    path = Path(path) if path else Path.cwd()
    if path.is_file():
        qwak_python_files = [(str(path), os.path.abspath(path))]
    elif Path.is_dir(path):
        with frogml_spinner(
            begin_text="Recursively looking for python files in input dir",
            print_callback=print,
        ) as sp:
            qwak_python_files = list_qwak_python_files(path, sp)

    register_automations(qwak_python_files, force)
