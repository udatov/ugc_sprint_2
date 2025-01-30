import asyncio
from functools import wraps
from typing import Any, Callable

import httpx
from core.config import settings


def backoff(
    start_sleep_time: float = 0.1, factor: int = 2, border_sleep_time: int = 10
) -> Callable:
    """
    A decorator for retrying a function execution in case of a request timeout.
    Implements naive exponential backoff with a maximum wait time.

    Backoff formula:
        t = start_sleep_time * (factor ** n), if t < border_sleep_time
        t = border_sleep_time, otherwise

    :param start_sleep_time: Initial wait time in seconds.
    :param factor: Factor by which the wait time increases on each retry.
    :param border_sleep_time: Maximum wait time in seconds.
    :return: Decorated function with retry logic.
    """

    def decorator(func: Callable) -> Callable:
        @wraps(func)
        async def wrapper(*args: Any, **kwargs: Any) -> Any:
            attempt = 0
            wait_time = start_sleep_time
            while attempt < settings.errors_max:
                try:
                    return await func(*args, **kwargs)
                except httpx.RequestError:
                    await asyncio.sleep(wait_time)
                    if wait_time < border_sleep_time:
                        wait_time = min(
                            start_sleep_time * (factor ** (attempt + 1)),
                            border_sleep_time,
                        )
                    attempt += 1
            raise Exception("Maximum retry limit exceeded due to request timeout.")

        return wrapper

    return decorator
