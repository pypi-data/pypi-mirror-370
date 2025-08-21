import os

import easymaker
from easymaker.api.request_body import TrainingCreateBody
from easymaker.common import utils
from easymaker.common.base_model.training_base_model import TrainingBaseModel
from easymaker.common.image import Image
from easymaker.common.instance_type import InstanceType
from easymaker.common.parameter import Parameter
from easymaker.training.components import Algorithm, Dataset


class Training(TrainingBaseModel):
    def run(
        self,
        training_name: str,
        experiment_id: str | None = None,
        description: str | None = None,
        image_name: str | None = None,
        instance_type_name: str | None = None,
        distributed_node_count: int | None = 1,
        data_storage_size: int | None = None,
        source_dir_uri: str | None = None,
        entry_point: str | None = None,
        algorithm_name: str | None = None,
        hyperparameter_list: list[Parameter] | None = None,
        dataset_list: list[Dataset] | None = None,
        check_point_input_uri: str | None = None,
        check_point_upload_uri: str | None = None,
        model_upload_uri: str | None = None,
        timeout_hours: int | None = 720,
        use_log: bool | None = False,
        wait: bool | None = True,
        use_torchrun: bool | None = False,
        nproc_per_node: int | None = 0,
    ):
        # run training
        instance_type_list = easymaker.easymaker_config.api_sender.get_instance_type_list()
        image_list = easymaker.easymaker_config.api_sender.get_image_list()
        algorithm_list = easymaker.easymaker_config.api_sender.get_algorithm_list()
        if not experiment_id:
            experiment_id = os.environ.get("EM_EXPERIMENT_ID")
        response = easymaker.easymaker_config.api_sender.run_training(
            TrainingCreateBody(
                training_name=training_name,
                description=description,
                experiment_id=experiment_id,
                image_id=utils.from_name_to_id(image_list, image_name, Image),
                flavor_id=utils.from_name_to_id(instance_type_list, instance_type_name, InstanceType),
                instance_count=distributed_node_count,
                data_storage_size=data_storage_size,
                source_dir_uri=source_dir_uri,
                entry_point=entry_point,
                algorithm_id=utils.from_name_to_id(algorithm_list, algorithm_name, Algorithm) if algorithm_name else None,
                hyperparameter_list=hyperparameter_list,
                dataset_list=dataset_list,
                check_point_input_uri=check_point_input_uri,
                check_point_upload_uri=check_point_upload_uri,
                model_upload_uri=model_upload_uri,
                training_type_code="NORMAL",
                timeout_minutes=timeout_hours * 60,
                use_log=use_log,
                use_torchrun=use_torchrun,
                nproc_per_node=nproc_per_node,
            )
        )
        super().__init__(**response)
        print(f"[AI EasyMaker] Training create request complete. training_id: {self.training_id}")
        if wait:
            self.wait()

        return self
