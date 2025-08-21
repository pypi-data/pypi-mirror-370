from frogml._proto.qwak.projects.projects_pb2 import GetProjectResponse
from frogml.core.clients.model_management.client import ModelsManagementClient
from frogml.core.clients.project.client import ProjectsManagementClient


def list_models(project_key: str):
    project_response: GetProjectResponse = ProjectsManagementClient().get_project(
        project_name=project_key
    )
    project_id: str = project_response.project.spec.project_id
    return ModelsManagementClient().list_models(project_id)
