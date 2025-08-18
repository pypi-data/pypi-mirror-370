"""
Unit tests for fabric.dataagent.evaluation._storage
"""
import pytest
import pandas as pd
from unittest.mock import patch, MagicMock

from fabric.dataagent.evaluation._storage import _save_output, _get_data, _on_jupyter, _default_lakehouse_path


@patch('fabric.dataagent.evaluation._storage._default_lakehouse_path')
@patch('fabric.dataagent.evaluation._storage._on_jupyter')
def test_save_output_jupyter(mock_on_jupyter, mock_default_lakehouse_path):
    """Test _save_output function in Jupyter environment."""
    # Setup
    mock_on_jupyter.return_value = True
    mock_default_lakehouse_path.return_value = "abfs://lakehouse@workspace"
    df = pd.DataFrame({"col1": [1, 2], "col2": ["a", "b"]})
    # Patch the correct deltalake writer using importlib to inject into sys.modules
    import sys
    import types
    mock_writer_module = types.ModuleType('deltalake.writer')
    def mock_write_deltalake(table_path, df_arg, mode=None):
        mock_write_deltalake.called = True
        mock_write_deltalake.args = (table_path, df_arg)
        mock_write_deltalake.kwargs = {'mode': mode}
    mock_write_deltalake.called = False
    mock_writer_module.write_deltalake = mock_write_deltalake
    sys.modules['deltalake.writer'] = mock_writer_module
    # Execute
    _save_output(df, "test_table")
    # Assert
    assert mock_write_deltalake.called
    args = mock_write_deltalake.args
    kwargs = mock_write_deltalake.kwargs
    assert args[0] == "abfs://lakehouse@workspace/Tables/test_table"
    assert args[1] is df
    assert kwargs["mode"] == "append"
    # Clean up
    del sys.modules['deltalake.writer']


@patch('fabric.dataagent.evaluation._storage._default_lakehouse_path')
@patch('fabric.dataagent.evaluation._storage._on_jupyter')
def test_save_output_spark(mock_on_jupyter, mock_default_lakehouse_path):
    """Test _save_output function in Spark environment (non-Jupyter)."""
    # Setup
    mock_on_jupyter.return_value = False
    mock_default_lakehouse_path.return_value = "abfs://lakehouse@workspace"
    df = pd.DataFrame({"col1": [1, 2], "col2": ["a", "b"]})
    # Mock the Spark session
    mock_spark = MagicMock()
    mock_spark_df = MagicMock()
    mock_spark.createDataFrame.return_value = mock_spark_df
    # Setup mock for reading existing table (table exists case)
    mock_delta_df = MagicMock()
    mock_delta_df.schema = "test_schema"
    mock_spark.read.format.return_value.load.return_value = mock_delta_df
    # Inject a mock pyspark.sql module into sys.modules
    import sys
    import types
    mock_pyspark_sql = types.ModuleType('pyspark.sql')
    mock_spark_session_cls = MagicMock()
    mock_spark_session_cls.builder.getOrCreate.return_value = mock_spark
    mock_pyspark_sql.SparkSession = mock_spark_session_cls
    sys.modules['pyspark.sql'] = mock_pyspark_sql
    # Execute
    _save_output(df, "test_table")
    # Assert
    mock_spark.createDataFrame.assert_called_once_with(df, schema="test_schema")
    mock_spark_df.write.format.assert_called_once_with("delta")
    mock_spark_df.write.format.return_value.mode.assert_called_once_with("append")
    mock_spark_df.write.format.return_value.mode.return_value.save.assert_called_once_with(
        "abfs://lakehouse@workspace/Tables/test_table"
    )
    # Clean up
    del sys.modules['pyspark.sql']


@patch('fabric.dataagent.evaluation._storage._default_lakehouse_path')
@patch('fabric.dataagent.evaluation._storage._on_jupyter')
def test_save_output_spark_new_table(mock_on_jupyter, mock_default_lakehouse_path):
    """Test _save_output function in Spark environment for a new table."""
    # Setup
    mock_on_jupyter.return_value = False
    mock_default_lakehouse_path.return_value = "abfs://lakehouse@workspace"
    df = pd.DataFrame({"col1": [1, 2], "col2": ["a", "b"], "run_timestamp": [pd.Timestamp("2023-01-01"), pd.Timestamp("2023-01-02")]})
    # Mock the Spark session
    mock_spark = MagicMock()
    mock_spark_df = MagicMock()
    mock_spark.createDataFrame.return_value = mock_spark_df
    # Setup mock for reading non-existing table (throws exception)
    mock_spark.read.format.return_value.load.side_effect = Exception("Table does not exist")
    # Inject a mock pyspark.sql module into sys.modules
    import sys
    import types
    mock_pyspark_sql = types.ModuleType('pyspark.sql')
    mock_spark_session_cls = MagicMock()
    mock_spark_session_cls.builder.getOrCreate.return_value = mock_spark
    mock_pyspark_sql.SparkSession = mock_spark_session_cls
    sys.modules['pyspark.sql'] = mock_pyspark_sql
    # Execute
    _save_output(df, "test_table")
    # Assert
    mock_spark.createDataFrame.assert_called_once_with(df)
    mock_spark_df.write.format.assert_called_once_with("delta")
    mock_spark_df.write.format.return_value.mode.assert_called_once_with("append")
    mock_spark_df.write.format.return_value.mode.return_value.save.assert_called_once_with(
        "abfs://lakehouse@workspace/Tables/test_table"
    )
    # Clean up
    del sys.modules['pyspark.sql']


