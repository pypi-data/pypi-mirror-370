import unittest
from unittest.mock import patch, MagicMock
from uuid import UUID
import pandas as pd

from fabric.dataagent.client._datasource import Datasource
from fabric.dataagent.client._fabric_data_agent_mgmt import FabricDataAgentManagement
from fabric.dataagent.client._tagged_value import TaggedValue


class TestFabricDataAgentManagement(unittest.TestCase):
    def setUp(self):
        # Patch fabric_env_config even if it does not exist
        self.fabric_env_patch = patch('sempy.fabric.fabric_env_config', {}, create=True)
        self.fabric_env_patch.start()
        # Patch get_fabric_env_config to return a mock with fabric_env_config.shared_host
        self.get_fabric_env_patch = patch('synapse.ml.fabric.service_discovery.get_fabric_env_config', autospec=True)
        self.mock_get_fabric_env_config = self.get_fabric_env_patch.start()
        mock_env = MagicMock()
        mock_env.fabric_env_config.shared_host = "dummy_host"
        self.mock_get_fabric_env_config.return_value = mock_env

        patcher1 = patch('fabric.dataagent.client._fabric_data_agent_mgmt.FabricDataAgentAPI')
        patcher2 = patch('fabric.dataagent.client._fabric_data_agent_mgmt.get_artifact_by_id_or_name')
        patcher3 = patch('fabric.dataagent.client._fabric_data_agent_mgmt.list_items')
        patcher4 = patch('fabric.dataagent.client._fabric_data_agent_mgmt.get_notebook_workspace_id')
        patcher5 = patch('fabric.dataagent.client._fabric_data_agent_mgmt.resolve_workspace_id')
        self.MockFabricDataAgentAPI = patcher1.start()
        self.MockGetArtifactByIDOrName = patcher2.start()
        self.MockListItems = patcher3.start()
        self.MockGetNotebookWorkspaceID = patcher4.start()
        self.MockResolveWorkspaceID = patcher5.start()
        self.addCleanup(patcher1.stop)
        self.addCleanup(patcher2.stop)
        self.addCleanup(patcher3.stop)
        self.addCleanup(patcher4.stop)
        self.addCleanup(patcher5.stop)
        self.addCleanup(self.fabric_env_patch.stop)
        self.addCleanup(self.get_fabric_env_patch.stop)

        self.mock_client = self.MockFabricDataAgentAPI.return_value
        self.mock_get_artifact_by_id_or_name = self.MockGetArtifactByIDOrName
        self.mock_list_items = self.MockListItems
        self.mock_get_notebook_workspace_id = self.MockGetNotebookWorkspaceID
        self.mock_resolve_workspace_id = self.MockResolveWorkspaceID
        self.data_agent_management = FabricDataAgentManagement(
            data_agent="test_data_agent", workspace="test_workspace"
        )

    def test_update_configuration(self):
        self.mock_client.get_configuration.return_value = TaggedValue(
            {"additionalInstructions": "", "userDescription": ""}, "etag"
        )
        self.data_agent_management.update_configuration(
            instructions="New instructions",
        )
        self.mock_client.set_configuration.assert_called_once()
        updated_config = self.mock_client.set_configuration.call_args[0][0]
        self.assertEqual(
            updated_config.value["additionalInstructions"], "New instructions"
        )

    def test_get_configuration(self):
        self.mock_client.get_configuration.return_value = TaggedValue(
            {
                "additionalInstructions": "instructions",
                "userDescription": "description",
            },
            "etag",
        )
        config = self.data_agent_management.get_configuration()
        self.assertEqual(config.instructions, "instructions")

    def test_publish(self):
        self.mock_client.get_configuration.return_value = TaggedValue({}, "etag")
        self.data_agent_management.publish()
        self.mock_client.publish.assert_called_once()

        args, _ = self.mock_client.publish.call_args
        self.assertEqual(len(args), 2)
        self.assertEqual(args[0].value, {})
        self.assertEqual(args[0].etag, "etag")
        self.assertIsNone(args[1])

    def test_publish_with_description(self):
        self.mock_client.get_configuration.return_value = TaggedValue({}, "etag")
        self.data_agent_management.publish("Test description")
        self.mock_client.publish.assert_called_once()

        args, _ = self.mock_client.publish.call_args
        self.assertEqual(len(args), 2)
        self.assertEqual(args[0].value, {})
        self.assertEqual(args[0].etag, "etag")
        self.assertEqual(args[1], "Test description")
        

    def test_get_datasources(self):
        self.mock_client.get_datasources.return_value = iter(
            [TaggedValue({"id": "ds1"}, "etag"), TaggedValue({"id": "ds2"}, "etag")]
        )
        datasources = self.data_agent_management.get_datasources()
        self.assertEqual(len(datasources), 2)
        self.assertIsInstance(datasources[0], Datasource)
        self.assertEqual(datasources[0]._id, "ds1")

    def test_remove_datasource(self):
        self.mock_client.get_configuration.return_value = TaggedValue({}, "etag")
        self.mock_client.get_datasources.return_value = iter(
            [TaggedValue({"id": "ds1", "display_name": "datasource1"}, "etag")]
        )
        self.data_agent_management.remove_datasource("datasource1")
        self.mock_client.remove_datasource.assert_called_once_with("ds1", "etag")

    def test_remove_datasource_by_id(self):
        config = TaggedValue({}, 'etag')
        ds = MagicMock()
        ds.value = {'id': 'id1', 'display_name': 'foo'}
        self.mock_client.get_configuration.return_value = config
        self.mock_client.get_datasources.return_value = [ds]
        self.data_agent_management.remove_datasource('id1')
        self.mock_client.remove_datasource.assert_called_once_with('id1', 'etag')

    def test_remove_datasource_by_display_name(self):
        config = TaggedValue({}, 'etag')
        ds = MagicMock()
        ds.value = {'id': 'id1', 'display_name': 'foo'}
        self.mock_client.get_configuration.return_value = config
        self.mock_client.get_datasources.return_value = [ds]
        self.data_agent_management.remove_datasource('foo')
        self.mock_client.remove_datasource.assert_called_once_with('id1', 'etag')

    def test_get_datasources_empty(self):
        self.mock_client.get_datasources.return_value = []
        result = self.data_agent_management.get_datasources()
        self.assertEqual(result, [])

    def test_get_configuration_no_instructions(self):
        self.mock_client.get_configuration.return_value = TaggedValue({}, 'etag')
        result = self.data_agent_management.get_configuration()
        self.assertIsNone(result.instructions)

    def test_add_datasource_already_exists(self):
        # Setup mocks for already existing datasource
        self.mock_get_notebook_workspace_id.return_value = "wsid"
        self.mock_resolve_workspace_id.return_value = "wsid"
        self.mock_list_items.return_value = pd.DataFrame({
            "Display Name": ["foo"],
            "Id": ["id1"],
            "Type": ["lakehouse"]
        })
        self.mock_get_artifact_by_id_or_name.return_value = ("foo", UUID("12345678-1234-5678-1234-567812345678"))
        ds = MagicMock()
        ds.get_configuration.return_value = {"id": UUID("12345678-1234-5678-1234-567812345678"), "display_name": "foo"}
        ds._id = "id1"
        # Patch the Datasource class to return our mock when constructed
        with patch('fabric.dataagent.client._fabric_data_agent_mgmt.Datasource', return_value=ds):
            self.mock_client.get_datasources.return_value = [ds]
            result = self.data_agent_management.add_datasource("foo")
            self.assertIsInstance(result, type(ds))
            self.assertEqual(result._id, "id1")

    def test_add_datasource_new(self):
        # Setup mocks for adding a new datasource
        self.mock_get_notebook_workspace_id.return_value = "wsid"
        self.mock_resolve_workspace_id.return_value = "wsid"
        self.mock_list_items.return_value = pd.DataFrame({
            "Display Name": ["foo"],
            "Id": ["id1"],
            "Type": ["lakehouse"]
        })
        self.mock_get_artifact_by_id_or_name.return_value = ("foo", UUID("12345678-1234-5678-1234-567812345678"))
        self.mock_client.get_datasources.return_value = []
        self.mock_client.get_schema.return_value = {"schema": {"id": "id1"}}
        # Patch add_datasource to return a dict with 'id' as a real string, not a MagicMock
        self.mock_client.add_datasource.return_value = {"id": "id1"}
        result = self.data_agent_management.add_datasource("foo")
        self.assertIsInstance(result, Datasource)
        self.assertEqual(result._id, "id1")

    def test_add_datasource_unsupported_type(self):
        self.mock_get_notebook_workspace_id.return_value = "wsid"
        self.mock_resolve_workspace_id.return_value = "wsid"
        self.mock_list_items.return_value = pd.DataFrame({
            "Display Name": ["foo"],
            "Id": ["id1"],
            "Type": ["unsupportedtype"]
        })
        # Patch get_artifact_by_id_or_name to return a tuple so the code reaches the type check
        self.mock_get_artifact_by_id_or_name.return_value = ("foo", UUID("12345678-1234-5678-1234-567812345678"))
        with self.assertRaises(ValueError) as ctx:
            self.data_agent_management.add_datasource("foo")
        self.assertIn("Unsupported artifact type", str(ctx.exception))

    def test_add_datasource_multiple_artifacts(self):
        self.mock_get_notebook_workspace_id.return_value = "wsid"
        self.mock_resolve_workspace_id.return_value = "wsid"
        self.mock_list_items.return_value = pd.DataFrame({
            "Display Name": ["foo", "foo"],
            "Id": ["id1", "id2"],
            "Type": ["lakehouse", "lakehouse"]
        })
        with self.assertRaises(ValueError) as ctx:
            self.data_agent_management.add_datasource("foo")
        self.assertIn("Found multiple artifacts with name", str(ctx.exception))

    def test_add_datasource_not_found(self):
        self.mock_get_notebook_workspace_id.return_value = "wsid"
        self.mock_resolve_workspace_id.return_value = "wsid"
        self.mock_list_items.return_value = pd.DataFrame({
            "Display Name": [],
            "Id": [],
            "Type": []
        })
        with self.assertRaises(ValueError) as ctx:
            self.data_agent_management.add_datasource("foo")
        self.assertIn("Could not find datasource artifact", str(ctx.exception))
