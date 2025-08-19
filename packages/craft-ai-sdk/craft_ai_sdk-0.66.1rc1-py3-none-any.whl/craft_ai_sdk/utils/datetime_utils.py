import re
from datetime import datetime


def datetime_to_timestamp_in_ms(dt: datetime) -> int:
    if not isinstance(dt, datetime):
        raise ValueError("Parameter must be a datetime.datetime object.")
    return int(1_000 * dt.timestamp())


def parse_isodate(date_string: str):
    """Parse a date string in ISO 8601 format and return a `datetime` object.

    Args:
        date_string (str): date in ISO 8601 format potentially ending with
            "Z" specific character.

    Returns:
        :obj:`datetime.datetime`: A `datetime` corresponding to `date_string`.

    """
    if date_string[-1] == "Z":
        date_string = date_string.rstrip("Z")

    return datetime.fromisoformat(re.sub(r"\.\d+", "", date_string))
