import io
import json

from ..exceptions import SdkException
from ..io import (
    INPUT_OUTPUT_TYPES,
    _format_execution_input,
    _format_execution_output,
    _validate_inputs_mapping,
    _validate_outputs_mapping,
)
from ..sdk import BaseCraftAiSdk
from ..shared.authentication import use_authentication
from ..shared.logger import log_action, log_func_result
from ..shared.request_response_handler import handle_http_response
from ..utils import datetime_to_timestamp_in_ms


@log_func_result("Pipeline execution startup")
def run_pipeline(
    sdk: BaseCraftAiSdk,
    pipeline_name,
    inputs=None,
    inputs_mapping=None,
    outputs_mapping=None,
    wait_for_completion=True,
):
    """Run a pipeline.

    Args:
        pipeline_name (:obj:`str`): Name of an existing pipeline.
        inputs (:obj:`dict`, optional): Dictionary of inputs to pass to the pipeline
            with input names as keys and corresponding values as values.
            For files, the value should be the path to the file or a file content
            in an instance of io.IOBase.
            For json, string, number, boolean and array inputs, the size of all values
            should be less than 0.06MB.
            Defaults to None.
        inputs_mapping(:obj:`list` of instances of :class:`InputSource`):
            List of input mappings, to map pipeline inputs to different
            sources (constant_value, environment_variable_name, datastore_path or
            is_null). See :class:`InputSource` for more details.
        outputs_mapping(:obj:`list` of instances of :class:`OutputDestination`):
            List of output mappings, to map pipeline outputs to different
            destinations (is_null or datastore_path). See
            :class:`OutputDestination` for more details.
        wait_for_completion (:obj:`bool`, optional): Wait for the end of the execution
            and returns the execution result.
            Defaults to `True`.

    Returns:
        :obj:`dict`: Pipeline execution outputs represented as a :obj:`dict` with
        the following keys:

        *   ``"execution_id"`` (:obj:`str`): Name of the pipeline execution.
        *   ``"outputs"`` (:obj:`dict`): Pipeline execution outputs with output
            names as keys and corresponding values as values. Note that this
            key is only returned if ``wait_for_completion`` is `True`.
    """
    if inputs is None:
        inputs = {}
    # Retrieve pipeline input types
    pipeline = sdk._get(f"{sdk.base_environment_api_url}/pipelines/{pipeline_name}")
    pipeline_inputs = pipeline["parameters"]["inputs"]
    input_types = {input["name"]: input["data_type"] for input in pipeline_inputs}

    # Get files to upload and data to send
    files = {}
    data = {"json_inputs": {}, "inputs_mapping": []}
    for input_name, input_value in inputs.items():
        if input_types.get(input_name) == INPUT_OUTPUT_TYPES.FILE:
            if isinstance(input_value, str):
                files[input_name] = open(input_value, "rb")
            elif isinstance(input_value, io.IOBase) and input_value.readable():
                files[input_name] = input_value
            else:
                raise SdkException(
                    f"Input {input_name} is a file but \
value is not a string or bytes"
                )
        elif input_types.get(input_name) != INPUT_OUTPUT_TYPES.FILE:
            data["json_inputs"][input_name] = input_value
    data["json_inputs"] = json.dumps(data["json_inputs"])

    _inputs_mapping = _validate_inputs_mapping(inputs_mapping)
    if inputs_mapping is not None:
        data["inputs_mapping"] = json.dumps(_inputs_mapping)

    _outputs_mapping = _validate_outputs_mapping(outputs_mapping)
    if outputs_mapping is not None:
        data["outputs_mapping"] = json.dumps(_outputs_mapping)

    # Execute pipeline
    url = f"{sdk.base_environment_api_url}/pipelines/{pipeline_name}/run"
    post_result = sdk._post(url, data=data, files=files, allow_redirects=False)
    execution_id = post_result["execution_id"]

    for file in files.values():
        file.close()
    log_action(
        sdk,
        f'The pipeline execution may take a while, \
you can check its status and get information on the Executions page of the front-end.\n\
Its execution ID is "{execution_id}".',
    )

    # Wait for pipeline execution to finish
    if wait_for_completion:
        return retrieve_pipeline_execution_outputs(sdk, execution_id)
    return {"execution_id": execution_id}


