from pydantic import Field

import easymaker
from easymaker.common.base_model.easymaker_base_model import EasyMakerBaseModel
from easymaker.common.image import Image
from easymaker.common.instance_type import InstanceType
from easymaker.common.parameter import Parameter
from easymaker.common.storage import Storage
from easymaker.experiment.experiment import Experiment
from easymaker.model.model import Model
from easymaker.training.components import Algorithm, Dataset


class TrainingCommonBaseModel(EasyMakerBaseModel):
    experiment: Experiment | None = None
    instance_count: int | None = None
    nproc_per_node: int | None = None
    algorithm: Algorithm | None = None
    source_dir_uri: str | None = None
    entry_point: str | None = None
    model_upload_uri: str | None = None
    check_point_input_uri: str | None = None
    check_point_upload_uri: str | None = None
    log_and_crash_app_key: str | None = None
    timeout_minutes: int | None = None
    elapsed_time_seconds: int | None = None
    tensorboard_access_uri: str | None = None
    tensorboard_access_path: str | None = None
    dataset_list: list[Dataset] | None = None
    instance_type: InstanceType | None = Field(default=None, validation_alias="flavor")
    image: Image | None = None
    boot_storage: Storage | None = None
    data_storage_list: list[Storage] | None = None
    model_list: list[Model] | None = None

    # Training, HyperarameterTuning에서만 사용됨, 튜닝도 TRAINING로 조회
    @classmethod
    def get_image_list(cls) -> list[Image]:
        image_list = easymaker.easymaker_config.api_sender.get_image_list(group_type="TRAINING")
        return Image._from_dict_list_to_em_class_list(image_list)

    @classmethod
    def get_algorithm_list(cls) -> list[Algorithm]:
        algorithm_dict_list = easymaker.easymaker_config.api_sender.get_algorithm_list()
        algorithm_list = Algorithm._from_dict_list_to_em_class_list(algorithm_dict_list)

        image_list = cls.get_image_list()
        image_map = {image.image_id: image.image_name for image in image_list}
        for algorithm in algorithm_list:
            if algorithm.cpu_training_image_id in image_map:
                algorithm.cpu_training_image_name = image_map[algorithm.cpu_training_image_id]
            if algorithm.gpu_training_image_id in image_map:
                algorithm.gpu_training_image_name = image_map[algorithm.gpu_training_image_id]

        return algorithm_list


class TrainingBaseModel(TrainingCommonBaseModel):
    training_id: str | None = None
    training_name: str | None = None
    training_status_code: str | None = None
    hyperparameter_list: list[Parameter] | None = None
