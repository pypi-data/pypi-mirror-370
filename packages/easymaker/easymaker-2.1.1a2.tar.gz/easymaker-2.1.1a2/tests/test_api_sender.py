import os
from unittest.mock import MagicMock, patch

import pytest
import responses
from requests.exceptions import RetryError

from easymaker.api.api_sender import ApiSender

TEST_REGION = "test_region"
TEST_APPKEY = "test_appkey"
TEST_ACCESS_TOKEN = "test_access_token"


@patch("easymaker.api.api_sender.Session")
def test_get_experiment_list_no_params(mock_session):
    os.environ["EM_PROFILE"] = "local"

    mock_response = MagicMock()
    mock_response.json.return_value = {
        "header": {
            "isSuccessful": True,
            "resultCode": 0,
            "resultMessage": "SUCCESS",
        },
        "paging": {
            "totalCount": 2,
            "page": 1,
            "limit": 50,
        },
        "experimentList": [
            {
                "experimentId": "1",
                "experimentName": "Experiment 1",
            },
            {
                "experimentId": "2",
                "experimentName": "Experiment 2",
            },
        ],
    }
    mock_session_instance = mock_session.return_value
    mock_session_instance.get.return_value = mock_response

    api_sender = ApiSender(region=TEST_REGION, appkey=TEST_APPKEY, access_token=TEST_ACCESS_TOKEN)
    result = api_sender.get_experiment_list()

    assert result == [{"experimentId": "1", "experimentName": "Experiment 1"}, {"experimentId": "2", "experimentName": "Experiment 2"}]
    mock_session_instance.get.assert_called_once_with(f"http://127.0.0.1:10090/v1.0/appkeys/{TEST_APPKEY}/experiments", params={})


@patch("easymaker.api.api_sender.Session")
def test_get_experiment_list_with_params(mock_session):
    os.environ["EM_PROFILE"] = "local"

    mock_response = MagicMock()
    mock_response.json.return_value = {
        "header": {
            "isSuccessful": True,
            "resultCode": 0,
            "resultMessage": "SUCCESS",
        },
        "paging": {
            "totalCount": 2,
            "page": 1,
            "limit": 50,
        },
        "experimentList": [
            {
                "experimentId": "3",
                "experimentName": "Experiment 3",
            },
            {
                "experimentId": "4",
                "experimentName": "Experiment 4",
            },
        ],
    }
    mock_session_instance = mock_session.return_value
    mock_session_instance.get.return_value = mock_response

    api_sender = ApiSender(region=TEST_REGION, appkey=TEST_APPKEY, access_token=TEST_ACCESS_TOKEN)
    result = api_sender.get_experiment_list(name_list=["Experiment 3", "Experiment 4"])

    assert result == [{"experimentId": "3", "experimentName": "Experiment 3"}, {"experimentId": "4", "experimentName": "Experiment 4"}]
    mock_session_instance.get.assert_called_once_with(f"http://127.0.0.1:10090/v1.0/appkeys/{TEST_APPKEY}/experiments", params={"experimentNameList": "Experiment 3,Experiment 4"})


@responses.activate
def test_retry_logic():
    os.environ["EM_PROFILE"] = "test"

    responses.add(
        responses.GET,
        f"https://{TEST_REGION}-easymaker-test.api.nhncloudservice.com/v1.0/appkeys/{TEST_APPKEY}/experiments",
        status=503,
    )

    api_sender = ApiSender(region=TEST_REGION, appkey=TEST_APPKEY, access_token=TEST_ACCESS_TOKEN)

    with pytest.raises(RetryError):
        api_sender.get_experiment_list()

    assert len(responses.calls) == 4
