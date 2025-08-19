from datetime import datetime
from typing import Literal, TypedDict, Union

from typing_extensions import NotRequired

from craft_ai_sdk.shared.types import Log

from ..constants import DEPLOYMENT_EXECUTION_RULES, DEPLOYMENT_MODES, DEPLOYMENT_STATUS
from ..exceptions import SdkException
from ..io import (
    InputSource,
    InputSourceDict,
    OutputDestination,
    _validate_inputs_mapping,
    _validate_outputs_mapping,
)
from ..sdk import BaseCraftAiSdk
from ..shared.logger import log_action, log_func_result
from ..utils import (
    datetime_to_timestamp_in_ms,
    remove_keys_from_dict,
    remove_none_values,
)


class DeploymentInputMapping(InputSourceDict):
    data_type: str
    description: str


class DeploymentOutputMapping(OutputDestination):
    data_type: str
    description: str


class DeploymentPipeline(TypedDict):
    name: str


class DeploymentPod(TypedDict):
    pod_id: str
    status: str


class DeploymentBase(TypedDict):
    name: str
    mode: str
    pipeline: DeploymentPipeline
    inputs_mapping: list[DeploymentInputMapping]
    outputs_mapping: list[DeploymentOutputMapping]
    created_at: str
    created_by: str
    updated_at: str
    updated_by: str
    last_execution_id: str
    is_enabled: bool
    description: str
    status: str
    enable_parallel_executions: bool
    max_parallel_executions_per_pod: int
    pods: NotRequired[list[DeploymentPod]]


class DeploymentEndpoint(DeploymentBase):
    endpoint_token: str
    endpoint_url_path: str
    execution_rule: Literal["endpoint"]


class DeploymentPeriodic(DeploymentBase):
    schedule: str
    human_readable_schedule: str
    execution_rule: Literal["periodic"]


Deployment = Union[DeploymentEndpoint, DeploymentPeriodic]


class DeploymentLog(Log):
    stream: str
    pod_id: str
    type: str


class DeploymentListItem(TypedDict):
    name: str
    pipeline_name: str
    execution_rule: str
    mode: str
    is_enabled: bool
    created_at: str


class DeploymentDeleted(TypedDict):
    name: str
    execution_rule: str


