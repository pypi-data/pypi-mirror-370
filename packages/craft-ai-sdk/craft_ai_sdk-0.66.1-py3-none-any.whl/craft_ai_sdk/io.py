from typing import Any, TypedDict, cast

from strenum import LowercaseStrEnum
from typing_extensions import NotRequired

from craft_ai_sdk.utils import remove_none_values


class INPUT_OUTPUT_TYPES(LowercaseStrEnum):
    """Enumeration for Input and Output data types."""

    STRING = "string"
    NUMBER = "number"
    BOOLEAN = "boolean"
    JSON = "json"
    ARRAY = "array"
    FILE = "file"


class Input:
    """Class to specify a pipeline input when creating a pipeline
    (cf. :meth:`.CraftAiSdk.create_pipeline`).

    Args:
        name (:obj:`str`): Name of the input. This corresponds to the name of a
            parameter of a pipeline function.
        data_type (:obj:`str`): Type of the input: It could be one of "string",
            "number","boolean", "json", "array" or "file". For convenience, members of
            the enumeration :class:`INPUT_OUTPUT_TYPES` could be used too.
        description (:obj:`str`, optional): Description. Defaults to None.
        is_required (:obj:`bool`, optional): Specify if an value should be provided at
            execution time. Defaults to None.
        default_value (:obj:`Any`, optional): A default value for the pipeline input at
            execution time. The type for `default_value` should match the type specified
            by `data_type`. Defaults to None.
    """

    def __init__(
        self, name, data_type, description=None, is_required=None, default_value=None
    ):
        self.name = name
        self.data_type = data_type
        self.description = description
        self.is_required = is_required
        self.default_value = default_value

    def to_dict(self):
        input = {
            "name": self.name,
            "data_type": self.data_type,
            "description": self.description,
            "is_required": self.is_required,
            "default_value": self.default_value,
        }
        return remove_none_values(input)


class Output:
    """Class to specify a pipeline output when creating a pipeline
    (cf. :meth:`.CraftAiSdk.create_pipeline`).

    Args:
        name (:obj:`str`): Name of the output. This corresponds to the key of the `dict`
            returned by the pipeline function.
        data_type (:obj:`str`): Type of the output. It could be one of "string",
            "number", "boolean", "json", "array" or "file". For convenience, members of
            the enumeration :class:`INPUT_OUTPUT_TYPES` could be used too.
        description (:obj:`str`, optional): Description. Defaults to None.
    """

    def __init__(self, name, data_type, description=None):
        self.name = name
        self.data_type = data_type
        self.description = description

    def to_dict(self):
        output = {
            "name": self.name,
            "data_type": self.data_type,
            "description": self.description,
        }

        return remove_none_values(output)


class InputSourceDict(TypedDict):
    pipeline_input_name: str
    description: str
    constant_value: NotRequired[Any]
    environment_variable_name: NotRequired[str]
    endpoint_input_name: NotRequired[str]
    is_null: NotRequired[bool]
    datastore_path: NotRequired[str]
    is_required: NotRequired[bool]
    default_value: NotRequired[Any]


class InputSource:
    """Class to specify to which source a pipeline input should be mapped when creating
    a deployment (cf. :meth:`.CraftAiSdk.create_deployment`). The different sources can
    be one of:

        * :obj:`endpoint_input_name` (:obj:`str`): An endpoint input with the provided
          name.
        * :obj:`constant_value`: A constant value.
        * :obj:`environment_variable_name`: The value of the provided
          environment variable.
        * :obj:`is_null`: Nothing.

    If the execution rule of the deployment is endpoint and the input is directly mapped
    to an endpoint input, two more parameters can be specified:

        * :obj:`default_value`
        * :obj:`is_required`

    Args:
        pipeline_input_name (:obj:`str`): Name of the pipeline input to be mapped.
        endpoint_input_name (:obj:`str`, optional): Name of the endpoint input to which
            the input is mapped.
        environment_variable_name (:obj:`str`, optional): Name of the environment
            variable to which the input is mapped.
        constant_value (:obj:`Any`, optional): A constant value.
        is_null (:obj:`True`, optional): If specified, the input is not provided any
            value at execution time.
        datastore_path (:obj:`str`, optional): Path of the input file in the datastore.
            If you want to use a file from the datastore as input, this file will then
            be accessible as if you passed the file path as an argument to the pipeline.
            The resulting input will be a :obj:`dict` with `"path"` as key and the
            file path as value. The file will be downloaded in the execution environment
            before the pipeline is executed. You can then use the file as you would
            use any other file in the execution environment. Here is an example of
            how to use this feature in the pipeline code:

            .. code-block:: python

                def pipeline_function(input):
                    with open(input["path"]) as f:
                        content = f.read()
                        print(content)

        default_value (:obj:`Any`, optional): This parameter could only be specified if
            the parameter `endpoint_input_name` is specified.
        is_required (:obj:`bool`, optional): This parameter could only be specified if
            the parameter `endpoint_input_name` is specified. If set to `True`, the
            corresponding endpoint input should be provided at execution time.
    """

    def __init__(
        self,
        pipeline_input_name=None,
        endpoint_input_name=None,
        environment_variable_name=None,
        is_required=None,
        default_value=None,
        constant_value=None,
        is_null=None,
        datastore_path=None,
    ):
        self.pipeline_input_name = pipeline_input_name
        self.endpoint_input_name = endpoint_input_name
        self.environment_variable_name = environment_variable_name
        self.is_required = is_required
        self.default_value = default_value
        self.constant_value = constant_value
        self.is_null = is_null
        self.datastore_path = datastore_path

    def to_dict(self) -> InputSourceDict:
        input_mapping_dict = {
            "pipeline_input_name": self.pipeline_input_name,
            "endpoint_input_name": self.endpoint_input_name,
            "environment_variable_name": self.environment_variable_name,
            "is_required": self.is_required,
            "default_value": self.default_value,
            "constant_value": self.constant_value,
            "is_null": self.is_null,
            "datastore_path": self.datastore_path,
        }

        return cast(InputSourceDict, remove_none_values(input_mapping_dict))


