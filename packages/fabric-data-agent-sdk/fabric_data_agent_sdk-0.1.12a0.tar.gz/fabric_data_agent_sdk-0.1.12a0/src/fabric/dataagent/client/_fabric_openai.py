import typing as t
import uuid

import httpx
from openai import OpenAI
from openai._exceptions import APIStatusError
from openai._models import FinalRequestOptions
from openai._types import Omit
from openai._utils import is_given
import sempy.fabric as fabric
from sempy.fabric._token_provider import SynapseTokenProvider
from sempy.fabric.exceptions import FabricHTTPException
from ._util import (
    get_artifact_by_id_or_name,
    get_workspace_capacity_id,
    resolve_workspace_name_and_id,
)
from synapse.ml.fabric.service_discovery import get_fabric_env_config


MONIKER_HEADER_NAME = "x-ms-workload-resource-moniker"
ARTIFACT_HEADER_NAME = "x-ms-upstream-artifact-id"
BYPASS_COMSOS_DB_HEADER_NAME = "x-ms-ai-assistant-bypass-cosmosdb"
FABRIC_RUN_ID_HEADER_NAME = "x-ms-ai-assistant-fabric-run-id"
ASSISTANT_SCENARIO_HEADER_NAME = "x-ms-ai-assistant-scenario"
AI_SKILL_STAGE_HEADER_NAME = "x-ms-ai-aiskill-stage"

AI_SKILL_STAGE_T = t.Literal["sandbox", "production", None]
ASSISTANT_SCENARIOS_T = t.Literal["aiskill", "dscopilot", "dwcopilot", "aiskillv1shim"]
FEATURE_NAMES_T: t.TypeAlias = t.Literal["AISkill", "DSCopilot", "DWCopilot"]


