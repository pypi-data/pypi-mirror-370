import os
import warnings
from typing import TypedDict, Union, cast

import requests
from typing_extensions import NotRequired

from craft_ai_sdk.io import Input, Output
from craft_ai_sdk.shared.types import Log

from ..sdk import BaseCraftAiSdk
from ..shared.helpers import wait_create_until_ready
from ..shared.logger import log_action, log_func_result
from ..shared.request_response_handler import handle_data_store_response
from ..utils import datetime_to_timestamp_in_ms, multipartify, remove_keys_from_dict
from .steps import (
    ContainerConfig,
    StepCreationInfo,
    _prepare_create_step_data,
    _prepare_create_step_files,
    _validate_create_step_parameters,
)


class PipelineParameter(TypedDict):
    step_name: NotRequired[str]
    pipeline_name: str
    function_path: str
    function_name: str
    description: str
    inputs: list[Input]
    outputs: list[Output]
    container_config: ContainerConfig


class PipelineTemplateReference(TypedDict):
    id: str
    name: str
    version: str
    display_name: str
    description: str
    hosting_type: str
    model_family: str


class PipelineCreationInfo(StepCreationInfo):
    last_execution_id: str
    pipeline_template: Union[PipelineTemplateReference, None]


class Pipeline(TypedDict):
    parameters: PipelineParameter
    creation_info: PipelineCreationInfo


class PipelineListItem(TypedDict):
    pipeline_name: str
    created_at: str
    status: str


class PipelineDeletedPipeline(TypedDict):
    name: str


class PipelineDeletedDeployment(TypedDict):
    name: str
    execution_rule: str


class PipelineDeleted(TypedDict):
    pipeline: PipelineDeletedPipeline
    deployments: list[PipelineDeletedDeployment]


def _create_pipeline_with_step(
    sdk: BaseCraftAiSdk, pipeline_name: str, step_name: str
) -> Pipeline:
    url = f"{sdk.base_environment_api_url}/pipelines"
    body = {
        "pipeline_name": pipeline_name,
        "step_names": [step_name],
    }

    return remove_keys_from_dict(
        sdk._post(url, json=body), {"is_archived", "pipeline_id"}
    )


