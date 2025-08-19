# Copyright 2023-2024 Luminary Cloud, Inc. All Rights Reserved.

from __future__ import annotations

import logging
import multiprocessing
from collections.abc import Iterable
from typing import Optional, Any

from waitress import serve
from werkzeug import Request, Response
from werkzeug.datastructures import MultiDict

from .util import is_port_in_use

logger = logging.getLogger(__name__)


class NoAvailablePortsException(Exception):
    pass


class CallbackListener:
    """
    A context manager class that spins up a server to listen for Auth0 callbacks.

    Requests to the server must be made to the "/callback" path. If the query parameters of a
    callback request does not include both "state" and "code" AND does not include "error" as keys,
    the callback will be ignored.

    Parameters
    ----------
    allowed_ports : list of int
        These ports will be tried in order

    Raises
    ------
    NoAvailablePortsException
        If all of the `allowed_ports` are in-use.

    Examples
    --------
    >>> with CallbackListener(allowed_ports=[1234, 5678]) as listener:
    ...     callback_args = listener.block_until_callback()
    Listening on port 5000...
    """

    def __init__(
        self,
        allowed_ports: Iterable[int],
    ):
        self.allowed_ports: list[int] = list(allowed_ports)
        self._port: Optional[int] = None
        self._callback_args_q: multiprocessing.Queue = multiprocessing.Queue()

    @property
    def port(self) -> Optional[int]:
        return self._port

    def start(self) -> None:
        port_q: multiprocessing.Queue = multiprocessing.Queue()

        logger.info("Starting the server as a separate process.")
        self.server = multiprocessing.Process(
            target=self._run_server,
            args=(self._callback_args_q, port_q),
        )
        self.server.start()

        logger.debug("Waiting for child process to report which port the server is running on.")
        self._port = port_q.get(block=True)

        # If the port is None, it means that none of the ports were available.
        if self._port is None:
            err = NoAvailablePortsException(
                f"None of the allowed callback ports are available. "
                f"The allowed ports are {' '.join(str(port) for port in self.allowed_ports)}"
            )
            logger.error(err.args[0], exc_info=err)
            raise err

    def shutdown(self) -> None:
        logger.info("Shutting down.")
        self.server.terminate()
        self._port = None

    def block_until_callback(self) -> MultiDict[str, str]:
        logger.debug("Waiting for callback.")
        while True:
            callback_args = self._callback_args_q.get(block=True)
            if "state" in callback_args and "code" in callback_args:
                logger.debug("Callback received!")
                return callback_args
            if "error" in callback_args:
                logger.debug("Error received.")
                return callback_args
            logger.debug("Invalid request. Ignoring.")

    def _run_server(
        self,
        callback_args_q: multiprocessing.Queue,
        port_q: multiprocessing.Queue,
    ) -> None:
        """
        Runs a WSGI server. Meant to run as a separate process.
        """

        @Request.application
        def app(request: Request) -> Response:
            if request.path != "/callback":
                return Response("Not Found", status=404)
            callback_args_q.put(request.args)
            return Response("Please return to the application.", 200)

        for port in self.allowed_ports:
            # There's technically a very slim race condition here.
            if not is_port_in_use(port):
                port_q.put(port)
                print(f"Listening on port {port}...")
                serve(app, host="0.0.0.0", port=port)
                return

        # If none of the allowed_ports are available, report failure.
        port_q.put(None)

    def __enter__(self) -> "CallbackListener":
        self.start()
        return self

    def __exit__(self, *exc: Any) -> None:
        self.shutdown()
