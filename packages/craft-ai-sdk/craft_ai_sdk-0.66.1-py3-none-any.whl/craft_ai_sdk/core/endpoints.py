import io
import json
from typing import Any, Literal, TypedDict, Union, overload
from urllib.parse import urlencode

import requests

from craft_ai_sdk.utils.dict_utils import remove_none_values

from ..sdk import BaseCraftAiSdk
from ..shared.authentication import use_authentication
from ..shared.logger import log_func_result
from ..shared.request_response_handler import handle_http_response
from .deployments import get_deployment


def _get_endpoint_url_path(sdk: BaseCraftAiSdk, endpoint_name: str):
    deployment = get_deployment(sdk, endpoint_name)

    if deployment.get("execution_rule", "") != "endpoint":
        raise ValueError(f"Deployment {endpoint_name} is not an endpoint deployment")

    return deployment.get("endpoint_url_path", "")


class EndpointTriggerBase(TypedDict):
    execution_id: str


class EndpointTriggerWithOutputs(EndpointTriggerBase):
    outputs: dict[str, Any]


class EndpointNewToken(TypedDict):
    endpoint_token: str


@overload
def trigger_endpoint(
    sdk: BaseCraftAiSdk,
    endpoint_name: str,
    endpoint_token: Union[str, None] = None,
    inputs: Union[dict[str, Any], None] = None,
    wait_for_completion: Literal[True] = True,
) -> EndpointTriggerWithOutputs: ...


@overload
def trigger_endpoint(
    sdk: BaseCraftAiSdk,
    endpoint_name: str,
    endpoint_token: Union[str, None] = None,
    inputs: Union[dict[str, Any], None] = None,
    wait_for_completion: Literal[False] = False,
) -> EndpointTriggerBase: ...


@log_func_result("Endpoint trigger")
def trigger_endpoint(
    sdk: BaseCraftAiSdk,
    endpoint_name: str,
    endpoint_token: Union[str, None] = None,
    inputs: Union[dict[str, Any], None] = None,
    wait_for_completion=True,
) -> Union[EndpointTriggerWithOutputs, EndpointTriggerBase]:
    """Trigger an endpoint.

    Args:
        endpoint_name (:obj:`str`): Name of the endpoint.
        endpoint_token (:obj:`str`, optional): Token to access endpoint. If not set,
            the SDK token will be used.
        inputs (:obj:`dict`, optional): Dictionary of inputs to pass to the endpoint
            with input names as keys and corresponding values as values.
            For files, the value should be an instance of io.IOBase.
            For json, string, number, boolean and array inputs, the size of all values
            should be less than 0.06MB.
            Defaults to {}.
        wait_for_completion (:obj:`bool`, optional): Automatically call
            `retrieve_endpoint_results` and returns the execution result.
            Defaults to `True`.

    Returns:
        :obj:`dict`: Created pipeline execution represented as :obj:`dict` with the
        following keys:

        * ``"execution_id"`` (:obj:`str`): ID of the execution.
        * ``"outputs"`` (:obj:`dict`): Dictionary of outputs of the pipeline with
          output names as keys and corresponding values as values. Note that this
          key is only returned if ``wait_for_completion`` is `True`.
    """
    if inputs is None:
        inputs = {}

    parameters = {}
    artifacts = {}
    for input_name, input_value in inputs.items():
        if isinstance(input_value, io.IOBase) and input_value.readable():
            artifacts[input_name] = input_value
        else:
            parameters[input_name] = input_value

    data = None
    # When using both files and parameters, parameters should
    # be passed through `data` instead
    if len(parameters) > 0 and len(artifacts) > 0:
        data = {key: json.dumps(value) for key, value in parameters.items()}
        parameters = None

    if endpoint_token is None:
        url = f"{sdk.base_environment_api_url}/deployments/{endpoint_name}/executions"
        do_post = use_authentication(
            lambda sdk, *args, **kwargs: sdk._session.post(*args, **kwargs)
        )
        post_result = do_post(
            sdk,
            url,
            allow_redirects=False,
            json=parameters,
            files=artifacts,
            data=data,
        )

    else:
        endpoint_url_path = _get_endpoint_url_path(sdk, endpoint_name)
        url = f"{sdk.base_environment_url}/endpoints/{endpoint_url_path}"
        post_result = requests.post(
            url,
            headers={
                "Authorization": f"EndpointToken {endpoint_token}",
                "craft-ai-client": f"craft-ai-sdk@{sdk._version}",
            },
            allow_redirects=False,
            json=parameters,
            files=artifacts,
            data=data,
        )
    response = handle_http_response(post_result)
    execution_id = response.get("execution_id", "")
    if wait_for_completion and 200 <= post_result.status_code < 400:
        return retrieve_endpoint_results(
            sdk,
            endpoint_name,
            execution_id,
            endpoint_token,
        )
    return {"execution_id": execution_id}


