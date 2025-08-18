import pytest
from unittest.mock import MagicMock, patch
from uuid import uuid4
from sempy.fabric.exceptions import FabricHTTPException
from fabric.dataagent.client._create_delete import create_data_agent, delete_data_agent

# Helper for DataFrame filtering mock

def make_match(empty, id_value):
    match = MagicMock()
    match.empty = empty
    id_col = MagicMock()
    id_col.values = id_value
    match.__getitem__.return_value = id_col
    return match

@patch('fabric.dataagent.client._create_delete.fabric')
@patch('fabric.dataagent.client._create_delete.FabricDataAgentManagement')
def test_create_data_agent_success(mock_mgmt, mock_fabric):
    mock_rest_client = mock_fabric.FabricRestClient
    mock_fabric.get_notebook_workspace_id.return_value = 'wsid'
    mock_response = MagicMock()
    mock_response.status_code = 201
    mock_response.reason = 'Created'
    mock_response.url = 'http://test-url'
    mock_response.text = 'OK'
    mock_response.headers = {}
    mock_rest_client.return_value.post.return_value = mock_response
    mock_mgmt.return_value = 'mgmt_obj'
    result = create_data_agent('agent1')
    assert result == 'mgmt_obj'
    mock_rest_client.return_value.post.assert_called_once()
    mock_mgmt.assert_called_once_with('agent1', 'wsid')

@patch('fabric.dataagent.client._create_delete.fabric')
@patch('fabric.dataagent.client._create_delete.FabricDataAgentManagement')
def test_create_data_agent_already_exists(mock_mgmt, mock_fabric):
    mock_rest_client = mock_fabric.FabricRestClient
    mock_fabric.get_notebook_workspace_id.return_value = 'wsid'
    mock_response = MagicMock()
    mock_response.status_code = 400
    mock_response.reason = 'Bad Request'
    mock_response.url = 'http://test-url'
    mock_response.text = 'Already exists'
    mock_response.headers = {}
    error_json = {'errorCode': 'ItemDisplayNameAlreadyInUse'}
    mock_response.json.return_value = error_json
    exc = FabricHTTPException(mock_response)
    mock_rest_client.return_value.post.side_effect = exc
    mock_mgmt.return_value = 'mgmt_obj'
    result = create_data_agent('agent1')
    assert result == 'mgmt_obj'
    mock_mgmt.assert_called_once_with('agent1', 'wsid')

@patch('fabric.dataagent.client._create_delete.fabric')
@patch('fabric.dataagent.client._create_delete.FabricDataAgentManagement')
def test_create_data_agent_error(mock_mgmt, mock_fabric):
    mock_rest_client = mock_fabric.FabricRestClient
    mock_fabric.get_notebook_workspace_id.return_value = 'wsid'
    mock_response = MagicMock()
    mock_response.status_code = 500
    mock_response.reason = 'Internal Server Error'
    mock_response.url = 'http://test-url'
    mock_response.text = 'Error'
    mock_response.headers = {}
    mock_rest_client.return_value.post.return_value = mock_response
    with pytest.raises(FabricHTTPException):
        create_data_agent('agent1')

@patch('fabric.dataagent.client._create_delete.fabric')
def test_delete_data_agent_by_id(mock_fabric):
    mock_rest_client = mock_fabric.FabricRestClient
    mock_fabric.get_notebook_workspace_id.return_value = 'wsid'
    mock_response = MagicMock(status_code=200)
    mock_rest_client.return_value.delete.return_value = mock_response
    delete_data_agent(uuid4())
    mock_rest_client.return_value.delete.assert_called_once()

@patch('fabric.dataagent.client._create_delete.fabric')
def test_delete_data_agent_by_name_success(mock_fabric):
    mock_rest_client = mock_fabric.FabricRestClient
    mock_fabric.get_notebook_workspace_id.return_value = 'wsid'
    mock_response = MagicMock(status_code=200)
    mock_rest_client.return_value.delete.return_value = mock_response
    df = MagicMock()
    df.__getitem__.side_effect = lambda mask: make_match(False, ['id1'])
    mock_fabric.list_items.return_value = df
    delete_data_agent('agent1')
    mock_rest_client.return_value.delete.assert_called_once()

@patch('fabric.dataagent.client._create_delete.fabric')
def test_delete_data_agent_not_found(mock_fabric):
    mock_rest_client = mock_fabric.FabricRestClient
    mock_fabric.get_notebook_workspace_id.return_value = 'wsid'
    df = MagicMock()
    df.__getitem__.side_effect = lambda mask: make_match(True, [])
    df_ai = MagicMock()
    df_ai.__getitem__.side_effect = lambda mask: make_match(True, [])
    mock_fabric.list_items.side_effect = [df, df_ai]
    with pytest.raises(ValueError, match="Data Agent 'agent1' not found."):
        delete_data_agent('agent1')

@patch('fabric.dataagent.client._create_delete.fabric')
def test_delete_data_agent_error(mock_fabric):
    mock_rest_client = mock_fabric.FabricRestClient
    mock_fabric.get_notebook_workspace_id.return_value = 'wsid'
    mock_response = MagicMock(status_code=500)
    mock_rest_client.return_value.delete.return_value = mock_response
    df = MagicMock()
    df.__getitem__.side_effect = lambda mask: make_match(False, ['id1'])
    mock_fabric.list_items.return_value = df
    with pytest.raises(FabricHTTPException):
        delete_data_agent('agent1')
