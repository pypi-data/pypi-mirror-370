from io import BytesIO, IOBase, StringIO
from typing import Iterable, TypedDict, Union


def merge_paths(prefix, path):
    components = (value for value in path.split("/") if value != "")
    return prefix + "/".join(components)


# From https://stackoverflow.com/a/58767245/4839162
class ChunkedIO(TypedDict):
    chunk: Union[BytesIO, StringIO]
    len: int
    lastChunk: bool


def chunk_buffer(buffer: IOBase, size: int) -> Iterable[ChunkedIO]:
    size_int = int(size)
    b = buffer.read(size_int)
    next_data = None
    while b:
        chunk = StringIO() if isinstance(b, str) else BytesIO()
        previous_data = next_data
        if previous_data:
            chunk.write(next_data)
        chunk.write(b)
        chunk.seek(0)

        next_data = buffer.read(1)

        data: ChunkedIO = {
            "chunk": chunk,
            "len": len(b) + (len(previous_data) if previous_data else 0),
            "lastChunk": len(next_data) == 0,
        }
        yield data
        chunk.close()
        b = buffer.read(size_int - 1)


def convert_size(size_in_bytes: Union[int, float]):
    """Convert a size in bytes to a human readable string."""
    units = ["B", "KB", "MB", "GB", "TB"]
    for unit in units:  # noqa: B007
        if size_in_bytes < 1024.0:
            break
        size_in_bytes /= 1024.0
    return "{:.2f} {}".format(size_in_bytes, unit)


# Adapted from
# https://gist.github.com/kazqvaizer/4cebebe5db654a414132809f9f88067b#file-multipartify-py-L13-L33
def multipartify(data, parent_key: Union[str, None] = None) -> dict:
    """Convert a nested dictionary or list into a format suitable for
    multipart/form-data. This is useful for triggering endpoints that require
    multipart/form-data payloads.

    Args:
        data (:obj:`any`):
            The data to convert, can be a dict, list, or a simple value.
        parent_key (:obj: `str`, optional):
            The key to use for the current level of the data structure.

    Returns:
        :obj:`dict`: A dictionary where keys are formatted for multipart/form-data.

    """

    def formatter(v):
        return (None, v if v is not None else "")

    if not isinstance(data, dict):
        return {parent_key: formatter(data)}

    converted = []

    for key, value in data.items():
        current_key = key if parent_key is None else f"{parent_key}[{key}]"
        if isinstance(value, dict):
            converted.extend(multipartify(value, current_key).items())
        elif isinstance(value, list):
            for ind, list_value in enumerate(value):
                iter_key = f"{current_key}[{ind}]"
                converted.extend(multipartify(list_value, iter_key).items())
        else:
            converted.append((current_key, formatter(value)))

    return dict(converted)