@log_func_result("Deployment creation")
def create_deployment(
    sdk: BaseCraftAiSdk,
    pipeline_name: str,
    deployment_name: str,
    execution_rule: DEPLOYMENT_EXECUTION_RULES,
    mode=DEPLOYMENT_MODES.ELASTIC,
    schedule: Union[str, None] = None,
    endpoint_url_path: Union[str, None] = None,
    inputs_mapping: Union[list[InputSource], None] = None,
    outputs_mapping: Union[list[OutputDestination], None] = None,
    description: Union[str, None] = None,
    enable_parallel_executions: Union[bool, None] = None,
    max_parallel_executions_per_pod: Union[int, None] = None,
    ram_request: Union[str, None] = None,
    gpu_request: Union[int, None] = None,
    wait_for_completion=True,
    timeout_s: Union[int, None] = None,
    execution_timeout_s: Union[int, None] = None,
    endpoint_token: Union[str, None] = None,
):
    """Create a deployment associated with a given pipeline.

    Args:
        pipeline_name (:obj:`str`): Name of the pipeline to deploy.
        deployment_name (:obj:`str`): Name of the deployment.
        execution_rule(:obj:`str`): Execution rule of the deployment. Can
            be ``"endpoint"`` or ``"periodic"``. For convenience, members of the
            enumeration :class:`DEPLOYMENT_EXECUTION_RULES` can be used. If the
            execution rule is ``"periodic"``, ``schedule`` must be provided. If it is
            ``"endpoint"``, see the note below on how to trigger the endpoint.
        mode (:obj:`str`): Mode of the deployment. Can be ``"elastic"`` or
            ``"low_latency"``. Defaults to ``"elastic"``. For convenience, members of
            the enumeration :class:`DEPLOYMENT_MODES` can be used. This defines how
            computing resources are allocated for pipeline executions:

                * ``"elastic"``: Each pipeline execution runs in a new isolated
                  container ("pod"), with its own memory (RAM, VRAM, disk). No
                  variables or files are shared between executions, and the pod is
                  destroyed when the execution ends. This mode is simple to use because
                  it automatically uses computing resources for running executions, and
                  each execution starts from an identical blank state. But it takes time
                  to create a new pod at the beginning of each execution (tens of
                  seconds), and computing resources can become saturated when there are
                  more executions.
                * ``"low_latency"``: All pipeline executions for the same deployment run
                  in a shared container ("pod") with shared memory. The pod is created
                  when the deployment is created, and deleted when the deployment is
                  deleted. Shared memory means that if one execution modifies a global
                  variable or a file, subsequent executions on the same pod will see the
                  modified value. This mode makes it possible for executions to respond
                  quickly (less than 0.5 seconds of overhead) because the pod is already
                  up and running when an execution starts, and it is possible to preload
                  or cache data. But it requires care in the code because of possible
                  interactions between executions. And it requires care in how computing
                  resources are used, because pods use resources continuously even when
                  there is no ongoing execution, and the number of pods does not
                  automatically adapt to the number of executions. During the lifetime
                  of a deployment, a pod may be re-created by the platform for
                  technical reasons (including if it tries to use more memory than
                  available). This mode is not compatible with steps created with a
                  ``container_config.dockerfile_path`` property in :func:`create_step`.

        schedule (:obj:`str`, optional): Schedule of the deployment. Required and
            applicable only if ``execution_rule`` is ``"periodic"``. Must be a valid
            `cron expression <https://www.npmjs.com/package/croner>`.
            The deployment will be executed periodically according to this schedule.
            The schedule must follow this format:
            ``<minute> <hour> <day of month> <month> <day of week>``.
            Note that the schedule is in UTC time zone.
            '*' means all possible values.
            Here are some examples:

                * ``"0 0 * * *"`` will execute the deployment every day at
                  midnight.
                * ``"0 0 5 * *"`` will execute the deployment every 5th day of
                  the month at midnight.

        endpoint_url_path (:obj:`str`, optional): Applicable only if ``execution_rule``
          is ``"endpoint"``. The last part of the URL (address) used to trigger the
          endpoint deployment. See the note below on how to trigger the endpoint. By
          default the value of ``deployment_name`` is used. This can be used to
          customize the URL independently of ``deployment_name``.

        inputs_mapping(:obj:`list` of instances of :class:`InputSource`):
            List of input mappings, to map pipeline inputs to different
            sources (such as constant values, endpoint inputs, or environment
            variables). See :class:`InputSource` for more details.
            For endpoint rules, if an input of the step in the pipeline is not
            explicitly mapped, it will be automatically mapped to an endpoint
            input with the same name.
            For periodic rules, all inputs of the step in the pipeline must be
            explicitly mapped.
        outputs_mapping(:obj:`list` of instances of :class:`OutputDestination`):
            List of output mappings, to map pipeline outputs to different
            destinations. See :class:`OutputDestination` for more details.
            For endpoint rules, if an output of the step in the pipeline is not
            explicitly mapped, it will be automatically mapped to an endpoint
            output with the same name.
            For periodic rules, all outputs of the step in the pipeline must be
            explicitly mapped.
        description (:obj:`str`, optional): Description of the deployment.
        enable_parallel_executions (:obj:`bool`, optional):
            .. _enable_parallel_executions:

            Whether to run several executions
            at the same time in the same pod, if ``mode`` is
            ``"low_latency"``. Not applicable if ``mode`` is ``"elastic"``, where each
            execution always runs in a new pod. This is disabled by default, which means
            that for a deployment with ``"low_latency"`` ``mode``, by default only one
            execution runs at a time on a pod, and other executions are pending while
            waiting for the running one to finish. Enabling this may be useful for
            inference batching on a model that takes much memory, so the model is loaded
            in memory only once and can be used for several inferences at the same time.
            If this is enabled then global variables, GPU memory and disk files are
            shared between multiple executions, so you must be mindful of potential race
            conditions and concurrency issues. For each execution running on a pod, the
            main Python function is run either as an ``asyncio`` coroutine with
            ``await`` if the function was defined with ``async def`` (recommended), or
            in a new thread if the function was defined simply with ``def``. Environment
            variables are updated whenever a new execution starts on the pod. Using some
            libraries with async/threaded methods in your code may cause logs to be
            associated with the wrong running execution (logs are associated with
            executions through Python ``contextvars``).
        max_parallel_executions_per_pod (:obj:`int`, optional):
            .. _max_parallel_executions_per_pod:

            Only applicable if
            ``enable_parallel_executions`` is ``True``. The maximum number of executions
            that can run at the same time on a deployment's pod in ``"low_latency"``
            ``mode`` where ``enable_parallel_executions`` is ``True``: if a greater
            number of executions are requested at the same time, then only
            ``max_parallel_executions_per_pod`` executions will actually be running on
            the pod, and the other ones will be pending until a running execution
            finishes. Defaults to 6.
        ram_request (:obj:`str`, optional): The amount of memory (RAM) requested for
            the deployment in KiB, MiB and GiB. The value must be a string with a number
            followed by a unit, for example "512MiB" or "1GiB". This is only available
            for "low_latency" deployments mode.
        gpu_request (:obj:`int`, optional): The number of GPUs requested for the
            deployment. This is only available for "low_latency" deployments mode.
        wait_for_completion (:obj:`bool`, optional): Whether to wait for the deployment
            to be ready. Defaults to ``True``.
        timeout_s (:obj:`int`): Maximum time (in seconds) to wait for the deployment to
            be ready. Set to None to wait indefinitely. Defaults to None.
            Only applicable if ``wait_for_completion`` is ``True``.
        endpoint_token (:obj:`str`, optional): Applicable only if ``execution_rule``
          is ``"endpoint"``. The token to access the endpoint. If not set, a token
          will be generated. This token is different from the SDK token, you can find it
          in the result of this function as "endpoint_token". It is used as a secret
          to trigger the endpoint.

    Returns:
        :obj:`dict[str, str]`: Created deployment represented as a dict with the
        following keys:

        * ``"name"`` (:obj:`str`): Name of the deployment.
        * ``"mode"`` (:obj:`str`): The deployment mode. Can be
          ``"elastic"`` or ``"low_latency"``.
        * ``"pipeline"`` (:obj:`dict`): Pipeline associated to the deployment
          represented as :obj:`dict` with the following keys:

          * ``"name"`` (:obj:`str`): Name of the pipeline.

        * ``"inputs_mapping"`` (:obj:`list` of :obj:`dict`): List of inputs
          mapping represented as :obj:`dict` with the following keys:

          * ``"pipeline_input_name"`` (:obj:`str`): Name of the step input.
          * ``"data_type"`` (:obj:`str`): Data type of the step input.
          * ``"description"`` (:obj:`str`): Description of the step input.
          * ``"constant_value"`` (:obj:`str`): Constant value of the step input.
            Note that this key is only returned if the step input is mapped to a
            constant value.
          * ``"environment_variable_name"`` (:obj:`str`): Name of the environment
            variable. Note that this key is only returned if the step input is
            mapped to an environment variable.
          * ``"endpoint_input_name"`` (:obj:`str`): Name of the endpoint input.
            Note that this key is only returned if the step input is mapped to an
            endpoint input.
          * ``"is_null"`` (:obj:`bool`): Whether the step input is mapped to null.
            Note that this key is only returned if the step input is mapped to
            null.
          * ``"datastore_path"`` (:obj:`str`): Datastore path of the step input.
            Note that this key is only returned if the step input is mapped to the
            datastore.
          * ``"is_required"`` (:obj:`bool`): Whether the step input is required.
            Note that this key is only returned if the step input is required.
          * ``"default_value"`` (:obj:`str`): Default value of the step input.
            Note that this key is only returned if the step input has a default
            value.

        * ``"outputs_mapping"`` (:obj:`list` of :obj:`dict`): List of outputs
          mapping represented as :obj:`dict` with the following keys:

          * ``"pipeline_output_name"`` (:obj:`str`): Name of the step output.
          * ``"data_type"`` (:obj:`str`): Data type of the step output.
          * ``"description"`` (:obj:`str`): Description of the step output.
          * ``"endpoint_output_name"`` (:obj:`str`): Name of the endpoint output.
            Note that this key is only returned if the step output is mapped to an
            endpoint output.
          * ``"is_null"`` (:obj:`bool`): Whether the step output is mapped to null.
            Note that this key is only returned if the step output is mapped to
            null.
          * ``"datastore_path"`` (:obj:`str`): Datastore path of the step output.
            Note that this key is only returned if the step output is mapped to
            the datastore.

        * ``"endpoint_token"`` (:obj:`str`): Token of the endpoint. Note that this
          key is only returned if the deployment is an endpoint.
        * ``"schedule"`` (:obj:`str`): Schedule of the deployment. Note that this key is
          only returned if the ``execution_rule``of the deployment is ``"periodic"``.
        * ``"human_readable_schedule"`` (:obj:`str`): Human readable schedule of the
          deployment. Note that this key is only returned if the ``execution_rule`` of
          the deployment is ``"periodic"``.
        * ``"created_at"`` (:obj:`str`): Date of creation of the deployment.
        * ``"created_by"`` (:obj:`str`): ID of the user who created the deployment.
        * ``"updated_at"`` (:obj:`str`): Date of last update of the deployment.
        * ``"updated_by"`` (:obj:`str`): ID of the user who last updated the
          deployment.
        * ``"last_execution_id"`` (:obj:`str`): ID of the last execution of the
          deployment.
        * ``"is_enabled"`` (:obj:`bool`): Whether the deployment is enabled.
        * ``"description"`` (:obj:`str`): Description of the deployment.
        * ``"execution_rule"`` (:obj:`str`): Execution rule of the deployment.
        * ``"status"`` (:obj:`str`): The deployment status. Can be
          ``"creation_pending"``, ``"up"``, ``"creation_failed"``, ``"down_retrying"``
          or ``"standby"``.
        * ``"enable_parallel_executions"`` (:obj:`bool`):
          Indicates whether multiple executions can run concurrently within the same
          pod. This key is only returned if the deployment mode is ``"low_latency"``.
          For more detailed information, see
          :ref:`enable_parallel_executions <enable_parallel_executions>` parameter
          of :func:`create_deployment` method.
        * ``"max_parallel_executions_per_pod"`` (:obj:`int`): Maximum number of
          executions that can run at the same time on a deployment's pod in
          ``"low_latency"`` mode. This key is only returned if the deployment mode is
          ``"low_latency"`` and if ``"enable_parallel_executions"`` is ``True``. For
          more detailed information, see
          :ref:`max_parallel_executions_per_pod <max_parallel_executions_per_pod>`
          parameter of :func:`create_deployment` method.
        * ``"pods"`` (:obj:`list` of :obj:`dict`): List of pods associated with the
          low latency deployment. Note that this key is only returned if the
          deployment is in low latency mode. Each pod is represented as :obj:`dict`
          with the following keys:

          * ``pod_id`` (:obj:`str`): ID of the pod.
          * ``status`` (:obj:`str`): Status of the pod.

    Note:
      When ``execution_rule`` is ``"endpoint"``:

        * When the endpoint deployment is created, it creates an HTTP endpoint which can
          be called at ``POST {environment_url}/endpoints/{endpoint_url_path}``. You can
          get `environment_url` with `sdk.base_environment_url`. `endpoint_url_path` is
          the `endpoint_name` if `endpoint_url_path` is not provided.

      | An endpoint token is required to call the HTTP endpoint. This token is different
        from the SDK token, you can find it in the result of this function as
        "endpoint_token". Use it to set the ``"Authorization"`` header as
        ``"EndpointToken {endpoint_token}"``.
      | Input can be passed to the endpoint either:

        * When there is no input file mapped to the endpoint, in the body in JSON with
          the `application/json` content type and with the format

          .. code-block:: json

              {
                "{input_name}": "{input_value}"
              }

        * When a file input is mapped to the endpoint, as a file with a
          `multipart/form-data` content type.

      This will return the output as:

        * When there is no output file, in the body in JSON in the format

          .. code-block:: json

              {
                "output": {
                  "{output_name}": "{output_value}"
                }
              }

        * When a file output is mapped, it will return the file as a response with the
          `application/octet-stream` content type.

      | A successful call will return results with a status code 200 after redirections.
      | If your HTTP client does not follow redirection automatically, redirections are
        indicated by a status code between 300 and 399, and the redirection URL is in
        the `Location` header. Keep calling the redirection URL until you get a
        non-redirection status code.
      | If an endpoint deployment's execution encounters an error, it will return a
        status code between 400 and 599, and an error message in the body at the
        property `message`.
      | Here is an example of a successful call with curl:

      .. code-block:: bash

        curl -L "{environment_url}/endpoints/{endpoint_name}" \\
          -H "Authorization: EndpointToken {endpoint_token}" \\
          -H "Content-Type: application/json; charset=utf-8" \\
          -d @- << EOF
        {"input_string": "value_1", "input_number": 0}
        EOF

        # The response will be:
        # {"output": {"output_string": "returned_value_1", "output_number": 1}}

    """

    if timeout_s is not None and timeout_s <= 0:
        raise ValueError("'timeout_s' must be greater than 0 or None.")

    if mode not in set(DEPLOYMENT_MODES):
        raise ValueError("Invalid 'mode', must be in ['elastic', 'low_latency'].")

    if execution_rule not in set(DEPLOYMENT_EXECUTION_RULES):
        raise ValueError(
            "Invalid 'execution_rule', must be in ['endpoint', 'periodic']."
        )

    url = (
        f"{sdk.base_environment_api_url}/endpoints"
        if execution_rule == "endpoint"
        else f"{sdk.base_environment_api_url}/periodic-deployment"
    )

    data = {
        "pipeline_name": pipeline_name,
        "name": deployment_name,
        "description": description,
        "mode": mode,
        "enable_parallel_executions": enable_parallel_executions,
        "max_parallel_executions_per_pod": max_parallel_executions_per_pod,
        "ram_request": ram_request,
        "gpu_request": gpu_request,
        "execution_timeout_s": execution_timeout_s,
    }

    if schedule is not None:
        if execution_rule != "periodic":
            raise ValueError(
                "'schedule' can only be specified if 'execution_rule' is \
'periodic'."
            )
        else:
            data["schedule"] = schedule

    if endpoint_url_path is not None:
        if execution_rule != "endpoint":
            raise ValueError(
                "'endpoint_url_path' can only be specified if 'execution_rule' is \
'endpoint'."
            )
        else:
            data["endpoint_url_path"] = endpoint_url_path
    if endpoint_token is not None:
        if execution_rule != "endpoint":
            raise ValueError(
                "'endpoint_token' can only be specified if 'execution_rule' is \
'endpoint'."
            )
        else:
            data["endpoint_token"] = endpoint_token

    data["inputs_mapping"] = _validate_inputs_mapping(inputs_mapping)
    data["outputs_mapping"] = _validate_outputs_mapping(outputs_mapping)

    data = remove_none_values(data)

    log_action(
        sdk,
        "Please wait while deployment is being created. This may take a while...",
    )

    sdk._post(url, json=data, get_response=True, allow_redirects=False)

    return get_deployment(
        sdk,
        deployment_name,
        wait_for_completion=wait_for_completion,
        timeout_s=timeout_s,
    )


