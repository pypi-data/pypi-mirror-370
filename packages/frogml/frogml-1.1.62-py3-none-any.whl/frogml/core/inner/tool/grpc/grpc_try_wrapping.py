from typing import Callable
import grpc
from frogml.core.exceptions import FrogmlException
from frogml.storage.logging import logger


def grpc_try_catch_wrapper(exception_message: str):
    def decorator(function: Callable):
        def _inner_wrapper(*args, **kwargs):
            try:
                return function(*args, **kwargs)
            except grpc.RpcError as e:
                err_msg: str = __get_error_msg(exception_message=exception_message, e=e)
                raise FrogmlException(err_msg)
            except Exception as e:
                raise FrogmlException(f"{exception_message}. Error is: {e}.") from e

        return _inner_wrapper

    return decorator


def __get_error_msg(exception_message: str, e: grpc.RpcError) -> str:
    err_msg: str = (
        f"{exception_message} - {e.code() if hasattr(e, 'code') else 'UNKNOWN'}"
    )
    if hasattr(e, "details") and e.details() is not None:
        err_msg: str = f"{err_msg} - {e.details()}"
    elif hasattr(e, "debug_error_string"):
        err_msg: str = f"{err_msg} - {e.debug_error_string()}"
    logger.debug(f"{err_msg}: {e}")
    return err_msg
