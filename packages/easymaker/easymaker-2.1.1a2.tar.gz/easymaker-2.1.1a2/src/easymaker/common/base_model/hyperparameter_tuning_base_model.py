from easymaker.common.base_model.training_base_model import TrainingCommonBaseModel
from easymaker.training.components import HyperparameterSpec, Metric, Trial


class HyperparameterTuningBaseModel(TrainingCommonBaseModel):
    hyperparameter_tuning_id: str | None = None
    hyperparameter_tuning_name: str | None = None
    hyperparameter_tuning_status_code: str | None = None
    hyperparameter_tuning_status_reason: str | None = None
    hyperparameter_spec_list: list[HyperparameterSpec] | None = None
    metric_list: list[Metric] | None = None
    metric_regex: str | None = None
    objective_metric_name: str | None = None
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
    successful_trial_count: int | None = None
    running_trial_count: int | None = None
    failed_trial_count: int | None = None
    optimal_trial_id: str | None = None
    optimal_trial: Trial | None = None