@log_func_result("Endpoint result retrieval")
def retrieve_endpoint_results(
    sdk: BaseCraftAiSdk,
    endpoint_name: str,
    execution_id: str,
    endpoint_token: Union[str, None] = None,
) -> EndpointTriggerWithOutputs:
    """Get the results of an endpoint execution.

    Args:
        endpoint_name (:obj:`str`): Name of the endpoint.
        execution_id (:obj:`str`): ID of the execution returned by
            `trigger_endpoint`.
        endpoint_token (:obj:`str`, optional): Token to access endpoint. If not set,
            the SDK token will be used.

    Returns:
        :obj:`dict`: Created pipeline execution represented as :obj:`dict` with the
        following keys:

        * ``"outputs"`` (:obj:`dict`): Dictionary of outputs of the pipeline with
          output names as keys and corresponding values as values.
    """

    if endpoint_token is None:
        return sdk.retrieve_pipeline_execution_outputs(execution_id)

    endpoint_url_path = _get_endpoint_url_path(sdk, endpoint_name)

    url = (
        f"{sdk.base_environment_url}"
        f"/endpoints/v1/{endpoint_url_path}/executions/{execution_id}"
    )
    query = urlencode({"token": endpoint_token})
    response = requests.get(f"{url}?{query}")

    handled_response = handle_http_response(response)

    # 500 is returned if the pipeline failed too. In that case, it is not a
    # standard API error
    if response.status_code == 500:
        try:
            return handled_response
        except KeyError:
            return response.json()

    response_data = handle_http_response(response)
    outputs = response_data.get("outputs", {})

    for key, value in outputs.items():
        if isinstance(value, dict) and "value" in value:
            outputs[key] = value["value"]
        if isinstance(value, dict) and "url" in value:
            # If the output is a file, we need to download it
            url = f"{value['url']}?token={endpoint_token}"
            file_response = requests.get(url)
            if file_response.status_code == 200:
                outputs[key] = file_response.content
            else:
                raise ValueError(
                    f"Failed to download file output {key}: {file_response.text}"
                )

    return {
        "outputs": response_data.get("outputs", []),
        "execution_id": execution_id,
    }


def generate_new_endpoint_token(
    sdk: BaseCraftAiSdk, endpoint_name: str, endpoint_token: Union[str, None] = None
) -> EndpointNewToken:
    """Generate a new endpoint token for an endpoint.

    Args:
        endpoint_name (:obj:`str`): Name of the endpoint.
        endpoint_token (:obj:`str`, optional): New endpoint token to set. If not set,
            a new token will be generated.

    Returns:
        :obj:`dict[str, str]`: New endpoint token represented as :obj:`dict` with
        the following keys:

        * ``"endpoint_token"`` (:obj:`str`): New endpoint token.
    """
    url = f"{sdk.base_environment_api_url}/endpoints/{endpoint_name}/generate-new-token"
    return sdk._post(url, data=remove_none_values({"endpoint_token": endpoint_token}))
