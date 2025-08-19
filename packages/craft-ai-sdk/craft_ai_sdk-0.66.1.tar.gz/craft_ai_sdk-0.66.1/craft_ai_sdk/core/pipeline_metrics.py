import warnings
from typing import TypedDict, Union

from ..sdk import BaseCraftAiSdk
from ..shared.execution_context import get_execution_id
from ..shared.logger import log_func_result
from ..utils import remove_none_values


class Metric(TypedDict):
    name: str
    value: float
    created_at: str
    execution_id: str
    deployment_name: str
    pipeline_name: str


class ListMetric(TypedDict):
    name: str
    values: list[float]
    created_at: str
    execution_id: str
    deployment_name: str
    pipeline_name: str


@log_func_result("Pipeline metrics definition", get_execution_id)
def record_metric_value(sdk: BaseCraftAiSdk, name: str, value: float):
    """Create or update a pipeline metric. Note that this function can only be used
    inside a step code.

    Args:
        name (:obj:`str`): Name of the metric to store.
        value (:obj:`float`): Value of the metric to store.

    Returns:
        True if sent, False otherwise
    """

    if not get_execution_id():
        if sdk.warn_on_metric_outside_of_step:
            warnings.warn(
                "You cannot send a metric outside a step code, the metric has not \
been sent",
                stacklevel=2,
            )
        return False
    url = f"{sdk.base_environment_api_url}/metrics/single-value/{name}"
    data = {"value": value, "execution_id": get_execution_id()}
    sdk._put(url, json=data)
    return True


@log_func_result("Pipeline list metric definition", get_execution_id)
def record_list_metric_values(sdk: BaseCraftAiSdk, name: str, values: list[float]):
    """Add values to a pipeline metric list. Note that this function can only be
    used inside a step code.

    Args:
        name (:obj:`str`):
            Name of the metric list to add values.
        values (:obj:`list` of :obj:`float` or :obj:`float`):
            Values of the metric list to add.

    Returns:
        True if sent, False otherwise
    """

    if not get_execution_id():
        if sdk.warn_on_metric_outside_of_step:
            warnings.warn(
                "You cannot send a metric outside a step code, the metric has not \
been sent",
                stacklevel=2,
            )
        return False

    if not isinstance(values, list):
        values = [values]

    BATCH_SIZE = 10000
    for i in range(0, len(values), BATCH_SIZE):
        url = f"{sdk.base_environment_api_url}/metrics/list-values/{name}"
        data = {
            "values": values[i : i + BATCH_SIZE],
            "execution_id": get_execution_id(),
        }
        sdk._post(url, json=data)
    return True


@log_func_result("Pipeline metrics listing")
def get_metrics(
    sdk: BaseCraftAiSdk,
    name: Union[str, None] = None,
    pipeline_name: Union[str, None] = None,
    deployment_name: Union[str, None] = None,
    execution_id: Union[str, None] = None,
) -> list[Metric]:
    """Get a list of pipeline metrics. Note that only one of the
    parameters (pipeline_name, deployment_name, execution_id) can be set.

    Args:
        name (:obj:`str`, optional): Name of the metric to retrieve.
        pipeline_name (:obj:`str`, optional):
            Filter metrics by pipeline, defaults to all the pipelines.
        deployment_name (:obj:`str`, optional):
            Filter metrics by deployment, defaults to all the deployments.
        execution_id (:obj:`str`, optional):
            Filter metrics by execution, defaults to all the executions.

    Returns:
        :obj:`list` of :obj:`dict`: List of execution metrics as :obj:`dict`
        with the following keys:

          * ``name`` (:obj:`str`): Name of the metric.
          * ``value`` (:obj:`float`): Value of the metric.
          * ``created_at`` (:obj:`str`): Date of the metric creation.
          * ``execution_id`` (:obj:`str`): Name of the execution the metric
            belongs to.
          * ``deployment_name`` (:obj:`str`): Name of the deployment the execution
            belongs to.
          * ``pipeline_name`` (:obj:`str`): Name of the pipeline the execution
            belongs to.
    """

    ITEMS_PER_PAGE = 5000

    data = {
        "filters[name]": name,
        "filters[pipeline_name]": pipeline_name,
        "filters[deployment_name]": deployment_name,
        "filters[execution_id]": execution_id,
        "items_per_page": ITEMS_PER_PAGE,
        "page": 1,
    }
    data = remove_none_values(data)

    url = f"{sdk.base_environment_api_url}/metrics/single-value"

    metrics = []

    result = sdk._get(url, params=data)
    metrics.extend(result.get("metrics", []))
    total_count = result["total_count"]
    data["page"] += 1

    while len(metrics) < total_count:
        result = sdk._get(url, params=data)
        metrics.extend(result.get("metrics", []))
        data["page"] += 1
        if metrics == []:
            break

    return metrics


@log_func_result("Pipeline list metrics listing")
def get_list_metrics(
    sdk: BaseCraftAiSdk,
    name: Union[str, None] = None,
    pipeline_name: Union[str, None] = None,
    deployment_name: Union[str, None] = None,
    execution_id: Union[str, None] = None,
) -> list[ListMetric]:
    """Get a list of pipeline metric lists. Note that only one of the
    parameters (pipeline_name, deployment_name, execution_id) can be set.

    Args:
        name (:obj:`str`, optional): Name of the metric list to retrieve.
        pipeline_name (:obj:`str`, optional):
            Filter metric lists by pipeline, defaults to all the pipelines.
        deployment_name (:obj:`str`, optional):
            Filter metric lists by deployment, defaults to all the deployments.
        execution_id (:obj:`str`, optional):
            Filter metric lists by execution, defaults to all the executions.

    Returns:
        :obj:`list` of :obj:`dict`: List of execution metric lists as :obj:`dict`
        with the following keys:

          * ``name`` (:obj:`str`): Name of the metric.
          * ``values`` (:obj:`list[float]`): Values list of the metric.
          * ``created_at`` (:obj:`str`): Date of the metric creation.
          * ``execution_id`` (:obj:`str`): Name of the execution the metric
            belongs to.
          * ``deployment_name`` (:obj:`str`): Name of the deployment the execution
            belongs to.
          * ``pipeline_name`` (:obj:`str`): Name of the pipeline the execution
            belongs to.
    """

    ITEMS_PER_PAGE = 5000

    data = {
        "filters[name]": name,
        "filters[pipeline_name]": pipeline_name,
        "filters[deployment_name]": deployment_name,
        "filters[execution_id]": execution_id,
        "items_per_page": ITEMS_PER_PAGE,
        "page": 1,
    }
    data = remove_none_values(data)

    url = f"{sdk.base_environment_api_url}/metrics/list-values"

    metrics = []

    result = sdk._get(url, params=data)
    metrics.extend(result.get("metrics", []))
    total_count = result["total_count"]
    data["page"] += 1

    while len(metrics) < total_count:
        result = sdk._get(url, params=data)
        metrics.extend(result.get("metrics", []))
        data["page"] += 1
        if metrics == []:
            break

    return metrics
