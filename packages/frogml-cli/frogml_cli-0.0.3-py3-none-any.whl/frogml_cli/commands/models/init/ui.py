from typing import List

import click
from frogml.core.tools.logger.logger import get_frogml_logger

from frogml_cli.commands.models.init._logic.initialize_model_structure import (
    initialize_model_structure,
)
from frogml_cli.inner.tools.cli_tools import FrogMLCommand
from frogml_cli.tools.utils import get_models_init_example_choices

logger = get_frogml_logger()


MODELS_INIT_EXAMPLE_CHOICES: List[str] = get_models_init_example_choices()


@click.command("init", cls=FrogMLCommand)
@click.option(
    "--model-directory", metavar="NAME", required=False, help="folder for model content"
)
@click.option(
    "--model-class-name",
    metavar="NAME",
    required=False,
    help="class name of created model",
)
@click.option(
    "--example",
    metavar="NAME",
    required=False,
    type=click.Choice(MODELS_INIT_EXAMPLE_CHOICES, case_sensitive=True),
    help=f"Generate a fully functioning example of a Qwak based model. Options: {' / '.join(MODELS_INIT_EXAMPLE_CHOICES)}",
)
@click.argument("uri", metavar="URI", required=True)
def model_init(
    uri: str, model_directory: str, model_class_name: str, example: str, **kwargs
):
    if example:
        if model_directory or model_class_name:
            logger.warning("--example flag detected. Other options will be overridden.")

        template = example
        template_args = {}

    else:
        if model_directory is None:
            model_directory = click.prompt(
                "Please enter the model directory name", type=str
            )
        if model_class_name is None:
            model_class_name = click.prompt(
                "Please enter the model class name", type=str
            )

        template = "general"
        template_args = {
            "model_class_name": model_class_name,
            "model_directory": model_directory,
        }
    try:
        initialize_model_structure(uri, template, logger, **template_args)
    except Exception as e:
        logger.error(f"Failed to initialize a Qwak model structure. Error reason:\n{e}")
        exit(1)