@log_func_result("Pipeline creation")
def create_pipeline(
    sdk: BaseCraftAiSdk,
    pipeline_name: str,
    function_path: Union[str, None] = None,
    function_name: Union[str, None] = None,
    description: Union[str, None] = None,
    container_config: Union[ContainerConfig, None] = None,
    inputs: Union[list[Input], None] = None,
    outputs: Union[list[Output], None] = None,
    wait_for_completion=True,
    timeout_s: Union[int, None] = None,
    **kwargs,
):
    """Create a pipeline from a function located on a remote repository or locally.

    Use :obj:`CREATION_PARAMETER_VALUE` to explicitly set a value to null or fall back
    on project information.
    You can also use :obj:`container_config.included_folders` to specify the files and
    folders required for the pipeline execution. This is useful if your repository
    contains large files that are not required for the pipeline execution, such as
    documentation or test files. Indeed there is a maximum limit of 5MB for the
    total size of the content specified with :obj:`included_folders`.

    Args:
        pipeline_name (:obj:`str`): Name of the pipeline to be created.
        function_path (:obj:`str`, optional): Path to the file that contains the
            function. This parameter is required if parameter "dockerfile_path"
            is not specified.
        function_name (:obj:`str`, optional): Name of the function in that file.
            This parameter is required if parameter "dockerfile_path" is not
            specified.
        description (:obj:`str`, optional): Description. Defaults to None.
        container_config (:obj:`dict[str, str]`, optional): Some pipeline configuration,
            with the following optional keys:

            * ``"language"`` (:obj:`str`): Language and version used for the pipeline.
              Defaults to falling back on project information. The accepted formats
              are "python:3.X-slim", where "3.X" is a supported version of Python,
              and "python-cuda:3.X-Y.Z" for GPU environments, where "Y.Z" is a
              supported version of CUDA. The list of supported versions is available
              on the official documentation website at
              https://mlops-platform-documentation.craft.ai.
            * ``"repository_url"`` (:obj:`str`): Remote repository url.
              Defaults to falling back on project information.
            * ``"repository_branch"`` (:obj:`str`): Branch name. Defaults to falling
              back on project information.
            * ``"repository_deploy_key"`` (:obj:`str`): Private SSH key of the
              repository.
              Defaults to falling back on project information, can be set to null.
              The key should retain the header/footer beacon with : "BEGIN/END RSA
              PRIVATE KEY".
            * ``"requirements_path"`` (:obj:`str`): Path to the requirements.txt
              file. Environment variables created through
              :func:`create_or_update_environment_variable` can be used
              in requirements.txt, as in ``"${ENV_VAR}"``.
              Defaults to falling back on project information, can be set to null.
            * ``"included_folders"`` (:obj:`list[str]`): List of folders and files
              in the repository required for the pipeline execution.
              Defaults to falling back on project information, can be set to null.
              Total size of included_folders must be less than 5MB.
            * ``"system_dependencies"`` (:obj:`list[str]`): List of system
              dependencies.
              Defaults to falling back on project information, can be set to null.
            * ``"dockerfile_path"`` (:obj:`str`): Path to the Dockerfile. This
              parameter should only be used as a last resort and for advanced use.
              When specified, the following parameters should be set to null:
              ``"function_path"``, ``"function_name"``, ``"language"``,
              ``"requirements_path"`` and ``"system_dependencies"``.
            * ``"local_folder`` (:obj:`str`): Path to local folder where the pipeline is
              stored.

        inputs(`list` of instances of :class:`Input`): List of inputs. Each
            parameter of the pipeline function should be specified as an instance of
            :class:`Input` via this parameter `inputs`.
            During the execution of the pipeline, the value of the inputs would be
            passed as function arguments.
        outputs(`list` of instances of :class:`Output`): List of the pipeline
            outputs. For the pipeline to have outputs, the function should return a
            :obj:`dict` with the name of the output as keys and the value of the
            output as values. Each output should be specified as an instance
            of :class:`Output` via this parameter `outputs`.
        wait_for_completion (:obj:`bool`, optional): Whether to wait for the pipeline
            to be created. Defaults to ``True``.
        timeout_s (:obj:`int`): Maximum time (in seconds) to wait for the pipeline to
            be created. Set to None to wait indefinitely. Defaults to None.
            Only applicable if ``wait_for_completion`` is ``True``.

    Returns:
        :obj:`dict`: Created pipeline represented as :obj:`dict` with the following
        keys:

        * ``"parameters"`` (:obj:`dict`): Information used to create the pipeline with
          the following keys:

          * ``"pipeline_name"`` (:obj:`str`): Name of the pipeline.
          * ``"function_path"`` (:obj:`str`): Path to the file that contains the
            function.
          * ``"function_name"`` (:obj:`str`): Name of the function in that file.
          * ``"description"`` (:obj:`str`): Description.
          * ``"inputs"`` (:obj:`list` of :obj:`dict`): List of inputs represented
            as a :obj:`dict` with the following keys:

            * ``"name"`` (:obj:`str`): Input name.
            * ``"data_type"`` (:obj:`str`): Input data type.
            * ``"is_required"`` (:obj:`bool`): Whether the input is required.
            * ``"default_value"`` (:obj:`str`): Input default value.

          * ``"outputs"`` (:obj:`list` of :obj:`dict`): List of outputs
            represented as a :obj:`dict` with the following keys:

            * ``"name"`` (:obj:`str`): Output name.
            * ``"data_type"`` (:obj:`str`): Output data type.
            * ``"description"`` (:obj:`str`): Output description.

          * ``"container_config"`` (:obj:`dict[str, str]`): Some pipeline
            configuration, with the following optional keys:

            * ``"language"`` (:obj:`str`): Language and version used for the pipeline.
              The accepted formats are "python:3.X-slim", where "3.X" is a supported
              version of Python, and "python-cuda:3.X-Y.Z" for GPU environments,
              where "Y.Z" is a supported version of CUDA. The list of supported
              versions is available on the official documentation website at
              https://mlops-platform-documentation.craft.ai.
            * ``"repository_url"`` (:obj:`str`): Remote repository url.
            * ``"repository_branch"`` (:obj:`str`): Branch name.
            * ``"included_folders"`` (:obj:`list[str]`): List of folders and
              files in the repository required for the pipeline execution.
            * ``"system_dependencies"`` (:obj:`list[str]`): List of system
              dependencies.
            * ``"dockerfile_path"`` (:obj:`str`): Path to the Dockerfile.
            * ``"requirements_path"`` (:obj:`str`): Path to the requirements.txt
              file.

        * ``"creation_info"`` (:obj:`dict`): Information about the pipeline creation:

          * ``"created_at"`` (:obj:`str`): The creation date in ISO format.
          * ``"commit_id"`` (:obj:`str`): The commit id on which the pipeline was
            built.
          * ``"status"`` (:obj:`str`): either ``"creation_pending"`` or ``"ready"``.
          * ``"origin"`` (:obj:`str`): The origin of the pipeline, can be
            ``"git_repository"`` or ``"local"``.
          * ``"last_execution_id"`` (:obj:`str`): The id of the last execution of
            the pipeline.
    """
    # For backward compatibility, a pipeline can be created with a single step:
    args_are_none = all(
        arg is None
        for arg in [
            function_name,
            description,
            container_config,
            inputs,
            outputs,
            timeout_s,
        ]
    )
    # with create_pipeline(:pipeline_name:, :step_name:),
    if args_are_none and function_path is not None and not kwargs:
        warnings.warn(
            "Providing the step name as a positional argument is deprecated and will "
            "be removed in a future version. Please use the step_name keyword argument instead.",  # noqa: E501
            FutureWarning,
            stacklevel=2,
        )
        return _create_pipeline_with_step(sdk, pipeline_name, function_path)

    # or with create_pipeline(:pipeline_name:, step_name=:step_name:).
    if "step_name" in kwargs:
        if not args_are_none or function_path is not None or len(kwargs) > 1:
            raise ValueError(
                "create_pipeline() got unexpected arguments. When specifying the"
                "'step_name' keyword argument, no other argument than 'pipeline_name'"
                "should be provided."
            )

        return _create_pipeline_with_step(sdk, pipeline_name, kwargs["step_name"])

    if len(kwargs) != 0:
        raise ValueError(
            f"create_pipeline() got unexpected keyword arguments: {kwargs}"
        )

    # Otherwise, the pipeline is created with a "hidden" step
    container_config = (
        cast(ContainerConfig, {})
        if container_config is None
        else cast(ContainerConfig, container_config.copy())
    )
    _validate_create_step_parameters(inputs, outputs, timeout_s)

    url = f"{sdk.base_environment_api_url}/pipelines"
    data = _prepare_create_step_data(
        function_path,
        function_name,
        description,
        container_config,
        inputs,
        outputs,
        pipeline_name=pipeline_name,
    )
    files = _prepare_create_step_files(sdk, container_config, data, function_path)

    log_action(
        sdk,
        f'Please wait while pipeline "{pipeline_name}" is being created. '
        "This may take a while...",
    )

    sdk._post(url, data=multipartify(data), files=files, allow_redirects=False)

    return get_pipeline(sdk, pipeline_name, wait_for_completion, timeout_s)


