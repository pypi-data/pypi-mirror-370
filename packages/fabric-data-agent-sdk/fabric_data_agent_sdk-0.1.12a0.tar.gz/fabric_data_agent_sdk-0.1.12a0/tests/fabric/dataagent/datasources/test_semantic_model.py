import unittest
from unittest.mock import patch, MagicMock
from fabric.dataagent.datasources.semantic_model import SemanticModelSource, _SemanticModelConnection

class TestSemanticModelSource(unittest.TestCase):
    def setUp(self):
        # Provide required arguments for BaseSource
        self.source = SemanticModelSource('dataset_id', 'workspace_id')

    @patch('fabric.dataagent.datasources.semantic_model._evaluate_dax')
    def test_semantic_model_connection_query_strips_brackets(self, mock_eval_dax):
        df = MagicMock()
        df.columns = ['[Sales]', '[Profit]', 'Other']
        mock_eval_dax.return_value = df
        conn = _SemanticModelConnection('dataset_id', 'workspace_id')
        result = conn.query('EVALUATE ...')
        self.assertEqual(df.columns, ['Sales', 'Profit', 'Other'])
        self.assertEqual(result, df)

    @patch('fabric.dataagent.datasources.semantic_model._evaluate_dax')
    def test_semantic_model_connection_query_no_brackets(self, mock_eval_dax):
        df = MagicMock()
        df.columns = ['Sales', 'Profit', 'Other']
        mock_eval_dax.return_value = df
        conn = _SemanticModelConnection('dataset_id', 'workspace_id')
        result = conn.query('EVALUATE ...')
        self.assertEqual(df.columns, ['Sales', 'Profit', 'Other'])
        self.assertEqual(result, df)

    def test_semantic_model_connection_context_manager(self):
        conn = _SemanticModelConnection('dataset_id', 'workspace_id')
        with conn as c:
            self.assertIs(c, conn)
        # __exit__ should return False
        self.assertFalse(conn.__exit__(None, None, None))

    @patch('fabric.dataagent.datasources.semantic_model._connect_tom')
    def test_connect_tom_default_readonly(self, mock_connect_tom):
        self.source.connect_tom()
        mock_connect_tom.assert_called_once_with(dataset='dataset_id', workspace='workspace_id', readonly=True)

    @patch('fabric.dataagent.datasources.semantic_model._connect_tom')
    def test_connect_tom_write_mode(self, mock_connect_tom):
        self.source.connect_tom(readonly=False)
        mock_connect_tom.assert_called_once_with(dataset='dataset_id', workspace='workspace_id', readonly=False)

    def test_connect_returns_semantic_model_connection(self):
        conn = self.source.connect()
        self.assertIsInstance(conn, _SemanticModelConnection)
        self.assertEqual(conn._dataset, 'dataset_id')
        self.assertEqual(conn._workspace, 'workspace_id')

    def test_semantic_model_connection_query_handles_non_str_columns(self):
        # Columns that are not strings should not be modified
        df = MagicMock()
        df.columns = [123, '[Profit]', None]
        with patch('fabric.dataagent.datasources.semantic_model._evaluate_dax', return_value=df):
            conn = _SemanticModelConnection('dataset_id', 'workspace_id')
            result = conn.query('EVALUATE ...')
            self.assertEqual(df.columns, [123, 'Profit', None])
            self.assertEqual(result, df)

    @patch('fabric.dataagent.datasources.semantic_model._evaluate_dax', side_effect=Exception('fail'))
    def test_semantic_model_connection_query_exception(self, mock_eval_dax):
        conn = _SemanticModelConnection('dataset_id', 'workspace_id')
        with self.assertRaises(Exception):
            conn.query('EVALUATE ...')
