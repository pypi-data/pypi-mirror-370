from pydantic import Field

from easymaker.common.base_model.easymaker_base_model import BaseModel


class InstanceType(BaseModel):
    id_: str | None = Field(default=None, alias="id")
    name_: str | None = Field(default=None, alias="name")
    vcpus: int | None = None
    ram: int | None = None
    disk: int | None = None
    gpu: bool | None = Field(default=None, validation_alias="gpuFlavor")
    gpu_count: int | None = Field(default=None, validation_alias="gpuCount")
    gpu_memory: int | None = Field(default=None, validation_alias="gpuMemory")

    @property
    def id(self) -> str:
        return self.id_

    @property
    def name(self) -> str:
        return self.name_
