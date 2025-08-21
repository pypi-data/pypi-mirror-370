import base64
from types import SimpleNamespace

import requests

classification_model = SimpleNamespace(
    train=SimpleNamespace(
        source_dir_uri="obs://kr1-api-object-storage.nhncloudservice.com/v1/AUTH_ed79fa143403492fbaf3ce31f0c03314/easymaker-sample/iris-tensorflow",
        entry_point="train.py",
        dataset=SimpleNamespace(
            train="obs://kr1-api-object-storage.nhncloudservice.com/v1/AUTH_ed79fa143403492fbaf3ce31f0c03314/easymaker-sample/iris-dataset/train",
            test="obs://kr1-api-object-storage.nhncloudservice.com/v1/AUTH_ed79fa143403492fbaf3ce31f0c03314/easymaker-sample/iris-dataset/test",
        ),
    ),
    model_uri="obs://kr1-api-object-storage.nhncloudservice.com/v1/AUTH_ed79fa143403492fbaf3ce31f0c03314/easymaker-sample/iris-tensorflow-model",
    model_type="TENSORFLOW",
    batch_inference=SimpleNamespace(
        input_data_uri="obs://kr1-api-object-storage.nhncloudservice.com/v1/AUTH_ed79fa143403492fbaf3ce31f0c03314/easymaker-sample/iris-inference/case_4_1000_json",
        input_data_type="JSON",
    ),
    model_evaluation=SimpleNamespace(
        input_data_uri="obs://kr1-api-object-storage.nhncloudservice.com/v1/AUTH_ed79fa143403492fbaf3ce31f0c03314/easymaker-sample/iris-dataset/model_evaluation",
        input_data_type="CSV",
        target_field_name="species",
        class_names="setosa,versicolor,virginica",
    ),
)

regression_model = SimpleNamespace(
    model_uri="obs://kr1-api-object-storage.nhncloudservice.com/v1/AUTH_ed79fa143403492fbaf3ce31f0c03314/easymaker-sample/tabular-regression/model",
    model_type="PYTORCH",
    model_evaluation=SimpleNamespace(
        input_data_uri="obs://kr1-api-object-storage.nhncloudservice.com/v1/AUTH_ed79fa143403492fbaf3ce31f0c03314/easymaker-sample/tabular-regression/data",
        input_data_type="CSV",
        target_field_name="quality",
    ),
)


# 인증 토큰 발급 가이드 : https://docs.nhncloud.com/ko/nhncloud/ko/public-api/api-authentication/#_1
def get_access_token(user_access_key_id, secret_access_key):
    credentials = f"{user_access_key_id}:{secret_access_key}"
    auth_header = f"Basic {base64.b64encode(credentials.encode('utf-8')).decode('utf-8')}"
    url = "https://oauth.api.nhncloudservice.com/oauth2/token/create"
    headers = {"Content-Type": "application/x-www-form-urlencoded", "Authorization": auth_header}
    data = {"grant_type": "client_credentials"}
    response = requests.post(url, headers=headers, data=data)
    return response.json().get("access_token")


# TODO.가이드 노트북 다운로드
def download_guide_notebook():
    pass
