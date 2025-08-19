# Copyright 2023 Luminary Cloud, Inc. All Rights Reserved.
import logging
from collections.abc import Callable
from typing import Any

import grpc
from .. import __version__
from grpc import (
    ClientCallDetails,
    UnaryUnaryClientInterceptor,
)
from grpc._interceptor import _ClientCallDetails

from .._version import __version__

logger = logging.getLogger(__name__)


def _get_ai_notebook_id() -> str:
    # This needs to match the file name in frodo/src/use-jupyter-temp-files
    ai_notebook_active_file = "lc-ai-nb-active-nb"
    # Check if we're in the AI notebook env and read the notebook ID file
    # if we are
    notebook_id = ""
    try:
        with open(ai_notebook_active_file, "r") as f:
            notebook_id = f.read()
    except:
        # Just suppress any errors in loading the notebook ID and don't include
        # the invalid/missing ID. Either we're not in the AI notebook or the ID
        # isn't in the file
        pass
    return notebook_id


class LoggingInterceptor(UnaryUnaryClientInterceptor):
    """
    A client interceptor that logs gRPC method calls and appends the SDK version
    to the request metadata.
    """

    def __init__(self) -> None:
        super().__init__()
        self._notebook_id = _get_ai_notebook_id()

    def intercept_unary_unary(
        self,
        continuation: Callable[[ClientCallDetails, Any], grpc.Call],
        client_call_details: ClientCallDetails,
        request: Any,
    ) -> grpc.Call:

        metadata = []
        if client_call_details.metadata is not None:
            metadata = list(client_call_details.metadata)
        # will look like: x-client-version: python-sdk-v0.1.0
        metadata.append(("x-client-version", f"python-sdk-v{__version__}"))

        if self._notebook_id != "":
            # will look like: x-ai-notebook-id: <id>
            metadata.append(("x-ai-notebook-id", self._notebook_id))

        client_call_details = _ClientCallDetails(
            client_call_details.method,
            client_call_details.timeout,
            metadata,
            client_call_details.credentials,
            client_call_details.wait_for_ready,
            client_call_details.compression,
        )

        logger.debug(
            f"[SDK v{__version__}] Sending unary-unary gRPC request: {client_call_details.method}."
        )
        try:
            call = continuation(client_call_details, request)
            call.result()
        except grpc.RpcError:
            logger.debug("Error occurred during gRPC request", exc_info=True)
            raise
        return call
