import json
import time
from datetime import timedelta
from typing import TYPE_CHECKING, Any, Union, get_args, get_origin

from pydantic import BaseModel as PydanticBaseModel
from pydantic import ConfigDict, TypeAdapter
from pydantic.alias_generators import to_camel, to_snake

import easymaker
from easymaker.common import constants, exceptions, utils

if TYPE_CHECKING:
    from easymaker.common.instance_type import InstanceType


complete_status = [
    "COMPLETE",
    "ACTIVE",
    "ENABLED",
]

fail_status = [
    "FAIL",
    "STOP",
]


class BaseModel(PydanticBaseModel):
    # camelCase의 API 응답을 snake_case 형태의 필드값에 셋팅할 수 있도록 camel 형태의 alias 일괄 추가 및 snake_case 입력도 처리하도록 설정
    model_config = ConfigDict(
        alias_generator=to_camel,
        populate_by_name=True,
        protected_namespaces=(),  # model_ 로 시작하는 필드명은 Pydantic에서 예약된 이름이라 충돌 가능성이 있어 발생하는 경고 끄는 옵션 (model_name은 충돌나는 이름)
    )

    @property
    def id_field(self) -> str:
        name = utils.pascal_to_snake(self.__class__.__name__)
        return f"{name}_id"

    @property
    def name_field(self) -> str:
        name = utils.pascal_to_snake(self.__class__.__name__)
        return f"{name}_name"

    @property
    def id(self) -> str | None:
        return getattr(self, self.id_field, None)

    @property
    def name(self) -> str | None:
        return getattr(self, self.name_field, None)

    def __setattr__(self, key: str, value: Any) -> None:
        read_only_fields = set(attribute_name for attribute_name, model_field in self.model_fields.items() if model_field.repr is False)
        if key in read_only_fields:
            return
        super().__setattr__(key, value)

    def model_dump(self, **kwargs):
        return super().model_dump(by_alias=True, exclude_none=True, **kwargs)

    def print_info(self):
        print(json.dumps(self.model_dump(), indent=4, ensure_ascii=False))

    @classmethod
    def _from_dict_list_to_em_class_list(cls: type["BaseModel"], data: list) -> list["BaseModel"]:
        adapter = TypeAdapter(list[cls])
        return adapter.validate_python(data)


class EasyMakerBaseModel(BaseModel):
    description: str | None = None
    app_key: str | None = None
    created_datetime: str | None = None

    def __init__(self, *args, **kwargs):
        fields = self.__class__.__annotations__
        # 모든 Optional 필드에 기본값으로 None 설정
        default_data = {field: None for field in fields if get_origin(fields[field]) is Union and type(None) in get_args(fields[field])}
        default_data.update(kwargs)

        # 키워드로 입력된 값이 없고, 아규먼트로 입력된 값이 있을 경우
        # 아규먼트로 입력된 값을 ID로 사용
        if not default_data.get(self.id_field) and len(args) == 1:
            default_data[self.id_field] = args[0]

        super().__init__(**default_data)
        if self.id and not self.status:
            self._fetch()

    def _fetch(self):
        get_method_name = f"get_{to_snake(self.__class__.__name__)}_by_id"
        get_method = getattr(easymaker.easymaker_config.api_sender, get_method_name)
        response = get_method(self.id)
        self.__init__(**response)

    @property
    def id_field(self) -> str:
        name = utils.pascal_to_snake(self.__class__.__name__)
        return f"{name}_id"

    @property
    def status_field(self) -> str:
        name = utils.pascal_to_snake(self.__class__.__name__)
        return f"{name}_status_code"

    @property
    def id(self) -> str | None:
        return getattr(self, self.id_field, None)

    @property
    def status(self) -> str | None:
        return getattr(self, self.status_field, None)

    def wait(self, action: str = "create", wait_interval_seconds: int = constants.EASYMAKER_API_WAIT_INTERVAL_SECONDS):
        class_name = self.__class__.__name__
        waiting_time_seconds = 0
        while self.status not in complete_status:
            print(f"[AI EasyMaker] {class_name} {action} status: {self.status} ({timedelta(seconds=waiting_time_seconds)}) Please wait...")
            time.sleep(wait_interval_seconds)
            waiting_time_seconds += wait_interval_seconds
            self._fetch()
            if any(fail in self.status for fail in fail_status):
                raise exceptions.EasyMakerError(f"{class_name} {action} failed with status: {self.status}.")
        print(f"[AI EasyMaker] {class_name} {action} complete. {self.id_field}: {self.id}")

    @classmethod
    def get_list(cls: type["EasyMakerBaseModel"], **kwargs) -> list["EasyMakerBaseModel"]:
        get_list_method_name = f"get_{to_snake(cls.__name__)}_list"
        get_list_method = getattr(easymaker.easymaker_config.api_sender, get_list_method_name)

        return cls._from_dict_list_to_em_class_list(get_list_method(**kwargs))

    @classmethod
    def get_by_id(cls: type["EasyMakerBaseModel"], id: str) -> "EasyMakerBaseModel":
        get_method_name = f"get_{to_snake(cls.__name__)}_by_id"
        get_method = getattr(easymaker.easymaker_config.api_sender, get_method_name)
        response = get_method(id)
        return cls(**response)

    @classmethod
    def get_by_name(cls: type["EasyMakerBaseModel"], name: str) -> "EasyMakerBaseModel":
        cls_list = cls.get_list(name_list=[name])
        if not cls_list:
            raise ValueError(f"[AI EasyMaker] No {cls.__name__} found with the name {name}.")

        if len(cls_list) > 1:
            raise ValueError(f"[AI EasyMaker] Multiple {cls.__name__} instances found with the name {name}.")

        return cls_list[0]

    @classmethod
    def get_by_id_or_name(cls: type["EasyMakerBaseModel"], id: str | None = None, name: str | None = None) -> "EasyMakerBaseModel":
        if id:
            return cls.get_by_id(id)
        elif name:
            return cls.get_by_name(name)
        else:
            raise ValueError(f"[AI EasyMaker] Either id or name must be provided to get {cls.__name__} instance.")

    def delete(self):
        if self.id:
            self.delete_by_id(self.id)
            self.__init__()
        else:
            print(f"[AI EasyMaker] Failed to delete {self.__class__.__name__}. ID is missing.")

    @classmethod
    def delete_by_id(cls: type["EasyMakerBaseModel"], id: str):
        if id:
            delete_method_name = f"delete_{to_snake(cls.__name__)}_by_id"
            delete_method = getattr(easymaker.easymaker_config.api_sender, delete_method_name)
            delete_method(id)
            print(f"[AI EasyMaker] {cls.__name__} deletion request completed. {cls.__name__} ID : {id}")
        else:
            print(f"[AI EasyMaker] Failed to delete {cls.__name__}. ID is missing.")

    @classmethod
    def _get_group_type(cls: type["EasyMakerBaseModel"]):
        return to_snake(cls.__name__).upper()

    @classmethod
    def get_instance_type_list(cls: type["EasyMakerBaseModel"], model_id: str = None, algorithm_id: str = None) -> list["InstanceType"]:
        instance_type_list = easymaker.easymaker_config.api_sender.get_instance_type_list(
            group_type=cls._get_group_type(),
            model_id=model_id,
            algorithm_id=algorithm_id,
        )
        from easymaker.common.instance_type import InstanceType

        return InstanceType._from_dict_list_to_em_class_list(instance_type_list)