FINAL_DEPLOYMENT_STATUSES = [
    DEPLOYMENT_STATUS.UP,
    DEPLOYMENT_STATUS.CREATION_FAILED,
    DEPLOYMENT_STATUS.DISABLED,
    DEPLOYMENT_STATUS.STANDBY,
]


def get_deployment(
    sdk: BaseCraftAiSdk,
    deployment_name: str,
    wait_for_completion=False,
    timeout_s: Union[int, None] = None,
) -> Deployment:
    """Get information of a deployment.

    Args:
        deployment_name (:obj:`str`): Name of the deployment.
        wait_for_completion (:obj:`bool`, optional): Whether to wait for the deployment
            to be ready. Defaults to ``False``.
        timeout_s (:obj:`int`, optional): Maximum time (in seconds) to wait for the
            deployment to be ready. Set to None to wait indefinitely. Defaults to None.
            Only applicable if ``wait_for_completion`` is ``True``.

    Returns:
        :obj:`dict`: Deployment information represented as :obj:`dict` with the
        following keys:

        * ``"name"`` (:obj:`str`): Name of the deployment.
        * ``"mode"`` (:obj:`str`): The deployment mode. Can be
          ``"elastic"`` or ``"low_latency"``.
        * ``"pipeline"`` (:obj:`dict`): Pipeline associated to the deployment
          represented as :obj:`dict` with the following keys:

          * ``"name"`` (:obj:`str`): Name of the pipeline.

        * ``"inputs_mapping"`` (:obj:`list` of :obj:`dict`): List of inputs
          mapping represented as :obj:`dict` with the following keys:

          * ``"pipeline_input_name"`` (:obj:`str`): Name of the step input.
          * ``"data_type"`` (:obj:`str`): Data type of the step input.
          * ``"description"`` (:obj:`str`): Description of the step input.
          * ``"constant_value"`` (:obj:`str`): Constant value of the step input.
            Note that this key is only returned if the step input is mapped to a
            constant value.
          * ``"environment_variable_name"`` (:obj:`str`): Name of the environment
            variable. Note that this key is only returned if the step input is
            mapped to an environment variable.
          * ``"endpoint_input_name"`` (:obj:`str`): Name of the endpoint input.
            Note that this key is only returned if the step input is mapped to an
            endpoint input.
          * ``"is_null"`` (:obj:`bool`): Whether the step input is mapped to null.
            Note that this key is only returned if the step input is mapped to
            null.
          * ``"datastore_path"`` (:obj:`str`): Datastore path of the step input.
            Note that this key is only returned if the step input is mapped to the
            datastore.
          * ``"is_required"`` (:obj:`bool`): Whether the step input is required.
            Note that this key is only returned if the step input is required.
          * ``"default_value"`` (:obj:`str`): Default value of the step input.
            Note that this key is only returned if the step input has a default
            value.

        * ``"outputs_mapping"`` (:obj:`list` of :obj:`dict`): List of outputs
          mapping represented as :obj:`dict` with the following keys:

          * ``"pipeline_output_name"`` (:obj:`str`): Name of the step output.
          * ``"data_type"`` (:obj:`str`): Data type of the step output.
          * ``"description"`` (:obj:`str`): Description of the step output.
          * ``"endpoint_output_name"`` (:obj:`str`): Name of the endpoint output.
            Note that this key is only returned if the step output is mapped to an
            endpoint output.
          * ``"is_null"`` (:obj:`bool`): Whether the step output is mapped to null.
            Note that this key is only returned if the step output is mapped to
            null.
          * ``"datastore_path"`` (:obj:`str`): Datastore path of the step output.
            Note that this key is only returned if the step output is mapped to
            the datastore.
        * ``"endpoint_token"`` (:obj:`str`): Token of the deployment. Note that this
          key is only returned if the ``execution_rule`` of the deployment is
          ``"endpoint"``.
        * ``"endpoint_url_path"`` (:obj:`str`): URL path of the deployment.
          Note that this key is only returned if the ``execution_rule`` of the
          deployment is ``"endpoint"``.
        * ``"schedule"`` (:obj:`str`): Schedule of the deployment. Note that this key is
          only returned if the ``execution_rule`` of the deployment is ``"periodic"``.
        * ``"human_readable_schedule"`` (:obj:`str`): Human readable schedule of the
          deployment. Note that this key is only returned if the ``execution_rule`` of
          the deployment is ``"periodic"``.
        * ``"created_at"`` (:obj:`str`): Date of creation of the deployment.
        * ``"created_by"`` (:obj:`str`): ID of the user who created the deployment.
        * ``"updated_at"`` (:obj:`str`): Date of last update of the deployment.
        * ``"updated_by"`` (:obj:`str`): ID of the user who last updated the
          deployment.
        * ``"last_execution_id"`` (:obj:`str`): ID of the last execution of the
          deployment.
        * ``"is_enabled"`` (:obj:`bool`): Whether the deployment is enabled.
        * ``"description"`` (:obj:`str`): Description of the deployment.
        * ``"execution_rule"`` (:obj:`str`): Execution rule of the deployment.
        * ``"status"`` (:obj:`str`): The deployment status. Can be
          ``"creation_pending"``, ``"up"``, ``"creation_failed"``, ``"down_retrying"``
          or ``"standby"``.
        * ``"enable_parallel_executions"`` (:obj:`bool`):
          Indicates whether multiple executions can run concurrently within the same
          pod. This key is only returned if the deployment mode is ``"low_latency"``.
          For more detailed information, see
          :ref:`enable_parallel_executions <enable_parallel_executions>` parameter
          of :func:`create_deployment` method.
        * ``"max_parallel_executions_per_pod"`` (:obj:`int`): Maximum number of
          executions that can run at the same time on a deployment's pod in
          ``"low_latency"`` mode. This key is only returned if the deployment mode is
          ``"low_latency"`` and if ``"enable_parallel_executions"`` is ``True``. For
          more detailed information, see
          :ref:`max_parallel_executions_per_pod <max_parallel_executions_per_pod>`
          parameter of :func:`create_deployment` method.
        * ``"pods"`` (:obj:`list` of :obj:`dict`): List of pods associated with the
          low latency deployment. Note that this key is only returned if the
          deployment is in low latency mode. Each pod is represented as :obj:`dict`
          with the following keys:

          * ``pod_id`` (:obj:`str`): ID of the pod.
          * ``status`` (:obj:`str`): Status of the pod.
    """

    if timeout_s is not None and timeout_s <= 0:
        raise ValueError("'timeout_s' must be greater than 0 or None.")

    deployment = None

    base_url = f"{sdk.base_environment_api_url}/deployments/{deployment_name}"

    if wait_for_completion:
        start_time = sdk._get_time()
        elapsed_time = 0
        deployment_status = DEPLOYMENT_STATUS.CREATION_PENDING
        while deployment_status not in FINAL_DEPLOYMENT_STATUSES and (
            timeout_s is None or elapsed_time < timeout_s
        ):
            deployment = sdk._get(
                f"{base_url}?wait_for_completion=true", allow_redirects=False
            )

            deployment_status = deployment.get("status", None)
            elapsed_time = sdk._get_time() - start_time

        if deployment_status == DEPLOYMENT_STATUS.CREATION_FAILED:
            raise SdkException(
                "The deployment creation failed. Please check the logs for more \
details.",
                name="CreationFailedException",
            )

        if deployment_status not in FINAL_DEPLOYMENT_STATUSES:
            raise SdkException(
                'The deployment was not ready in time. It is still being created but \
this function stopped trying. Please check its status with "get_deployment" with \
wait_for_completion parameter set to false.',
                name="TimeoutException",
            )
    else:
        deployment = sdk._get(base_url)
    if deployment is not None:
        latest_execution = sdk._get(
            f"\
{sdk.base_environment_api_url}/deployments/{deployment_name}/executions/latest"
        )
        deployment["last_execution_id"] = (
            latest_execution.get("execution_id", None)
            if latest_execution is not None
            else None
        )

    return remove_keys_from_dict(deployment, {"is_archived", "id", "pipeline.id"})


