import os
from typing import Any

from pydantic import Field

from easymaker.common.base_model.easymaker_base_model import EasyMakerBaseModel
from easymaker.training.components import HyperparameterSpec


class EasyMakerResourceCreateCommonBody(EasyMakerBaseModel):
    parent_pipeline_run_id: str | None = Field(os.getenv("EM_PIPELINE_RUN_ID", None), repr=False)
    parent_pipeline_run_task_name: str | None = Field(os.getenv("EM_KUBEFLOW_PIPELINE_RUN_TASK_NAME", None), repr=False)


class ExperimentCreateBody(EasyMakerResourceCreateCommonBody):
    experiment_name: str | None = None


class ModelCreateBody(EasyMakerResourceCreateCommonBody):
    model_name: str
    training_id: str | None = None
    hyperparameter_tuning_id: str | None = None
    model_type_code: str | None = None
    parameter_list: list[Any] | None = None
    model_upload_uri: str | None = None


class TrainingCommonBody(EasyMakerResourceCreateCommonBody):
    experiment_id: str | None = None
    experiment_name: str | None = None
    experiment_description: str | None = None
    image_id: str
    flavor_id: str
    instance_count: int = 1
    data_storage_size: int | None = None
    algorithm_id: str | None = None
    dataset_list: list[Any] | None = []
    check_point_input_uri: str | None = None
    check_point_upload_uri: str | None = None
    source_dir_uri: str | None = None
    entry_point: str | None = None
    model_upload_uri: str
    timeout_minutes: int = 43200
    use_log: bool | None = False
    nproc_per_node: int | None = 1
    use_torchrun: bool | None = False


class TrainingCreateBody(TrainingCommonBody):
    training_name: str
    hyperparameter_list: list[Any] | None = None
    training_type_code: str


class HyperparameterTuningCreateBody(TrainingCommonBody):
    hyperparameter_tuning_name: str
    hyperparameter_spec_list: list[HyperparameterSpec] | None = None
    metric_list: list[Any] | None = None
    metric_regex: str | None = None
    objective_metric: dict | None = None
    objective_type_code: str | None = None
    objective_goal: float | None = None
    max_failed_trial_count: int | None = None
    max_trial_count: int | None = None
    parallel_trial_count: int | None = None
    tuning_strategy_name: str | None = None
    tuning_strategy_random_state: int | None = None
    early_stopping_algorithm: str | None = None
    early_stopping_min_trial_count: int | None = None
    early_stopping_start_step: int | None = None


class EndpointCreateBody(EasyMakerResourceCreateCommonBody):
    endpoint_name: str
    flavor_id: str
    endpoint_model_resource_list: list[Any] = None
    node_count: int
    ca_enable: bool | None = None
    ca_min_node_count: int | None = None
    ca_max_node_count: int | None = None
    ca_scale_down_enable: bool | None = None
    ca_scale_down_util_thresh: int | None = None
    ca_scale_down_unneeded_time: int | None = None
    ca_scale_down_delay_after_add: int | None = None
    use_log: bool | None = None


class StageCreateBody(EasyMakerResourceCreateCommonBody):
    endpoint_id: str
    apigw_stage_name: str
    flavor_id: str
    endpoint_model_resource_list: list[Any] = None
    node_count: int
    ca_enable: bool | None = None
    ca_min_node_count: int | None = None
    ca_max_node_count: int | None = None
    ca_scale_down_enable: bool | None = None
    ca_scale_down_util_thresh: int | None = None
    ca_scale_down_unneeded_time: int | None = None
    ca_scale_down_delay_after_add: int | None = None
    use_log: bool | None = None


class BatchInferenceBody(EasyMakerResourceCreateCommonBody):
    batch_inference_name: str
    instance_count: int
    timeout_minutes: int
    flavor_id: str
    model_id: str
    image_id: str | None = None
    pod_count: int
    max_batch_size: int
    inference_timeout_seconds: int
    input_data_uri: str
    input_data_type_code: str
    include_glob_pattern: str | None = None
    exclude_glob_pattern: str | None = None
    output_upload_uri: str
    data_storage_size: int
    use_log: bool | None = None


class PipelineUploadBody(EasyMakerResourceCreateCommonBody):
    pipeline_name: str | None = None
    base64_pipeline_spec_manifest: str | None = None


class PipelineRunCreateBody(EasyMakerResourceCreateCommonBody):
    pipeline_run_or_recurring_run_name: str | None = None
    pipeline_id: str | None = None
    experiment_id: str | None = None
    experiment_name: str | None = None
    experiment_description: str | None = None
    parameter_list: list[Any] | None = None
    flavor_id: str | None = None
    instance_count: int | None = None
    boot_storage_size: int | None = None
    nas_list: list[Any] | None = None


class PipelineRecurringRunCreateBody(PipelineRunCreateBody):
    schedule_periodic_minutes: int | None = None
    schedule_cron_expression: str | None = None
    max_concurrency_count: int | None = None
    schedule_start_datetime: str | None = None
    schedule_end_datetime: str | None = None
    use_catchup: bool | None = None


class ModelEvaluationBatchInferenceBody(EasyMakerBaseModel):
    flavor_id: str
    instance_count: int
    pod_count: int
    output_upload_uri: str
    max_batch_size: int
    inference_timeout_seconds: int


class ModelEvaluationCreateBody(EasyMakerResourceCreateCommonBody):
    model_evaluation_name: str
    model_id: str
    objective_code: str
    flavor_id: str
    input_data_uri: str
    input_data_type_code: str
    target_field_name: str
    class_names: str | None = None
    boot_storage_size: int | None = None
    data_storage_size: int | None = None
    generate_feature_attributions: bool | None = None
    timeout_minutes: int | None = None
    use_log: bool | None = None
    batch_inference: ModelEvaluationBatchInferenceBody | None = None
