import os

import easymaker
from easymaker.api.request_body import HyperparameterTuningCreateBody
from easymaker.common import utils
from easymaker.common.base_model.hyperparameter_tuning_base_model import (
    HyperparameterTuningBaseModel,
)
from easymaker.common.image import Image
from easymaker.common.instance_type import InstanceType
from easymaker.training.components import Algorithm, Dataset, HyperparameterSpec, Metric


class HyperparameterTuning(HyperparameterTuningBaseModel):
    def run(
        self,
        hyperparameter_tuning_name: str,
        experiment_id: str | None = None,
        description: str | None = None,
        algorithm_name: str | None = None,
        image_name: str | None = None,
        instance_type_name: str | None = None,
        distributed_node_count: int | None = 1,
        parallel_trial_count: int | None = 1,
        data_storage_size: int | None = None,
        source_dir_uri: str | None = None,
        entry_point: str | None = None,
        hyperparameter_spec_list: list[HyperparameterSpec] | None = None,
        dataset_list: list[Dataset] | None = None,
        check_point_input_uri: str | None = None,
        check_point_upload_uri: str | None = None,
        model_upload_uri: str | None = None,
        timeout_hours: int | None = 720,
        use_log: bool | None = False,
        wait: bool | None = True,
        metric_list: list[Metric] | None = None,
        metric_regex: str | None = None,
        objective_metric_name: str | None = None,  # name 값만 입력받아 {"name": ""} 형태로 변경
        objective_type_code: str | None = None,  # easymaker.OBJECTIVE_TYPE_CODE.MINIMIZE, MAXIMIZE
        objective_goal: float | None = None,
        max_failed_trial_count: int | None = None,
        max_trial_count: int | None = None,
        tuning_strategy_name: str | None = None,  # easymaker.TUNING_STRATEGY.BAYESIAN_OPTIMIZATION, RANDOM, GRID
        tuning_strategy_random_state: int | None = None,
        early_stopping_algorithm: str | None = None,  # easymaker.EARLY_STOPPING_ALGORITHM.MEDIAN
        early_stopping_min_trial_count: int | None = 3,
        early_stopping_start_step: int | None = 4,
        use_torchrun: bool | None = False,
        nproc_per_node: int | None = 0,
    ):
        def convertMetricFormat(name):
            return {"name": name}

        # run hyperparameter tuning
        instance_type_list = easymaker.easymaker_config.api_sender.get_instance_type_list()
        image_list = easymaker.easymaker_config.api_sender.get_image_list()
        algorithm_list = easymaker.easymaker_config.api_sender.get_algorithm_list()
        if not experiment_id:
            experiment_id = os.environ.get("EM_EXPERIMENT_ID")
        response = easymaker.easymaker_config.api_sender.run_hyperparameter_tuning(
            HyperparameterTuningCreateBody(
                hyperparameter_tuning_name=hyperparameter_tuning_name,
                description=description,
                experiment_id=experiment_id,
                algorithm_id=utils.from_name_to_id(algorithm_list, algorithm_name, Algorithm) if algorithm_name else None,
                image_id=utils.from_name_to_id(image_list, image_name, Image),
                flavor_id=utils.from_name_to_id(instance_type_list, instance_type_name, InstanceType),
                instance_count=distributed_node_count * parallel_trial_count,
                parallel_trial_count=parallel_trial_count,
                data_storage_size=data_storage_size,
                source_dir_uri=source_dir_uri,
                entry_point=entry_point,
                hyperparameter_spec_list=hyperparameter_spec_list,
                dataset_list=dataset_list,
                check_point_input_uri=check_point_input_uri,
                check_point_upload_uri=check_point_upload_uri,
                model_upload_uri=model_upload_uri,
                timeout_minutes=timeout_hours * 60,
                use_log=use_log,
                metric_list=metric_list,
                metric_regex=metric_regex,
                objective_metric=convertMetricFormat(objective_metric_name) if objective_metric_name else None,
                objective_type_code=objective_type_code,
                objective_goal=objective_goal,
                max_failed_trial_count=max_failed_trial_count,
                max_trial_count=max_trial_count,
                tuning_strategy_name=tuning_strategy_name,
                tuning_strategy_random_state=tuning_strategy_random_state,
                early_stopping_algorithm=early_stopping_algorithm,
                early_stopping_min_trial_count=early_stopping_min_trial_count,
                early_stopping_start_step=early_stopping_start_step,
                use_torchrun=use_torchrun,
                nproc_per_node=nproc_per_node,
            )
        )
        super().__init__(**response)
        print(f"[AI EasyMaker] Hyperparameter tuning create request complete. hyperparameter_tuning_id: {self.hyperparameter_tuning_id}")
        if wait:
            self.wait()

        return self
