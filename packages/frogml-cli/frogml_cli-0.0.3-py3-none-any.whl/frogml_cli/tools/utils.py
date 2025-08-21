import logging
import sys
from contextlib import contextmanager
from pathlib import Path
from typing import Callable, List, Optional

from frogml.core.tools.logger.logger import (
    get_frogml_logger,
    get_frogml_logger_verbosity_level,
)
from yaspin import yaspin

logger = get_frogml_logger()


@contextmanager
def frogml_spinner(
    begin_text: Optional[str],
    end_text: Optional[str] = "",
    print_callback: Callable[[str], None] = logger.info,
):
    """FrogML spinner.

    Args:
        begin_text: Text to shown when spinner starts.
        end_text: Text to shown when spinner ends.
        print_callback: Callback used to print the output.
    """
    if (
        logging.getLevelName(get_frogml_logger_verbosity_level()) < logging.WARNING
        if print_callback != print
        else False
    ) or not sys.stdout.isatty():
        print_callback(begin_text)
        yield
        print_callback(end_text)
    else:
        with yaspin(text=begin_text, color="blue", timer=True) as sp:
            try:
                yield sp
            except Exception as e:
                sp.fail("💥")
                raise e
            if end_text:
                sp.text = end_text
            sp.ok("✅")


def get_models_init_example_choices() -> List[str]:
    """Dynamically get available template choices from the template directory."""
    template_dir = (
        Path(__file__).parent.parent
        / "commands"
        / "models"
        / "init"
        / "_logic"
        / "template"
    )

    return [
        item.name
        for item in template_dir.iterdir()
        if item.is_dir() and not item.name.startswith(".")
    ]
