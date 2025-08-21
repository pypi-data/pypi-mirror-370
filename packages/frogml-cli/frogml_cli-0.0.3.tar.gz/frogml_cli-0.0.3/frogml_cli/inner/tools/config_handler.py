from typing import Any, Tuple, Union

from frogml.core.clients.build_orchestrator import BuildOrchestratorClient
from frogml.core.clients.instance_template.client import (
    InstanceTemplateManagementClient,
)
from frogml.core.inner.build_config.build_config_v1 import BuildConfigV1
from frogml.core.inner.tool.run_config import FrogmlConfigBase, YamlConfigMixin


def config_handler(
    config: Union[FrogmlConfigBase, YamlConfigMixin, Any],
    from_file: str,
    out_conf: bool,
    sections: Tuple[str, ...] = (),
    **kwargs,
) -> Any:
    conf: Union[FrogmlConfigBase, YamlConfigMixin] = config.from_yaml(from_file)
    conf.merge_cli_argument(sections=sections, **kwargs)

    if isinstance(conf, BuildConfigV1):
        conf.fetch_base_docker_image_name(
            BuildOrchestratorClient(), InstanceTemplateManagementClient()
        )

    if out_conf:
        print(conf.to_yaml())

    return conf
