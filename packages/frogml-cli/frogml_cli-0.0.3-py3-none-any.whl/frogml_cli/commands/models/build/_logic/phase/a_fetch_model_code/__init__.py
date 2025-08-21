from typing import List

from frogml.core.inner.build_logic.interface.step_inteface import Step
from frogml.core.inner.build_logic.phases.phase_010_fetch_model.fetch_model_step import FetchModelStep
from frogml.core.inner.build_logic.phases.phase_010_fetch_model.post_fetch_validation_step import PostFetchValidationStep
from frogml.core.inner.build_logic.phases.phase_010_fetch_model.pre_fetch_validation_step import PreFetchValidationStep

from frogml_cli.commands.models.build._logic.phase.a_fetch_model_code.get_sdk_version_step import SdkVersionStep
from frogml_cli.commands.models.build._logic.util.step_decorator import add_decorator_to_steps


def get_fetch_model_code_steps() -> List[Step]:
    phase_steps = [
        SdkVersionStep(),
        PreFetchValidationStep(),
        FetchModelStep(),
        PostFetchValidationStep(),
    ]

    return add_decorator_to_steps(phase_steps)
