import pytest
from unittest.mock import MagicMock, patch
import pandas as pd
from fabric.dataagent.datasources.kustodb import _KustoConnection, KustoDBSource

@patch('fabric.dataagent.datasources.kustodb._token_utils')
@patch('fabric.dataagent.datasources.kustodb.KustoConnectionStringBuilder')
@patch('fabric.dataagent.datasources.kustodb.KustoClient')
def test_kusto_connection_init(mock_client, mock_kcsb, mock_token_utils):
    mock_token_utils.get_access_token.return_value = 'token'
    mock_token_utils.get_aad_token.return_value = 'aad_token'
    mock_kcsb.with_token_provider.return_value = 'kcsb_obj'
    instance = _KustoConnection('cluster', 'db')
    assert instance._client == mock_client.return_value
    assert instance._database == 'db'
    mock_kcsb.with_token_provider.assert_called_once()

@patch('fabric.dataagent.datasources.kustodb.dataframe_from_result_table')
@patch('fabric.dataagent.datasources.kustodb.KustoClient')
def test_kusto_connection_query_success(mock_client, mock_df_from_result):
    conn = _KustoConnection('cluster', 'db')
    conn._client = MagicMock()
    response = MagicMock()
    response.primary_results = [MagicMock()]
    conn._client.execute.return_value = response
    mock_df_from_result.return_value = pd.DataFrame({'a': [1]})
    df = conn.query('KQL', max_rows=10, request_options={'foo': 'bar'})
    assert isinstance(df, pd.DataFrame)
    conn._client.execute.assert_called_once()
    mock_df_from_result.assert_called_once()

@patch('fabric.dataagent.datasources.kustodb.KustoClient')
def test_kusto_connection_query_kusto_service_error(mock_client):
    conn = _KustoConnection('cluster', 'db')
    conn._client = MagicMock()
    from azure.kusto.data.exceptions import KustoServiceError
    conn._client.execute.side_effect = KustoServiceError()
    with pytest.raises(RuntimeError, match='KustoServiceError'):
        conn.query('KQL')

@patch('fabric.dataagent.datasources.kustodb.KustoClient')
def test_kusto_connection_query_kusto_client_error(mock_client):
    conn = _KustoConnection('cluster', 'db')
    conn._client = MagicMock()
    from azure.kusto.data.exceptions import KustoClientError
    conn._client.execute.side_effect = KustoClientError()
    with pytest.raises(RuntimeError, match='KustoClientError'):
        conn.query('KQL')

@patch('fabric.dataagent.datasources.kustodb.KustoClient')
def test_kusto_connection_query_generic_error(mock_client):
    conn = _KustoConnection('cluster', 'db')
    conn._client = MagicMock()
    conn._client.execute.side_effect = Exception('other error')
    with pytest.raises(RuntimeError, match='Unexpected Kusto query failure:'):
        conn.query('KQL')

@patch('fabric.dataagent.datasources.kustodb.KustoClient')
def test_kusto_connection_context_manager(mock_client):
    conn = _KustoConnection('cluster', 'db')
    # No close method
    assert conn.__enter__() is conn
    assert conn.__exit__(None, None, None) is False
    # With close method
    conn._client.close = MagicMock()
    assert conn.__exit__(None, None, None) is False
    conn._client.close.assert_called_once()


def test_kustodbsource_init():
    cfg = {'database_name': 'db', 'workspace_id': 'wsid'}
    src = KustoDBSource(cfg)
    assert src._cfg == cfg
    assert src.artifact_id_or_name == 'db'
    assert src.workspace_id_or_name == 'wsid'
    cfg2 = {'display_name': 'disp', 'workspace_id': 'wsid', 'database_name': 'db'}
    src2 = KustoDBSource(cfg2)
    assert src2.artifact_id_or_name == 'db'

@patch('fabric.dataagent.datasources.kustodb._KustoConnection')
def test_kustodbsource_connect_endpoint(mock_conn):
    cfg = {'endpoint': 'https://cluster', 'database_name': 'db', 'workspace_id': 'wsid'}
    src = KustoDBSource(cfg)
    src.connect()
    mock_conn.assert_called_once_with(cluster='https://cluster', database='db')

@patch('fabric.dataagent.datasources.kustodb._KustoConnection')
def test_kustodbsource_connect_workspace_guid(mock_conn):
    cfg = {'database_name': 'db', 'workspace_id': 'wsid'}
    src = KustoDBSource(cfg)
    src.connect()
    mock_conn.assert_called_once_with(cluster='https://wsid', database='db')

@patch('fabric.dataagent.datasources.kustodb._KustoConnection')
def test_kustodbsource_connect_workspace_guid_with_http(mock_conn):
    cfg = {'database_name': 'db', 'workspace_id': 'http://wsid'}
    src = KustoDBSource(cfg)
    src.connect()
    mock_conn.assert_called_once_with(cluster='http://wsid', database='db')
