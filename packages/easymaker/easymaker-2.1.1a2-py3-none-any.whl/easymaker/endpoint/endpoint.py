import requests
from pydantic import Field

import easymaker
from easymaker.api.request_body import EndpointCreateBody, StageCreateBody
from easymaker.common import utils
from easymaker.common.base_model.easymaker_base_model import EasyMakerBaseModel
from easymaker.common.image import Image
from easymaker.common.instance_type import InstanceType
from easymaker.common.storage import Storage
from easymaker.endpoint import ApiSpec
from easymaker.endpoint import utils as endpoint_utils
from easymaker.endpoint.components import ApigwStage, AutoScaler, EndpointModelResource
from easymaker.model.model import Model


class Endpoint(EasyMakerBaseModel):
    endpoint_id: str | None = None
    endpoint_name: str | None = None
    endpoint_status_code: str | None = None
    apigw_app_key: str | None = None
    apigw_region: str | None = None
    apigw_service_id: str | None = None
    image: Image | None = None
    boot_storage: Storage | None = None
    data_storage_list: list[Storage] | None = None
    endpoint_stage_list: "list[EndpointStage] | None" = None
    default_stage: "EndpointStage | None" = None

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if self.endpoint_id:
            self.default_stage = get_default_endpoint_stage(endpoint_id=self.endpoint_id)

    def create(
        self,
        endpoint_name: str | None,
        endpoint_model_resource_list: list[EndpointModelResource],
        instance_type_name: str | None,
        instance_count: int = 1,
        description: str | None = None,
        use_log: bool | None = False,
        wait: bool | None = True,
        autoscaler_enable: bool | None = False,
        autoscaler_min_node_count: int | None = 1,
        autoscaler_max_node_count: int | None = 10,
        autoscaler_scale_down_enable: bool | None = True,
        autoscaler_scale_down_util_threshold: int | None = 50,
        autoscaler_scale_down_unneeded_time: int | None = 10,
        autoscaler_scale_down_delay_after_add: int | None = 10,
    ):
        instance_type_list = easymaker.easymaker_config.api_sender.get_instance_type_list()
        response = easymaker.easymaker_config.api_sender.create_endpoint(
            EndpointCreateBody(
                endpoint_name=endpoint_name,
                description=description,
                flavor_id=utils.from_name_to_id(instance_type_list, instance_type_name, InstanceType),
                endpoint_model_resource_list=endpoint_model_resource_list,
                node_count=instance_count,
                use_log=use_log,
                ca_enable=autoscaler_enable,
                ca_min_node_count=autoscaler_min_node_count,
                ca_max_node_count=autoscaler_max_node_count,
                ca_scale_down_enable=autoscaler_scale_down_enable,
                ca_scale_down_util_thresh=autoscaler_scale_down_util_threshold,
                ca_scale_down_unneeded_time=autoscaler_scale_down_unneeded_time,
                ca_scale_down_delay_after_add=autoscaler_scale_down_delay_after_add,
            )
        )
        super().__init__(**response)
        print(f"[AI EasyMaker] Endpoint create request complete. endpoint_id: {self.endpoint_id}")
        if wait:
            self.wait()
            self.default_stage = get_default_endpoint_stage(endpoint_id=self.endpoint_id)
            self.default_stage.wait()

        return self

    def predict(self, model_id, json=None, api_spec: ApiSpec = ApiSpec.auto):
        if self.default_stage:
            endpoint_model = next((x for x in self.default_stage.endpoint_model_list if x.model_id == model_id), {})
            model_name = endpoint_model.model.model_name
            endpoint_url = "https://" + self.default_stage.apigw_stage_url

            if api_spec == ApiSpec.auto:
                api_spec = endpoint_utils.get_api_spec(json)

            resource_uri = endpoint_model.apigw_resource_uri or endpoint_utils.get_inference_url(api_spec, model_name)
            response = requests.post(f"{endpoint_url}{resource_uri}", json=json).json()
            return response

    def get_stage_list(self):
        return get_endpoint_stage_list(self.endpoint_id)


def get_endpoint_list() -> list[Endpoint]:
    endpoint_list_response = easymaker.easymaker_config.api_sender.get_endpoint_list()
    endpoint_list = []
    for endpoint_response in endpoint_list_response:
        endpoint_list.append(Endpoint(**endpoint_response))
    return endpoint_list


