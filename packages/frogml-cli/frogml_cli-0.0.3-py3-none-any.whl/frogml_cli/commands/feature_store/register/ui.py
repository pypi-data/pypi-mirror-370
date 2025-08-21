import os
from pathlib import Path
from typing import List, Optional, Tuple

import click
from frogml.core.clients.feature_store import FeatureRegistryClient

from frogml_cli.commands.feature_store.register._logic import (
    _register_data_sources,
    _register_entities,
    _register_features_sets,
)
from frogml_cli.inner.file_registry import list_qwak_python_files
from frogml_cli.inner.tools.cli_tools import FrogMLCommand
from frogml_cli.tools.utils import frogml_spinner


@click.command(
    "register",
    cls=FrogMLCommand,
    help="Register and deploy all feature store object under the given path. Registered "
    "features will be visible on the Frogml management platform after registration",
)
@click.option(
    "--path",
    "-p",
    type=click.Path(exists=True),
    metavar="PATH",
    help="Directory / module where frogml feature store objects are stored",
)
@click.option(
    "--force",
    "-f",
    default=False,
    is_flag=True,
    metavar="FLAG",
    help="Force register all found frogml Feature Store objects",
)
@click.option(
    "--no-validation",
    "-nv",
    default=False,
    is_flag=True,
    metavar="FLAG",
    help="Skip validation for all found frogml Feature Store objects",
)
@click.option(
    "--ignore-validation-errors",
    "-ive",
    default=False,
    is_flag=True,
    metavar="FLAG",
    help="Ignore validation errors. Continue registering even if an error occurs",
)
@click.option(
    "--fs-validation-ds-limit",
    type=click.IntRange(1, 10000),
    help="Limit the number of records to be fetched from each datasource during featureset validation",
)
def register_fs_objects(
    path: Path,
    force: bool,
    no_validation: bool,
    ignore_validation_errors: bool,
    fs_validation_ds_limit: Optional[int],
    **kwargs,
):
    qwak_python_files: List[Tuple[str, str]]

    if not path:
        path = Path.cwd()
    else:
        path = Path(path)

    if path.is_file():
        qwak_python_files = [(str(path), os.path.abspath(path))]
    elif Path.is_dir(path):
        with frogml_spinner(
            begin_text="Recursively looking for python files in input dir",
            print_callback=print,
        ) as sp:
            qwak_python_files = list_qwak_python_files(path, sp)

    try:
        import git

        git_commit = git.Repo(path, search_parent_directories=True).head.commit.hexsha
    except Exception:
        # be super defensive on Git errors. Failing to fetch anything git related should not fail the registration
        git_commit = None

    registry_client = FeatureRegistryClient()
    _register_entities(qwak_python_files, registry_client, force)

    _register_data_sources(
        qwak_python_files,
        registry_client,
        force,
        no_validation,
        ignore_validation_errors,
    )

    _register_features_sets(
        qwak_python_files,
        registry_client,
        force,
        git_commit,
        no_validation,
        ignore_validation_errors,
        fs_validation_ds_limit,
    )
