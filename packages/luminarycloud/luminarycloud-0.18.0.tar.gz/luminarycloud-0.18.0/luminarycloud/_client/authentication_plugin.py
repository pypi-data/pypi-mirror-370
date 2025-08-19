# Copyright 2023 Luminary Cloud, Inc. All Rights Reserved.

import grpc

from .._auth import Auth0Client


class AuthenticationPlugin(grpc.AuthMetadataPlugin):
    """
    Adds authentication headers for each outgoing RPC.

    Supports two authentication methods:
    1. Bearer token authentication using Auth0
    2. API key authentication using x-api-key header

    The __call__ function is invoked for every outgoing call. If using Bearer token
    and the token has expired or doesn't exist, the Auth0 client tries to acquire
    a new one.
    """

    def __init__(self, auth0_client: Auth0Client, api_key: str | None = None):
        super(AuthenticationPlugin, self).__init__()
        self.auth0_client = auth0_client
        self.api_key = api_key

    def __call__(
        self,
        context: grpc.AuthMetadataContext,
        # Takes the list of headers to add as tuples
        callback: grpc.AuthMetadataPluginCallback,
    ) -> None:
        try:
            if self.api_key and isinstance(self.api_key, str):
                metadata = [("x-api-key", self.api_key)]
            else:
                access_token = self.auth0_client.fetch_access_token()
                metadata = [("authorization", "Bearer " + access_token)]
            callback(metadata, None)
        except Exception as err:
            callback(None, err)
