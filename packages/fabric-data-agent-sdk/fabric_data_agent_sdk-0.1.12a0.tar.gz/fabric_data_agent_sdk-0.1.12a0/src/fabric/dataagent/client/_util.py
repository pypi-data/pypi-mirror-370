from uuid import UUID
import typing as t
import sempy.fabric as sf
from sempy.fabric.exceptions import FabricHTTPException
from typing import Sequence

_DEFAULT_ITEM_TYPES: tuple[str, ...] = (
    "Lakehouse",
    "Warehouse",
    "KQLDatabase",
    "SemanticModel",
)
def get_artifact_by_id_or_name(
    identifier: str | UUID,
    type_or_types: str | Sequence[str] | None,
    workspace_id: t.Optional[UUID | str] = None,
) -> t.Tuple[str, UUID]:
    """
    Retrieve the artifact name and ID by its name or ID within the specified workspace.
    Supports a single artifact type or a list of types.

    Parameters
    ----------
    identifier : str or UUID
        The name or ID of the artifact.
    type_or_types : str or list of str
        The type(s) of the artifact to search (e.g., "Lakehouse" or ["Lakehouse", "DataAgent"]).
    workspace_id : Optional[str or UUID], optional
        The workspace ID. If not provided, the current workspace ID is used.

    Returns
    -------
    tuple[str, UUID]
        A tuple containing the artifact name and its UUID.

    Raises
    ------
    ValueError
        If the workspace contains no artifacts of the supplied type(s),
        or if the specified artifact is not found.
    KeyError
        If required columns are missing in the artifact DataFrame.
    """

    # normalize parameter
    if type_or_types is None:
        types: Sequence[str] = _DEFAULT_ITEM_TYPES
    elif isinstance(type_or_types, str):
        types = [type_or_types]
    else:
        types = type_or_types

    last_error = None

    for artifact_type in types:
        try:
            df = sf.list_items(type=artifact_type, workspace=workspace_id)
            if df.empty:
                continue

            if isinstance(identifier, UUID):
                artifact_row = df[df["Id"] == str(identifier)]
                if not artifact_row.empty:
                    artifact_name = artifact_row["Display Name"].values[0]
                    return artifact_name, identifier
            else:
                artifact_row = df[df["Display Name"] == identifier]
                if not artifact_row.empty:
                    artifact_id = UUID(artifact_row["Id"].values[0])
                    return identifier, artifact_id

        except (ValueError, KeyError) as e:
            last_error = e
            continue

    if last_error is None:
        raise ValueError(
            f"Workspace contains no artifacts of the supplied type(s): {types}"
        )
    else:
        raise ValueError(
            f"Artifact '{identifier}' not found in any of the types: {types}"
        ) from last_error


def resolve_workspace_name_and_id(workspace: str | UUID | None) -> t.Tuple[str, UUID]:
    """
    Resolve the workspace name and ID based on the provided input.

    Parameters
    ----------
    workspace : str or UUID or None
        The workspace name or ID. If None, the current notebook's workspace is used.

    Returns
    -------
    tuple[str, UUID]
        A tuple containing the workspace name and its UUID.
    """
    if workspace is None:
        workspace_id = UUID(sf.get_notebook_workspace_id())
        workspace_name = sf.resolve_workspace_name(workspace_id)
    else:
        workspace_name = sf.resolve_workspace_name(workspace)
        workspace_id = UUID(sf.resolve_workspace_id(workspace))

    return workspace_name, workspace_id


def get_workspace_capacity_id(workspace_id: str | UUID) -> str:
    """
    Retrieve the capacity ID for the specified workspace.

    Parameters
    ----------
    workspace_id : str or UUID
        The ID of the workspace.

    Returns
    -------
    str
        The capacity ID associated with the workspace.

    Raises
    ------
    FabricHTTPException
        If the workspace data retrieval fails.
    ValueError
        If the capacity ID is not found in the response.
    """
    fabric_rest_client = sf.FabricRestClient()
    response = fabric_rest_client.get(f'/v1/workspaces/{workspace_id}')

    if response.status_code != 200:
        raise FabricHTTPException(
            f"Failed to retrieve workspace data: {response.status_code}, {response.text}"
        )

    content = response.json()
    capacity_id = content.get('capacityId')
    if not capacity_id:
        raise ValueError("Capacity ID not found in the response.")

    return capacity_id
