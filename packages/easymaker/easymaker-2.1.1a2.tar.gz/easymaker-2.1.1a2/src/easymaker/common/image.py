from pydantic import Field

from easymaker.common.base_model.easymaker_base_model import BaseModel


class Image(BaseModel):
    image_id: str | None = Field(default=None, validation_alias="imageId")
    image_name: str | None = Field(default=None, validation_alias="imageName")
    image_type_code: str | None = Field(default=None, validation_alias="imageTypeCode")
    core_type_code: str | None = Field(default=None, validation_alias="coreTypeCode")
    framework_code: str | None = Field(default=None, validation_alias="frameworkCode")
    framework_version: str | None = Field(default=None, validation_alias="frameworkVersion")
    python_version: str | None = Field(default=None, validation_alias="pythonVersion")
    description: str | None = Field(default=None, validation_alias="description")
