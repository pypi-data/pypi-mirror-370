from frogml._proto.qwak.builds.builds_pb2 import BuildStatus
from frogml.core.clients.build_orchestrator import BuildOrchestratorClient


def execute_get_build_status(build_id) -> BuildStatus:
    return BuildOrchestratorClient().get_build(build_id).build.build_status
