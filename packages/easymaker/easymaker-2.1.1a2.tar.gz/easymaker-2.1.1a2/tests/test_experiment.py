import unittest
from unittest.mock import patch

import pytest

from easymaker.api.request_body import ExperimentCreateBody
from easymaker.common import exceptions
from easymaker.experiment.experiment import Experiment


class TestExperiment(unittest.TestCase):
    @patch("easymaker.easymaker_config.api_sender")
    def test_create_experiment_already_exists(self, mock_api_sender):
        mock_response = {
            "experimentId": "existing_experiment_id",
            "experimentName": "Existing Experiment",
            "experimentStatusCode": "ACTIVE",
            "description": "This is a existing experiment",
        }
        mock_api_sender.get_experiment_list.return_value = [{"id": "existing_experiment_id"}]
        mock_api_sender.get_experiment_by_id.return_value = mock_response

        experiment = Experiment()
        response = experiment.create(
            experiment_name="Existing Experiment",
            description="This is an existing experiment",
            wait=False,
        )

        self.assertEqual(response.experiment_id, "existing_experiment_id")
        mock_api_sender.create_experiment.assert_not_called()
        mock_api_sender.get_experiment_list.assert_called_once_with(name_list=["Existing Experiment"], id_list=None)
        mock_api_sender.get_experiment_by_id.assert_called_once_with("existing_experiment_id")

    @patch("easymaker.easymaker_config.api_sender")
    def test_create_experiment_new_experiment(self, mock_api_sender):
        mock_response = {
            "experimentId": "new_experiment_id",
            "experimentName": "New Experiment",
            "experimentStatusCode": "ACTIVE",
            "description": "This is a new experiment",
        }
        mock_api_sender.create_experiment.return_value = mock_response
        mock_api_sender.get_experiment_list.return_value = []

        experiment = Experiment()
        response = experiment.create(
            experiment_name="New Experiment",
            description="This is a new experiment",
            wait=False,
        )

        self.assertEqual(response.experiment_id, "new_experiment_id")
        self.assertEqual(response.experiment_name, "New Experiment")
        mock_api_sender.create_experiment.assert_called_once_with(
            ExperimentCreateBody(
                experiment_name="New Experiment",
                description="This is a new experiment",
            )
        )

    @patch("easymaker.easymaker_config.api_sender")
    def test_create_experiment_missing_name(self, mock_api_sender):
        mock_response = {
            "header": {
                "isSuccessful": False,
                "resultCode": 4000302,
                "resultMessage": "올바르지 않은 실험 이름입니다.",
            }
        }
        mock_api_sender.get_experiment_list.return_value = []
        mock_api_sender.create_experiment.side_effect = exceptions.EasyMakerError(mock_response)

        experiment = Experiment()
        with pytest.raises(exceptions.EasyMakerError):
            experiment.create("", wait=False)
