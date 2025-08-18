import unittest
from unittest.mock import patch, MagicMock
from fabric.dataagent.client._fabric_openai import FabricOpenAI


class TestFabricOpenAI(unittest.TestCase):

    @patch('fabric.dataagent.client._fabric_openai.get_fabric_env_config')
    @patch('fabric.dataagent.client._fabric_openai.get_artifact_by_id_or_name')
    @patch('fabric.dataagent.client._fabric_openai.get_workspace_capacity_id')
    @patch('fabric.dataagent.client._fabric_openai.resolve_workspace_name_and_id')
    def setUp(
        self,
        mock_resolve_workspace,
        mock_get_capacity,
        mock_get_artifact,
        mock_get_config,
    ):

        self.mock_resolve_workspace = mock_resolve_workspace
        self.mock_get_capacity = mock_get_capacity
        self.mock_get_artifact = mock_get_artifact
        self.mock_get_config = mock_get_config

        self.artifact_name = "artifact_name"
        self.artifact_id = "artifact_id"
        self.workspace_name = "workspace_name"
        self.workspace_id = "workspace_id"
        self.capacity_id = "capacity_id"
        self.wl_host = "https://fabric_host"

        self.mock_resolve_workspace.return_value = (
            self.workspace_name,
            self.workspace_id,
        )
        self.mock_get_capacity.return_value = self.capacity_id
        self.mock_get_artifact.return_value = (self.artifact_name, self.artifact_id)
        self.mock_get_config.return_value = MagicMock(
            fabric_env_config=MagicMock(wl_host=self.wl_host)
        )

        self.fabric_openai = FabricOpenAI(artifact_name=self.artifact_name)

    def test_initialization(self):
        # Assert the instance variables
        self.assertEqual(self.fabric_openai.workspace_name, self.workspace_name)
        self.assertEqual(self.fabric_openai.workspace_id, self.workspace_id)
        self.assertEqual(self.fabric_openai.capacity_id, self.capacity_id)
        self.assertEqual(self.fabric_openai.artifact_name, self.artifact_name)
        self.assertEqual(self.fabric_openai.artifact_id, self.artifact_id)

        # Assert the default values
        self.assertEqual(self.fabric_openai.api_version, "2024-05-01-preview")
        self.assertEqual(self.fabric_openai.assistant_scenario, "aiskill")
        self.assertEqual(self.fabric_openai.ai_skill_stage, "sandbox")
        self.assertTrue(self.fabric_openai._moniker_id)

        # Assert the base_url
        # TODO: Change once base_url is modified:
        expected_base_url = f"{self.wl_host}/webapi/capacities/{self.capacity_id}/workloads/ML/AISkill/Automatic/v1/workspaces/{self.workspace_id}/artifacts/{self.artifact_id}/aiassistant/openai/"
        self.assertEqual(self.fabric_openai.base_url, expected_base_url)

    @patch('fabric.dataagent.client._fabric_openai.SynapseTokenProvider')
    def test_prepare_options(self, mock_token_provider):

        mock_token_provider.return_value = MagicMock(return_value="mock_token")
        options = MagicMock(headers={"Custom-Header": "value"})

        prepared_options = self.fabric_openai._prepare_options(options)

        # Assert the headers
        self.assertEqual(prepared_options.headers["Authorization"], "Bearer mock_token")
        self.assertEqual(prepared_options.headers["Accept"], "application/json")
        self.assertIn("ActivityId", prepared_options.headers)
        self.assertEqual(
            prepared_options.headers["x-ms-workload-resource-moniker"],
            self.fabric_openai._moniker_id,
        )
        self.assertEqual(
            prepared_options.headers["x-ms-ai-assistant-scenario"], "aiskill"
        )
        self.assertEqual(prepared_options.headers["x-ms-ai-aiskill-stage"], "sandbox")

    def test_make_status_error(self):

        response = MagicMock(
            status_code=500,
            headers={
                "x-ms-root-activity-id": "raid_value",
                "ActivityId": "correlation_id_value",
            },
        )

        error = self.fabric_openai._make_status_error(
            "Error message", body={}, response=response
        )

        # Assert the error message
        self.assertIn("RAID: raid_value", str(error))
        self.assertIn("Correlation ID: correlation_id_value", str(error))

    @patch('sempy.fabric.FabricRestClient')
    def test_get_or_create_thread(self, MockFabricRestClient):
        self.mock_client = MockFabricRestClient.return_value
        self.mock_client.get.return_value = MagicMock(status_code=200)
        self.fabric_openai.beta.threads.retrieve = MagicMock(return_value="123")

        self.fabric_openai.get_or_create_thread("new_thread")
        self.mock_client.get.assert_called_once()

    @patch('sempy.fabric.FabricRestClient')
    def test_delete_thread(self, MockFabricRestClient):
        self.mock_client = MockFabricRestClient.return_value
        self.mock_client.delete.return_value = MagicMock(status_code=200)
        self.fabric_openai.delete_thread("new_thread")
        self.mock_client.delete.assert_called_once()
