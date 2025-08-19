import xml.etree.ElementTree as ET
from json import JSONDecodeError
from typing import Any, Callable

from requests import RequestException, Response

from craft_ai_sdk.exceptions import SdkException
from craft_ai_sdk.shared.execution_context import get_execution_id


def handle_data_store_response(response: Response):
    """Return the content of a response received from the datastore
    or parse the send error and raise it.

    Args:
        response (requests.Response): A response from the data store.

    Raises:
        SdkException: When the response contains an error.

    Returns:
        :obj:`str`: Content of the response.

    """
    if 200 <= response.status_code < 300:
        return response.content

    try:
        # Parse XML error returned by the data store before raising it
        xml_error_node = ET.fromstring(response.text)
        error_infos = {node.tag: node.text for node in xml_error_node}
        error_code = error_infos.pop("Code")
        error_message = error_infos.pop("Message")
        raise SdkException(
            message=error_message,
            status_code=response.status_code,
            name=error_code,
            additional_data=error_infos,
        )
    except ET.ParseError as error:
        raise SdkException(
            "Unable to decode response from the data store: "
            f"Content being:\n'{response.text}'",
            status_code=response.status_code,
        ) from error


def _parse_json_response(response: Response):
    if response.status_code == 204 or response.text == "OK":
        return
    try:
        response_json = response.json()
    except JSONDecodeError:
        raise SdkException(
            f"Unable to decode response data into json. Data being:\n'{response.text}'",
            status_code=response.status_code,
        ) from None
    return response_json


def _raise_craft_ai_error_from_response(response: Response):
    try:
        error_content = response.json()
        error_message = error_content.get("message", "The server returned an error")

        # Permission denied inside a running execution
        if response.status_code == 403 and get_execution_id() is not None:
            error_message = (
                "Insufficient permissions. This is probably because "
                "you called an SDK function that is not permitted from "
                "inside a running deployment or execution, even if it "
                "works from your computer. Original error: " + error_message
            )

        raise SdkException(
            message=error_message,
            status_code=response.status_code,
            name=error_content.get("name"),
            request_id=error_content.get("request_id"),
            additional_data=error_content.get("additional_data"),
        )
    except JSONDecodeError:
        raise SdkException(
            "The server returned an invalid response content. "
            f"Content being:\n'{response.text}'",
            status_code=response.status_code,
        ) from None


def handle_http_response(response: Response):
    if 200 <= response.status_code < 400:
        if "application/octet-stream" in response.headers.get(
            "content-type", ""
        ) or "text/csv" in response.headers.get("content-type", ""):
            return response.content
        return _parse_json_response(response)
    _raise_craft_ai_error_from_response(response)


def handle_http_request(request_func: Callable[..., Response]) -> Callable[..., Any]:
    def wrapper(*args, **kwargs) -> Any:
        get_response = kwargs.pop("get_response", False)
        try:
            response = request_func(*args, **kwargs)
        except RequestException as error:
            raise SdkException(
                "Unable to perform the request", name="RequestError"
            ) from error

        content = handle_http_response(response)
        if get_response:
            return content, response
        return content

    return wrapper
