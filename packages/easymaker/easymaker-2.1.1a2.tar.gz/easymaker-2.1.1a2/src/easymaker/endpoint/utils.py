from easymaker.endpoint import ApiSpec


def get_api_spec(data: dict) -> ApiSpec:
    if "instances" in data:
        return ApiSpec.kserve_v1
    elif "inputs" in data:
        return ApiSpec.kserve_v2
    elif "model" in data and "prompt" in data:
        return ApiSpec.openai_completion_v1
    elif "model" in data and "messages" in data:
        return ApiSpec.openai_chat_completion_v1

    return ApiSpec.kserve_v1


def get_inference_url(api_spec: ApiSpec, model_name: str) -> str:
    if api_spec == ApiSpec.kserve_v2:
        return f"/{model_name}/v2/models/{model_name}/infer"
    elif api_spec == ApiSpec.openai_completion_v1:
        return f"/{model_name}/v1/models/completions"
    elif api_spec == ApiSpec.openai_chat_completion_v1:
        return f"/{model_name}/v1/models/chat/completions"

    return f"/{model_name}/v1/models/{model_name}/predict"
