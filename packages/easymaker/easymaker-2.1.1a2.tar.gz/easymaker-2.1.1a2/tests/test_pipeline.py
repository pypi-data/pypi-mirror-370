import unittest
from unittest.mock import patch

from easymaker.pipeline.pipeline import Pipeline


class TestPipeline(unittest.TestCase):
    @patch("easymaker.easymaker_config.api_sender")
    def test_init(self, mock_api_sender):
        mock_response = {
            "pipelineId": "test_id",
            "appKey": "test_key",
            "pipelineName": "test_name",
            "pipelineParameterSpecList": [],
            "description": "test description",
            "pipelineStatusCode": "ACTIVE",
            "createdDatetime": "2025-01-01T00:00:00Z",
        }
        mock_api_sender.get_pipeline_by_id.return_value = mock_response

        pipeline = Pipeline("test_id")
        self.assertEqual(pipeline.pipeline_id, "test_id")
        self.assertEqual(pipeline.app_key, "test_key")
        self.assertEqual(pipeline.pipeline_name, "test_name")
        self.assertEqual(pipeline.pipeline_parameter_spec_list, [])
        self.assertEqual(pipeline.description, "test description")
        self.assertEqual(pipeline.pipeline_status_code, "ACTIVE")
        self.assertEqual(pipeline.created_datetime, "2025-01-01T00:00:00Z")

    @patch("easymaker.easymaker_config.api_sender")
    def test_upload_pipeline(self, mock_api_sender):
        mock_response = {
            "pipelineId": "test_id",
            "appKey": "test_key",
            "pipelineName": "test_name",
            "pipelineParameterSpecList": [],
            "description": "test description",
            "pipelineStatusCode": "CREATE_REQUESTED",
            "createdDatetime": "2025-01-01T00:00:00Z",
        }
        mock_api_sender.upload_pipeline.return_value = mock_response

        with patch("builtins.open", unittest.mock.mock_open(read_data=b"tesasdfeawft")) as mock_file:
            pipeline = Pipeline().upload(
                "test_name",
                "test_path",
                "test_description",
                ["tag1", "tag2"],
                wait=False,
            )
            self.assertEqual(pipeline.pipeline_id, "test_id")
            self.assertEqual(pipeline.app_key, "test_key")
            self.assertEqual(pipeline.pipeline_name, "test_name")
            self.assertEqual(pipeline.pipeline_parameter_spec_list, [])
            self.assertEqual(pipeline.description, "test description")
            self.assertEqual(pipeline.pipeline_status_code, "CREATE_REQUESTED")
            self.assertEqual(pipeline.created_datetime, "2025-01-01T00:00:00Z")
            mock_file.assert_called_with("test_path", "rb")

    @patch("easymaker.easymaker_config.api_sender")
    def test_delete_pipeline(self, mock_api_sender):
        mock_response = {"pipelineId": "test_id", "pipelineStatusCode": "ACTIVE"}
        mock_api_sender.get_pipeline_by_id.return_value = mock_response
        mock_api_sender.delete_pipeline_by_id.return_value = {}

        pipeline = Pipeline("test_id")
        pipeline.delete()
        self.assertIsNone(pipeline.pipeline_id)
        mock_api_sender.delete_pipeline_by_id.assert_called_once_with("test_id")
