from __future__ import annotations

from typing import Dict, List

from frogml._proto.qwak.auto_scaling.v1.auto_scaling_pb2 import AutoScalingConfig
from frogml._proto.qwak.deployment.deployment_pb2 import (
    RealTimeConfig,
    ServingStrategy,
    TrafficConfig,
)
from frogml._proto.qwak.ecosystem.v0.ecosystem_pb2 import UserContextEnvironmentDetails
from frogml.core.exceptions import FrogmlException

from frogml_cli.commands.audience._logic.config.v1.audience_config import AudienceConfig
from frogml_cli.commands.models.deployments.deploy._logic.deploy_config import (
    DeployConfig,
)


def create_realtime_serving_strategy(
    auto_scaling: AutoScalingConfig,
    audiences: List[AudienceConfig],
    fallback_variation: str,
    variation_name: str,
    variation_protected_state: bool = False,
) -> ServingStrategy:
    return ServingStrategy(
        realtime_config=(
            RealTimeConfig(
                auto_scaling_config=auto_scaling,
                traffic_config=TrafficConfig(
                    selected_variation_name=variation_name,
                    audience_routes_entries=[
                        audience.to_audience_route_entry(index)
                        for index, audience in enumerate(audiences)
                    ],
                    fallback_variation=fallback_variation,
                    selected_variation_protect_state=variation_protected_state,
                ),
            )
        )
    )


def create_realtime_serving_strategy_from_deploy_config(
    deploy_config: DeployConfig,
    environment_name_to_config: Dict[str, UserContextEnvironmentDetails],
) -> Dict[str, ServingStrategy]:
    serving_strategies = {}
    errors = []
    variation_name = deploy_config.realtime.variation_name or "default"
    variation_protected_state = deploy_config.realtime.variation_protected_state
    fallback_variation = deploy_config.realtime.fallback_variation
    auto_scaling = (
        deploy_config.auto_scaling.to_autoscaling_api()
        if deploy_config.auto_scaling
        else None
    )
    for env_name, env_config in environment_name_to_config.items():
        try:
            serving_strategies[env_config.id] = create_realtime_serving_strategy(
                auto_scaling,
                deploy_config.realtime.audiences,
                fallback_variation,
                variation_name,
                variation_protected_state,
            )

        except FrogmlException as e:
            errors.append(e.message)

    if errors:
        raise FrogmlException("\n".join(errors))

    return serving_strategies