@log_func_result("Deployment update")
def update_deployment(
    sdk: BaseCraftAiSdk,
    deployment_name: str,
    is_enabled: Union[bool, None] = None,
    inputs_mapping: Union[list[InputSource], None] = None,
    outputs_mapping: Union[list[OutputDestination], None] = None,
    schedule: Union[str, None] = None,
    wait_for_completion=True,
    timeout_s: Union[int, None] = None,
):
    """Update the specified properties of a deployment. The properties that can be
    updated include enabling/disabling the deployment, updating input/output values,
    and changing the deployment schedule. Only one property can be updated at a time.

    Args:
        deployment_name (:obj:`str`): Name of the deployment to update.
        is_enabled (:obj:`bool`, optional): Whether the deployment should be enabled
          or disabled. Disabling a deployment prevents new executions from being
          triggered. It also frees up computing resources associated to a low-latency
          deployment. Defaults to `None`.
        inputs_mapping(:obj:`list` of instances of :class:`InputSource`):
          List of inputs mapping to update with keys `pipeline_input_name`, and
          `constant_value` or `datastore_path`. The mapping types can not be changed;
          only the values of constant values (`constant_value`) and data store paths
          (`datastore_path`) can be updated. See :class:`InputSource` for more details.
        outputs_mapping(:obj:`list` of instances of :class:`OutputDestination`):
          List of outputs mapping to update with keys `pipeline_output_name` and
          `datastore_path`. The mapping types can not be changed;
          only the values of data store paths (`datastore_path`) can be updated.
          See :class:`OutputDestination` for more details.
        schedule (:obj:`str`, optional): New schedule to be assigned to the periodic
          deployment. Must be a valid CRON expression. Defaults to `None`.

    Returns:
        :obj:`dict`: Deployment information represented as :obj:`dict` as described
        in :func:`get_deployment`.
    """
    if timeout_s is not None and timeout_s <= 0:
        raise ValueError("'timeout_s' must be greater than 0 or None.")

    url = f"{sdk.base_environment_api_url}/deployments/{deployment_name}"

    data = remove_none_values(
        {
            "is_enabled": is_enabled,
            "schedule": schedule,
            "inputs_mapping": _validate_inputs_mapping(inputs_mapping),
            "outputs_mapping": _validate_outputs_mapping(outputs_mapping),
        }
    )

    sdk._patch(url, json=data, allow_redirects=False)

    return get_deployment(
        sdk,
        deployment_name,
        wait_for_completion=wait_for_completion,
        timeout_s=timeout_s,
    )