class FabricOpenAI(OpenAI):
    """
    Interact with Fabric's AI Assistant API.

    Parameters
    ----------
    artifact_name : str
        The name of the Data Agent artifact.
    workspace_name : str, optional
        The name of the workspace. If not provided, it defaults to the notebook's workspace name.
    api_version : str, default="2024-05-01-preview"
        The API version to be used for the OpenAI.
    assistant_scenario : str, default="aiskill"
        The scenario for the assistant. Options are "aiskill", "dscopilot", "dwcopilot", "aiskillv1shim".
    ai_skill_stage : str, default="production"
        The stage of the Data Agent. Options are "sandbox", "production".
    kwargs : Any
        Additional keyword arguments.
    """

    def __init__(
        self,
        artifact_name: str,
        workspace_name: str | None = None,
        api_version: str = "2024-05-01-preview",
        assistant_scenario: ASSISTANT_SCENARIOS_T = "aiskill",
        ai_skill_stage: AI_SKILL_STAGE_T = "sandbox",
        **kwargs: t.Any,
    ) -> None:
        """
        Initialize a FabricOpenAI object.

        Parameters
        ----------
        artifact_name : str
            The name of the Data Agent artifact.
        workspace_name : str, optional
            The name of the workspace. If not provided, it defaults to the notebook's workspace name.
        api_version : str, default="2024-05-01-preview"
            The API version to be used for the OpenAI.
        assistant_scenario : str, default="aiskill"
            The scenario for the assistant. Options are "aiskill", "dscopilot", "dwcopilot", "aiskillv1shim".
        ai_skill_stage : str, default="sandbox"
            The stage of the Data Agent. Options are "sandbox", "production".
        kwargs : Any
            Additional keyword arguments.
        """
        self.workspace_name, self.workspace_id = resolve_workspace_name_and_id(
            workspace_name
        )
        self.capacity_id = get_workspace_capacity_id(self.workspace_id)

        self.artifact_name, self.artifact_id = get_artifact_by_id_or_name(
            artifact_name, ["DataAgent", "Warehouse"], self.workspace_id
        )

        self.api_version = api_version
        self.assistant_scenario = assistant_scenario
        self.ai_skill_stage = ai_skill_stage
        default_query = kwargs.pop("default_query", {})
        default_query["api-version"] = self.api_version
        self._moniker_id = str(uuid.uuid4())

        self._host = get_fabric_env_config().fabric_env_config.wl_host
        # TODO: Change when base_url is modified
        base_url = f"{self._host}/webapi/capacities/{self.capacity_id}/workloads/ML/AISkill/Automatic/v1/workspaces/{self.workspace_id}/artifacts/{self.artifact_id}/aiassistant/openai"

        super().__init__(
            api_key="",
            base_url=base_url,
            default_query=default_query,
            **kwargs,
        )

    def _prepare_options(self, options: FinalRequestOptions) -> FinalRequestOptions:
        """
        Prepare the request options by setting headers and other necessary parameters.

        Parameters
        ----------
        options : FinalRequestOptions
            The request options to be prepared.
        """
        headers: dict[str, str | Omit] = (
            {**options.headers} if is_given(options.headers) else {}
        )
        options.headers = headers
        headers["Authorization"] = f"Bearer {SynapseTokenProvider()()}"
        if "Accept" not in headers:
            headers["Accept"] = "application/json"
        if "ActivityId" not in headers:
            correlation_id = str(uuid.uuid4())
            headers["ActivityId"] = correlation_id
        if MONIKER_HEADER_NAME not in headers:
            headers[MONIKER_HEADER_NAME] = self._moniker_id
        headers[ASSISTANT_SCENARIO_HEADER_NAME] = self.assistant_scenario
        if self.assistant_scenario == "aiskill":
            headers[AI_SKILL_STAGE_HEADER_NAME] = self.ai_skill_stage

        return super()._prepare_options(options)

    def _make_status_error(
        self, err_msg: str, *, body: object, response: httpx.Response
    ) -> APIStatusError:
        """
        Create and return an API status error with additional information from the response headers.

        Parameters
        ----------
        err_msg : str
            The error message.
        body : object
            The body of the response.
        response : httpx.Response
            The HTTP response object.

        Returns
        -------
        APIStatusError
            The API status error with additional information such as RAID and correlation ID.
        """
        if raid := response.headers.get("x-ms-root-activity-id", None):
            err_msg += f" RAID: {raid}"
        if correlation_id := response.headers.get("ActivityId", None):
            err_msg += f" Correlation ID: {correlation_id}"

        return super()._make_status_error(err_msg, body=body, response=response)

    def get_or_create_thread(self, tag: str = ""):
        """
        Retrieve or create a thread with the specified tag.

        Parameters
        ----------
        tag : str
            The tag for the thread. No tag means get the default thread.

        Returns
        -------
        UUID
            The ID of the thread.
        """
        headers = {
            "Content-Type": "application/json",
            "x-ms-workload-resource-moniker": f"{self._moniker_id}",
        }

        artifact_url = f"{self._host}/webapi/capacities/{self.capacity_id}/workloads/ML/AISkill/Automatic/v1/workspaces/{self.workspace_id}/artifacts/{self.artifact_id}"
        client = fabric.FabricRestClient()

        response = client.get(
            f"{artifact_url}/aiassistant/threads/fabric?agent=aiskill&stage={self.ai_skill_stage}&client=dataagentsdk&tag={tag}&scenario={self.assistant_scenario}",
            headers=headers,
        )

        if response.status_code != 200:
            raise FabricHTTPException(response)

        return self.beta.threads.retrieve(response.json()['id'])

    def delete_thread(self, tag: str = ""):
        """
        Delete a thread with the specified tag.

        Parameters
        ----------
        tag : str
            The tag for the thread. No tag means delete the default thread.
        """
        headers = {
            "Content-Type": "application/json",
            "x-ms-workload-resource-moniker": f"{self._moniker_id}",
        }

        artifact_url = f"{self._host}/webapi/capacities/{self.capacity_id}/workloads/ML/AISkill/Automatic/v1/workspaces/{self.workspace_id}/artifacts/{self.artifact_id}"
        client = fabric.FabricRestClient()

        response = client.delete(
            f"{artifact_url}/aiassistant/threads/fabric?agent=aiskill&stage={self.ai_skill_stage}&client=dataagentsdk&tag={tag}&scenario={self.assistant_scenario}",
            headers=headers,
        )

        if response.status_code != 200:
            raise FabricHTTPException(response)
