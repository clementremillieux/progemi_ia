"""This module contains a decorator to log the execution time of a function."""

import time

import asyncio

from functools import wraps

from config.logger_config import logger


def time_execution(func):
    """Decorator to log the execution time of a function.

    Args:
        func (callable): The function to be decorated.

    Returns:
        callable: The decorated function.
    """

    @wraps(func)
    async def async_wrapper(*args, **kwargs):
        """Wrapper for asynchronous functions.

        Returns:
            Any: The result of the function.
        """
        start_time = time.time()

        result = await func(*args, **kwargs)

        end_time = time.time()

        execution_time = end_time - start_time

        logger.info(
            "PERFORMANCES => Function '%s' executed in : %.3f seconds",
            func.__name__,
            execution_time,
        )

        return result

    @wraps(func)
    def sync_wrapper(*args, **kwargs):
        """Wrapper for synchronous functions.

        Returns:
            Any: The result of the function.
        """
        start_time = time.time()

        result = func(*args, **kwargs)

        end_time = time.time()

        execution_time = end_time - start_time

        logger.info(
            "PERFORMANCES => Async function '%s' executed in : %.6f seconds",
            func.__name__,
            execution_time,
        )

        return result

    if asyncio.iscoroutinefunction(func):
        return async_wrapper

    return sync_wrapper