class EndpointStage(EasyMakerBaseModel):
    endpoint_stage_id: str | None = None
    endpoint_id: str | None = None
    endpoint_stage_name: str | None = None
    endpoint_stage_status_code: str | None = None
    apigw_stage_id: str | None = None
    apigw_stage_name: str | None = None
    log_and_crash_app_key: str | None = None
    instance_type: InstanceType | None = Field(default=None, validation_alias="flavor")
    auto_scaler: AutoScaler | None = None
    node_count: int | None = None
    is_active_node_group_status: bool | None = None
    is_cluster_latest: bool | None = None
    expired_datetime: str | None = None
    apigw_stage_url: str | None = None
    deploy_status: str | None = None
    default_stage: bool | None = None
    pod_count: int | None = None
    endpoint_model_list: "list[EndpointModel] | None" = None

    def create(
        self,
        stage_name: str | None,
        endpoint_id: str | None,
        instance_type_name: str | None,
        endpoint_model_resource_list: list[EndpointModelResource],
        instance_count: int = 1,
        description: str | None = None,
        use_log: bool | None = False,
        autoscaler_enable: bool | None = False,
        autoscaler_min_node_count: int | None = 1,
        autoscaler_max_node_count: int | None = 10,
        autoscaler_scale_down_enable: bool | None = True,
        autoscaler_scale_down_util_threshold: int | None = 50,
        autoscaler_scale_down_unneeded_time: int | None = 10,
        autoscaler_scale_down_delay_after_add: int | None = 10,
        wait: bool | None = True,
    ):
        instance_type_list = easymaker.easymaker_config.api_sender.get_instance_type_list()
        response = easymaker.easymaker_config.api_sender.create_stage(
            StageCreateBody(
                endpoint_id=endpoint_id,
                apigw_stage_name=stage_name,
                description=description,
                flavor_id=utils.from_name_to_id(instance_type_list, instance_type_name, InstanceType),
                endpoint_model_resource_list=endpoint_model_resource_list,
                node_count=instance_count,
                use_log=use_log,
                ca_enable=autoscaler_enable,
                ca_min_node_count=autoscaler_min_node_count,
                ca_max_node_count=autoscaler_max_node_count,
                ca_scale_down_enable=autoscaler_scale_down_enable,
                ca_scale_down_util_thresh=autoscaler_scale_down_util_threshold,
                ca_scale_down_unneeded_time=autoscaler_scale_down_unneeded_time,
                ca_scale_down_delay_after_add=autoscaler_scale_down_delay_after_add,
            )
        )
        super().__init__(**response)
        print(f"[AI EasyMaker] Endpoint stage create request complete. endpoint_stage_id: {self.endpoint_stage_id}")
        if wait:
            self.wait()

        return self

    def predict(self, model_id, json=None, api_spec: ApiSpec = ApiSpec.auto):
        endpoint_model = next((x for x in self.endpoint_model_list if x.model_id == model_id), {})
        model_name = endpoint_model.model.model_name
        endpoint_url = "https://" + self.apigw_stage_url

        if api_spec == ApiSpec.auto:
            api_spec = endpoint_utils.get_api_spec(json)

        resource_uri = endpoint_model.apigw_resource_uri or endpoint_utils.get_inference_url(api_spec, model_name)
        response = requests.post(f"{endpoint_url}{resource_uri}", json=json).json()
        return response


def get_endpoint_stage_list(endpoint_id: str) -> list[EndpointStage]:
    endpoint_stage_list_response = easymaker.easymaker_config.api_sender.get_endpoint_stage_list(endpoint_id)
    endpoint_stage_list = []
    for endpoint_stage_response in endpoint_stage_list_response:
        endpoint_stage_list.append(EndpointStage(**endpoint_stage_response))
    return endpoint_stage_list


def get_default_endpoint_stage(endpoint_id: str) -> EndpointStage:
    endpoint_stage_list = get_endpoint_stage_list(endpoint_id)

    for endpoint_stage in endpoint_stage_list:
        if endpoint_stage.default_stage:
            return endpoint_stage
    return EndpointStage()


class EndpointModel(EasyMakerBaseModel):
    endpoint_model_id: str | None = None
    endpoint_id: str | None = None
    endpoint_model_status_code: str | None = None
    endpoint_stage_id: str | None = None
    model_id: str | None = None
    image_id: str | None = None
    stage: ApigwStage | None = None
    model: Model | None = None
    running_pod_count: int | None = None
    pod_count: int | None = None
    apigw_resource_uri: str | None = None
    apigw_endpoint_uri: str | None = None


def get_endpoint_model_list(endpoint_model_id: str):
    endpoint_model_list_response = easymaker.easymaker_config.api_sender.get_endpoint_model_list(endpoint_model_id)
    endpoint_model_list = []
    for endpoint_model_response in endpoint_model_list_response:
        endpoint_model_list.append(EndpointModel(**endpoint_model_response))
    return endpoint_model_list
