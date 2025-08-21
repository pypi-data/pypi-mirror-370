from pathlib import Path
from typing import Optional

import grpc
from frogml.core.clients.audience import AudienceClient

from frogml_cli.commands.audience._logic.config.config_base import ConfigBase
from frogml_cli.commands.audience._logic.config.parser import parse_audience_from_yaml
from frogml_cli.commands.audience._logic.config.v1.config_v1 import ConfigV1
from frogml_cli.exceptions import FrogmlCommandException, FrogmlResourceNotFound


def update_audience(
    audience_id: str, name: str = "", description: str = "", file: Optional[Path] = None
) -> None:
    config = parse_audience_from_yaml(file)
    config = merge_kw_yaml(config=config, name=name, description=description)
    audience_api = config.to_audiences_api()[0]

    try:
        AudienceClient().update_audience(audience_id=audience_id, audience=audience_api)
    except grpc.RpcError as e:
        if e.args[0].code == grpc.StatusCode.NOT_FOUND:
            raise FrogmlResourceNotFound(e.args[0].details)
        raise FrogmlCommandException(e.args[0].details)


def merge_kw_yaml(
    config: ConfigBase, name: str = "", description: str = ""
) -> ConfigBase:
    if isinstance(config, ConfigV1):
        if name:
            config.spec.audiences[0].name = name
        if description:
            config.spec.audiences[0].description = description

    return config