@patch('fabric.dataagent.evaluation._storage._default_lakehouse_path')
@patch('fabric.dataagent.evaluation._storage._on_jupyter')
def test_get_data_jupyter(mock_on_jupyter, mock_default_lakehouse_path):
    """Test _get_data function in Jupyter environment."""
    # Setup
    mock_on_jupyter.return_value = True
    mock_default_lakehouse_path.return_value = "abfs://lakehouse@workspace"
    mock_delta_table = MagicMock()
    mock_df = pd.DataFrame({"col1": [1, 2], "col2": ["a", "b"]})
    mock_delta_table.to_pandas.return_value = mock_df
    # Inject a mock deltalake module with DeltaTable
    import sys
    import types
    mock_deltalake = types.ModuleType('deltalake')
    mock_deltalake.DeltaTable = MagicMock(return_value=mock_delta_table)
    sys.modules['deltalake'] = mock_deltalake
    # Execute
    result = _get_data("test_table")
    # Assert
    mock_deltalake.DeltaTable.assert_called_once_with("abfs://lakehouse@workspace/Tables/test_table")
    assert result is mock_df
    # Clean up
    del sys.modules['deltalake']


@patch('fabric.dataagent.evaluation._storage._default_lakehouse_path')
@patch('fabric.dataagent.evaluation._storage._on_jupyter')
def test_get_data_spark(mock_on_jupyter, mock_default_lakehouse_path):
    """Test _get_data function in Spark environment."""
    # Setup
    mock_on_jupyter.return_value = False
    mock_default_lakehouse_path.return_value = "abfs://lakehouse@workspace"
    # Mock the Spark session
    mock_spark = MagicMock()
    mock_spark_df = MagicMock()
    mock_df = pd.DataFrame({"col1": [1, 2], "col2": ["a", "b"]})
    mock_spark_df.toPandas.return_value = mock_df
    mock_spark.read.format.return_value.load.return_value = mock_spark_df
    # Inject a mock pyspark.sql module into sys.modules
    import sys
    import types
    mock_pyspark_sql = types.ModuleType('pyspark.sql')
    mock_spark_session_cls = MagicMock()
    mock_spark_session_cls.builder.getOrCreate.return_value = mock_spark
    mock_pyspark_sql.SparkSession = mock_spark_session_cls
    sys.modules['pyspark.sql'] = mock_pyspark_sql
    # Execute
    result = _get_data("test_table")
    # Assert
    mock_spark.read.format.assert_called_once_with("delta")
    mock_spark.read.format.return_value.load.assert_called_once_with("abfs://lakehouse@workspace/Tables/test_table")
    assert result is mock_df
    # Clean up
    del sys.modules['pyspark.sql']


@patch('fabric.dataagent.evaluation._storage._default_lakehouse_path')
@patch('fabric.dataagent.evaluation._storage._on_jupyter')
@patch('fabric.dataagent.evaluation._storage.display')
@patch('fabric.dataagent.evaluation._storage.HTML', return_value="HTML")
def test_get_data_exception(mock_html, mock_display, mock_on_jupyter, mock_default_lakehouse_path):
    """Test _get_data function when an exception occurs."""
    mock_on_jupyter.return_value = True
    mock_default_lakehouse_path.return_value = "abfs://lakehouse@workspace"
    import sys
    import types
    mock_deltalake = types.ModuleType('deltalake')
    def raise_exception(*args, **kwargs):
        raise Exception("Table does not exist. Please provide the table name from attached default lakehouse.")
    mock_deltalake.DeltaTable = raise_exception
    sys.modules['deltalake'] = mock_deltalake
    # Execute
    result = _get_data("test_table")
    # Assert
    assert result is None
    mock_display.assert_called()
    # Clean up
    del sys.modules['deltalake']


