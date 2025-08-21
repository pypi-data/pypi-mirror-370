from frogml.core.inner.build_logic.phases.phase_020_remote_register_frogml_build.cleanup_step import CleanupStep
from frogml.core.inner.build_logic.phases.phase_020_remote_register_frogml_build.start_remote_build_step import \
    StartRemoteBuildStep
from frogml.core.inner.build_logic.phases.phase_020_remote_register_frogml_build.upload_step import UploadStep

from ...util.step_decorator import add_decorator_to_steps


def get_remote_register_frogml_build_steps():
    phase_steps = [
        UploadStep(),
        StartRemoteBuildStep(),
        CleanupStep(),
    ]

    return add_decorator_to_steps(phase_steps)