def get_pipeline(
    sdk: BaseCraftAiSdk, pipeline_name, wait_for_completion=False, timeout_s=None
) -> Pipeline:
    """Get a single pipeline if it exists.

    Args:
        pipeline_name (:obj:`str`): Name of the pipeline to get.
        wait_for_completion (:obj:`bool`, optional): Whether to wait for the pipeline
            to be created. Defaults to ``False``.
        timeout_s (:obj:`int`): Maximum time (in seconds) to wait for the pipeline to
            be created. Set to None to wait indefinitely. Defaults to None.
            Only applicable if ``wait_for_completion`` is ``True``.

    Returns:
        None if the pipeline does not exist, otherwise pipeline information, with
        the following keys:

        * ``"parameters"`` (:obj:`dict`): Information used to create the pipeline with
          the following keys:

          * ``"pipeline_name"`` (:obj:`str`): Name of the pipeline.
          * ``"function_path"`` (:obj:`str`): Path to the file that contains the
            function.
          * ``"function_name"`` (:obj:`str`): Name of the function in that file.
          * ``"description"`` (:obj:`str`): Description.
          * ``"inputs"`` (:obj:`list` of :obj:`dict`): List of inputs represented
            as a :obj:`dict` with the following keys:

            * ``"name"`` (:obj:`str`): Input name.
            * ``"data_type"`` (:obj:`str`): Input data type.
            * ``"is_required"`` (:obj:`bool`): Whether the input is required.
            * ``"default_value"`` (:obj:`str`): Input default value.

          * ``"outputs"`` (:obj:`list` of :obj:`dict`): List of outputs
            represented as a :obj:`dict` with the following keys:

            * ``"name"`` (:obj:`str`): Output name.
            * ``"data_type"`` (:obj:`str`): Output data type.
            * ``"description"`` (:obj:`str`): Output description.

          * ``"container_config"`` (:obj:`dict[str, str]`): Some pipeline
            configuration, with the following optional keys:

            * ``"language"`` (:obj:`str`): Language and version used for the pipeline.
              The accepted formats are "python:3.X-slim", where "3.X" is a supported
              version of Python, and "python-cuda:3.X-Y.Z" for GPU environments,
              where "Y.Z" is a supported version of CUDA. The list of supported
              versions is available on the official documentation website at
              https://mlops-platform-documentation.craft.ai.
            * ``"repository_url"`` (:obj:`str`): Remote repository url.
            * ``"repository_branch"`` (:obj:`str`): Branch name.
            * ``"included_folders"`` (:obj:`list[str]`): List of folders and
              files in the repository required for the pipeline execution.
            * ``"system_dependencies"`` (:obj:`list[str]`): List of system
              dependencies.
            * ``"dockerfile_path"`` (:obj:`str`): Path to the Dockerfile.
            * ``"requirements_path"`` (:obj:`str`): Path to the requirements.txt
              file.

        * ``"creation_info"`` (:obj:`dict`): Information about the pipeline creation:

          * ``"created_at"`` (:obj:`str`): The creation date in ISO format.
          * ``"created_by"`` (:obj:`str`): The user who created the pipeline.
          * ``"commit_id"`` (:obj:`str`): The commit id on which the pipeline was
            built.
          * ``"status"`` (:obj:`str`): either ``"creation_pending"`` or ``"ready"``.
          * ``"origin"`` (:obj:`str`): The origin of the pipeline, can be
            ``"git_repository"`` or ``"local"``.
          * ``"last_execution_id"`` (:obj:`str`): The id of the last execution of
            the pipeline.
    """
    base_url = f"{sdk.base_environment_api_url}/pipelines/{pipeline_name}"
    if wait_for_completion:
        pipeline = wait_create_until_ready(
            sdk,
            pipeline_name,
            lambda sdk, _: sdk._get(
                f"{base_url}?wait_for_completion=true", allow_redirects=False
            ),
            timeout_s,
            sdk._get_time(),
            get_pipeline_logs,
        )
    else:
        pipeline = sdk._get(base_url)

    latest_execution = sdk._get(
        f"{sdk.base_environment_api_url}/pipelines/{pipeline_name}/executions/latest"
    )
    pipeline["creation_info"]["last_execution_id"] = (
        latest_execution.get("execution_id", None)
        if latest_execution is not None
        else None
    )
    return remove_keys_from_dict(
        pipeline, {"creation_info.is_archived", "creation_info.id"}
    )