def get_deployment_logs(
    sdk: BaseCraftAiSdk,
    deployment_name: str,
    from_datetime: Union[datetime, None] = None,
    to_datetime: Union[datetime, None] = None,
    limit: Union[int, None] = None,
) -> list[DeploymentLog]:
    """Get the logs of a deployment with ``"low_latency"`` mode.

    Args:
        deployment_name (:obj:`str`): Name of the deployment.
        from_datetime (:obj:`datetime.time`, optional): Datetime from which the logs
            are collected. If not specified, logs are collected from the beginning.
        to_datetime (:obj:`datetime.time`, optional): Datetime until which the logs
            are collected. If not specified, logs are collected until the end.
        limit (:obj:`int`, optional): Maximum number of logs that are collected.
            If not specified, all logs are collected.

    Returns:
        :obj:`list` of :obj:`dict`: List of logs represented as :obj:`dict` with
        the following keys:

        * ``"timestamp"`` (:obj:`str`): Timestamp of the log.
        * ``"message"`` (:obj:`str`): Message of the log.
        * ``"stream"`` (:obj:`str`): Stream of the log. Typically, ``"stdout"`` or
          ``"stderr"``
        * ``"pod_id"`` (:obj:`str`): ID of the pod.
        * ``"type"`` (:obj:`str`): Type of the log. Can be ``"deployment"``.
    """
    url = f"{sdk.base_environment_api_url}/deployments/{deployment_name}/logs"
    data = {}
    if from_datetime is not None:
        data["from"] = datetime_to_timestamp_in_ms(from_datetime)
    if to_datetime is not None:
        data["to"] = datetime_to_timestamp_in_ms(to_datetime)
    if limit is not None:
        data["limit"] = limit

    log_action(
        sdk,
        "Please wait while logs are being fetched. This may take a while...",
    )
    return sdk._post(url, json=data)


