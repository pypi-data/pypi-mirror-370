from datetime import datetime
from typing import Literal, TypedDict, Union, overload

from typing_extensions import NotRequired

from ..sdk import BaseCraftAiSdk
from ..utils import datetime_to_timestamp_in_ms


class AdditionalData(TypedDict):
    total_disk: int
    total_ram: int
    total_vram: NotRequired[str]


class MetricWorker(TypedDict):
    worker: str


class Metric(TypedDict):
    metric: MetricWorker
    values: list[list[Union[int, float]]]


class MetricsDict(TypedDict):
    cpu_usage: list[Metric]
    disk_usage: list[Metric]
    ram_usage: list[Metric]
    vram_usage: NotRequired[list[Metric]]
    gpu_usage: NotRequired[list[Metric]]
    network_input_usage: list[Metric]
    network_output_usage: list[Metric]


class ResourceMetrics(TypedDict):
    additional_data: AdditionalData
    metrics: MetricsDict


@overload
def get_resource_metrics(
    sdk: BaseCraftAiSdk, start_date: datetime, end_date: datetime, csv: Literal[True]
) -> bytes: ...


@overload
def get_resource_metrics(
    sdk: BaseCraftAiSdk,
    start_date: datetime,
    end_date: datetime,
    csv: Literal[False] = False,
) -> ResourceMetrics: ...


def get_resource_metrics(
    sdk: BaseCraftAiSdk, start_date: datetime, end_date: datetime, csv=False
) -> Union[ResourceMetrics, bytes]:
    """Get resource metrics of the environment.

    Args:
        start_date (:obj:`datetime.datetime`): The beginning of the period.
        end_date (:obj:`datetime.datetime`): The end of the period.
        csv (:obj:`bool`): If True, it will return a csv file as bytes.

    Returns:
        If csv is True, it will return :obj:`bytes`.
        Otherwise: :obj:`dict`: The resource metrics, with the following keys:

          * ``additional_data`` (:obj:`dict`): Additional data with the following keys:

            * ``total_disk`` (:obj:`int`): Total disk size in bytes.
            * ``total_ram`` (:obj:`int`): Total RAM size in bytes.
            * ``total_vram`` (:obj:`int`): Total VRAM size in bytes if there is a GPU.

          * ``metrics`` (:obj:`dict`): The metrics of the environment with the following
            keys:

            * ``cpu_usage`` (:obj:`list` of :obj:`dict`): The CPU usage in percent.
            * ``disk_usage`` (:obj:`list` of :obj:`dict`): The disk usage in percent.
            * ``ram_usage`` (:obj:`list` of :obj:`dict`): The RAM usage in percent.
            * ``vram_usage`` (:obj:`list` of :obj:`dict`): The VRAM usage in percent if
              there is a GPU.
            * ``gpu_usage`` (:obj:`list` of :obj:`dict`): The GPU usage in percent if
              there is a GPU.
            * ``network_input_usage`` (:obj:`list` of :obj:`dict`): The network input
              usage in bytes.
            * ``network_output_usage`` (:obj:`list` of :obj:`dict`): The network output
              usage in bytes.

        Each element of the lists is a dict with the following keys:

          * ``metric`` (:obj:`dict`): Dictionary with the following key:

            * ``worker`` (:obj:`str`): The worker name.

          * ``values`` (:obj:`list` of :obj:`list`): The values of the metrics in the
            following format: ``[[timestamp, value], ...]``.

    """

    url = (
        f"{sdk.base_environment_api_url}/resource-metrics"
        f"?start={datetime_to_timestamp_in_ms(start_date)}"
        f"&end={datetime_to_timestamp_in_ms(end_date)}"
        f"&download={csv}"
    )

    return sdk._get(url)
