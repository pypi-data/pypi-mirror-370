import functools
import logging
import inspect
from typing import Any, Callable


def log_method(func: Callable) -> Callable:
    """
    Decorator that logs method calls, arguments, return values, and exceptions.
    Usage: @log_method (no parentheses)
    """
    logger = logging.getLogger(func.__module__)

    @functools.wraps(func)
    def wrapper(*args: Any, **kwargs: Any) -> Any:
        method_name = func.__qualname__

        try:
            bound = inspect.signature(func).bind(*args, **kwargs)
            bound.apply_defaults()
            args_to_log = {k: v for k, v in bound.arguments.items() if k != "self"}

            logger.debug(
                "Calling method: %s with arguments: %s", method_name, args_to_log
            )

            result = func(*args, **kwargs)

            logger.debug(
                "Returned from method: %s with result: %r", method_name, result
            )
            return result

        except Exception:
            logger.exception("Exception in method: %s", method_name)
            raise

    return wrapper
