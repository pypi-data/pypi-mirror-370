import unittest
from unittest.mock import patch

from easymaker.pipeline.pipeline_run import PipelineRun


class TestPipelineRun(unittest.TestCase):
    @patch("easymaker.easymaker_config.api_sender")
    def test_init(self, mock_api_sender):
        mock_response = {
            "pipelineRunId": "test_id",
            "appKey": "test_key",
            "pipelineRunName": "test_name",
            "description": "test description",
            "pipelineRunStatusCode": "RUNNING",
            "createdDatetime": "2025-01-01T00:00:00Z",
        }
        mock_api_sender.get_pipeline_run_by_id.return_value = mock_response

        pipeline_run = PipelineRun("test_id")
        self.assertEqual(pipeline_run.pipeline_run_id, "test_id")
        self.assertEqual(pipeline_run.app_key, "test_key")
        self.assertEqual(pipeline_run.pipeline_run_name, "test_name")
        self.assertEqual(pipeline_run.description, "test description")
        self.assertEqual(pipeline_run.pipeline_run_status_code, "RUNNING")
        self.assertEqual(pipeline_run.created_datetime, "2025-01-01T00:00:00Z")

    @patch("easymaker.easymaker_config.api_sender")
    def test_create_pipeline_run(self, mock_api_sender):
        instance_type_list_mock_response = [{"name": "m2.c4m8", "id": "test_id"}]
        mock_api_sender.get_instance_type_list.return_value = instance_type_list_mock_response

        mock_response = {
            "pipelineRunId": "test_id",
            "appKey": "test_key",
            "pipelineRunName": "test_name",
            "description": "test description",
            "pipelineRunStatusCode": "RUNNING",
            "createdDatetime": "2025-01-01T00:00:00Z",
        }
        mock_api_sender.create_pipeline_run.return_value = mock_response

        pipeline_run = PipelineRun().create(
            pipeline_run_name="test_name",
            description="test description",
            pipeline_id="test_id",
            experiment_id="test_id",
            parameter_list=[],
            instance_type_name="m2.c4m8",
            instance_count=1,
            boot_storage_size=50,
            wait=False,
        )
        self.assertEqual(pipeline_run.pipeline_run_id, "test_id")
        self.assertEqual(pipeline_run.app_key, "test_key")
        self.assertEqual(pipeline_run.pipeline_run_name, "test_name")
        self.assertEqual(pipeline_run.description, "test description")
        self.assertEqual(pipeline_run.pipeline_run_status_code, "RUNNING")
        self.assertEqual(pipeline_run.created_datetime, "2025-01-01T00:00:00Z")

    @patch("easymaker.easymaker_config.api_sender")
    def test_delete_pipeline_run(self, mock_api_sender):
        mock_response = {"pipelineRunId": "test_id", "pipelineRunStatusCode": "ACTIVE"}
        mock_api_sender.get_pipeline_run_by_id.return_value = mock_response
        mock_api_sender.delete_pipeline_run_by_id.return_value = {}

        pipeline_run = PipelineRun("test_id")
        pipeline_run.delete()
        self.assertIsNone(pipeline_run.pipeline_run_id)
        mock_api_sender.delete_pipeline_run_by_id.assert_called_once_with("test_id")
