from fabric.dataagent.client._fabric_data_agent_api import (
    FabricDataAgentAPI,
    get_artifact_by_id_or_name,
)
from fabric.dataagent.client._datasource import Datasource
import typing as t
from uuid import UUID
from sempy.fabric import list_items, get_notebook_workspace_id, resolve_workspace_id
from dataclasses import dataclass


@dataclass
class DataAgentConfiguration:
    """
    Configuration settings for an DataAgent.

    Attributes
    ----------
    instructions : str or None
        Additional instructions for the DataAgent.
    """

    instructions: str | None


class FabricDataAgentManagement:
    """
    Management class for DataAgent operations.

    Attributes
    ----------
    _client : FabricDataAgentAPI
        The FabricDataAgentAPI client instance.
    """

    _client: FabricDataAgentAPI

    def __init__(
        self, data_agent: str | UUID, workspace: t.Optional[str | UUID] = None
    ) -> None:
        """
        Initialize a FabricDataAgentManagement instance.

        Parameters
        ----------
        data_agent : str or UUID
            The name or ID of the DataAgent.
        workspace : str or UUID, optional
            The name or ID of the workspace. If not provided, it defaults to the current workspace.
        """
        self._client = FabricDataAgentAPI(data_agent=data_agent, workspace=workspace)

    def update_configuration(
        self, instructions: str | None = None,
    ) -> None:
        """
        Update the configuration of the Data Agent.

        Parameters
        ----------
        instructions : str, optional
            Additional instructions for the data agent.
        """
        config = self._client.get_configuration()

        if instructions:
            config.value["additionalInstructions"] = instructions

        self._client.set_configuration(config)

    def get_configuration(self) -> DataAgentConfiguration:
        """
        Retrieve the configuration of the Data Agent.

        Returns
        -------
        DataAgentConfiguration
            The configuration of the Data Agent.
        """
        config = self._client.get_configuration()

        return DataAgentConfiguration(
            instructions=config.value.get("additionalInstructions"),
        )

    def publish(self, description: t.Optional[str] = None) -> None:
        """
        Publish the Data Agent configuration.

        Parameters
        ----------
        description : str, optional
            The description to set before publishing. If None, existing description is preserved.
        """
        self._client.publish(self._client.get_configuration(), description)

    def get_datasources(self) -> t.List[Datasource]:
        """
        Retrieve the list of datasources for the Data Agent.

        Returns
        -------
        t.List[Datasource]
            The list of datasources.
        """
        return [
            Datasource(self._client, datasource.value['id'])
            for datasource in self._client.get_datasources()
        ]

    def add_datasource(
        self,
        artifact_name_or_id: str | UUID,
        workspace_id_or_name: t.Optional[str | UUID] = None,
        type: str | None = None,
    ) -> Datasource:
        """
        Add a new datasource to the Data Agent.

        Parameters
        ----------
        artifact_name_or_id : str or UUID
            The name or ID of the artifact.
        workspace_id_or_name : str or UUID, optional
            The workspace ID or name. Defaults to None.
        type : str, optional
            The type of the artifact. Defaults to None.

        Returns
        -------
        Datasource
            The added datasource.

        Raises
        ------
        ValueError
            If the datasource artifact type is unsupported or if the artifact cannot be found.
        """
        if workspace_id_or_name is None:
            workspace_id_or_name = get_notebook_workspace_id()

        workspace_id = resolve_workspace_id(workspace_id_or_name)

        if type is None:
            # auto-resolve type
            df_items = list_items(workspace=workspace_id_or_name)

            if isinstance(artifact_name_or_id, UUID):
                df_item = df_items[df_items['Id'] == str(artifact_name_or_id)]
            else:
                df_item = df_items[df_items['Display Name'] == artifact_name_or_id]

            if df_item.empty:
                raise ValueError(
                    f"Could not find datasource artifact '{artifact_name_or_id}' in workspace '{workspace_id_or_name}'"
                )

            if df_item.shape[0] > 1:
                raise ValueError(
                    f"Found multiple artifacts with name '{artifact_name_or_id}' in workspace '{workspace_id_or_name}'"
                )

            type = df_item['Type'].iloc[0]

        (artifact_name, artifact_id) = get_artifact_by_id_or_name(
            artifact_name_or_id, type, workspace_id_or_name
        )

        schema_types = {
            "lakehouse": "lakehouse_tables",
            "kqldatabase": "kusto",
            "warehouse": "data_warehouse",
            "semanticmodel": "semantic_model",
        }

        if type not in schema_types:
            raise ValueError(f"Unsupported artifact type '{type}'")
        
        # Check if datasource already exists
        for ds in self.get_datasources():
            cfg = ds.get_configuration()
            if (
                cfg.get("id") == artifact_id
                or cfg.get("display_name") == artifact_name
            ):
                return ds  # Already exists, return existing Datasource
        # If not found, add new datasource
        # also contains "cacheLastUpdatedTime" value
        schema = self._client.get_schema(
            workspace_id, artifact_id, schema_types[type.lower()]
        )

        ds = self._client.add_datasource(schema["schema"])

        return Datasource(self._client, ds["id"])

    def remove_datasource(self, datasource_name_or_id: str) -> None:
        """
        Remove a datasource from the Data Agent.

        Parameters
        ----------
        datasource_name_or_id : str
            The name or ID of the datasource to remove.

        Raises
        ------
        ValueError
            If the datasource cannot be found.
        """
        # to remove a datasource, we need to know the etag of the configuration
        config = self._client.get_configuration()

        datasources = self._client.get_datasources()

        for ds in datasources:
            if (
                ds.value['id'] == datasource_name_or_id
                or ds.value['display_name'] == datasource_name_or_id
            ):
                self._client.remove_datasource(ds.value['id'], config.etag)
                return

        raise ValueError(f"Could not find datasource '{datasource_name_or_id}'")
