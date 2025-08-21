import os

from pydantic import Field

import easymaker
from easymaker.api.request_body import PipelineRunCreateBody
from easymaker.common import utils
from easymaker.common.base_model.easymaker_base_model import EasyMakerBaseModel
from easymaker.common.instance_type import InstanceType
from easymaker.common.parameter import Parameter
from easymaker.common.storage import Nas, Storage
from easymaker.experiment.experiment import Experiment
from easymaker.pipeline.pipeline import Pipeline
from easymaker.pipeline.pipeline_recurring_run import PipelineRecurringRun


class PipelineRun(EasyMakerBaseModel):
    pipeline_run_id: str | None = None
    pipeline_run_name: str | None = None
    pipeline_run_status_code: str | None = None
    pipeline: Pipeline | None = None
    experiment: Experiment | None = None
    pipeline_recurring_run: PipelineRecurringRun | None = None
    instance_type: InstanceType | None = Field(default=None, validation_alias="flavor")
    instance_count: int | None = None
    boot_storage: Storage | None = None
    elapsed_time_seconds: int | None = None
    started_datetime: str | None = None
    finished_datetime: str | None = None
    nas_list: list[Nas] | None = None
    parameter_list: list[Parameter] | None = None

    def create(
        self,
        pipeline_run_name: str,
        description: str | None = None,
        pipeline_id: str | None = None,
        experiment_id: str | None = None,
        experiment_name: str | None = None,
        experiment_description: str | None = None,
        instance_type_name: str | None = None,
        instance_count: int = 1,
        boot_storage_size: int = 50,
        parameter_list: list[Parameter] | None = None,
        nas_list: list[Nas] | None = None,
        wait: bool | None = True,
    ):
        if not experiment_id:
            experiment_id = os.environ.get("EM_EXPERIMENT_ID")
        instance_type_list = easymaker.easymaker_config.api_sender.get_instance_type_list()
        response = easymaker.easymaker_config.api_sender.create_pipeline_run(
            PipelineRunCreateBody(
                pipeline_run_or_recurring_run_name=pipeline_run_name,
                description=description,
                pipeline_id=pipeline_id,
                experiment_id=experiment_id,
                experiment_name=experiment_name,
                experiment_description=experiment_description,
                parameter_list=parameter_list,
                flavor_id=utils.from_name_to_id(instance_type_list, instance_type_name, InstanceType),
                instance_count=instance_count,
                boot_storage_size=boot_storage_size,
                nas_list=nas_list,
            )
        )
        super().__init__(**response)
        print(f"[AI EasyMaker] Pipeline run create request complete. pipeline_run_id: {self.pipeline_run_id}")
        if wait:
            self.wait()

        return self

    def stop(self):
        if self.pipeline_run_id:
            easymaker.easymaker_config.api_sender.stop_pipeline_run_by_id(self.pipeline_run_id)
            print(f"[AI EasyMaker] Pipeline run stop request complete. Pipeline run ID : {self.pipeline_run_id}")
        else:
            print("[AI EasyMaker] Pipeline run stop fail. pipeline_run_id is empty.")
