from typing import Callable

from frogml.core.exceptions import FrogmlException


def grpc_try_catch_wrapper(exception_message: str):
    def decorator(function: Callable):
        def _inner_wrapper(*args, **kwargs):
            try:
                return function(*args, **kwargs)
            except Exception as e:
                raise FrogmlException(f"{exception_message}. Error is: {e}.") from e

        return _inner_wrapper

    return decorator
