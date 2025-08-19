import io
from typing import TypedDict, Union

import requests

from ..sdk import BaseCraftAiSdk
from ..shared.logger import log_action, log_func_result
from ..shared.request_response_handler import handle_data_store_response
from ..utils import chunk_buffer, convert_size


class DataStoreObjectInformation(TypedDict):
    path: str
    last_modified: str
    size: str


class DataStoreDeletedObject(TypedDict):
    path: str


def get_data_store_object_information(
    sdk: BaseCraftAiSdk, object_path_in_datastore: str
) -> DataStoreObjectInformation:
    """Get information about a single object in the data store.

    Args:
        object_path_in_datastore (:obj:`str`): Location of the object in the data
            store.

    Returns:
        :obj:`dict`: Object information, with the following keys:

            * ``"path"`` (:obj:`str`): Location of the object in the data store.
            * ``"last_modified"`` (:obj:`str`): The creation date or last
              modification date in ISO format.
            * ``"size"`` (:obj:`str`): The size of the object.
    """
    url = f"{sdk.base_environment_api_url}/data-store/information"
    data = {
        "path_to_object": object_path_in_datastore,
    }
    result = sdk._post(url, json=data)

    result["size"] = convert_size(result["size"])
    return result


def list_data_store_objects(
    sdk: BaseCraftAiSdk, folder_path: Union[str, None] = None
) -> list[DataStoreObjectInformation]:
    """Get the list of the objects stored in the data store.

    Args:
        folder_path (:obj:`str`, optional): Location of the requested folder in the data
            store.

    Returns:
        :obj:`list` of :obj:`dict`: List of objects in the data store represented
        as :obj:`dict` with the following keys:

            * ``"path"`` (:obj:`str`): Location of the object in the data store.
            * ``"last_modified"`` (:obj:`str`): The creation date or last
              modification date in ISO format.
            * ``"size"`` (:obj:`int`): The size of the object in bytes.
    """
    url = f"{sdk.base_environment_api_url}/data-store/list"
    params = {"folder_path": folder_path} if folder_path else {}
    result = sdk._get(url, params=params)
    all_items = result["items"]
    while result.get("continuation_token", None):
        params = {"continuation_token": result["continuation_token"], **params}
        result = sdk._get(url, params=params)
        all_items.extend(result["items"])

    for object in all_items:
        object["size"] = convert_size(object["size"])
    return all_items


def _get_upload_presigned_url(sdk: BaseCraftAiSdk, object_path_in_datastore: str):
    url = f"{sdk.base_environment_api_url}/data-store/upload"
    params = {"path_to_object": object_path_in_datastore}
    resp = sdk._get(url, params=params)
    presigned_url, data = resp["signed_url"], resp["fields"]

    return presigned_url, data


@log_func_result("Object upload")
def upload_data_store_object(
    sdk: BaseCraftAiSdk,
    filepath_or_buffer: Union[str, io.IOBase],
    object_path_in_datastore: str,
):
    """Upload a file as an object into the data store.

    Args:
        filepath_or_buffer (:obj:`str`, or file-like object): String, path to the
            file to be uploaded ;
            or file-like object implementing a ``read()`` method (e.g. via builtin
            ``open`` function). The file object must be opened in binary mode,
            not text mode.
        object_path_in_datastore (:obj:`str`): Destination of the uploaded file.
    """
    if isinstance(filepath_or_buffer, str):
        # this is a filepath: call the method again with a buffer
        with open(filepath_or_buffer, "rb") as file_buffer:
            return upload_data_store_object(sdk, file_buffer, object_path_in_datastore)

    if not hasattr(filepath_or_buffer, "read"):  # not a readable buffer
        raise ValueError(
            "'filepath_or_buffer' must be either a string (filepath) or an object "
            "with a read() method (file-like object)."
        )
    if isinstance(filepath_or_buffer, io.IOBase) and filepath_or_buffer.tell() > 0:
        filepath_or_buffer.seek(0)

    first_read_size = len(filepath_or_buffer.read(sdk._MULTIPART_THRESHOLD))
    filepath_or_buffer.seek(0)
    if first_read_size < sdk._MULTIPART_THRESHOLD:
        return _upload_singlepart_data_store_object(
            sdk, filepath_or_buffer, object_path_in_datastore
        )
    log_action(
        sdk,
        "Uploading object with multipart (chunk size {:f}MB)".format(
            sdk._MULTIPART_PART_SIZE / 2**20
        ),
    )
    return _upload_multipart_data_store_object(
        sdk, filepath_or_buffer, object_path_in_datastore
    )


