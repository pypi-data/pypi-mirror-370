import unittest
from unittest.mock import patch

import easymaker
from easymaker.api.request_body import ModelCreateBody
from easymaker.model.model import Model, delete


class TestModel(unittest.TestCase):
    @patch("easymaker.easymaker_config.api_sender")
    def test_create_by_model_upload_uri(self, mock_api_sender):
        mock_response = {
            "modelId": "test_id",
            "appKey": "test_key",
            "modelName": "test_name",
            "modelTypeCode": "test_code",
            "modelUploadUri": "test_uri",
            "modelStatusCode": "CREATE_REQUESTED",
            "description": "test_description",
            "createdDatetime": "2025-01-01T00:00:00Z",
        }
        mock_api_sender.create_model.return_value = mock_response

        model = Model()
        response = model.create_by_model_upload_uri(
            "test_name",
            model_type_code="test_code",
            model_upload_uri="test_uri",
            description="test_description",
            wait=False,
        )

        self.assertEqual(response.model_id, "test_id")
        self.assertEqual(response.app_key, "test_key")
        self.assertEqual(response.model_name, "test_name")
        self.assertEqual(response.model_type_code, "test_code")
        self.assertEqual(response.model_upload_uri, "test_uri")
        self.assertEqual(response.description, "test_description")
        mock_api_sender.create_model.assert_called_once_with(
            ModelCreateBody(
                model_name="test_name",
                model_type_code="test_code",
                model_upload_uri="test_uri",
                description="test_description",
                parameter_list=None,
            )
        )

    @patch("easymaker.easymaker_config.api_sender")
    def test_create_hugging_face_model(self, mock_api_sender):
        model = Model()
        model.create_hugging_face_model(
            "test_model",
            wait=False,
        )
        mock_api_sender.create_model.assert_called_once_with(
            ModelCreateBody(
                model_name="test_model",
                model_type_code=easymaker.HUGGING_FACE,
                parameter_list=None,
                description=None,
            )
        )

    @patch("easymaker.easymaker_config.api_sender")
    def test_delete(self, mock_api_sender):
        model_id = "test_model_id"
        model = Model(model_id=model_id)
        model.delete()
        mock_api_sender.get_model_by_id.assert_called_once_with(model_id)

    @patch("easymaker.easymaker_config.api_sender")
    def test_delete_function(self, mock_api_sender):
        model_id = "test_model_id"
        delete(model_id)
        mock_api_sender.delete_model_by_id.assert_called_once_with(model_id)