class OutputDestinationDict(TypedDict):
    pipeline_output_name: str
    endpoint_output_name: NotRequired[str]
    is_null: NotRequired[bool]
    datastore_path: NotRequired[str]


class OutputDestination:
    """Class to specify to which destination a pipeline output should be mapped when
    creating a deployment (cf. :meth:`.CraftAiSdk.create_deployment`). If the execution
    rule of the deployment is endpoint, an output could either be exposed as an output
    of the endpoint (via `endpoint_output_name` parameter) or not (via `is_null`
    parameter).


    Args:
        pipeline_output_name (:obj:`str`): Name of the pipeline output to be mapped.
        endpoint_output_name (:obj:`str`, optional): Name of the endpoint output to
            which the output is mapped.
        is_null (:obj:`True`, optional): If specified, the output is not exposed as a
            deployment output.
        datastore_path (:obj:`str`, optional): Path of the output file in the datastore.
            If you want to upload a file to the datastore as output, you can specify
            this parameter. The file will be uploaded to the datastore after the
            pipeline is executed. In order to pass the file to be uploaded in the
            datastore, you will have to do the same as if you were passing a file
            as output. You will have to return a :obj:`dict` with `"path"` as key
            and the file path as value. The file will be uploaded to the datastore
            after the pipeline is executed. Here is an example of how to use this
            feature in the pipeline code:

            .. code-block:: python

                def pipeline_function():
                    file_path = "path/to/file"
                    with open(file_path, "w") as f:
                        f.write("content")
                    return {"output_file": {"path": file_path}}

            You can also specify a dynamic path for the file to be uploaded by using one
            of the following patterns in your datastore path:

              * `{execution_id}`: The execution id of the deployment.
              * `{date}`: The date of the execution in truncated ISO 8601 (`YYYYMMDD`)
                format.
              * `{date_time}`: The date of the execution in ISO 8601 (`YYYYMMDD_hhmmss`)
                format.

    """

    def __init__(
        self,
        pipeline_output_name=None,
        endpoint_output_name=None,
        is_null=None,
        datastore_path=None,
    ):
        self.pipeline_output_name = pipeline_output_name
        self.endpoint_output_name = endpoint_output_name
        self.is_null = is_null
        self.datastore_path = datastore_path

    def to_dict(self) -> OutputDestinationDict:
        output_mapping_dict = {
            "pipeline_output_name": self.pipeline_output_name,
            "endpoint_output_name": self.endpoint_output_name,
            "is_null": self.is_null,
            "datastore_path": self.datastore_path,
        }

        return cast(OutputDestinationDict, remove_none_values(output_mapping_dict))


def _format_execution_output(name, output):
    mapping_to_return = output["mapping_value"]
    mapping_to_return.pop("is_required", None)
    mapping_to_return.pop("default_value", None)
    mapping_to_return.pop("run_output_name", None)

    return {
        "pipeline_output_name": name,
        "data_type": output["data_type"],
        **mapping_to_return,
        "destination": output["mapping_type"],
        "value": output["value"],
    }


def _format_execution_input(name, input):
    mapping_to_return = input["mapping_value"]
    mapping_to_return.pop("is_required", None)
    mapping_to_return.pop("default_value", None)
    mapping_to_return.pop("run_input_name", None)
    return {
        "pipeline_input_name": name,
        "data_type": input["data_type"],
        **mapping_to_return,
        "source": input["mapping_type"],
        "value": input["value"],
    }


def _validate_inputs_mapping(inputs_mapping):
    if inputs_mapping is None:
        return None
    if any(
        not isinstance(input_mapping_, InputSource) for input_mapping_ in inputs_mapping
    ):
        raise ValueError("'inputs_mapping' must be a list of instances of InputSource.")
    return [input_mapping_.to_dict() for input_mapping_ in inputs_mapping]


def _validate_outputs_mapping(outputs_mapping):
    if outputs_mapping is None:
        return None
    if any(
        not isinstance(output_mapping_, OutputDestination)
        for output_mapping_ in outputs_mapping
    ):
        raise ValueError(
            "'outputs_mapping' must be a list of instances of OutputDestination."
        )
    return [output_mapping_.to_dict() for output_mapping_ in outputs_mapping]
