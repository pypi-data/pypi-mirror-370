# Copyright 2023-2024 Luminary Cloud, Inc. All Rights Reserved.

from typing import Optional

from .client import Client, _DEFAULT_CLIENT


def set_default_client(client: Client) -> None:
    """
    Set the default client object used by wrappers.

    This may be useful for setting custom options or mocking the client for testing.

    Examples
    --------
    >>> options = [("grpc.keepalive_time_ms", 800)]
    >>> client = Client(grpc_channel_options=options)
    >>> set_default_client(client)
    """
    _DEFAULT_CLIENT.set(client)


def get_default_client() -> Client:
    """
    Get the default client object used by wrappers.
    """
    return _DEFAULT_CLIENT.get()
