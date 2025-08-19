from typing import TypedDict

from ..sdk import BaseCraftAiSdk
from ..shared.logger import log_func_result


class EnvironmentVariable(TypedDict):
    name: str
    value: str


@log_func_result("Environment variable definition")
def create_or_update_environment_variable(
    sdk: BaseCraftAiSdk, environment_variable_name: str, environment_variable_value: str
):
    """Create or update an environment variable available for
    all pipelines executions.

    Args:
        environment_variable_name (:obj:`str`):
            Name of the environment variable to create.
        environment_variable_value (:obj:`str`):
            Value of the environment variable to create.

    Returns:
        None
    """
    url = f"{sdk.base_environment_api_url}/environment-variables"
    data = {
        "environment_variables": {
            environment_variable_name: environment_variable_value
        },
    }
    sdk._put(url, json=data)
    return None


def list_environment_variables(sdk: BaseCraftAiSdk) -> list[EnvironmentVariable]:
    """Get a list of all environments variables.

    Returns:
        :obj:`list` of :obj:`dict`: List of environment variable represented as
        :obj:`dict` with the following keys:

          * ``name`` (:obj:`str`): Name of the environment variable.
          * ``value`` (:obj:`str`): Value of the environment variable.
    """
    url = f"{sdk.base_environment_api_url}/environment-variables"
    return sdk._get(url)


@log_func_result("Environment variable deletion")
def delete_environment_variable(
    sdk: BaseCraftAiSdk, environment_variable_name: str
) -> EnvironmentVariable:
    """Delete the specified environment variable

    Args:
        environment_variable_name (:obj:`str`): Name of the environment variable to
            delete.

    Returns:
        :obj:`dict`: Deleted environment variable represented as :obj:`dict` with
        the following keys:

          * ``name`` (:obj:`str`): Name of the environment variable.
          * ``value`` (:obj:`str`): Value of the environment variable.
    """
    url = (
        f"{sdk.base_environment_api_url}"
        f"/environment-variables/{environment_variable_name}"
    )
    return sdk._delete(url)