@log_func_result("Pipeline execution results retrieval")
def retrieve_pipeline_execution_outputs(sdk: BaseCraftAiSdk, execution_id):
    """Get the results of a pipeline execution.

    Args:
        execution_id (:obj:`str`): Name of the pipeline execution.

    Returns:
        :obj:`dict`: Created pipeline execution represented as :obj:`dict` with the
        following keys:

        * ``execution_id`` (str): Name of the pipeline execution.
        * ``"outputs"`` (:obj:`dict`): Dictionary of outputs of the pipeline with
          output names as keys and corresponding values as values.
    """

    url = (
        f"{sdk.base_environment_api_url}"
        f"/executions/{execution_id}/outputs?wait_for_completion=true"
    )

    do_get = use_authentication(
        lambda sdk, *args, **kwargs: sdk._session.get(*args, **kwargs)
    )
    response = do_get(sdk, url, allow_redirects=False)
    while response is None or response.status_code == 307:
        response = do_get(sdk, url, allow_redirects=False)
    response = handle_http_response(response)

    outputs = {}
    for output_item in response["outputs"]:
        value = output_item.get("value", None)
        output_name = output_item["pipeline_output_name"]

        if (
            output_item["data_type"] == INPUT_OUTPUT_TYPES.FILE
            and output_item["mapping_type"] != "is_null"
            and output_item["mapping_type"] != "datastore"
        ):
            value = _retrieve_pipeline_execution_output_value(
                sdk,
                execution_id,
                output_name,
            )

        outputs[output_name] = value
    return {
        "execution_id": execution_id,
        "outputs": outputs,
    }


def _retrieve_pipeline_execution_output_value(
    sdk: BaseCraftAiSdk, execution_id, output_name
):
    url = (
        f"{sdk.base_environment_api_url}"
        f"/executions/{execution_id}/outputs/{output_name}"
    )
    response = sdk._get(url)
    return response


def _retrieve_pipeline_execution_input_value(
    sdk: BaseCraftAiSdk, execution_id, input_name
):
    url = (
        f"{sdk.base_environment_api_url}/executions/{execution_id}/inputs/{input_name}"
    )
    response = sdk._get(url)
    return response


def list_pipeline_executions(sdk: BaseCraftAiSdk, pipeline_name):
    """Get a list of executions for the given pipeline

    Args:
        pipeline_name (:obj:`str`): Name of an existing pipeline.

    Returns:
        :obj:`list`: A list of information on the pipeline execution
        represented as dict with the following keys:

        * ``"execution_id"`` (:obj:`str`): Name of the pipeline execution.
        * ``"status"`` (:obj:`str`): Status of the pipeline execution.
        * ``"created_at"`` (:obj:`str`): Date of creation of the pipeline
          execution.
        * ``"created_by"`` (:obj:`str`): ID of the user who created the pipeline
          execution. In the case of a pipeline run, this is the user who triggered
          the run. In the case of an execution via a deployment, this is the user
          who created the deployment.
        * ``"end_date"`` (:obj:`str`): Date of completion of the pipeline
          execution. Can be `None` if the execution is still running.
        * ``"pipeline_name"`` (:obj:`str`): Name of the pipeline used for the
          execution.
        * ``"deployment_name"`` (:obj:`str`): Name of the deployment used for the
          execution.
    """
    url = f"{sdk.base_environment_api_url}/pipelines/{pipeline_name}/executions"

    return sdk._get(url)