@patch('os.environ.get')
def test_on_jupyter(mock_environ_get):
    """Test _on_jupyter function."""
    # Test when running in Jupyter
    mock_environ_get.return_value = "jupyter"
    assert _on_jupyter() is True
    # Test when not running in Jupyter
    mock_environ_get.return_value = "not_jupyter"
    assert _on_jupyter() is False
    # Test when environment variable is not set
    mock_environ_get.return_value = ""
    assert _on_jupyter() is False


@patch('fabric.dataagent.evaluation._storage.get_fabric_context')
def test_default_lakehouse_path(mock_get_fabric_context):
    """Test _default_lakehouse_path function."""
    # Setup
    mock_get_fabric_context.return_value = {
        'fs.defaultFS': 'abfs://workspace@account/',
        'trident.lakehouse.id': 'lakehouse_id'
    }
    # Execute
    result = _default_lakehouse_path()
    # Assert
    assert result == 'abfs://workspace@account/lakehouse_id'


@patch('fabric.dataagent.evaluation._storage._default_lakehouse_path')
@patch('fabric.dataagent.evaluation._storage._on_jupyter')
def test_save_output_jupyter_importerror(mock_on_jupyter, mock_default_lakehouse_path):
    mock_on_jupyter.return_value = True
    mock_default_lakehouse_path.return_value = "abfs://lakehouse@workspace"
    df = pd.DataFrame({"col1": [1, 2], "col2": ["a", "b"]})
    import sys
    import types
    mock_writer_module = types.ModuleType('deltalake.writer')
    def raise_import_error(*a, **k):
        raise ImportError("deltalake not found")
    mock_writer_module.write_deltalake = raise_import_error
    sys.modules['deltalake.writer'] = mock_writer_module
    _save_output(df, "test_table")  # Should log error, not raise
    del sys.modules['deltalake.writer']


@patch('fabric.dataagent.evaluation._storage._default_lakehouse_path')
@patch('fabric.dataagent.evaluation._storage._on_jupyter')
def test_save_output_jupyter_exception(mock_on_jupyter, mock_default_lakehouse_path):
    mock_on_jupyter.return_value = True
    mock_default_lakehouse_path.return_value = "abfs://lakehouse@workspace"
    df = pd.DataFrame({"col1": [1, 2], "col2": ["a", "b"]})
    import sys
    import types
    mock_writer_module = types.ModuleType('deltalake.writer')
    def raise_exception(*a, **k):
        raise Exception("fail")
    mock_writer_module.write_deltalake = raise_exception
    sys.modules['deltalake.writer'] = mock_writer_module
    _save_output(df, "test_table")  # Should log error, not raise
    del sys.modules['deltalake.writer']


@patch('fabric.dataagent.evaluation._storage._default_lakehouse_path')
@patch('fabric.dataagent.evaluation._storage._on_jupyter')
def test_save_output_spark_importerror(mock_on_jupyter, mock_default_lakehouse_path):
    mock_on_jupyter.return_value = False
    mock_default_lakehouse_path.return_value = "abfs://lakehouse@workspace"
    df = pd.DataFrame({"col1": [1, 2], "col2": ["a", "b"]})
    import sys
    import types
    mock_pyspark_sql = types.ModuleType('pyspark.sql')
    def raise_import_error(*a, **k):
        raise ImportError("pyspark not found")
    mock_pyspark_sql.SparkSession = raise_import_error
    sys.modules['pyspark.sql'] = mock_pyspark_sql
    _save_output(df, "test_table")  # Should log error, not raise
    del sys.modules['pyspark.sql']


@patch('fabric.dataagent.evaluation._storage._default_lakehouse_path')
@patch('fabric.dataagent.evaluation._storage._on_jupyter')
def test_save_output_spark_exception(mock_on_jupyter, mock_default_lakehouse_path):
    mock_on_jupyter.return_value = False
    mock_default_lakehouse_path.return_value = "abfs://lakehouse@workspace"
    df = pd.DataFrame({"col1": [1, 2], "col2": ["a", "b"]})
    import sys
    import types
    mock_pyspark_sql = types.ModuleType('pyspark.sql')
    def raise_exception(*a, **k):
        raise Exception("fail")
    mock_pyspark_sql.SparkSession = raise_exception
    sys.modules['pyspark.sql'] = mock_pyspark_sql
    _save_output(df, "test_table")  # Should log error, not raise
    del sys.modules['pyspark.sql']


