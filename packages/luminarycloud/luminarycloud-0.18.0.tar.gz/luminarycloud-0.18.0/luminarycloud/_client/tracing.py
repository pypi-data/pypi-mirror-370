# Copyright 2023-2025 Luminary Cloud, Inc. All Rights Reserved.
import logging
import re
from typing import Optional, Any

import requests
from grpc import Channel
from opentelemetry.exporter.otlp.proto.http.trace_exporter import OTLPSpanExporter
from opentelemetry.instrumentation.grpc import client_interceptor, intercept_channel
from opentelemetry.sdk.resources import SERVICE_NAME, SERVICE_VERSION, Resource
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import (
    BatchSpanProcessor,
    SpanExportResult,
)

from .logging_interceptor import _get_ai_notebook_id
from .. import __version__
from .._auth import Auth0Client
from .._version import __version__

logger = logging.getLogger(__name__)

# By default, OpenTelemetry Python uses W3C Trace Context and W3C Baggage for propagation:
# https://opentelemetry.io/docs/instrumentation/python/manual/#change-the-default-propagation-format


# This is a hack to get opentelemetry to skip SSL verification when exporting traces.
# We do it this way because opentelemetry overrides the `verify` option in their code when they make
# the POST request.
class InsecureSession(requests.Session):
    def post(self, *args: Any, **kwargs: Any) -> Any:
        kwargs["verify"] = False
        return super(InsecureSession, self).post(*args, **kwargs)


# We're creating our own SpanExporter here so that we can dynamically update the
# auth headers with the latest credentials across token refreshes.
class Auth0SpanExporter(OTLPSpanExporter):
    def __init__(
        self,
        auth0_client: Auth0Client,
        endpoint: str,
        verify_ssl: bool = True,
    ):
        session = None
        if not verify_ssl:
            session = InsecureSession()
        OTLPSpanExporter.__init__(self, endpoint=endpoint, session=session)
        self.auth0_client = auth0_client

    def export(self, spans: Any) -> SpanExportResult:
        token = self.auth0_client.access_token
        if token is None:
            logger.debug("No access token found. Skipping trace export.")
            return SpanExportResult.FAILURE
        headers = {
            "authorization": "Bearer " + token,
        }
        self._session.headers.update(headers)
        try:
            return OTLPSpanExporter.export(self, spans)
        except Exception as e:
            logger.debug(f"Failed to export traces: {e}")
            return SpanExportResult.FAILURE


class ApiKeySpanExporter(OTLPSpanExporter):
    """A span exporter that uses API key authentication."""

    def __init__(
        self,
        api_key: str,
        endpoint: str,
        verify_ssl: bool = True,
    ):
        session = None
        if not verify_ssl:
            session = InsecureSession()
        OTLPSpanExporter.__init__(self, endpoint=endpoint, session=session)
        # Always use masked key since it's just for logging
        self.api_key = "masked_key" if len(api_key) < 10 else api_key[:4] + "..." + api_key[-6:]

    def export(self, spans: Any) -> SpanExportResult:
        headers = {
            "x-api-key": self.api_key,
        }
        self._session.headers.update(headers)
        try:
            return OTLPSpanExporter.export(self, spans)
        except Exception as e:
            logger.debug(f"Failed to export traces: {e}")
            return SpanExportResult.FAILURE


def _get_collector_endpoint(primary_domain: str) -> str:
    """Get the opentelemetry collector endpoint given the primary domain."""
    return f"https://{primary_domain}/v1/traces"


def _get_trace_resource() -> Resource:
    resource = Resource(
        attributes={
            SERVICE_NAME: "python/sdk",
            SERVICE_VERSION: __version__,
            "notebook_id": _get_ai_notebook_id(),
        }
    )
    return resource


def _add_instrumentation(
    channel: Channel,
    endpoint: str,
    auth0_client: Optional[Auth0Client],
    api_key: Optional[str],
    verify_ssl: bool = True,
) -> Channel:
    provider = TracerProvider(resource=_get_trace_resource())
    if api_key:
        processor = BatchSpanProcessor(
            ApiKeySpanExporter(
                endpoint=endpoint,
                api_key=api_key,
                verify_ssl=verify_ssl,
            )
        )
    else:
        if auth0_client is None:
            raise ValueError("Either api_key or auth0_client must be provided")
        processor = BatchSpanProcessor(
            Auth0SpanExporter(
                endpoint=endpoint,
                auth0_client=auth0_client,
                verify_ssl=verify_ssl,
            )
        )
    provider.add_span_processor(processor)
    return intercept_channel(  # type: ignore[no-untyped-call]
        channel,
        client_interceptor(tracer_provider=provider),  # type: ignore[no-untyped-call]
    )


def add_instrumentation(
    channel: Channel,
    apiserver_domain: str,
    primary_domain: Optional[str],
    auth0_client: Optional[Auth0Client],
    api_key: Optional[str] = None,
) -> Channel:
    """Add tracing instrumentation to a gRPC channel.

    Args:
        channel: The gRPC channel to instrument.
        apiserver_domain: The domain of the API server.
        primary_domain: The primary domain to use for tracing.
        auth0_client: The Auth0 client to use for authentication.
        api_key: Optional API key to use for authentication instead of Auth0.

    Returns:
        The instrumented channel.
    """
    if primary_domain is None or "itar" in primary_domain:
        logger.debug("Tracing is disabled for this gRPC client.")
        return channel

    endpoint = _get_collector_endpoint(primary_domain)

    # skip SSL verification for internal domains
    verify_ssl = ".int." not in apiserver_domain
    if not verify_ssl:
        logger.debug("SSL verification will be skipped when exporting traces.")

    logger.debug("Adding tracing instrumentation to gRPC client.")
    return _add_instrumentation(
        channel,
        endpoint,
        auth0_client,
        api_key,
        verify_ssl,
    )
