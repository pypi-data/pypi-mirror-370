import uuid
from typing import Iterator, Optional
from uuid import UUID

import sempy.fabric as fabric
from sempy.fabric.exceptions import FabricHTTPException
import synapse.ml.fabric.service_discovery as service_discovery
from ._tagged_value import TaggedValue
from ._util import (
    get_artifact_by_id_or_name,
    get_workspace_capacity_id,
    resolve_workspace_name_and_id,
)


class FabricDataAgentAPI:
    """
    Client for interacting with the Fabric DataAgent REST API.

    Attributes
    ----------
    _data_agent_base_url : str
        The base URL for DataAgent management endpoints.
    _client : FabricRestClient
        The REST client used for API communication.
    _workspace_id : str
        The ID of the workspace associated with the DataAgent.
    _workspace_name : str
        The name of the workspace associated with the DataAgent.
    data_agent_name : str
        The name of the DataAgent.
    data_agent_id : UUID
        The unique identifier of the DataAgent.
    capacity_id : str
        The capacity ID associated with the workspace.
    workload_resource_moniker : str
        A unique identifier for the workload resource.
    scenario : str
        The scenario type, default is "data_agent".
    stage : str
        The stage type, default is "sandbox".
    """

    def __init__(
        self, data_agent: str | UUID, workspace: Optional[str | UUID] = None
    ) -> None:
        """
        Initialize the client for interacting with the Fabric REST API.

        Parameters
        ----------
        data_agent : str or UUID
            The name or ID of the Data Agent to be used.
        workspace : Optional[str or UUID], optional
            The workspace name or ID. If not provided, it will be fetched automatically.
        """
        self._client = fabric.FabricRestClient()

        self.workspace_name, self.workspace_id = resolve_workspace_name_and_id(
            workspace
        )

        self.scenario = "data_agent"
        self.stage = "sandbox"
        self.workload_resource_moniker = str(uuid.uuid4())  # Generate a new GUID

        # resolve the Data Agent artifact ID and capacity ID
        self.data_agent_name, self.data_agent_id = get_artifact_by_id_or_name(
            data_agent, ["DataAgent", "Warehouse"], self.workspace_id
        )

        self.capacity_id = get_workspace_capacity_id(self.workspace_id)

        # Get the fabric environment configuration
        self._host = service_discovery.get_fabric_env_config().fabric_env_config.wl_host
        self._data_agent_base_url = f"{self._host}/webapi/capacities/{self.capacity_id}/workloads/ML/AISkill/Automatic/workspaces/{self.workspace_id}/dataagents/{self.data_agent_id}"

    def get_configuration(self) -> TaggedValue:
        """
        Retrieve the configuration from the Data Agent.

        Returns
        -------
        TaggedValue
            The configuration of the Data Agent.
        """

        return TaggedValue.from_response(
            self._client.get(f"{self._data_agent_base_url}/management/configuration")
        )

    def set_configuration(self, value: TaggedValue) -> TaggedValue:
        """
        Set the configuration for the Data Agent.

        Parameters
        ----------
        value : TaggedValue
            The configuration to set.

        Returns
        -------
        TaggedValue
            The updated configuration of the Data Agent with the new ETag.
        """

        # copy
        body = dict(value.value)

        # we can't update dataSources directly
        if "dataSources" in body:
            del body["dataSources"]

        response = self._client.patch(
            f"{self._data_agent_base_url}/management/configuration",
            json=body,
            headers={
                "x-ms-ai-aiskill-stage": self.stage,
                "If-Match": value.etag,
            },
        )

        if response.status_code != 200:
            raise FabricHTTPException(response)

        return TaggedValue(value.value, response.headers.get("ETag", ""))

    def get_datasources(self) -> Iterator[TaggedValue]:
        """
        Retrieve the list of datasources from the Data Agent.

        Returns
        -------
        Iterator[TaggedValue]
            The list of datasources.
        """

        config = self.get_configuration()

        for ds in config.value.get("dataSources", []):
            yield self.get_datasource(ds["id"])

    def get_datasource(self, datasource_id: str) -> TaggedValue:
        """
        Retrieve a specific datasource by its ID.

        Parameters
        ----------
        datasource_id : str
            The ID of the datasource.

        Returns
        -------
        TaggedValue
            The datasource.
        """
        return TaggedValue.from_response(
            self._client.get(
                f"{self._data_agent_base_url}/management/datasources/{datasource_id}"
            )
        )

    def remove_datasource(self, datasource_id: str, configuration_etag: str) -> None:
        """
        Remove a datasource from the Data Agent.

        Parameters
        ----------
        datasource_id : str
            The ID of the datasource to remove.
        configuration_etag : str
            The ETag of the current configuration.

        Raises
        ------
        FabricHTTPException
            If the response status code is not 200.
        """
        response = self._client.delete(
            f"{self._data_agent_base_url}/management/datasources/{datasource_id}",
            headers={
                "x-ms-ai-aiskill-stage": self.stage,
                "If-Match": configuration_etag,
            },
        )

        if response.status_code != 200:
            raise FabricHTTPException(response)

    def set_datasource(self, datasource: TaggedValue) -> TaggedValue:
        """
        Set the datasource for the Data Agent.

        Parameters
        ----------
        datasource : TaggedValue
            The datasource to set.

        Returns
        -------
        TaggedValue
            The updated datasource of the Data Agent with the new ETag.
        """

        response = self._client.put(
            f"{self._data_agent_base_url}/management/datasources/{datasource.value['id']}",
            json=datasource.value,
            headers={
                "x-ms-ai-aiskill-stage": self.stage,
                "If-Match": datasource.etag,
            },
        )

        if response.status_code != 200:
            raise FabricHTTPException(response)

        return TaggedValue(datasource.value, response.headers.get("ETag", ""))

    def get_publishing_info(self) -> TaggedValue:
        """
        Retrieve the publishing information.

        Returns
        -------
        TaggedValue
            The publishing information.
        """

        return TaggedValue.from_response(
            self._client.get(f"{self._data_agent_base_url}/management/publishing")
        )

    def put_publish_info(self, value: TaggedValue) -> TaggedValue:
        """
        Update the publishing information with the provided description.

        Parameters
        ----------
        value : TaggedValue
            The new publishing information.

        Returns
        -------
        TaggedValue
            The updated publishing information with the new ETag.
        """

        return TaggedValue.from_response(
            self._client.put(
                f"{self._data_agent_base_url}/management/publishing",
                json=value.value,
                headers={
                    "Content-Type": "application/json",
                    "If-Match": value.etag,
                },
            )
        )

    def add_datasource(self, datasource_body: dict) -> dict:
        """
        Add a new datasource to the system.

        Parameters
        ----------
        datasource_body : dict
            A dictionary containing the details of the datasource to be added.

        Returns
        -------
        dict
            A dictionary containing the response content of the added datasource.

        Raises
        ------
        FabricHTTPException
            If the response status code is not 200.
        """

        # Common header for all the datasources
        headers = {
            "Content-Type": "application/json",
            "x-ms-workload-resource-moniker": f"{self.workload_resource_moniker}",
            "x-ms-ai-assistant-scenario": f"{self.scenario}",
            "x-ms-ai-aiskill-stage": f"{self.stage}",
        }
        # Make the POST request
        add_datasource_response = self._client.post(
            f"{self._data_agent_base_url}/management/datasources",
            json=datasource_body,
            headers=headers,
        )
        # Raise FabricHTTPException if the status code is not 200
        if add_datasource_response.status_code != 200:
            raise FabricHTTPException(add_datasource_response)

        return add_datasource_response.json()

    def publish(self, configuration: TaggedValue, description: Optional[str] = None) -> None:
        """
        Publish the Data Agent configuration.

        Parameters
        ----------
        configuration : TaggedValue
            The configuration to publish.
        description : Optional[str], optional
            The description to set before publishing. If None, existing description is preserved.

        Raises
        ------
        FabricHTTPException
            If the response status code is not 200.
        """
        if description is not None:
            try:
                publishing_info = self.get_publishing_info()
                publishing_info.value["description"] = description
                self.put_publish_info(publishing_info)
            except FabricHTTPException as e:
                if e.status_code == 404:
                    # If publishing info does not exist, create it
                    publishing_info = TaggedValue(
                        value={"description": description},
                        etag=""
                    )
                    self.put_publish_info(publishing_info)
                else:
                    raise

        response = self._client.put(
            f"{self._data_agent_base_url}/management/deploy",
            headers={
                "Content-Type": "application/json",
                "If-Match": configuration.etag,
            },
        )

        if response.status_code != 200:
            raise FabricHTTPException(response)

    def get_schema(
        self,
        datasource_workspace_id: str,
        datasource_id: str,
        type: str,
        response_source: str = "live",
    ) -> dict:
        """
        Retrieve the schema for a specified datasource.

        Parameters
        ----------
        datasource_workspace_id : UUID
            The workspace ID of the datasource.
        datasource_id : str
            The unique identifier of the datasource.
        type : str
            The type of the datasource (e.g., "LakehouseTables", "Kusto").
        response_source : str, optional
            The source of the response, default is "live".

        Returns
        -------
        dict
            The JSON response containing the schema of the datasource.

        Raises
        ------
        FabricHTTPException
            If the response status code is not 200.
        """

        # Construct the URL
        get_schema_url = f"{self._host}/webapi/capacities/{self.capacity_id}/workloads/ML/AISkill/Automatic/v1/workspaces/{datasource_workspace_id}/artifacts/{datasource_id}/schema?responseSource={response_source}&dataSourceType={type}"

        # Construct the headers
        headers = {
            "Content-Type": "application/json",
            "x-ms-upstream-artifact-id": str(self.data_agent_id),
            "x-ms-workload-resource-moniker": self.workload_resource_moniker,
        }
        # Make the GET request
        response = self._client.get(get_schema_url, headers=headers)
        # Raise FabricHTTPException if the status code is not 200
        if response.status_code != 200:
            raise FabricHTTPException(response)
        return response.json()

    def get_datasource_fewshots(self, datasource_id: str):
        return TaggedValue.from_response(
            self._client.get(
                f"{self._data_agent_base_url}/management/datasources/{datasource_id}/fewshots"
            )
        )

    def set_datasource_fewshots(self, datasource_id: str, fewshots: TaggedValue):
        response = self._client.post(
            f"{self._data_agent_base_url}/management/datasources/{datasource_id}/fewshots",
            json=fewshots.value,
            headers={"If-Match": fewshots.etag},
        )

        if response.status_code != 200:
            raise FabricHTTPException(response)