def get_pipeline_execution(sdk: BaseCraftAiSdk, execution_id):
    """Get the status of one pipeline execution identified by its execution_id.

    Args:
        execution_id (:obj:`str`): Name of the pipeline execution.

    Returns:
        :obj:`dict`: Information on the pipeline execution represented as dict
        with the following keys:

        * ``"execution_id"`` (:obj:`str`): Name of the pipeline execution.
        * ``"status"`` (:obj:`str`): Status of the pipeline execution.
        * ``"created_at"`` (:obj:`str`): Date of creation of the pipeline
        * ``"created_by"`` (:obj:`str`): ID of the user who created the pipeline
          execution. In the case of a pipeline run, this is the user who triggered
          the run. In the case of an execution via a deployment, this is the user
          who created the deployment.
        * ``"end_date"`` (:obj:`str`): Date of completion of the pipeline
          execution.
        * ``"pipeline_name"`` (:obj:`str`): Name of the pipeline used for the
          execution.
        * ``"deployment_name"`` (:obj:`str`): Name of the deployment used for the
          execution.
        * ``"steps"`` (:obj:`list` of `obj`): List of the step executions
          represented as :obj:`dict` with the following keys:

          * ``"name"`` (:obj:`str`): Name of the step.
          * ``"status"`` (:obj:`str`): Status of the step.
          * ``"start_date"`` (:obj:`str`): Date of start of the step execution.
          * ``"end_date"`` (:obj:`str`): Date of completion of the step execution.
          * ``"commit_id"`` (:obj:`str`): Id of the commit used to build the
            step.
          * ``"repository_url"`` (:obj:`str`): Url of the repository used to
            build the step.
          * ``"repository_branch"`` (:obj:`str`): Branch of the repository used
            to build the step.
          * ``"requirements_path"`` (:obj:`str`): Path of the requirements.txt file.
          * ``"origin"`` (:obj:`str`): The origin of the step, can be
            ``"git_repository"`` or ``"local"``.
        * ``"inputs"`` (:obj:`list` of :obj:`dict`): List of inputs represented
          as a dict with the following keys:

          * ``"pipeline_input_name"`` (:obj:`str`): Name of the input.
          * ``"data_type`` (:obj:`str`): Data type of the input.
          * ``"source`` (:obj:`str`): Source of type of the input. Can be
            "environment_variable", "datastore", "constant", "is_null" "endpoint"
            or "run".
          * ``"endpoint_input_name"`` (:obj:`str`): Name of the input in the
            endpoint execution if source is "endpoint".
          * ``"constant_value"`` (:obj:`str`): Value of the constant if source is
            "constant".
          * ``"environment_variable_name"`` (:obj:`str`): Name of the environment
            variable if source is "environment_variable".
          * ``"is_null"`` (:obj:`bool`): True if source is "is_null".
          * ``"value"``: Value of the input.

        * ``"outputs"`` (:obj:`list` of :obj:`dict`): List of outputs represented
          as a dict with the following keys:

          * ``"pipeline_output_name"`` (:obj:`str`): Name of the output.
          * ``"data_type`` (:obj:`str`): Data type of the output.
          * ``"destination`` (:obj:`str`): Destination of type of the output. Can be
            "datastore", "is_null" "endpoint" or "run".
          * ``"endpoint_output_name"`` (:obj:`str`): Name of the output in the
            endpoint execution if destination is "endpoint".
          * ``"is_null"`` (:obj:`bool`): True if destination is "is_null".
          * ``"value"``: Value of the output.
    """

    url = f"{sdk.base_environment_api_url}/executions/{execution_id}"

    execution = sdk._get(url)
    inputs_list = []
    for input_item in execution["inputs"]:
        value = input_item.get("value", None)
        if (
            input_item["data_type"] == INPUT_OUTPUT_TYPES.FILE
            and input_item["mapping_type"] != "is_null"
            and input_item["mapping_type"] != "datastore"
        ):
            value = _retrieve_pipeline_execution_input_value(
                sdk,
                execution_id,
                input_item["pipeline_input_name"],
            )

        inputs_list.append(
            _format_execution_input(
                input_item["pipeline_input_name"], {**input_item, "value": value}
            )
        )

    outputs_list = []
    for output_item in execution["outputs"]:
        value = output_item.get("value", None)
        if (
            output_item["data_type"] == INPUT_OUTPUT_TYPES.FILE
            and output_item["mapping_type"] != "is_null"
        ):
            value = _retrieve_pipeline_execution_output_value(
                sdk,
                execution_id,
                output_item["pipeline_output_name"],
            )

        outputs_list.append(
            _format_execution_output(
                output_item["pipeline_output_name"], {**output_item, "value": value}
            )
        )
    execution["inputs"] = inputs_list
    execution["outputs"] = outputs_list
    return execution


