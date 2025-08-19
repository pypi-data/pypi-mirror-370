# -*- coding: utf-8 -*-
"""
"""

from datetime import datetime
from datetime import timedelta



from typing import Union


def get_timestamp() -> float:
    """
    Returns the current UTC timestamp.
    """
    return datetime.utcnow().timestamp()


def from_timestamp(
    timestamp: float
) -> Union[datetime, None]:
    """
    Gets datetime object from timestamp.

    Args
        timestamp: float, timestamp.

    Returns
        datetime: datetime instance from timestamp.
        None: if `timestamp` is not float.
    """
    if isinstance(timestamp, float):
        return datetime.fromtimestamp(timestamp)
    return None


def difference_times(
    start: float,
    end: float
) -> Union[timedelta, None]:
    """
    Gets the difference between two timestamps.

    Args
        start: float, start timestamp.
        end: float, end timestamp.

    Returns
        datetime.timedelta: between `end` an `start`.
        None: if `start` and `end` are not floats.
    """
    if isinstance(start, float) and isinstance(end, float):
        return datetime.fromtimestamp(end) - datetime.fromtimestamp(start)
    return None
