import functools
import sys
from typing import Callable, Union

from craft_ai_sdk.exceptions import SdkException


def log_action(sdk, message: str, should_log: Union[bool, Callable[[], bool]] = True):
    if sdk.verbose_log and (should_log() if callable(should_log) else should_log):
        print(message, file=sys.stderr)  # noqa: T201


def log_func_result(message: str, should_log: Union[bool, Callable[[], bool]] = True):
    def decorator_log_func_result(action_func):
        @functools.wraps(action_func)
        def wrapper_log_func_result(*args, **kwargs):
            sdk = args[0]
            try:
                res = action_func(*args, **kwargs)
                log_action(sdk, "{:s} succeeded".format(message), should_log)
                return res
            except SdkException as error:
                log_action(
                    sdk,
                    "{:s} failed ! {}".format(message, error),
                    should_log,
                )
                raise error
            except Exception as error:
                log_action(
                    sdk,
                    "{:s} failed for unexpected reason ! {}".format(message, error),
                    should_log,
                )
                raise error

        return wrapper_log_func_result

    return decorator_log_func_result