def list_deployments(sdk: BaseCraftAiSdk) -> list[DeploymentListItem]:
    """Get the list of all deployments.

    Returns:
        :obj:`list` of :obj:`dict`: List of deployments represented as :obj:`dict`
        with the following keys:

        * ``"name"`` (:obj:`str`): Name of the deployment.
        * ``"pipeline_name"`` (:obj:`str`): Name of the pipeline associated to
          the deployment.
        * ``"execution_rule"`` (:obj:`str`): Execution rule of the deployment. Can be
          ``"endpoint"``, ``"run"`` or ``"periodic"``.
        * ``"mode"``  (:obj:`str`): Mode of the deployment. Can be
          ``"elastic"`` or ``"low_latency"``.
        * ``"is_enabled"`` (:obj:`bool`): Whether the deployment is enabled.
        * ``"created_at"`` (:obj:`str`): Date of creation of the deployment.
    """
    url = f"{sdk.base_environment_api_url}/deployments"
    return sdk._get(url)


@log_func_result("Deployment deletion")
def delete_deployment(sdk: BaseCraftAiSdk, deployment_name: str) -> DeploymentDeleted:
    """Delete a deployment identified by its name.

    Args:
        deployment_name (:obj:`str`): Name of the deployment.

    Returns:
        :obj:`dict`: Deleted deployment represented as dict with the following
        keys:

        * ``"name"`` (:obj:`str`): Name of the deployment.
        * ``"execution_rule"`` (:obj:`str`): Execution rule of the deployment. Can be
          ``"endpoint"``, ``"run"`` or ``"periodic"``.
    """
    url = f"{sdk.base_environment_api_url}/deployments/{deployment_name}"
    return sdk._delete(url)