def get_pipeline_execution_output(sdk: BaseCraftAiSdk, execution_id, output_name):
    """Get the output value of an executed pipeline identified by its execution_id.

    Args:
        execution_id (:obj:`str`): ID of the pipeline execution.
        output_name (:obj:`str`): Name of the output.

    Returns:
        :obj:`dict`: Information on the output represented as a dict with the
        following keys :

        * ``"pipeline_output_name"`` (:obj:`str`): Name of the output.
        * ``"data_type`` (:obj:`str`): Data type of the output.
        * ``"destination`` (:obj:`str`): Destination of type of the output. Can be
          "datastore", "is_null" "endpoint" or "run".
        * ``"endpoint_output_name"`` (:obj:`str`): Name of the output in the
          endpoint execution if destination is "endpoint".
        * ``"is_null"`` (:obj:`bool`): True if destination is "is_null".
        * ``"value"``: Value of the output.
    """
    exec_url = f"{sdk.base_environment_api_url}/executions/{execution_id}\
?include_io_values=false"
    execution_information = sdk._get(exec_url)

    output = [
        output_item
        for output_item in execution_information["outputs"]
        if output_item["pipeline_output_name"] == output_name
    ]

    if len(output) == 0:
        raise SdkException(
            f"Cannot find output {output_name} for execution {execution_id}"
        )

    output_value = _retrieve_pipeline_execution_output_value(
        sdk,
        execution_id,
        output_name,
    )

    return _format_execution_output(output_name, {**output[0], "value": output_value})


def get_pipeline_execution_input(sdk: BaseCraftAiSdk, execution_id, input_name):
    """Get the input value of an executed pipeline identified by its execution_id.

    Args:
        execution_id (:obj:`str`): ID of the pipeline execution.
        input_name (:obj:`str`): Name of the input.

    Returns:
        :obj:`dict`: Information on the input represented as a dict with the
        following keys :

        * ``"pipeline_input_name"`` (:obj:`str`): Name of the input.
        * ``"data_type`` (:obj:`str`): Data type of the input.
        * ``"source`` (:obj:`str`): Source of type of the input. Can be
          "environment_variable", "datastore", "constant", "is_null" "endpoint"
          or "run".
        * ``"endpoint_input_name"`` (:obj:`str`): Name of the input in the
          endpoint execution if source is "endpoint".
        * ``"constant_value"`` (:obj:`str`): Value of the constant if source is
          "constant".
        * ``"environment_variable_name"`` (:obj:`str`): Name of the environment
          variable if source is "environment_variable".
        * ``"is_null"`` (:obj:`bool`): True if source is "is_null".
        * ``"value"``: Value of the input.
    """

    exec_url = f"{sdk.base_environment_api_url}/executions/{execution_id}\
?include_io_values=false"
    execution_information = sdk._get(exec_url)

    input = [
        input_item
        for input_item in execution_information["inputs"]
        if input_item["pipeline_input_name"] == input_name
    ]

    if len(input) == 0:
        raise SdkException(
            f"Cannot find input {input_name} for execution {execution_id}"
        )

    input_value = _retrieve_pipeline_execution_input_value(
        sdk,
        execution_id,
        input_name,
    )

    return _format_execution_input(input_name, {**input[0], "value": input_value})


def get_pipeline_execution_logs(
    sdk: BaseCraftAiSdk,
    execution_id,
    from_datetime=None,
    to_datetime=None,
    limit=None,
):
    """Get the logs of an executed pipeline identified by its name.

    Args:
        execution_id (:obj:`str`): ID of the pipeline execution.
        from_datetime (:obj:`datetime.time`, optional): Datetime from which the logs
            are collected.
        to_datetime (:obj:`datetime.time`, optional): Datetime until which the logs
            are collected.
        limit (:obj:`int`, optional): Maximum number of logs that are collected.

    Returns:
        :obj:`list` of :obj:`dict`: List of collected logs represented as dict with
        the following keys:

        * ``"timestamp"`` (:obj:`str`): Timestamp of the log.
        * ``"message"`` (:obj:`str`): Log message.
    """
    url = f"{sdk.base_environment_api_url}/executions/{execution_id}/logs"

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
    logs_by_steps = sdk._post(url, json=data)

    if len(logs_by_steps) == 0:
        return []

    return logs_by_steps[0]


def delete_pipeline_execution(sdk: BaseCraftAiSdk, execution_id):
    """Delete one pipeline execution identified by its execution_id.

    Args:
        execution_id (:obj:`str`): Name of the pipeline execution.

    Returns:
        :obj:`dict`: Deleted pipeline execution represented as dict with
        the following keys:

        * ``"execution_id"`` (:obj:`str`): Name of the pipeline execution.
    """
    url = f"{sdk.base_environment_api_url}/executions/{execution_id}"
    return sdk._delete(url)
