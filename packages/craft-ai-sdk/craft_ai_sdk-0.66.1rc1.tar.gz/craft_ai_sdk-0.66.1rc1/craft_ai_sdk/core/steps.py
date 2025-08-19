import io
import os
import tarfile
from datetime import datetime
from typing import TypedDict, TypeVar, Union, cast

import requests
from typing_extensions import NotRequired

from craft_ai_sdk.shared.types import Log

from ..constants import CREATION_PARAMETER_VALUE
from ..io import Input, Output
from ..sdk import BaseCraftAiSdk
from ..shared.helpers import wait_create_until_ready
from ..shared.logger import log_action, log_func_result
from ..shared.request_response_handler import handle_data_store_response
from ..utils import datetime_to_timestamp_in_ms, multipartify, remove_none_values

T = TypeVar("T")

CreationParameter = Union[T, CREATION_PARAMETER_VALUE, None]


class ContainerConfigBase(TypedDict):
    language: NotRequired[CreationParameter[str]]
    requirements_path: NotRequired[CreationParameter[str]]
    included_folders: NotRequired[CreationParameter[list[str]]]
    system_dependencies: NotRequired[CreationParameter[list[str]]]
    dockerfile_path: NotRequired[CreationParameter[str]]


class ContainerConfigWithGit(ContainerConfigBase):
    repository_url: NotRequired[CreationParameter[str]]
    repository_branch: NotRequired[CreationParameter[str]]
    repository_deploy_key: NotRequired[CreationParameter[str]]


class ContainerConfigWithLocalFolder(ContainerConfigBase):
    local_folder: str


ContainerConfig = Union[ContainerConfigWithGit, ContainerConfigWithLocalFolder]


class StepParameter(TypedDict):
    step_name: str
    function_path: str
    function_name: str
    description: str
    inputs: list[Input]
    outputs: list[Output]
    container_config: ContainerConfig
    "This type is actually too large, you'll not get any CREATION_PARAMETER_VALUE here"


class StepCreationInfo(TypedDict):
    created_at: str
    created_by: str
    commit_id: str
    status: str
    origin: str


class Step(TypedDict):
    parameters: StepParameter
    creation_info: StepCreationInfo


class StepListItem(TypedDict):
    step_name: str
    status: str
    created_at: str


class StepDeleted(TypedDict):
    step_name: str


def _compress_folder_to_memory(local_folder: str, include: list[str]):
    tar_data = io.BytesIO()
    # Remove leading slashes from the paths
    include = [item.lstrip("/") for item in include]
    with tarfile.open(fileobj=tar_data, mode="w:gz") as tar:
        for item in include:
            tar.add(os.path.join(os.path.abspath(local_folder), item), arcname=item)
    tar_data.seek(0)
    return tar_data


def _validate_create_step_parameters(
    inputs: Union[list[Input], None],
    outputs: Union[list[Output], None],
    timeout_s: Union[int, None],
):
    if timeout_s is not None and timeout_s <= 0:
        raise ValueError("The timeout must be greater than 0 or None.")

    if inputs is not None:
        if any(not isinstance(input_, Input) for input_ in inputs):
            raise ValueError("'inputs' must be a list of instances of Input.")

    if outputs is not None:
        if any(not isinstance(output_, Output) for output_ in outputs):
            raise ValueError("'outputs' must be a list of instances of Output.")


def _map_container_config_step_parameter(container_config: ContainerConfig):
    """
    Maps container config with :obj:`CREATION_PARAMETER_VALUE` enum values to final
    container config. `None` is considered to be equivalent to
    :obj:`CREATION_PARAMETER_VALUE.FALLBACK_PROJECT`, and should not be projected to
    output
    """
    ret = {}
    for key in container_config:
        if key == "local_folder":
            continue
        val = container_config[key]
        if val is CREATION_PARAMETER_VALUE.NULL:
            ret[key] = None
        elif val is not CREATION_PARAMETER_VALUE.FALLBACK_PROJECT and val is not None:
            ret[key] = val
    return ret


