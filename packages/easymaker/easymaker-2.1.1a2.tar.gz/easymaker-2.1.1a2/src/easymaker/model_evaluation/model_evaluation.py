from pydantic import Field

import easymaker
from easymaker.api.request_body import ModelEvaluationBatchInferenceBody, ModelEvaluationCreateBody
from easymaker.common import utils
from easymaker.common.base_model.easymaker_base_model import BaseModel, EasyMakerBaseModel
from easymaker.common.instance_type import InstanceType
from easymaker.model.model import Model
from easymaker.model_evaluation.model_evaluation_metrics import ClassificationEvaluationMetrics, RegressionEvaluationMetrics


class ModelEvaluationBatchInference(BaseModel):
    batch_inference_id: str | None = None
    batch_inference_name: str | None = None
    instance_type: InstanceType | None = Field(default=None, validation_alias="flavor")
    instance_count: int | None = None
    pod_count: int | None = None
    output_upload_uri: str | None = None
    max_batch_size: int | None = None
    inference_timeout_seconds: int | None = None


class ModelEvaluation(EasyMakerBaseModel):
    model_evaluation_id: str | None = None
    model_evaluation_name: str | None = None
    model_evaluation_status_code: str | None = None
    model: Model | None = None
    objective_code: str | None = None
    class_names: str | None = None
    instance_type: InstanceType | None = Field(default=None, validation_alias="flavor")
    availability_zone: str | None = None
    input_data_uri: str | None = None
    input_data_type_code: str | None = None
    target_field_name: str | None = None
    batch_inference: ModelEvaluationBatchInference | None = None
    timeout_hours: int | None = None
    metrics: RegressionEvaluationMetrics | ClassificationEvaluationMetrics | None = None
    # TODO
    # generate_feature_attributions: bool | None = None
    # feature_attributions: dict | None = None
    # evaluation_slices: list | None = None

    def create(
        self,
        model_evaluation_name: str,
        model_id: str,
        objective_code: str,
        instance_type_name: str,
        input_data_uri: str,
        input_data_type_code: str,
        target_field_name: str,
        batch_inference_instance_type_name: str,
        batch_inference_instance_count: int,
        batch_inference_pod_count: int,
        batch_inference_output_upload_uri: str,
        batch_inference_max_batch_size: int,
        batch_inference_inference_timeout_seconds: int,
        timeout_hours: int | None = 720,
        class_names: str | None = None,
        description: str | None = None,
        use_log: bool | None = False,
        wait: bool | None = True,
        # generate_feature_attributions: bool | None = False,
    ):
        instance_type_list = easymaker.easymaker_config.api_sender.get_instance_type_list()
        response = easymaker.easymaker_config.api_sender.create_model_evaluation(
            ModelEvaluationCreateBody(
                model_evaluation_name=model_evaluation_name,
                model_id=model_id,
                objective_code=objective_code,
                flavor_id=utils.from_name_to_id(instance_type_list, instance_type_name, InstanceType),
                input_data_uri=input_data_uri,
                input_data_type_code=input_data_type_code,
                target_field_name=target_field_name,
                timeout_minutes=timeout_hours * 60,
                class_names=class_names,
                # generate_feature_attributions=generate_feature_attributions,
                batch_inference=ModelEvaluationBatchInferenceBody(
                    flavor_id=utils.from_name_to_id(instance_type_list, batch_inference_instance_type_name, InstanceType),
                    instance_count=batch_inference_instance_count,
                    pod_count=batch_inference_pod_count,
                    output_upload_uri=batch_inference_output_upload_uri,
                    max_batch_size=batch_inference_max_batch_size,
                    inference_timeout_seconds=batch_inference_inference_timeout_seconds,
                ),
                description=description,
                use_log=use_log,
            )
        )
        super().__init__(**response)
        print(f"[AI EasyMaker] Model evaluation create request complete. model_evaluation_id: {self.model_evaluation_id}")
        if wait:
            self.wait()

        return self

    def stop(self):
        if self.model_evaluation_id:
            easymaker.easymaker_config.api_sender.stop_model_evaluation_by_id(self.model_evaluation_id)
            print(f"[AI EasyMaker] Model evaluation stop request complete. Model evaluation ID : {self.model_evaluation_id}")
        else:
            print("[AI EasyMaker] Model evaluation stop fail. model_evaluation_id is empty.")
