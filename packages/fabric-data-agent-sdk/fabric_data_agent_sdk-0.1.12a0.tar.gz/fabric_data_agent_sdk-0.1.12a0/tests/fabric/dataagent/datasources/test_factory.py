import pytest
from unittest.mock import patch, MagicMock

def test_make_source_supported_types():
    from fabric.dataagent.datasources.factory import make_source
    with patch('fabric.dataagent.datasources.factory._TYPE_MAP', {
        'lakehouse_tables': MagicMock(),
        'data_warehouse': MagicMock(),
        'semantic_model': MagicMock(),
        'kusto': MagicMock(),
    }) as type_map:
        # Lakehouse
        cfg_lakehouse = {'type': 'lakehouse_tables', 'display_name': 'lh', 'id': 'lhid', 'workspace_id': 'wsid'}
        make_source(cfg_lakehouse)
        type_map['lakehouse_tables'].assert_called_once_with(artifact_id_or_name='lhid', workspace_id_or_name='wsid')
        # Warehouse
        cfg_warehouse = {'type': 'data_warehouse', 'display_name': 'wh', 'id': 'whid', 'workspace_id': 'wsid'}
        make_source(cfg_warehouse)
        type_map['data_warehouse'].assert_called_once_with(artifact_id_or_name='whid', workspace_id_or_name='wsid')
        # Semantic Model
        cfg_semantic = {'type': 'semantic_model', 'display_name': 'sm', 'id': 'smid', 'workspace_id': 'wsid'}
        make_source(cfg_semantic)
        type_map['semantic_model'].assert_called_once_with(artifact_id_or_name='smid', workspace_id_or_name='wsid')
        # Kusto
        cfg_kusto = {'type': 'kusto', 'display_name': 'kusto', 'endpoint': 'https://cluster', 'database_name': 'db', 'workspace_id': 'wsid'}
        make_source(cfg_kusto)
        type_map['kusto'].assert_called_once_with(cfg_kusto)


def test_make_source_missing_type_or_display_name():
    from fabric.dataagent.datasources.factory import make_source
    with pytest.raises(ValueError, match="cfg must contain 'type' and 'display_name'"):
        make_source({'type': 'lakehouse_tables'})
    with pytest.raises(ValueError, match="cfg must contain 'type' and 'display_name'"):
        make_source({'display_name': 'lh'})


def test_make_source_unsupported_type():
    from fabric.dataagent.datasources.factory import make_source
    cfg = {'type': 'unknown', 'display_name': 'lh'}
    with pytest.raises(ValueError, match="Unsupported datasource type 'unknown'"):
        make_source(cfg)
