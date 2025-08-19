import requests

from craft_ai_sdk.sdk import BaseCraftAiSdk
from craft_ai_sdk.shared.request_response_handler import handle_http_response


def get_environment_id(sdk: BaseCraftAiSdk):
    health_url = f"{sdk.base_environment_api_url}/health"
    health_result = requests.get(
        health_url,
        headers={
            "craft-ai-client": f"craft-ai-sdk@{sdk._version}",
        },
    )
    handle_http_response(health_result)
    return health_result.json().get("environment_id", {}).get("info", "")
