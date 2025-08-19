import os
import sys
import time
import warnings
from abc import ABC, abstractmethod
from datetime import timedelta
from typing import Any

import jwt
import requests

from .shared.authentication import use_authentication
from .shared.request_response_handler import handle_http_request

warnings.simplefilter("always", DeprecationWarning)


class BaseCraftAiSdk(ABC):
    _get_time = time.time  # For tests fake timing
    base_environment_url: str
    base_environment_api_url: str
    base_control_api_url: str
    _MULTIPART_THRESHOLD: int
    _MULTIPART_PART_SIZE: int
    _version: str
    _session: requests.Session
    warn_on_metric_outside_of_step: bool

    @abstractmethod
    def _get(self, url: str, params=None, **kwargs) -> Any:
        pass

    @abstractmethod
    def _post(self, url: str, data=None, params=None, files=None, **kwargs) -> Any:
        pass

    @abstractmethod
    def _put(self, url: str, data=None, params=None, files=None, **kwargs) -> Any:
        pass

    @abstractmethod
    def _patch(self, url: str, data=None, params=None, files=None, **kwargs) -> Any:
        pass

    @abstractmethod
    def _delete(self, url: str, **kwargs) -> Any:
        pass


class CraftAiSdk(BaseCraftAiSdk):
    """Main class to instantiate

    Attributes:
        base_environment_url (:obj:`str`): Base URL to CraftAI Environment.
        base_environment_api_url (:obj:`str`): Base URL to CraftAI Environment API.
        base_control_url (:obj:`str`): Base URL to CraftAI authorization server.
        base_control_api_url (:obj:`str`): Base URL to CraftAI authorization server API.
        verbose_log (bool): If True, information during method execution will be
            printed.
        warn_on_metric_outside_of_step (bool): If True, a warning will be printed when
            a metric is added outside of a step.
    """

    from .core.data_store import (
        delete_data_store_object,
        download_data_store_object,
        get_data_store_object_information,
        list_data_store_objects,
        upload_data_store_object,
    )
    from .core.deployments import (
        create_deployment,
        delete_deployment,
        get_deployment,
        get_deployment_logs,
        list_deployments,
        update_deployment,
    )
    from .core.endpoints import (
        generate_new_endpoint_token,
        retrieve_endpoint_results,
        trigger_endpoint,
    )
    from .core.environment_variables import (
        create_or_update_environment_variable,
        delete_environment_variable,
        list_environment_variables,
    )
    from .core.pipeline_executions import (
        delete_pipeline_execution,
        get_pipeline_execution,
        get_pipeline_execution_input,
        get_pipeline_execution_logs,
        get_pipeline_execution_output,
        list_pipeline_executions,
        retrieve_pipeline_execution_outputs,
        run_pipeline,
    )
    from .core.pipeline_metrics import (
        get_list_metrics,
        get_metrics,
        record_list_metric_values,
        record_metric_value,
    )
    from .core.pipelines import (
        create_pipeline,
        delete_pipeline,
        download_pipeline_local_folder,
        get_pipeline,
        get_pipeline_logs,
        list_pipelines,
    )
    from .core.resource_metrics import get_resource_metrics
    from .core.steps import (
        create_step,
        delete_step,
        download_step_local_folder,
        get_step,
        get_step_logs,
        list_steps,
    )
    from .core.users import get_user
    from .core.vector_database import (
        get_vector_database_credentials,
        get_weaviate_client,
    )

    # Size (in bytes) from which datastore upload will switch to multipart
    # AWS: minimum part size is 5MiB
    # (https://docs.aws.amazon.com/AmazonS3/latest/userguide/qfacts.html)
    # AWS: 100MiB is the recommended size to switch to multipart
    # (https://docs.aws.amazon.com/AmazonS3/latest/userguide/mpuoverview.html)
    # GCS: part size must be a multiple of 256KiB
    # (https://cloud.google.com/storage/docs/performing-resumable-uploads#chunked-upload)
    _MULTIPART_THRESHOLD = int(
        os.environ.get("CRAFT_AI__MULTIPART_THRESHOLD__B", "100_000_000")
    )
    _MULTIPART_PART_SIZE = int(
        os.environ.get("CRAFT_AI__MULTIPART_PART_SIZE__B", str(38 * 256 * 1024))
    )
    _access_token_margin = timedelta(seconds=30)
    _version = "0.66.1"  # Would be better to share it somewhere

    def __init__(
        self,
        sdk_token=None,
        environment_url=None,
        control_url=None,
        verbose_log=None,
        warn_on_metric_outside_of_step=True,
    ):
        """Inits CraftAiSdk.

        Args:
            sdk_token (:obj:`str`, optional): SDK token. You can retrieve it
                from the website.
                Defaults to ``CRAFT_AI_SDK_TOKEN`` environment variable.
            environment_url (:obj:`str`, optional): URL to CraftAI environment.
                Defaults to ``CRAFT_AI_ENVIRONMENT_URL`` environment variable.
            control_url (:obj:`str`, optional): URL to CraftAI authorization server.
                You probably don't need to set it.
                Defaults to ``CRAFT_AI_CONTROL_URL`` environment variable, or
                https://mlops-platform.craft.ai.
            verbose_log (:obj:`bool`, optional): If ``True``, information during method
                execution will be printed.
                Defaults to ``True`` if the environment variable ``SDK_VERBOSE_LOG`` is
                set to ``true``; ``False`` if it is set to ``false``; else, defaults to
                ``True`` in interactive mode; ``False`` otherwise.
            warn_on_metric_outside_of_step (:obj:`bool`, optional): If ``True``, a
                warning will be raised when a metric is added outside of a step.
                Defaults to ``True``.

        Raises:
            ValueError: if the ``sdk_token`` or ``environment_url`` is not defined and
            the corresponding environment variable is not set.
        """
        self._session = requests.Session()
        self._session.headers["craft-ai-client"] = f"craft-ai-sdk@{self._version}"

        # Set authorization token
        if sdk_token is None:
            sdk_token = os.environ.get("CRAFT_AI_SDK_TOKEN")
        if not sdk_token:
            raise ValueError(
                'Parameter "sdk_token" should be set, since '
                '"CRAFT_AI_SDK_TOKEN" environment variable is not defined.'
            )
        self._refresh_token = sdk_token
        self._access_token = None
        self._access_token_data = None

        # Set base environment url
        if environment_url is None:
            environment_url = os.environ.get("CRAFT_AI_ENVIRONMENT_URL")
        if not environment_url:
            raise ValueError(
                'Parameter "environment_url" should be set, since '
                '"CRAFT_AI_ENVIRONMENT_URL" environment variable is not defined.'
            )
        environment_url = environment_url.rstrip("/")
        self.base_environment_url = environment_url
        self.base_environment_api_url = f"{environment_url}/api/v1"

        # Set base control url
        if control_url is None:
            control_url = os.environ.get("CRAFT_AI_CONTROL_URL")
        if not control_url:
            control_url = "https://mlops-platform.craft.ai"
        control_url = control_url.rstrip("/")
        self.base_control_url = control_url
        self.base_control_api_url = f"{control_url}/api/v1"

        if verbose_log is None:
            env_verbose_log = os.environ.get("SDK_VERBOSE_LOG", "").lower()
            # Detect interactive mode: https://stackoverflow.com/a/64523765
            verbose_log = (
                True
                if env_verbose_log == "true"
                else False
                if env_verbose_log == "false"
                else hasattr(sys, "ps1")
            )
        self.verbose_log = verbose_log

        # Set warn_on_metric_outside_of_step
        self.warn_on_metric_outside_of_step = warn_on_metric_outside_of_step

    # _____ REQUESTS METHODS _____

    @handle_http_request
    @use_authentication
    def _get(self, url, params=None, **kwargs):
        return self._session.get(
            url,
            params=params,
            **kwargs,
        )

    @handle_http_request
    @use_authentication
    def _post(self, url, data=None, params=None, files=None, **kwargs):
        return self._session.post(
            url,
            data=data,
            params=params,
            files=files,
            **kwargs,
        )

    @handle_http_request
    @use_authentication
    def _put(self, url, data=None, params=None, files=None, **kwargs):
        return self._session.put(
            url,
            data=data,
            params=params,
            files=files,
            **kwargs,
        )

    @handle_http_request
    @use_authentication
    def _patch(self, url, data=None, params=None, files=None, **kwargs):
        return self._session.patch(
            url,
            data=data,
            params=params,
            files=files,
            **kwargs,
        )

    @handle_http_request
    @use_authentication
    def _delete(self, url, **kwargs):
        return self._session.delete(url, **kwargs)

    # _____ AUTHENTICATION & PROFILE _____

    @handle_http_request
    def _query_refresh_access_token(self):
        url = f"{self.base_control_api_url}/auth/refresh"
        data = {"refresh_token": self._refresh_token}
        return self._session.post(url, json=data)

    def _refresh_access_token(self):
        response = self._query_refresh_access_token()
        self._access_token = response["access_token"]
        self._access_token_data = jwt.decode(
            self._access_token, options={"verify_signature": False}
        )

    def _clear_access_token(self):
        self._access_token = None
        self._access_token_data = None

    def who_am_i(self):
        """Get the information of the current user

        Returns:
            :obj:`dict` containing user infos"""
        url = f"{self.base_control_api_url}/users/me"
        user = self._get(url)
        return {
            key: value for key, value in user.items() if key in ["id", "name", "email"]
        }

    @property
    def warn_on_metric_outside_of_step(self):
        """Whether a warning should be raised when a metric is added outside of a
        step."""
        return self._warn_on_metric_outside_of_step

    @warn_on_metric_outside_of_step.setter
    def warn_on_metric_outside_of_step(self, value):
        if not isinstance(value, bool):
            raise TypeError("warn_on_metric_outside_of_step must be a boolean")
        self._warn_on_metric_outside_of_step = value
