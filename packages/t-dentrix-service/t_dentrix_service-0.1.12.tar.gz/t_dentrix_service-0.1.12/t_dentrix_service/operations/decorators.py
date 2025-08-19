"""Module that contains a variety of decorators to be used in the main process."""

import time
from collections.abc import Callable
from typing import Any

from requests.exceptions import HTTPError
from selenium.common import (
    ElementClickInterceptedException,
    ElementNotInteractableException,
    NoSuchElementException,
    StaleElementReferenceException,
    TimeoutException,
)
from SeleniumLibrary.errors import ElementNotFound

from t_dentrix_service.exceptions import (
    ConnectionRefusedException,
    ConnectionTimeoutException,
    InvalidRequestException,
    NotFoundException,
    NotLoggedInError,
    RateLimitExceededException,
    UnexpectedServerError,
)

SELENIUM_RETRY_EXCEPTIONS = (
    StaleElementReferenceException,
    ElementClickInterceptedException,
    NoSuchElementException,
    ElementNotInteractableException,
    ElementNotFound,
    AssertionError,
    TimeoutException,
)


def custom_selenium_retry(
    exceptions: tuple = (),
    tries: int = 3,
    delay: int = 5,
    ignore_exception: tuple = None,
) -> Callable:
    """Base decorator to retry if specified exceptions occur."""
    ignore_exception = () if ignore_exception is None else ignore_exception
    exceptions += SELENIUM_RETRY_EXCEPTIONS

    def decorator(func: Callable) -> Callable:
        def wrapper(self: Callable, *args, **kwargs) -> Callable:
            exception = None
            result = None
            for _ in range(tries):
                try:
                    result = func(self, *args, **kwargs)
                    break
                except ignore_exception:
                    pass
                except exceptions as e:
                    exception = e
                    if isinstance(e, TimeoutException):
                        time.sleep(60)
                    else:
                        time.sleep(delay)
            else:
                if exception:
                    raise exception
            return result

        return wrapper

    return decorator


def dentrix_request_handling(func: Callable) -> Callable[..., Any]:
    """A decorator for handling general HTTP exceptions from Dentrix."""

    def wrapper(*args, **kwargs) -> Any:
        try:
            return func(*args, **kwargs)
        except HTTPError as e:
            match e.response.status_code:
                case 401:
                    msg = "Please log into Dentrix before attempting any operation."
                    raise NotLoggedInError(msg)
                case _:
                    raise e

    return wrapper


def ascend_request_handling(func: Callable) -> Callable[..., None]:
    """A decorator for handling general HTTP exceptions from Ascend API."""

    def wrapper(*args, **kwargs) -> Any:
        try:
            func(*args, **kwargs)
        except HTTPError as e:
            match e.response.status_code:
                case 400:
                    msg = "The request was invalid or cannot be processed"
                    raise InvalidRequestException(msg)
                case 401:
                    msg = "Authentication is required and has failed or has not been provided"
                    raise NotLoggedInError(msg)
                case 403:
                    msg = "The request is understood, but it has been refused or access is not allowed"
                    raise ConnectionRefusedException(msg)
                case 404:
                    msg = "The requested resource is either missing or does not exist"
                    raise NotFoundException(msg)
                case 408:
                    msg = "The server timed out while processing the request"
                    raise ConnectionTimeoutException(msg)
                case 429:
                    msg = "Rate limit exceeded"
                    raise RateLimitExceededException(msg)
                case 500:
                    msg = "An unexpected error occurred"
                    raise UnexpectedServerError(msg)
                case _:
                    raise e

    return wrapper
