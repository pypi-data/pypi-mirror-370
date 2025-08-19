from functools import wraps
from typing import Any, Callable
import logging

import grpc

import luminarycloud.exceptions as exceptions

logger = logging.getLogger("luminarycloud")

_CODE_TO_EXCEPTION: dict[grpc.StatusCode, type[exceptions.RpcError]] = {
    grpc.StatusCode.INVALID_ARGUMENT: exceptions.InvalidRequestError,
    grpc.StatusCode.UNAUTHENTICATED: exceptions.AuthenticationError,
    grpc.StatusCode.PERMISSION_DENIED: exceptions.PermissionDeniedError,
    grpc.StatusCode.NOT_FOUND: exceptions.NotFoundError,
    grpc.StatusCode.ALREADY_EXISTS: exceptions.AlreadyExistsError,
    grpc.StatusCode.FAILED_PRECONDITION: exceptions.FailedPreconditionError,
}


def rpc_error(func: Callable[..., Any]) -> Callable[..., Any]:
    @wraps(func)
    def wrapper(*args: Any, **kwargs: Any) -> Any:
        try:
            return func(*args, **kwargs)
        except grpc.RpcError as e:
            for code, exception in _CODE_TO_EXCEPTION.items():
                if e.code() == code:
                    logger.debug(f"RPC failed: {e.code().name}", exc_info=True)
                    raise exception(e.details(), code) from None
            raise e

    return wrapper