def _prepare_create_step_data(
    function_path: Union[str, None],
    function_name: Union[str, None],
    description: Union[str, None],
    container_config: ContainerConfig,
    inputs: Union[list[Input], None],
    outputs: Union[list[Output], None],
    **step_or_pipeline_name,
):
    assert step_or_pipeline_name.keys() == {
        "step_name"
    } or step_or_pipeline_name.keys() == {"pipeline_name"}
    data = remove_none_values(
        {
            **step_or_pipeline_name,
            "function_path": function_path,
            "function_name": function_name,
            "description": description,
            "container_config": _map_container_config_step_parameter(container_config),
        }
    )

    if inputs is not None:
        data["inputs"] = [inp.to_dict() for inp in inputs]

    if outputs is not None:
        data["outputs"] = [output.to_dict() for output in outputs]

    return data


def _prepare_create_step_files(
    sdk: BaseCraftAiSdk,
    container_config: ContainerConfig,
    data: dict,
    function_path: Union[str, None],
):
    if "local_folder" not in container_config:
        return {}

    url = f"{sdk.base_environment_api_url}/project-information"
    project_information = sdk._get(url)

    included = [
        *(
            data.get("container_config", {}).get(
                "included_folders", project_information.get("included_folders")
            )
            or []
        ),
        data.get("container_config", {}).get(
            "requirements_path", project_information.get("requirements_path")
        ),
        function_path,
    ]

    tar_data = _compress_folder_to_memory(
        container_config["local_folder"], include=list(filter(None, included))
    )
    return {"step_file": tar_data}


def _add_inputs_outputs_in_message(message, inputs, outputs):
    if inputs:
        message += "\n  Inputs: "
        for inp in inputs:
            required_str = ", required" if inp.get("is_required", False) else ""
            message += f"\n    - {inp.get('name', inp.get('input_name'))} ({inp['data_type']}{required_str})"  # noqa: E501

    if outputs:
        message += "\n  Outputs: "
        for output in outputs:
            message += f"\n    - {output.get('name', output.get('output_name'))} ({output['data_type']})"  # noqa: E501
    return message


def _remove_id_from_step(step):
    if {"creation_info"} <= step.keys():
        step["creation_info"].pop("id", None)
    return step


