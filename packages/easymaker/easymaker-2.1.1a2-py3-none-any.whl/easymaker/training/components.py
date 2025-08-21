from pydantic import Field

from easymaker.common.base_model.easymaker_base_model import BaseModel
from easymaker.common.parameter import Parameter


class HyperparameterSpec(BaseModel):
    hyperparameter_name: str | None = None
    hyperparameter_type_code: str | None = None
    hyperparameter_min_value: str | None = None
    hyperparameter_max_value: str | None = None
    hyperparameter_step: str | None = None
    hyperparameter_specified_values: str | None = None
    is_optional: bool | None = None
    default_value: str | None = None


class Algorithm(BaseModel):
    algorithm_id: str | None = Field(default=None, validation_alias="algorithmId")
    algorithm_name: str | None = Field(default=None, validation_alias="algorithmName")
    cpu_training_image_id: str | None = Field(default=None, validation_alias="cpuTrainingImageId")
    cpu_training_image_name: str | None = None
    gpu_training_image_id: str | None = Field(default=None, validation_alias="gpuTrainingImageId")
    gpu_training_image_name: str | None = None
    algorithm_dataset_schema: list[dict] | None = Field(default=None, validation_alias="algorithmDatasetSchema")
    hyperparameter_spec_list: list[HyperparameterSpec] | None = Field(default=None, validation_alias="hyperparameterSpecList")


class Dataset(BaseModel):
    dataset_name: str | None = None
    data_uri: str | None = None


class Metric(BaseModel):
    name_: str | None = Field(default=None, alias="name")

    @property
    def name(self) -> str:
        return self.name_


class TrialMetric(BaseModel):
    trial_metric_name: str | None = None
    trial_metric_min_value: str | None = None
    trial_metric_max_value: str | None = None
    trial_metric_latest_value: str | None = None


class Trial(BaseModel):
    trial_id: str | None = None
    trial_name: str | None = None
    trial_status_code: str | None = None
    hyperparameter_tuning_id: str | None = None
    hyperparameter_list: list[Parameter] | None = None
    trial_metric_list: list[TrialMetric] | None = None
