from frogml._proto.qwak.projects.projects_pb2 import GetProjectResponse
from frogml.core.clients.model_management import ModelsManagementClient
from frogml.core.clients.project.client import ProjectsManagementClient
from frogml.core.exceptions import FrogmlException


def execute_model_delete(project_key: str, model_id: str):
    project_response: GetProjectResponse = ProjectsManagementClient().get_project(
        project_name=project_key
    )
    is_model_exists: bool = any(
        m.model_id == model_id for m in project_response.project.models
    )
    if not is_model_exists:
        raise FrogmlException(f"No such model {model_id} for project {project_key}")

    project_id: str = project_response.project.spec.project_id
    return ModelsManagementClient().delete_model(project_id, model_id)
