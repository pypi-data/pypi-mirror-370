import os

import pytest

from easymaker.api.api_sender import ApiSender
from easymaker.common import exceptions
from easymaker.storage import objectstorage


def test_parse_obs_uri():
    obs_full_url, obs_host, container_url, tenant_id, container_name, object_prefix = objectstorage.parse_obs_uri("obs://kr1-api-object-storage.nhncloudservice.com/v1/AUTH_b5adb9b2ecda4c5aa1a6e93d1a40aacc/training_data/image/cat.zip")
    assert obs_full_url == "https://kr1-api-object-storage.nhncloudservice.com/v1/AUTH_b5adb9b2ecda4c5aa1a6e93d1a40aacc/training_data/image/cat.zip"
    assert obs_host == "kr1-api-object-storage.nhncloudservice.com"
    assert container_url == "https://kr1-api-object-storage.nhncloudservice.com/v1/AUTH_b5adb9b2ecda4c5aa1a6e93d1a40aacc/training_data"
    assert tenant_id == "b5adb9b2ecda4c5aa1a6e93d1a40aacc"
    assert container_name == "training_data"
    assert object_prefix == "image/cat.zip"

    # OBS API를 사용하면 오브젝트 경로에 빈 폴더와 특수문자(유니코드)도 사용 가능
    *_, object_prefix = objectstorage.parse_obs_uri("obs://kr1-api-object-storage.nhncloudservice.com/v1/AUTH_b5adb9b2ecda4c5aa1a6e93d1a40aacc/training_data//image//cat.zip")
    assert object_prefix == "/image//cat.zip"
    *_, object_prefix = objectstorage.parse_obs_uri("obs://kr1-api-object-storage.nhncloudservice.com/v1/AUTH_b5adb9b2ecda4c5aa1a6e93d1a40aacc/training_data/가나 다!@#$.'\"`<>;\♥/cat.zip")
    assert object_prefix == "가나 다!@#$.'\"`<>;\♥/cat.zip"

    with pytest.raises(exceptions.EasyMakerError):
        assert objectstorage.parse_obs_uri("obs://kr1-api-object-storage.nhncloudservice.com/v1/AUTH_b5adb9b2ecda4c5aa1a6e93d1a40aacc/training_data")
    with pytest.raises(exceptions.EasyMakerError):
        assert objectstorage.parse_obs_uri("obs://kr1-api-object-storage.nhncloudservice.com//v1/AUTH_b5adb9b2ecda4c5aa1a6e93d1a40aacc/training_data/image/cat.zip")
    with pytest.raises(exceptions.EasyMakerError):
        assert objectstorage.parse_obs_uri("obs://kr1-api-object-storage.nhncloudservice.com/v1/AUTH_b5adb9b2ecda4c5aa1a6e93d1a40aacc//training_data/image/cat.zip")

    with pytest.raises(exceptions.EasyMakerError):
        assert objectstorage.parse_obs_uri("obs:/kr1-api-object-storage.nhncloudservice.com/v1/AUTH_b5adb9b2ecda4c5aa1a6e93d1a40aacc/training_data/image/cat.zip")
    with pytest.raises(exceptions.EasyMakerError):
        assert objectstorage.parse_obs_uri("https://kr1-api-object-storage.nhncloudservice.com/v1/AUTH_b5adb9b2ecda4c5aa1a6e93d1a40aacc/training_data/image/cat.zip")

    with pytest.raises(exceptions.EasyMakerError):
        assert objectstorage.parse_obs_uri("obs://kr1-api-object-storage.nhncloudservice.com/v1/AUTHb5adb9b2ecda4c5aa1a6e93d1a40aacc/training_data/image/cat.zip")
    with pytest.raises(exceptions.EasyMakerError):
        assert objectstorage.parse_obs_uri("obs://kr1-api-object-storage.nhncloudservice.com/AUTH_b5adb9b2ecda4c5aa1a6e93d1a40aacc/training_data/image/cat.zip")


def test_objectstorage_download_by_token():
    os.environ["EM_REGION"] = "kr1"
    os.environ["EM_APPKEY"] = "yAUSAfY0ZfUz0nAx"
    # 테스트시 API 서버에서 토큰 생성하여 수정 필요 (TokenUtilTest::createSdkTestToken_Test)
    os.environ["EM_TOKEN"] = "ZLnTI89S996kWDPrlIjw5RbDaOtYP14EBetz9XlxO8u1GSwxpa9z1U2baDs1QWYo7cMWpr37z7k3UmoG4rnO6A=="
    os.environ["EM_GROUP_ID"] = "test-training-id"
    objectstorage.download("obs://kr1-api-object-storage.nhncloudservice.com/v1/AUTH_59ed815ebc6b4391802d4848329cebe7/SDK/sample/dataset_test/x_test.csv", "./")
    assert os.path.exists("./x_test.csv")
    os.remove("./x_test.csv")

    objectstorage.download("obs://kr1-api-object-storage.nhncloudservice.com/v1/AUTH_034405a26323482285b79bbe73fd523c/easymaker/datasets/iris/raw/Iris.csv", "./")
    assert os.path.exists("./Iris.csv")
    os.remove("./Iris.csv")


def test_objectstorage_download_by_password():
    objectstorage.download("obs://kr1-api-object-storage.nhncloudservice.com/v1/AUTH_59ed815ebc6b4391802d4848329cebe7/SDK/sample/dataset_test/x_test.csv", "./", easymaker_region="kr1", username="kmh@nhn.com", password="easymaker!@#123")
    assert os.path.exists("./x_test.csv")
    os.remove("./x_test.csv")


def test_objectstorage_upload_by_token():
    os.environ["EM_REGION"] = "kr1"
    os.environ["EM_APPKEY"] = "yAUSAfY0ZfUz0nAx"
    # 테스트시 API 서버에서 토큰 생성하여 수정 필요 (TokenUtilTest::createSdkTestToken_Test)
    os.environ["EM_TOKEN"] = "ZLnTI89S996kWDPrlIjw5RbDaOtYP14EBetz9XlxO8u1GSwxpa9z1U2baDs1QWYo7cMWpr37z7k3UmoG4rnO6A=="
    os.environ["EM_GROUP_ID"] = "test-training-id"

    objectstorage.upload("obs://kr1-api-object-storage.nhncloudservice.com/v1/AUTH_59ed815ebc6b4391802d4848329cebe7/SDK/upload_test", "./up")


def test_api_sender_validation_region():
    # then: valid region code
    os.environ["EM_REGION"] = "kr1"
    assert ApiSender(os.environ["EM_REGION"], os.environ.get("EM_APPKEY"), os.environ.get("EM_ACCESS_TOKEN"))

    # then: invalid region code
    with pytest.raises(exceptions.EasyMakerRegionError):
        os.environ["EM_REGION"] = "invalid_region"
        assert ApiSender(os.environ["EM_REGION"], os.environ.get("EM_APPKEY"), os.environ.get("EM_ACCESS_TOKEN"))
