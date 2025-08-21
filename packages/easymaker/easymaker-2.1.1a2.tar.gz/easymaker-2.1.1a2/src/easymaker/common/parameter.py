from easymaker.common.base_model.easymaker_base_model import BaseModel


class Parameter(BaseModel):
    parameter_name: str | None = None
    parameter_value: str | None = None
