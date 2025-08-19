from craft_ai_sdk.exceptions import SdkException


def wait_create_until_ready(sdk, name, get_func, timeout_s, start_time, get_log_func):
    elapsed_time = sdk._get_time() - start_time
    status = "creation_pending"
    while status == "creation_pending" and (
        timeout_s is None or elapsed_time < timeout_s
    ):
        created_obj = get_func(sdk, name)
        status = created_obj.get("creation_info", {}).get("status", None)
        elapsed_time = sdk._get_time() - start_time

    if status == "creation_failed":
        raise SdkException(
            f'The creation of "{name}" has failed. You can check the logs with '
            f'the "{get_log_func.__name__}" function.',
            name="CreationFailed",
        )
    if status != "ready":
        raise SdkException(
            f'The creation of "{name}" was not ready in time. It is still being '
            "created but this function stopped trying. Please check its status with "
            f'"{get_func.__name__}".',
            name="TimeoutException",
        )
    return created_obj
