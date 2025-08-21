import unittest
from unittest.mock import patch

from easymaker.model_evaluation.model_evaluation import ModelEvaluation


class TestModelEvaluation(unittest.TestCase):
    @patch("easymaker.easymaker_config.api_sender")
    def test_create_model_evaluation(self, mock_api_sender):
        mock_response = {
            "modelEvaluationId": "test_id",
            "appKey": "test_key",
            "modelEvaluationName": "test_name",
            "modelEvaluationTypeCode": "test_code",
            "inputDataUri": "test_input_data_uri",
            "inputDataTypeCode": "test_input_data_type_code",
            "modelEvaluationStatusCode": "CREATE_REQUESTED",
            "description": "test_description",
            "createdDatetime": "2025-01-01T00:00:00Z",
        }
        mock_api_sender.create_model_evaluation.return_value = mock_response

        instance_type_list_mock_response = [{"name": "m2.c4m8", "id": "test_id"}]
        mock_api_sender.get_instance_type_list.return_value = instance_type_list_mock_response

        model_evaluation = ModelEvaluation()
        response = model_evaluation.create(
            model_evaluation_name="test_name",
            input_data_type_code="test_input_data_type_code",
            input_data_uri="test_input_data_uri",
            description="test_description",
            model_id="test_model_id",
            objective_code="REGRESSION",
            instance_type_name="m2.c4m8",
            target_field_name="targetFieldName",
            boot_storage_size=50,
            data_storage_size=300,
            timeout_hours=1,
            batch_inference_instance_type_name="m2.c4m8",
            batch_inference_instance_count=1,
            batch_inference_pod_count=1,
            batch_inference_output_upload_uri="obs://kr1-api-object-storage.nhncloudservice.com/v1/AUTH_37afa82e33d64247ad031af52879e5df/em-test/model",
            batch_inference_max_batch_size=32,
            batch_inference_inference_timeout_seconds=120,
            wait=False,
        )

        self.assertEqual(response.model_evaluation_id, "test_id")
        self.assertEqual(response.app_key, "test_key")
        self.assertEqual(response.model_evaluation_name, "test_name")
        self.assertEqual(response.model_evaluation_status_code, "CREATE_REQUESTED")
        self.assertEqual(response.input_data_uri, "test_input_data_uri")
        self.assertEqual(response.input_data_type_code, "test_input_data_type_code")
        self.assertEqual(response.description, "test_description")
        mock_api_sender.create_model_evaluation.assert_called_once()

    @patch("easymaker.easymaker_config.api_sender")
    def test_delete(self, mock_api_sender):
        mock_response = {"modelEvaluationId": "test_model_evaluation_id", "modelEvaluationStatusCode": "ACTIVE"}
        mock_api_sender.get_model_evaluation_by_id.return_value = mock_response
        mock_api_sender.delete_model_evaluation_by_id.return_value = {}
        model_evaluation_id = "test_model_evaluation_id"
        model_evaluation = ModelEvaluation(model_evaluation_id=model_evaluation_id)
        model_evaluation.delete()

        self.assertIsNone(model_evaluation.model_evaluation_id)
        mock_api_sender.get_model_evaluation_by_id.assert_called_once_with(model_evaluation_id)
        mock_api_sender.delete_model_evaluation_by_id.assert_called_once_with(model_evaluation_id)

    @patch("easymaker.easymaker_config.api_sender")
    def test_delete_function(self, mock_api_sender):
        model_evaluation_id = "test_model_evaluation_id"
        ModelEvaluation.delete_by_id(model_evaluation_id)
        mock_api_sender.delete_model_evaluation_by_id.assert_called_once_with(model_evaluation_id)
