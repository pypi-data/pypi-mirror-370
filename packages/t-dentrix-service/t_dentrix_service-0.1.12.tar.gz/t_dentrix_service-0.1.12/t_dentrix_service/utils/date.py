"""Contains data methods for general use within the service."""

from datetime import date, datetime, time

import pytz


def now() -> datetime:
    """Gets the current date and time in UTC.

    Returns:
        datetime: The current date and time in UTC timezone.
    """
    return datetime.now(pytz.utc)


def today() -> datetime:
    """Gets the current date in UTC.

    Returns:
        date: The current date UTC timezone.
    """
    return now().date()


def now_timestamp() -> int:
    """Get the current UTC timestamp in milliseconds.

    Returns:
        int: The current UTC timestamp in milliseconds.
    """
    return int(datetime.now(pytz.utc).timestamp() * 1000)


def get_equivalent_utc_time_of_midnights_date(date_object: datetime | date) -> datetime:
    """Get the equivalent UTC time of midnight of the given date.

    Returns:
        datetime: A datetime object representing the equivalent UTC time of midnight of the given date.
    """
    if isinstance(date_object, date):
        date_object = datetime(year=date_object.year, month=date_object.month, day=date_object.day)
    tz = pytz.timezone("US/Pacific")
    midnight = tz.localize(datetime.combine(date_object, time(0, 0)), is_dst=None)
    return midnight.astimezone(pytz.utc)