@log_func_result("Steps creation")
def create_step(
    sdk: BaseCraftAiSdk,
    step_name: str,
    function_path: Union[str, None] = None,
    function_name: Union[str, None] = None,
    description: Union[str, None] = None,
    container_config: Union[ContainerConfig, None] = None,
    inputs: Union[list[Input], None] = None,
    outputs: Union[list[Output], None] = None,
    wait_for_completion=True,
    timeout_s: Union[int, None] = None,
):
    """Create pipeline step from a function located on a remote repository or locally.

    Use :obj:`CREATION_PARAMETER_VALUE` to explicitly set a value to null or fall back
    on project information.
    You can also use :obj:`container_config.included_folders` to specify the files and
    folders required for the step execution. This is useful if your repository
    contains large files that are not required for the step execution, such as
    documentation or test files. Indeed there is a maximum limit of 5MB for the
    total size of the content specified with :obj:`included_folders`.

    Args:
        step_name (:obj:`str`): Step name.
        function_path (:obj:`str`, optional): Path to the file that contains the
            function. This parameter is required if parameter "dockerfile_path"
            is not specified.
        function_name (:obj:`str`, optional): Name of the function in that file.
            This parameter is required if parameter "dockerfile_path" is not
            specified.
        description (:obj:`str`, optional): Description. Defaults to None.
        container_config (:obj:`dict[str, str]`, optional): Some step configuration,
            with the following optional keys:

            * ``"language"`` (:obj:`str`): Language and version used for the step.
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
              in the repository required for the step execution.
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
            * ``"local_folder`` (:obj:`str`): Path to local folder where the step is
              stored.

        inputs(`list` of instances of :class:`Input`): List of inputs. Each
            parameter of the step function should be specified as an instance of
            :class:`Input` via this parameter `inputs`.
            During the execution of the step, the value of the inputs would be
            passed as function arguments.
        outputs(`list` of instances of :class:`Output`): List of the step
            outputs. For the step to have outputs, the function should return a
            :obj:`dict` with the name of the output as keys and the value of the
            output as values. Each output should be specified as an instance
            of :class:`Output` via this parameter `outputs`.
        wait_for_completion (:obj:`bool`, optional): Whether to wait for the step
            to be created. Defaults to ``True``.
        timeout_s (:obj:`int`): Maximum time (in seconds) to wait for the step to
            be created. Set to None to wait indefinitely. Defaults to None.
            Only applicable if ``wait_for_completion`` is ``True``.

    Returns:
        :obj:`dict`: Created step represented as a :obj:`dict` with the following
        keys:

        * ``"parameters"`` (:obj:`dict`): Information used to create the step with
          the following keys:

          * ``"step_name"`` (:obj:`str`): Name of the step.
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

          * ``"container_config"`` (:obj:`dict[str, str]`): Some step
            configuration, with the following optional keys:

            * ``"language"`` (:obj:`str`): Language and version used for the step.
              The accepted formats are "python:3.X-slim", where "3.X" is a supported
              version of Python, and "python-cuda:3.X-Y.Z" for GPU environments,
              where "Y.Z" is a supported version of CUDA. The list of supported
              versions is available on the official documentation website at
              https://mlops-platform-documentation.craft.ai.
            * ``"repository_branch"`` (:obj:`str`): Branch name.
            * ``"repository_url"`` (:obj:`str`): Remote repository url.
            * ``"included_folders"`` (:obj:`list[str]`): List of folders and
              files in the repository required for the step execution.
            * ``"system_dependencies"`` (:obj:`list[str]`): List of system
              dependencies.
            * ``"dockerfile_path"`` (:obj:`str`): Path to the Dockerfile.
            * ``"requirements_path"`` (:obj:`str`): Path to the requirements.txt
              file.

        * ``"creation_info"`` (:obj:`dict`): Information about the step creation:

          * ``"created_at"`` (:obj:`str`): The creation date in ISO format.
          * ``"commit_id"`` (:obj:`str`): The commit id on which the step was
            built.
          * ``"status"`` (:obj:`str`): The step status, always ``"ready"`` when
            this function returns.
          * ``"origin"`` (:obj:`str`): The origin of the step, can be
            ``"git_repository"`` or ``"local"``.
    """

    container_config = (
        cast(ContainerConfig, {})
        if container_config is None
        else cast(ContainerConfig, container_config.copy())
    )
    _validate_create_step_parameters(inputs, outputs, timeout_s=timeout_s)

    url = f"{sdk.base_environment_api_url}/steps"
    data = _prepare_create_step_data(
        function_path,
        function_name,
        description,
        container_config,
        inputs,
        outputs,
        step_name=step_name,
    )
    files = _prepare_create_step_files(sdk, container_config, data, function_path)

    log_action(
        sdk,
        "Please wait while step is being created. This may take a while...",
    )

    sdk._post(url, data=multipartify(data), files=files, allow_redirects=False)

    return get_step(sdk, step_name, wait_for_completion, timeout_s)


def get_step(
    sdk: BaseCraftAiSdk,
    step_name: str,
    wait_for_completion=False,
    timeout_s: Union[int, None] = None,
) -> Step:
    """Get a single step if it exists.

    Args:
        step_name (:obj:`str`): The name of the step to get.
        wait_for_completion (:obj:`bool`, optional): Whether to wait for the step
            to be created. Defaults to ``False``.
        timeout_s (:obj:`int`): Maximum time (in seconds) to wait for the step to
            be created. Set to None to wait indefinitely. Defaults to None.
            Only applicable if ``wait_for_completion`` is ``True``.

    Returns:
        :obj:`dict`: ``None`` if the step does not exist; otherwise
        the step information, with the following keys:

        * ``"parameters"`` (:obj:`dict`): Information used to create the step with
          the following keys:

          * ``"step_name"`` (:obj:`str`): Name of the step.
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

          * ``"container_config"`` (:obj:`dict[str, str]`): Some step
            configuration, with the following optional keys:

            * ``"language"`` (:obj:`str`): Language and version used for the step.
              The accepted formats are "python:3.X-slim", where "3.X" is a supported
              version of Python, and "python-cuda:3.X-Y.Z" for GPU environments,
              where "Y.Z" is a supported version of CUDA. The list of supported
              versions is available on the official documentation website at
              https://mlops-platform-documentation.craft.ai.
            * ``"repository_url"`` (:obj:`str`): Remote repository url.
            * ``"repository_branch"`` (:obj:`str`): Branch name.
            * ``"included_folders"`` (:obj:`list[str]`): List of folders and
              files in the repository required for the step execution.
            * ``"system_dependencies"`` (:obj:`list[str]`): List of system
              dependencies.
            * ``"dockerfile_path"`` (:obj:`str`): Path to the Dockerfile.
            * ``"requirements_path"`` (:obj:`str`): Path to the requirements.txt
              file.

        * ``"creation_info"`` (:obj:`dict`): Information about the step creation:

          * ``"created_at"`` (:obj:`str`): The creation date in ISO format.
          * ``"commit_id"`` (:obj:`str`): The commit id on which the step was
            built.
          * ``"status"`` (:obj:`str`): either ``"creation_pending"`` or ``"ready"``.
          * ``"origin"`` (:obj:`str`): The origin of the step, can be
            ``"git_repository"`` or ``"local"``.
    """
    if timeout_s is not None and timeout_s <= 0:
        raise ValueError("The timeout must be greater than to 0 or None.")

    step = None

    base_url = f"{sdk.base_environment_api_url}/steps/{step_name}"

    if wait_for_completion:
        step = wait_create_until_ready(
            sdk,
            step_name,
            lambda sdk, _: sdk._get(
                f"{base_url}?wait_for_completion=true", allow_redirects=False
            ),
            timeout_s,
            sdk._get_time(),
            get_step_logs,
        )
    else:
        step = sdk._get(base_url)
    return _remove_id_from_step(step)


