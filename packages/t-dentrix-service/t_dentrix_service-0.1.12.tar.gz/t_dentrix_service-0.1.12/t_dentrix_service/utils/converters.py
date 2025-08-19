"""Contains data converters for general use within the service."""

from datetime import date, datetime, timedelta

import pytz

pst_timezone = pytz.timezone("US/Pacific")


def convert_date_to_timestamp(date_object: date) -> int:
    """Converts a date object to a timestamp.

    Args:
        date_object (date): The date object to be converted.

    Returns:
        int: The timestamp representation of the date object.
    """
    if isinstance(date_object, datetime):
        date_with_tz = pst_timezone.localize(date_object.replace(tzinfo=None))
        return int(date_with_tz.timestamp() * 1000)
    else:
        dt = datetime.combine(date_object, datetime.min.time())
        dt_with_tz = pst_timezone.localize(dt)
        return int(dt_with_tz.timestamp() * 1000)


def convert_timestamp_to_date(timestamp: int) -> date:
    """Converts a timestamp to datetime.

    Args:
        timestamp (int): The timestamp in milliseconds to be converted.

    Returns:
        datetime: The datetime object representation of the given timestamp.
    """
    return (datetime(1970, 1, 1, tzinfo=pst_timezone) + timedelta(milliseconds=timestamp)).date()
