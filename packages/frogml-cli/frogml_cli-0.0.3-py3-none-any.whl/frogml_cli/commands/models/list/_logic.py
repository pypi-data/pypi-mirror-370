from frogml.core.clients.project.client import ProjectsManagementClient


def execute_models_list(project_key: str):
    return ProjectsManagementClient().get_project(project_name=project_key)