def list_steps(sdk: BaseCraftAiSdk) -> list[StepListItem]:
    """Get the list of all steps.

    Returns:
        :obj:`list` of :obj:`dict`: List of steps represented as :obj:`dict` with
        the following keys:

        * ``"step_name"`` (:obj:`str`): Name of the step.
        * ``"status"`` (:obj:`str`): either ``"creation_pending"`` or ``"ready"``.
        * ``"created_at"`` (:obj:`str`): The creation date in ISO format.
    """
    url = f"{sdk.base_environment_api_url}/steps"

    return sdk._get(url)


@log_func_result("Step deletion")
def delete_step(
    sdk: BaseCraftAiSdk, step_name: str, force_dependents_deletion=False
) -> StepDeleted:
    """Delete one step.

    Args:
        step_name (:obj:`str`): Name of the step to delete
            as defined in the ``config.yaml`` configuration file.
        force_dependents_deletion (:obj:`bool`, optional): if True the associated
            step's dependencies will be deleted too (pipeline, pipeline executions,
            deployments). Defaults to False.

    Returns:
        :obj:`dict[str, str]`: The deleted step represented as a :obj:`dict` with
        the following keys:

        * ``"step_name"`` (:obj:`str`): Name of the step.
    """
    url = f"{sdk.base_environment_api_url}/steps/{step_name}"
    params = {
        "force_dependents_deletion": force_dependents_deletion,
    }
    return sdk._delete(url, params=params)


def _get_download_presigned_url(sdk: BaseCraftAiSdk, step_name: str) -> str:
    url = f"{sdk.base_environment_api_url}/steps/{step_name}/download"
    presigned_url = sdk._get(url)["signed_url"]
    return presigned_url


@log_func_result("Step download")
def download_step_local_folder(sdk: BaseCraftAiSdk, step_name: str, folder: str):
    """Download a step's local folder as a `.tgz` archive.

    Only available if the step's ``origin`` is ``"local_folder"``. This archive
    contains the files that were in the ``local_folder`` parameter provided during
    step creation, and that were included based on the step's
    ``container_config`` property.

    Args:
        step_name (:obj:`str`): Name of the step to be downloaded.
        folder (:obj:`str`): Path to the folder where the file will be saved.

    Returns:
        None
    """
    presigned_url = _get_download_presigned_url(sdk, step_name)
    resp = requests.get(presigned_url)
    object_content = handle_data_store_response(resp)

    if isinstance(folder, str):
        path = os.path.join(os.path.abspath(folder), f"{step_name}.tgz")
        with open(path, "wb") as f:
            f.write(object_content)
    else:
        raise ValueError("'folder' must be a string")


@log_func_result("Step logs")
def get_step_logs(
    sdk: BaseCraftAiSdk,
    step_name: str,
    from_datetime: Union[datetime, None] = None,
    to_datetime: Union[datetime, None] = None,
    limit: Union[int, None] = None,
) -> list[Log]:
    """Get the logs of a step.

    Args:
        step_name (:obj:`str`): Name of the step.
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
    url = f"{sdk.base_environment_api_url}/steps/{step_name}/logs"

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
