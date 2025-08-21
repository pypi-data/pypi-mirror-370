import base64

import easymaker
from easymaker.api.request_body import PipelineUploadBody
from easymaker.common.base_model.easymaker_base_model import EasyMakerBaseModel
from easymaker.pipeline.components import PipelineParameterSpec


class Pipeline(EasyMakerBaseModel):
    pipeline_id: str | None = None
    pipeline_name: str | None = None
    pipeline_parameter_spec_list: list[PipelineParameterSpec] | None = None
    pipeline_status_code: str | None = None

    def upload(
        self,
        pipeline_name: str,
        pipeline_spec_manifest_path: str,
        description: str | None = None,
        wait: bool | None = True,
    ):
        with open(pipeline_spec_manifest_path, "rb") as file:
            pipeline_spec_manifest = file.read()
        base64_pipeline_spec_manifest = base64.b64encode(pipeline_spec_manifest).decode("utf-8")

        response = easymaker.easymaker_config.api_sender.upload_pipeline(
            PipelineUploadBody(
                pipeline_name=pipeline_name,
                base64_pipeline_spec_manifest=base64_pipeline_spec_manifest,
                description=description,
            )
        )
        super().__init__(**response)
        print(f"[AI EasyMaker] Pipeline upload request complete. Pipeline ID : {self.pipeline_id}")
        if wait:
            self.wait(action="upload")

        return self