@patch('fabric.dataagent.evaluation._storage._default_lakehouse_path')
@patch('fabric.dataagent.evaluation._storage._on_jupyter')
@patch('fabric.dataagent.evaluation._storage.display')
@patch('fabric.dataagent.evaluation._storage.HTML', return_value="HTML")
def test_get_data_jupyter_importerror(mock_html, mock_display, mock_on_jupyter, mock_default_lakehouse_path):
    mock_on_jupyter.return_value = True
    mock_default_lakehouse_path.return_value = "abfs://lakehouse@workspace"
    import sys
    import types
    mock_deltalake = types.ModuleType('deltalake')
    def raise_import_error(*a, **k):
        raise ImportError("deltalake not found")
    mock_deltalake.DeltaTable = raise_import_error
    sys.modules['deltalake'] = mock_deltalake
    result = _get_data("test_table")
    assert result is None
    mock_display.assert_called()
    del sys.modules['deltalake']


@patch('fabric.dataagent.evaluation._storage._default_lakehouse_path')
@patch('fabric.dataagent.evaluation._storage._on_jupyter')
@patch('fabric.dataagent.evaluation._storage.display')
@patch('fabric.dataagent.evaluation._storage.HTML', return_value="HTML")
def test_get_data_jupyter_exception(mock_html, mock_display, mock_on_jupyter, mock_default_lakehouse_path):
    mock_on_jupyter.return_value = True
    mock_default_lakehouse_path.return_value = "abfs://lakehouse@workspace"
    import sys
    import types
    mock_deltalake = types.ModuleType('deltalake')
    def raise_exception(*a, **k):
        raise Exception("fail")
    mock_deltalake.DeltaTable = raise_exception
    sys.modules['deltalake'] = mock_deltalake
    result = _get_data("test_table")
    assert result is None
    mock_display.assert_called()
    del sys.modules['deltalake']


@patch('fabric.dataagent.evaluation._storage._default_lakehouse_path')
@patch('fabric.dataagent.evaluation._storage._on_jupyter')
@patch('fabric.dataagent.evaluation._storage.display')
@patch('fabric.dataagent.evaluation._storage.HTML', return_value="HTML")
def test_get_data_spark_exception(mock_html, mock_display, mock_on_jupyter, mock_default_lakehouse_path):
    mock_on_jupyter.return_value = False
    mock_default_lakehouse_path.return_value = "abfs://lakehouse@workspace"
    import sys
    import types
    mock_pyspark_sql = types.ModuleType('pyspark.sql')
    def raise_exception(*a, **k):
        raise Exception("fail")
    mock_pyspark_sql.SparkSession = raise_exception
    sys.modules['pyspark.sql'] = mock_pyspark_sql
    result = _get_data("test_table")
    assert result is None
    mock_display.assert_called()
    del sys.modules['pyspark.sql']


@patch('fabric.dataagent.evaluation._storage.get_fabric_context', side_effect=Exception('fail'))
def test_default_lakehouse_path_exception(mock_get_fabric_context):
    result = _default_lakehouse_path()
    assert result == 'abfs://default@fabric/default_lakehouse'


@patch('fabric.dataagent.evaluation._storage._default_lakehouse_path')
@patch('fabric.dataagent.evaluation._storage._on_jupyter')
def test_save_output_outer_exception(mock_on_jupyter, mock_default_lakehouse_path):
    # Simulate an exception in the outer try block
    mock_on_jupyter.side_effect = Exception('outer fail')
    mock_default_lakehouse_path.return_value = "abfs://lakehouse@workspace"
    df = pd.DataFrame({"col1": [1, 2], "col2": ["a", "b"]})
    _save_output(df, "test_table")  # Should log error, not raise


@patch('fabric.dataagent.evaluation._storage._default_lakehouse_path')
@patch('fabric.dataagent.evaluation._storage._on_jupyter')
def test_get_data_outer_exception(mock_on_jupyter, mock_default_lakehouse_path):
    # Simulate an exception in the outer try block
    mock_on_jupyter.side_effect = Exception('outer fail')
    mock_default_lakehouse_path.return_value = "abfs://lakehouse@workspace"
    result = _get_data("test_table")
    assert result is None


@patch('fabric.dataagent.evaluation._storage.get_fabric_context')
def test_default_lakehouse_path_missing_keys(mock_get_fabric_context):
    # Missing required keys in context
    mock_get_fabric_context.return_value = {'fs.defaultFS': None, 'trident.lakehouse.id': None}
    result = _default_lakehouse_path()
    assert result == 'abfs://default@fabric/default_lakehouse'


@patch('os.environ.get', side_effect=Exception('fail'))
def test_on_jupyter_exception(mock_environ_get):
    # Should log a warning and return False
    assert _on_jupyter() is False
