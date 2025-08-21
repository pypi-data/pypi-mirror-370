import unittest
from unittest.mock import patch

from easymaker.training.training import Training


class TestTraining(unittest.TestCase):
    @patch("easymaker.easymaker_config.api_sender")
    def test_init(self, mock_api_sender):
        mock_response = {
            "trainingId": "test_id",
            "appKey": "test_key",
            "trainingName": "test_name",
            "instanceCount": 1,
            "nprocPerNode": 1,
            "algorithm": {},
            "sourceDirUri": "test_uri",
            "entryPoint": "test_entry",
            "modelUploadUri": "test_uri",
            "checkPointInputUri": "test_uri",
            "checkPointUploadUri": "test_uri",
            "logAndCrashAppKey": "test_key",
            "timeoutMinutes": 1,
            "elapsedTimeSeconds": 1,
            "tensorboardAccessUri": "test_uri",
            "tensorboardAccessPath": "test_path",
            "datasetList": [],
            "bootStorage": {},
            "dataStorageList": [],
            "flavor": {},
            "image": {},
            "modelList": [],
            "hyperparameterList": [],
            "experiment": {},
            "description": "test description",
            "trainingStatusCode": "CREATED",
            "createdDatetime": "2025-01-01T00:00:00Z",
        }
        mock_api_sender.get_training_by_id.return_value = mock_response

        training = Training(training_id="test_id")
        self.assertEqual(training.training_id, "test_id")
        self.assertEqual(training.app_key, "test_key")
        self.assertEqual(training.training_name, "test_name")
        self.assertEqual(training.instance_count, 1)
        self.assertEqual(training.nproc_per_node, 1)
        self.assertEqual(training.algorithm, {})
        self.assertEqual(training.source_dir_uri, "test_uri")
        self.assertEqual(training.entry_point, "test_entry")
        self.assertEqual(training.model_upload_uri, "test_uri")
        self.assertEqual(training.check_point_input_uri, "test_uri")
        self.assertEqual(training.check_point_upload_uri, "test_uri")
        self.assertEqual(training.log_and_crash_app_key, "test_key")
        self.assertEqual(training.timeout_minutes, 1)
        self.assertEqual(training.elapsed_time_seconds, 1)
        self.assertEqual(training.tensorboard_access_uri, "test_uri")
        self.assertEqual(training.tensorboard_access_path, "test_path")
        self.assertEqual(training.dataset_list, [])
        self.assertEqual(training.boot_storage, {})
        self.assertEqual(training.data_storage_list, [])
        self.assertEqual(training.flavor, {})
        self.assertEqual(training.image, {})
        self.assertEqual(training.model_list, [])
        self.assertEqual(training.hyperparameter_list, [])
        self.assertEqual(training.experiment, {})
        self.assertEqual(training.description, "test description")
        self.assertEqual(training.training_status_code, "CREATED")
        self.assertEqual(training.created_datetime, "2025-01-01T00:00:00Z")

        mock_api_sender.get_training_by_id.assert_called_once_with("test_id")