def list_pipelines(sdk: BaseCraftAiSdk) -> list[PipelineListItem]:
    """Get the list of all pipelines.

    Returns:
        :obj:`list` of :obj:`dict`: List of pipelines represented as :obj:`dict`
        with the following keys:

        * ``"pipeline_name"`` (:obj:`str`): Name of the pipeline.
        * ``"created_at"`` (:obj:`str`): Pipeline date of creation.
        * ``"status"`` (:obj:`str`): Status of the pipeline.
    """
    url = f"{sdk.base_environment_api_url}/pipelines"

    return sdk._get(url)


@log_func_result("Pipeline deletion")
def delete_pipeline(
    sdk: BaseCraftAiSdk, pipeline_name: str, force_deployments_deletion=False
) -> PipelineDeleted:
    """Delete a pipeline identified by its name.

    Args:
        pipeline_name (:obj:`str`): Name of the pipeline.
        force_deployments_deletion (:obj:`bool`, optional): if True the associated
            endpoints will be deleted too. Defaults to False.

    Returns:
        :obj:`dict`: The deleted pipeline and its associated deleted deployments
        represented as a :obj:`dict` with the following keys:

            * ``"pipeline"`` (:obj:`dict`): Deleted pipeline represented as
              :obj:`dict` with the following keys:

              * ``"name"`` (:obj:`str`): Name of the deleted pipeline.

            * ``"deployments"`` (:obj:`list`): List of deleted deployments
              represented as :obj:`dict` with the following keys:

              * ``"name"`` (:obj:`str`): Name of the deleted deployments.
              * ``"execution_rule"`` (:obj:`str`): Execution rule of the deleted
                deployments.
    """
    url = f"{sdk.base_environment_api_url}/pipelines/{pipeline_name}"
    params = {
        "force_deployments_deletion": force_deployments_deletion,
    }
    return sdk._delete(url, params=params)


