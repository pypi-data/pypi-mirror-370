from typing import TYPE_CHECKING

from easymaker.common.exceptions import EasyMakerError

if TYPE_CHECKING:
    from easymaker.common.base_model.easymaker_base_model import BaseModel


def from_name_to_id(item_list: list[dict | type["BaseModel"]], name: str, cls: type["BaseModel"]) -> str:
    if len(item_list) > 0 and isinstance(item_list[0], dict):
        item_list = cls._from_dict_list_to_em_class_list(item_list)

    for item in item_list:
        if item.name == name:
            return item.id

    raise EasyMakerError(f"Invalid {cls.__name__} name: {name}")


def snake_to_kebab(snake_str: str):
    return snake_str.replace("_", "-")


def snake_to_pascal(snake_str: str):
    # snake_sace -> SnakeCase
    return "".join(word.title() for word in snake_str.split("_"))


def pascal_to_snake(pascal_str: str):
    # SnakeCase -> snake_case
    return "".join(["_" + i.lower() if i.isupper() else i for i in pascal_str]).lstrip("_")
