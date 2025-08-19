"""Utils."""

import re
from typing import Any


def clean_name(name: str) -> str:
    """Clean the name by removing non-alphanumeric characters and converting to lowercase."""
    return re.sub(r"\W+", "", name).lower() if name else ""


def gather_credentials(credentials: tuple | dict | Any) -> tuple[str, str]:
    """Gather credentials from many possible credential objects.

    Args:
        credentials (tuple | dict | Any): credentials given by the user.

    Raises:
        ValueError: Raised when an unrecognizable credential object is given.

    Returns:
        tuple[str, str]: username, password paired tuple.
    """
    if isinstance(credentials, tuple):
        username, password = credentials
    elif isinstance(credentials, dict):
        username, password = credentials["username"], credentials["password"]
    else:
        try:
            username, password = credentials.username, credentials.password
        except AttributeError:
            msg = f"Unrecognizable credentials object given: {type(credentials)}"
            raise ValueError(msg)

    return username, password