def _get_download_presigned_url(sdk: BaseCraftAiSdk, pipeline_name: str) -> str:
    url = f"{sdk.base_environment_api_url}/pipelines/{pipeline_name}/download"
    presigned_url = sdk._get(url)["signed_url"]
    return presigned_url


@log_func_result("pipeline download")
def download_pipeline_local_folder(
    sdk: BaseCraftAiSdk, pipeline_name: str, folder: str
):
    """Download a pipeline's local folder as a `.tgz` archive.

    Only available if the pipeline's ``origin`` is ``"local_folder"``. This archive
    contains the files that were in the ``local_folder`` parameter provided during
    pipeline creation, and that were included based on the pipeline's
    ``container_config`` property.

    Args:
        pipeline_name (:obj:`str`): Name of the pipline to be downloaded.
        folder (:obj:`str`): Path to the folder where the file will be saved.

    Returns:
        None
    """
    presigned_url = _get_download_presigned_url(sdk, pipeline_name)
    resp = requests.get(presigned_url)
    object_content = handle_data_store_response(resp)

    if isinstance(folder, str):
        path = os.path.join(os.path.abspath(folder), f"{pipeline_name}.tgz")
        with open(path, "wb") as f:
            f.write(object_content)
    else:
        raise ValueError("'folder' must be a string")


@log_func_result("Pipeline logs")
def get_pipeline_logs(
    sdk: BaseCraftAiSdk,
    pipeline_name,
    from_datetime=None,
    to_datetime=None,
    limit=None,
) -> list[Log]:
    """Get the logs of a pipeline.

    Args:
        pipeline_name (:obj:`str`): Name of the pipeline.
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
    url = f"{sdk.base_environment_api_url}/pipelines/{pipeline_name}/logs"

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
    logs = sdk._post(url, json=data)

    return logs
