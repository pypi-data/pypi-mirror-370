import logging

from frogml._proto.qwak.model_group.model_group_pb2 import ModelGroupBriefInfoResponse
from frogml._proto.qwak.models.models_pb2 import CreateModelResponse
from frogml.core.clients.model_group_management import ModelGroupManagementClient
from frogml.core.clients.model_management import ModelsManagementClient
from frogml.core.exceptions import FrogmlException

from frogml_cli.exceptions import FrogmlCommandException

logger = logging.getLogger(__name__)


def execute_model_create(
    model_name: str,
    model_description: str,
    jfrog_project_key: str,
) -> CreateModelResponse:
    if not jfrog_project_key:
        raise FrogmlCommandException("You must supply project key")
    try:
        response: ModelGroupBriefInfoResponse = (
            ModelGroupManagementClient().create_if_not_exists_model_group(
                project_key=jfrog_project_key
            )
        )
        logger.info(
            "Retrieved model group id %s that associated with project %s",
            response.model_group_id,
            jfrog_project_key,
        )
        return ModelsManagementClient().create_model(
            project_id=response.model_group_id,
            model_name=model_name,
            model_description=model_description,
            jfrog_project_key=jfrog_project_key,
        )
    except FrogmlException as e:
        logger.error("Error occurred during model creation due to %s", e.message)
        raise FrogmlCommandException(e)
