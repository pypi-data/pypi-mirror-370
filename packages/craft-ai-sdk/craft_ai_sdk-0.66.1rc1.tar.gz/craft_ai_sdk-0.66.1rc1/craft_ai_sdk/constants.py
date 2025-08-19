from enum import Enum, auto

from strenum import LowercaseStrEnum


class DEPLOYMENT_EXECUTION_RULES(LowercaseStrEnum):
    """Enumeration for deployments execution rules."""

    ENDPOINT = auto()
    PERIODIC = auto()


class DEPLOYMENT_MODES(LowercaseStrEnum):
    """Enumeration for deployments modes."""

    LOW_LATENCY = auto()
    ELASTIC = auto()


class DEPLOYMENT_STATUS(LowercaseStrEnum):
    """Enumeration for deployments status."""

    CREATION_PENDING = auto()
    UP = auto()
    CREATION_FAILED = auto()
    DOWN_RETRYING = auto()
    STANDBY = auto()
    DISABLED = auto()


CREATION_REQUESTS_RETRY_INTERVAL = 10


class CREATION_PARAMETER_VALUE(Enum):
    """Enumeration for creation parameters special values."""

    #: Special value to indicate that the parameter should be set to the
    #: project information value.
    FALLBACK_PROJECT = "FALLBACK_PROJECT"
    #: Special value to indicate that the parameter should be set to `None`.
    NULL = "NULL"
