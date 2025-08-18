import sempy.fabric as fabric
from typing import Optional
from uuid import UUID
import json
from sempy.fabric.exceptions import FabricHTTPException

from ._fabric_data_agent_mgmt import FabricDataAgentManagement

ARTIFACT_TYPE = 'dataagent'

def create_data_agent(
    data_agent_name: str, workspace_id: Optional[UUID | str] = None
) -> FabricDataAgentManagement:
    """
    Create a new Data Agent and return an instance of FabricDataAgentAPI.

    Parameters
    ----------
    data_agent_name : str
        The name of the Data Agent to be created.
    workspace_id : Optional[UUID or str], optional
        The workspace ID. If not provided, it will be fetched automatically.

    Returns
    -------
    FabricDataAgentAPI
        An instance of FabricDataAgentAPI initialized with the created Data Agent.

    Raises
    ------
    FabricHTTPException
        If the response status code is not 200.
    """
    if not workspace_id:
        workspace_id = fabric.get_notebook_workspace_id()

    create_artifact_url = f"v1/workspaces/{workspace_id}/{ARTIFACT_TYPE}s"
    # Construct the body
    create_artifact_body = {
        "artifactType": "LLMPlugin",
        "displayName": data_agent_name,
    }

    fabric_client = fabric.FabricRestClient()
    try:
        response = fabric_client.post(create_artifact_url, json=create_artifact_body)
        if response.status_code not in [200, 201, 202]:
            raise FabricHTTPException(response)
    except FabricHTTPException as exc:
        # Check for "already exists" error code
        if hasattr(exc, "response") and hasattr(exc.response, "json"):
            try:
                error_json = exc.response.json()
                if error_json.get("errorCode") == "ItemDisplayNameAlreadyInUse":
                    # Fetch and return the existing Data Agent
                    return FabricDataAgentManagement(data_agent_name, workspace_id)
            except (ValueError, json.JSONDecodeError):
                pass
        raise

    return FabricDataAgentManagement(data_agent_name, workspace_id)


def delete_data_agent(data_agent_name_or_id: str,
                      workspace_id: Optional[UUID | str] = None
                      ) -> None:
    """
    Delete a Data Agent.

    Parameters
    ----------
    data_agent_name_or_id : str
        The name or ID of the Data Agent to delete.

    Raises
    ------
    FabricHTTPException
        If the response status code is not 200.
    """
    if not workspace_id:
        workspace_id = fabric.get_notebook_workspace_id()
    if isinstance(data_agent_name_or_id, UUID):
        data_agent_id = str(data_agent_name_or_id)
    else:
        df = fabric.list_items(type="DataAgent", workspace=workspace_id)
        match = df[
            (df["Display Name"] == data_agent_name_or_id)
            | (df["Id"] == data_agent_name_or_id)
        ]

        if match.empty:
            df_ai_skills = fabric.list_items(type="AISkill")
            match = df_ai_skills[
                (df_ai_skills["Display Name"] == data_agent_name_or_id)
                | (df_ai_skills["Id"] == data_agent_name_or_id)
            ]

        if match.empty:
            raise ValueError(f"Data Agent '{data_agent_name_or_id}' not found.")

        data_agent_id = match["Id"].values[0]

    workspace_id = fabric.get_notebook_workspace_id()
    artifact_url = f"v1/workspaces/{workspace_id}/{ARTIFACT_TYPE}s/{data_agent_id}"

    fabric_client = fabric.FabricRestClient()
    response = fabric_client.delete(artifact_url)

    if response.status_code != 200:
        raise FabricHTTPException(response)
