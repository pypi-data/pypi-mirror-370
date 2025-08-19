# Copyright 2025 Luminary Cloud, Inc. All Rights Reserved.
"""Custom exceptions for the Luminary Cloud SDK."""

import grpc


class SDKException(Exception):
    """Base exception for all Luminary SDK exceptions."""

    def __init__(self, message: str) -> None:
        self.message: str = message
        super().__init__(self.message)

    def __str__(self) -> str:
        return self.message

    def __repr__(self) -> str:
        return f"{self.__class__.__name__}: {self.message}"

    def _render_traceback_(self) -> list[str]:
        """Custom traceback for IPython"""
        return [self.message]


class RpcError(SDKException):
    """Raised when an RPC error occurs."""

    code: grpc.StatusCode

    def __init__(self, message: str, code: grpc.StatusCode) -> None:
        super().__init__(message)
        self.code = code


class AuthenticationError(RpcError):
    """Raised when authentication fails."""

    def _render_traceback_(self) -> list[str]:
        return ["Authentication failed; please check your credentials and try again."]


class InvalidRequestError(RpcError):
    """Raised when the request is invalid."""

    pass


class PermissionDeniedError(RpcError):
    """Raised when the user does not have permission to access the resource."""

    pass


class NotFoundError(RpcError):
    """Raised when the resource is not found."""

    pass


class AlreadyExistsError(RpcError):
    """Raised when the resource already exists."""

    pass


class FailedPreconditionError(RpcError):
    """Raised when the resource is not in the correct state to perform the operation."""

    pass