def _upload_singlepart_data_store_object(
    sdk: BaseCraftAiSdk, buffer: io.IOBase, object_path_in_datastore: str
):
    files = {"file": buffer}

    presigned_url, data = _get_upload_presigned_url(sdk, object_path_in_datastore)

    resp = requests.post(url=presigned_url, data=data, files=files)
    handle_data_store_response(resp)


def _upload_multipart_data_store_object(
    sdk: BaseCraftAiSdk, buffer: io.IOBase, object_path_in_datastore: str
):
    multipart_base_url = f"{sdk.base_environment_api_url}/data-store/upload/multipart"
    multipart_upload_configuration = sdk._post(
        url=f"{multipart_base_url}",
        json={"path_to_object": object_path_in_datastore},
    )

    parts = []
    part_idx = 0
    for part in chunk_buffer(buffer, sdk._MULTIPART_PART_SIZE):
        chunk = part["chunk"]
        len = part["len"]
        part_idx += 1
        data = {
            "path_to_object": object_path_in_datastore,
            "multipart_upload_configuration": multipart_upload_configuration,
            "chunk_size": sdk._MULTIPART_PART_SIZE,
            "part_number": part_idx,
        }
        if part["lastChunk"]:
            data["size"] = (part_idx - 1) * sdk._MULTIPART_PART_SIZE + len
        multipart_part_result = sdk._post(url=f"{multipart_base_url}/part", json=data)
        resp = requests.put(
            url=multipart_part_result["signed_url"],
            data=chunk,
            headers=multipart_part_result["headers"],
        )
        part_data: dict = {"number": part_idx}
        if "ETag" in resp.headers:
            part_data["metadata"] = resp.headers["ETag"]
        parts.append(part_data)
        if part["lastChunk"]:
            break

    sdk._post(
        url=f"{multipart_base_url}/end",
        json={
            "path_to_object": object_path_in_datastore,
            "multipart_upload_configuration": multipart_upload_configuration,
            "parts": parts,
        },
    )


def _get_download_presigned_url(
    sdk: BaseCraftAiSdk, object_path_in_datastore: str
) -> str:
    url = f"{sdk.base_environment_api_url}/data-store/download"
    data = {
        "path_to_object": object_path_in_datastore,
    }
    presigned_url = sdk._post(url, data=data)["signed_url"]
    return presigned_url


@log_func_result("Object download")
def download_data_store_object(
    sdk: BaseCraftAiSdk,
    object_path_in_datastore: str,
    filepath_or_buffer: Union[str, io.IOBase],
):
    """Download an object in the data store and save it into a file.

    Args:
        object_path_in_datastore (:obj:`str`): Location of the object to download
            from the data store.
        filepath_or_buffer (:obj:`str` or file-like object):
            String, filepath to save the file to ; or a file-like object
            implementing a ``write()`` method, (e.g. via builtin ``open`` function).
            The file object must be opened in binary mode, not text mode.

    Returns:
        None
    """
    presigned_url = _get_download_presigned_url(sdk, object_path_in_datastore)
    resp = requests.get(presigned_url)
    object_content = handle_data_store_response(resp)

    if isinstance(filepath_or_buffer, str):  # filepath
        with open(filepath_or_buffer, "wb") as f:
            f.write(object_content)
    elif hasattr(filepath_or_buffer, "write"):  # writable buffer
        filepath_or_buffer.write(object_content)
        if isinstance(filepath_or_buffer, io.IOBase) and filepath_or_buffer.tell() > 0:
            filepath_or_buffer.seek(0)
    else:
        raise ValueError(
            "'filepath_or_buffer' must be either a string (filepath) or an object "
            "with a write() method (file-like object)."
        )


@log_func_result("Object deletion")
def delete_data_store_object(
    sdk: BaseCraftAiSdk, object_path_in_datastore: str
) -> DataStoreDeletedObject:
    """Delete an object on the datastore.

    Args:
        object_path_in_datastore (:obj:`str`): Location of the object to be deleted
            in the data store.

    Returns:
        :obj:`dict`: Deleted object represented as dict with the following keys:

          * ``path`` (:obj:`str`): Path of the deleted object.
    """
    url = f"{sdk.base_environment_api_url}/data-store/delete"
    data = {
        "path_to_object": object_path_in_datastore,
    }
    return sdk._delete(url, data=data)
