from easymaker.common.base_model.easymaker_base_model import BaseModel


class ApigwStage(BaseModel):
    stage_id: str | None = None
    deploy_status: str | None = None
    stage_url: str | None = None


class AutoScaler(BaseModel):
    enable: bool | None = None
    min_node_count: int | None = None
    max_node_count: int | None = None
    scale_down_enable: bool | None = None
    scale_down_util_thresh_percentage: int | None = None
    scale_down_unneeded_minute: int | None = None
    scale_down_delay_after_add_minute: int | None = None


class EndpointModelResource(BaseModel):
    model_id: str | None = None
    resource_option_detail: object | None = None
    pod_auto_scale_enable: bool | None = None
    scale_metric_code: str | None = None
    scale_metric_target: int | None = None
    description: str | None = None


class ResourceOptionDetail(BaseModel):
    cpu: str | None = None
    memory: str | None = None
    gpu: str | None = None
