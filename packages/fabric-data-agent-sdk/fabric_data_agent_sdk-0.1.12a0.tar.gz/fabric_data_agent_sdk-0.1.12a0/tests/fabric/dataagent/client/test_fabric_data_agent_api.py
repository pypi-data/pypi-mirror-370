import unittest
from unittest.mock import MagicMock, patch
from uuid import UUID
from fabric.dataagent.client._fabric_data_agent_api import FabricDataAgentAPI
from fabric.dataagent.client._tagged_value import TaggedValue
from sempy.fabric.exceptions import FabricHTTPException


class TestFabricDataAgentAPI(unittest.TestCase):

    @patch('fabric.dataagent.client._fabric_data_agent_api.get_artifact_by_id_or_name')
    @patch('fabric.dataagent.client._fabric_data_agent_api.get_workspace_capacity_id')
    @patch(
        'fabric.dataagent.client._fabric_data_agent_api.resolve_workspace_name_and_id'
    )
    @patch('synapse.ml.fabric.service_discovery.get_fabric_env_config')
    @patch('sempy.fabric.FabricRestClient')
    def setUp(
        self,
        MockFabricRestClient,
        MockGetFabricEnvConfig,
        MockResolveWorkspaceNameAndID,
        MockGetWorkspaceCapacityID,
        MockGetArtifactByIDOrName,
    ):
        self.mock_client = MockFabricRestClient.return_value
        self.mock_get_fabric_env_config = MockGetFabricEnvConfig
        self.mock_resolve_workspace_name_and_id = MockResolveWorkspaceNameAndID
        self.mock_get_workspace_capacity_id = MockGetWorkspaceCapacityID
        self.mock_get_artifact_by_id_or_name = MockGetArtifactByIDOrName

        self.mock_resolve_workspace_name_and_id.return_value = (
            "workspace_name",
            UUID("12345678123456781234567812345678"),
        )
        self.mock_get_workspace_capacity_id.return_value = "capacity_id"
        self.mock_get_artifact_by_id_or_name.return_value = (
            "data_agent_name",
            UUID("12345678123456781234567812345678"),
        )
        self.mock_get_fabric_env_config.return_value.fabric_env_config.wl_host = (
            "http://fabric_host"
        )

        self.data_agent_api = FabricDataAgentAPI(
            data_agent="test_data_agent", workspace="test_workspace"
        )

    def test_get_configuration(self):
        self.mock_client.get.return_value = MagicMock(
            status_code=200, json=lambda: {}, headers={"ETag": "etag"}
        )
        config = self.data_agent_api.get_configuration()
        self.assertIsInstance(config, TaggedValue)
        self.assertEqual(config.etag, "etag")

    def test_set_configuration(self):
        self.mock_client.patch.return_value = MagicMock(
            status_code=200, headers={"ETag": "new_etag"}
        )
        value = TaggedValue({"key": "value"}, "etag")
        updated_config = self.data_agent_api.set_configuration(value)
        self.assertIsInstance(updated_config, TaggedValue)
        self.assertEqual(updated_config.etag, "new_etag")

    def test_set_configuration_removes_dataSources(self):
        self.mock_client.patch.return_value = MagicMock(
            status_code=200, headers={"ETag": "new_etag"}
        )
        value = TaggedValue({"key": "value", "dataSources": [1, 2, 3]}, "etag")
        updated_config = self.data_agent_api.set_configuration(value)
        self.assertIsInstance(updated_config, TaggedValue)
        args, kwargs = self.mock_client.patch.call_args
        self.assertNotIn("dataSources", kwargs["json"])

    def test_set_configuration_raises_on_error(self):
        self.mock_client.patch.return_value = MagicMock(status_code=500)
        value = TaggedValue({"key": "value"}, "etag")
        with self.assertRaises(FabricHTTPException):
            self.data_agent_api.set_configuration(value)

    def test_get_datasources_empty(self):
        self.mock_client.get.side_effect = [
            MagicMock(
                status_code=200,
                json=lambda: {},
            )
        ]
        datasources = list(self.data_agent_api.get_datasources())
        self.assertEqual(len(datasources), 0)

    def test_get_datasources(self):
        self.mock_client.get.side_effect = [
            MagicMock(
                status_code=200,
                json=lambda: {"dataSources": [{"id": "ds1"}, {"id": "ds2"}]},
            ),
            MagicMock(
                status_code=200, json=lambda: {"id": "ds1"}, headers={"ETag": "etag"}
            ),
            MagicMock(
                status_code=200, json=lambda: {"id": "ds2"}, headers={"ETag": "etag"}
            ),
        ]
        datasources = list(self.data_agent_api.get_datasources())
        self.assertEqual(len(datasources), 2)
        self.assertEqual(datasources[0].value["id"], "ds1")

    def test_get_datasource(self):
        self.mock_client.get.return_value = MagicMock(
            status_code=200, json=lambda: {}, headers={"ETag": "etag"}
        )
        datasource = self.data_agent_api.get_datasource("ds1")
        self.assertIsInstance(datasource, TaggedValue)
        self.assertEqual(datasource.etag, "etag")

    def test_remove_datasource(self):
        self.mock_client.delete.return_value = MagicMock(status_code=200)
        self.data_agent_api.remove_datasource("ds1", "etag")
        self.mock_client.delete.assert_called_once()

    def test_remove_datasource_raises_on_error(self):
        self.mock_client.delete.return_value = MagicMock(status_code=500)
        with self.assertRaises(FabricHTTPException):
            self.data_agent_api.remove_datasource("ds1", "etag")

    def test_set_datasource(self):
        self.mock_client.put.return_value = MagicMock(
            status_code=200, headers={"ETag": "new_etag"}
        )
        value = TaggedValue({"id": "ds1"}, "etag")
        updated_datasource = self.data_agent_api.set_datasource(value)
        self.assertIsInstance(updated_datasource, TaggedValue)
        self.assertEqual(updated_datasource.etag, "new_etag")

    def test_set_datasource_raises_on_error(self):
        self.mock_client.put.return_value = MagicMock(status_code=500)
        value = TaggedValue({"id": "ds1"}, "etag")
        with self.assertRaises(FabricHTTPException):
            self.data_agent_api.set_datasource(value)

    def test_add_datasource(self):
        self.mock_client.post.return_value = MagicMock(
            status_code=200, json=lambda: {"id": "new_ds"}
        )
        new_datasource = self.data_agent_api.add_datasource({"key": "value"})
        self.assertEqual(new_datasource["id"], "new_ds")

    def test_add_datasource_raises_on_error(self):
        self.mock_client.post.return_value = MagicMock(status_code=500)
        with self.assertRaises(FabricHTTPException):
            self.data_agent_api.add_datasource({"key": "value"})

    def test_get_publishing_info(self):
        self.mock_client.get.return_value = MagicMock(
            status_code=200, json=lambda: {}, headers={"ETag": "etag"}
        )
        publishing_info = self.data_agent_api.get_publishing_info()
        self.assertIsInstance(publishing_info, TaggedValue)
        self.assertEqual(publishing_info.etag, "etag")

    def test_put_publish_info(self):
        self.mock_client.put.return_value = MagicMock(
            status_code=200, json=lambda: {}, headers={"ETag": "new_etag"}
        )
        value = TaggedValue({"description": "value"}, "etag")
        updated_publishing_info = self.data_agent_api.put_publish_info(value)
        self.assertIsInstance(updated_publishing_info, TaggedValue)
        self.assertEqual(updated_publishing_info.etag, "new_etag")

    def test_publish(self):
        self.mock_client.put.return_value = MagicMock(status_code=200)
        value = TaggedValue({}, "etag")
        self.data_agent_api.publish(value)
        self.mock_client.put.assert_called_once()
    
    def test_publish_with_description_existing_publish(self):
        self.mock_client.get.return_value = MagicMock(
            status_code=200, 
            json=lambda: {"description": "old description"}, 
            headers={"ETag": "pub_etag"}
        )
        self.mock_client.put.return_value = MagicMock(
            status_code=200, 
            json=lambda: {"description": "new description"}, 
            headers={"ETag": "new_etag"}
        )
        
        tagged_value = TaggedValue({}, "etag")
        self.data_agent_api.publish(tagged_value, "new description")

        # Verify both publishing info update and deploy were called
        self.assertEqual(self.mock_client.put.call_count, 2)  # publish info + deploy
        self.assertEqual(self.mock_client.get.call_count, 1)  # get publishing info

    def test_publish_with_description_new_publish(self):
        
        # Mock 404 for get_publishing_info (doesn't exist)
        mock_404_response = MagicMock()
        mock_404_response.status_code = 404
        self.mock_client.get.side_effect = FabricHTTPException(mock_404_response)
        
        # Mock successful put operations
        self.mock_client.put.return_value = MagicMock(
            status_code=200, 
            json=lambda: {"description": "new description"}, 
            headers={"ETag": "new_etag"}
        )
        
        tagged_value = TaggedValue({}, "etag")
        self.data_agent_api.publish(tagged_value, "new description")
        
        # Verify both publishing info creation and deploy were called
        self.assertEqual(self.mock_client.put.call_count, 2)  # publish info + deploy
        self.assertEqual(self.mock_client.get.call_count, 1)  # get publishing info

    def test_publish_raises_on_error(self):
        self.mock_client.put.return_value = MagicMock(status_code=500)
        value = TaggedValue({}, "etag")
        with self.assertRaises(FabricHTTPException):
            self.data_agent_api.publish(value)

    def test_get_schema(self):
        self.mock_client.get.return_value = MagicMock(
            status_code=200, json=lambda: {"schema": {}}
        )
        schema = self.data_agent_api.get_schema("workspace_id", "datasource_id", "type")
        self.assertEqual(schema, {"schema": {}})

    def test_get_schema_raises_on_error(self):
        self.mock_client.get.return_value = MagicMock(status_code=500)
        with self.assertRaises(FabricHTTPException):
            self.data_agent_api.get_schema("workspace_id", "datasource_id", "type")

    def test_get_datasource_fewshots(self):
        self.mock_client.get.return_value = MagicMock(
            status_code=200, json=lambda: {}, headers={"ETag": "etag"}
        )
        fewshots = self.data_agent_api.get_datasource_fewshots("ds1")
        self.assertIsInstance(fewshots, TaggedValue)
        self.assertEqual(fewshots.etag, "etag")

    def test_set_datasource_fewshots(self):
        self.mock_client.post.return_value = MagicMock(status_code=200)
        value = TaggedValue({"fewShots": []}, "etag")
        self.data_agent_api.set_datasource_fewshots("ds1", value)
        self.mock_client.post.assert_called_once()

    def test_set_datasource_fewshots_raises_on_error(self):
        self.mock_client.post.return_value = MagicMock(status_code=500)
        value = TaggedValue({"fewShots": []}, "etag")
        with self.assertRaises(FabricHTTPException):
            self.data_agent_api.set_datasource_fewshots("ds1", value)
