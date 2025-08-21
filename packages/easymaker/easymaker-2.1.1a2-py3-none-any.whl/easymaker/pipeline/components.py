from easymaker.common.base_model.easymaker_base_model import BaseModel


class PipelineParameterSpec(BaseModel):
    parameter_name: str | None = None
    parameter_type: str | None = None
    is_optional: bool | None = None
    default_value: str | None = None
