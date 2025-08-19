# Copyright 2023-2025 Luminary Cloud, Inc. All Rights Reserved.
from collections.abc import Callable
from time import sleep
from typing import Any

import grpc
from grpc import (
    ClientCallDetails,
    UnaryUnaryClientInterceptor,
)

from luminarycloud.exceptions import AuthenticationError


class RetryInterceptor(UnaryUnaryClientInterceptor):
    """
    A retry interceptor that retries on status code RESOURCE_EXHAUSTED (i.e. rate-limited).

    This is required because, while the retry policy for the gRPC client is configurable via
    https://github.com/grpc/grpc-proto/blob/master/grpc/service_config/service_config.proto,
    the initial backoff is selected randomly between 0 and the configured value (also the
    number of attempts is capped at 5). We currently have a fixed-window rate-limiting system,
    and there's no way to guarantee that a retry will be attempted outside the current window
    using the service config.

    Note: the default retry policy is to retry on UNAVAILABLE (i.e. transient unavailability),
    which is why that status is not being handled here.

    Another note: although AFAIK not documented explicitly, each call made by this interceptor is
    subject to the retry policy of the underlying channel. (Glancing at the source, interceptors
    just call the underlying channel, and the service config is passed to the underlying channel,
    e.g. grpc.secure_channel.) So each "inner" retry handles transient failures while the "outer"
    calls handled by this interceptor handles failures due to rate-limiting.
    """

    def intercept_unary_unary(
        self,
        continuation: Callable[[ClientCallDetails, Any], grpc.Call],
        client_call_details: ClientCallDetails,
        request: Any,
    ) -> grpc.Call:
        retryable_codes = [grpc.StatusCode.RESOURCE_EXHAUSTED, grpc.StatusCode.UNAVAILABLE]
        n_max_retries = 20
        max_retry_seconds = 20
        backoffs = [min(i * 2, max_retry_seconds) for i in range(1, n_max_retries)]
        for backoff in backoffs:  # in seconds
            call = continuation(client_call_details, request)
            if call.code() not in retryable_codes:
                break
            if call.code() == grpc.StatusCode.UNAVAILABLE:
                # if the auth plugin errors, that unfortunately shows up here as UNAVAILABLE, so we
                # have to check for auth plugin exceptions that shouldn't be retried by matching
                # their name in the details string
                details = call.details() or ""
                if "InteractiveAuthException" in details:
                    break
            sleep(backoff)
        try:
            call.result()
        except grpc.RpcError as e:
            if e.code() == grpc.StatusCode.UNAUTHENTICATED:
                raise AuthenticationError(e.details(), e.code()) from None
            raise
        return call
