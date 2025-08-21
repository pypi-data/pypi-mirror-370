from pathlib import Path
from typing import Optional, Union

import yaml

from frogml_cli.commands.auto_scalling._logic.config import Config
from frogml_cli.inner.tools.dataclasses_utils import create_dataclass_instance


def parse_autoscaling_from_yaml(file_path: Optional[Union[Path, str]] = None) -> Config:
    if file_path:
        file_obj = Path(file_path)
        if file_obj.exists():
            autoscaling_dict = yaml.safe_load(file_obj.open("r"))
            return create_dataclass_instance(Config, autoscaling_dict)
        else:
            raise FileNotFoundError(
                f"autoscaling file {file_obj} definition isn't found"
            )
    else:
        return Config()
