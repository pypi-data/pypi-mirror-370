import pytest
from unittest.mock import MagicMock, patch
from uuid import uuid4, UUID
from fabric.dataagent.client._util import (
    get_artifact_by_id_or_name,
    resolve_workspace_name_and_id,
    get_workspace_capacity_id,
)
from sempy.fabric.exceptions import FabricHTTPException

# Helper for DataFrame filtering mock
def make_artifact_row(empty=False, name='Lakehouse', id_val='12345678123456781234567812345678'):
    artifact_row = MagicMock()
    artifact_row.empty = empty
    display_name_col = MagicMock()
    display_name_col.values = [name]
    id_col = MagicMock()
    id_col.values = [id_val]
    artifact_row.__getitem__.side_effect = lambda k: display_name_col if k == 'Display Name' else id_col
    return artifact_row

@patch('fabric.dataagent.client._util.sf')
def test_get_artifact_by_id_or_name_found_by_name(mock_sf):
    df = MagicMock()
    df.empty = False
    df.__getitem__.side_effect = lambda mask: make_artifact_row()
    mock_sf.list_items.return_value = df
    name, artifact_id = get_artifact_by_id_or_name('Lakehouse', 'Lakehouse', 'wsid')
    assert name == 'Lakehouse'
    assert artifact_id == UUID('12345678123456781234567812345678')

@patch('fabric.dataagent.client._util.sf')
def test_get_artifact_by_id_or_name_found_by_id(mock_sf):
    df = MagicMock()
    df.empty = False
    df.__getitem__.side_effect = lambda mask: make_artifact_row()
    mock_sf.list_items.return_value = df
    name, artifact_id = get_artifact_by_id_or_name(UUID('12345678123456781234567812345678'), 'Lakehouse', 'wsid')
    assert name == 'Lakehouse'
    assert artifact_id == UUID('12345678123456781234567812345678')

@patch('fabric.dataagent.client._util.sf')
def test_get_artifact_by_id_or_name_not_found(mock_sf):
    df = MagicMock()
    df.empty = False
    df.__getitem__.side_effect = lambda mask: make_artifact_row(empty=True)
    mock_sf.list_items.return_value = df
    with pytest.raises(ValueError):
        get_artifact_by_id_or_name('notfound', 'Lakehouse', 'wsid')

@patch('fabric.dataagent.client._util.sf')
def test_get_artifact_by_id_or_name_no_artifacts(mock_sf):
    df = MagicMock()
    df.empty = True
    mock_sf.list_items.return_value = df
    with pytest.raises(ValueError):
        get_artifact_by_id_or_name('notfound', 'Lakehouse', 'wsid')

@patch('fabric.dataagent.client._util.sf')
def test_get_artifact_by_id_or_name_missing_column(mock_sf):
    df = MagicMock()
    df.empty = False
    def getitem(key):
        raise KeyError(key)
    df.__getitem__.side_effect = getitem
    mock_sf.list_items.return_value = df
    with pytest.raises(ValueError):
        get_artifact_by_id_or_name('notfound', 'Lakehouse', 'wsid')

@patch('fabric.dataagent.client._util.sf')
def test_resolve_workspace_name_and_id_none(mock_sf):
    mock_sf.get_notebook_workspace_id.return_value = str(uuid4())
    mock_sf.resolve_workspace_name.return_value = 'wsname'
    name, wsid = resolve_workspace_name_and_id(None)
    assert name == 'wsname'
    assert isinstance(wsid, UUID)

@patch('fabric.dataagent.client._util.sf')
def test_resolve_workspace_name_and_id_str(mock_sf):
    mock_sf.resolve_workspace_name.return_value = 'wsname'
    mock_sf.resolve_workspace_id.return_value = str(uuid4())
    name, wsid = resolve_workspace_name_and_id('wsname')
    assert name == 'wsname'
    assert isinstance(wsid, UUID)

@patch('fabric.dataagent.client._util.sf')
def test_resolve_workspace_name_and_id_uuid(mock_sf):
    mock_sf.resolve_workspace_name.return_value = 'wsname'
    mock_sf.resolve_workspace_id.return_value = str(uuid4())
    wsid = uuid4()
    name, wsid_out = resolve_workspace_name_and_id(wsid)
    assert name == 'wsname'
    assert isinstance(wsid_out, UUID)

@patch('fabric.dataagent.client._util.sf')
def test_get_workspace_capacity_id_success(mock_sf):
    mock_client = MagicMock()
    mock_sf.FabricRestClient.return_value = mock_client
    mock_response = MagicMock()
    mock_response.status_code = 200
    mock_response.json.return_value = {'capacityId': 'capid'}
    mock_response.reason = b'OK'
    mock_response.headers = {}
    mock_response.url = 'http://test-url'
    mock_client.get.return_value = mock_response
    capid = get_workspace_capacity_id('wsid')
    assert capid == 'capid'

@patch('fabric.dataagent.client._util.sf')
def test_get_workspace_capacity_id_http_error(mock_sf):
    mock_client = MagicMock()
    mock_sf.FabricRestClient.return_value = mock_client
    from sempy.fabric import exceptions
    original_init = exceptions.FabricHTTPException.__init__
    def patched_init(self, response):
        self.error_reason = str(response)
    exceptions.FabricHTTPException.__init__ = patched_init
    mock_response = MagicMock()
    mock_response.status_code = 500
    mock_response.text = 'fail'
    mock_client.get.return_value = mock_response
    try:
        with pytest.raises(FabricHTTPException):
            get_workspace_capacity_id('wsid')
    finally:
        exceptions.FabricHTTPException.__init__ = original_init

@patch('fabric.dataagent.client._util.sf')
def test_get_workspace_capacity_id_missing(mock_sf):
    mock_client = MagicMock()
    mock_sf.FabricRestClient.return_value = mock_client
    mock_response = MagicMock()
    mock_response.status_code = 200
    mock_response.json.return_value = {}
    mock_response.reason = b'OK'
    mock_response.headers = {}
    mock_response.url = 'http://test-url'
    mock_client.get.return_value = mock_response
    with pytest.raises(ValueError):
        get_workspace_capacity_id('wsid')
