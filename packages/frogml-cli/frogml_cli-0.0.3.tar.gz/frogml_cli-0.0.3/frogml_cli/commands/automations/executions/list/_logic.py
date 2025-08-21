from typing import List

from frogml.core.automations.automation_executions import AutomationExecution
from frogml.core.clients.automation_management.client import AutomationsManagementClient


def execute_list_executions(automation_id: str) -> List[AutomationExecution]:
    return AutomationsManagementClient().list_executions(automation_id)
