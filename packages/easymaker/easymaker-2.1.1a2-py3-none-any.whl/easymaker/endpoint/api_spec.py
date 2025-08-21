from enum import Enum


class ApiSpec(Enum):

    auto = "auto"
    kserve_v1 = "kserve_v1"
    kserve_v2 = "kserve_v2"
    openai_completion_v1 = "openai_completion_v1"
    openai_chat_completion_v1 = "openai_chat_completion_v1"

    @classmethod
    def _missing_(cls, value: str):
        value = value.lower()
        for member in cls:
            if member.value == value:
                return member
        return None
