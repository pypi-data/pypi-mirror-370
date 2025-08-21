from pydantic import Field

import easymaker
from easymaker.api.request_body import BatchInferenceBody
from easymaker.common import utils
from easymaker.common.base_model.easymaker_base_model import EasyMakerBaseModel
from easymaker.common.image import Image
from easymaker.common.instance_type import InstanceType
from easymaker.common.storage import Storage
from easymaker.model.model import Model


class BatchInference(EasyMakerBaseModel):
    batch_inference_id: str | None = None
    batch_inference_name: str | None = None
    batch_inference_status_code: str | None = None
    instance_count: int | None = None
    timeout_minutes: int | None = None
    image: Image | None = None
    model: Model | None = None
    pod_count: int | None = None
    max_batch_size: int | None = None
    inference_timeout_seconds: int | None = None
    input_data_uri: str | None = None
    input_data_type_code: str | None = None
    include_glob_pattern: str | None = None
    exclude_glob_pattern: str | None = None
    output_upload_uri: str | None = None
    log_and_crash_app_key: str | None = None
    input_file_count: int | None = None
    input_data_count: int | None = None
    process_count: int | None = None
    success2xx_count: int | None = None
    fail4xx_count: int | None = None
    fail5xx_count: int | None = None
    elapsed_time_seconds: int | None = None
    instance_type: InstanceType | None = Field(default=None, validation_alias="flavor")
    boot_storage: Storage | None = None
    data_storage_list: list[Storage] | None = None

    def run(
        self,
        batch_inference_name: str,
        instance_count: int = 1,
        timeout_hours: int = 720,
        instance_type_name: str = None,
        model_id: str = None,
        #
        pod_count: int = 1,
        batch_size: int = 32,
        inference_timeout_seconds: int = 120,
        #
        input_data_uri: str = None,
        input_data_type: str = None,
        include_glob_pattern: str | None = None,
        exclude_glob_pattern: str | None = None,
        output_upload_uri: str = None,
        #
        data_storage_size: int = 300,
        #
        description: str | None = None,
        use_log: bool | None = False,
        wait: bool | None = True,
    ):
        instance_type_list = easymaker.easymaker_config.api_sender.get_instance_type_list()
        response = easymaker.easymaker_config.api_sender.run_batch_inference(
            BatchInferenceBody(
                batch_inference_name=batch_inference_name,
                instance_count=instance_count,
                timeout_minutes=timeout_hours * 60,
                flavor_id=utils.from_name_to_id(instance_type_list, instance_type_name, InstanceType),
                model_id=model_id,
                #
                pod_count=pod_count,
                max_batch_size=batch_size,
                inference_timeout_seconds=inference_timeout_seconds,
                #
                input_data_uri=input_data_uri,
                input_data_type_code=input_data_type,
                include_glob_pattern=include_glob_pattern,
                exclude_glob_pattern=exclude_glob_pattern,
                output_upload_uri=output_upload_uri,
                #
                data_storage_size=data_storage_size,
                #
                description=description,
                use_log=use_log,
            )
        )
        super().__init__(**response)
        print(f"[AI EasyMaker] Batch Inference create request complete. batch_inference_id: {self.batch_inference_id}")
        if wait:
            self.wait()

        return self
