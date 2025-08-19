# Copyright 2023-2025 Luminary Cloud, Inc. All Rights Reserved.
import logging
import re
import atexit
from contextvars import ContextVar, Token
from collections.abc import Iterable
from typing import Any, Optional, Union

import grpc

from .._auth import Auth0Client
from .._proto.api.v0.luminarycloud.geometry.geometry_pb2_grpc import GeometryServiceStub
from .._proto.api.v0.luminarycloud.mesh.mesh_pb2_grpc import MeshServiceStub
from .._proto.api.v0.luminarycloud.output_node.output_node_pb2_grpc import OutputNodeServiceStub
from .._proto.api.v0.luminarycloud.output_definition.output_definition_pb2_grpc import (
    OutputDefinitionServiceStub,
)
from .._proto.api.v0.luminarycloud.stopping_condition.stopping_condition_pb2_grpc import (
    StoppingConditionServiceStub,
)
from .._proto.api.v0.luminarycloud.project.project_pb2_grpc import ProjectServiceStub
from .._proto.api.v0.luminarycloud.simulation.simulation_pb2_grpc import (
    SimulationServiceStub,
)
from .._proto.api.v0.luminarycloud.simulation_template.simulation_template_pb2_grpc import (
    SimulationTemplateServiceStub,
)
from .._proto.api.v0.luminarycloud.named_variable_set.named_variable_set_pb2_grpc import (
    NamedVariableSetServiceStub,
)
from .._proto.api.v0.luminarycloud.pipelines.pipelines_pb2_grpc import PipelineServiceStub
from .._proto.api.v0.luminarycloud.physics_ai.physics_ai_pb2_grpc import (
    PhysicsAiServiceStub,
)
from .._proto.api.v0.luminarycloud.inference.inference_pb2_grpc import InferenceServiceStub
from .._proto.api.v0.luminarycloud.thirdpartyintegration.onshape.onshape_pb2_grpc import (
    OnshapeServiceStub,
)
from .._proto.api.v0.luminarycloud.project_ui_state.project_ui_state_pb2_grpc import (
    ProjectUIStateServiceStub,
)
from .._proto.api.v0.luminarycloud.solution.solution_pb2_grpc import SolutionServiceStub
from .._proto.api.v0.luminarycloud.upload.upload_pb2_grpc import UploadServiceStub
from .._proto.api.v0.luminarycloud.vis.vis_pb2_grpc import VisAPIServiceStub
from .authentication_plugin import AuthenticationPlugin
from .config import LC_DOMAIN, LC_API_KEY
from .logging_interceptor import LoggingInterceptor
from .retry_interceptor import RetryInterceptor
from .rpc_error import rpc_error
from .tracing import add_instrumentation

logger = logging.getLogger(__name__)


class Client(
    ProjectServiceStub,
    MeshServiceStub,
    SimulationServiceStub,
    SimulationTemplateServiceStub,
    GeometryServiceStub,
    SolutionServiceStub,
    UploadServiceStub,
    VisAPIServiceStub,
    OutputNodeServiceStub,
    OutputDefinitionServiceStub,
    StoppingConditionServiceStub,
    NamedVariableSetServiceStub,
    PipelineServiceStub,
    PhysicsAiServiceStub,
    InferenceServiceStub,
    OnshapeServiceStub,
    ProjectUIStateServiceStub,
):
    """
    Creates a Luminary API client.

    The returned client automatically obtains access tokens for the Luminary API and
    sends them with each RPC call. See auth/auth.py for details.

    Supports "with" syntax to set as the default client for all API calls inside the
    "with" block. Exiting the block restores the previous default client.

    Parameters
    ----------
    target : str
        The URL of the API server.
    localhost : bool
        True if the API server is running locally.
    grpc_channel_options : Optional[Iterable[tuple[str, str]]]
        A list of gRPC channel args. The full list is available here:
        https://github.com/grpc/grpc/blob/v1.46.x/include/grpc/impl/codegen/grpc_types.h
    api_key : Optional[str]
        The API key to use for authentication.
    **kwargs : dict, optional
        Additional arguments are passed to Auth0Client. See _auth/auth.py.

    Examples
    --------
    Using the "with" syntax to set the default client within a scope:

    >>> import luminarycloud as lc
    >>> with lc.Client(access_token="blahblahblah"):
    >>>     project = lc.list_projects()[0]
    >>>     sims = project.list_simulations()
    """

    def __init__(
        self,
        target: str = LC_DOMAIN,
        localhost: bool = False,
        grpc_channel_options: Optional[Iterable[tuple[str, Union[str, int]]]] = None,
        channel_credentials: Optional[grpc.ChannelCredentials] = None,
        api_key: Optional[str] = LC_API_KEY,
        **kwargs: Any,
    ):
        self._target = target
        self._apiserver_domain = target.split(":", maxsplit=1)[0]
        # Initialize Auth0 client only if not using API key
        self._auth0_client = None if api_key else Auth0Client(**kwargs)
        # It seems that both python and golang cliens have trouble sometimes RPC calls getting
        # stuck. In go, setting some keepalive options seems to help, so we'll do the same here. See
        # https://github.com/grpc/grpc/blob/d8b7d55975b945a9dee40db5ee87f170590721d9/examples/python/keep_alive/greeter_client.py#L1.
        grpc_channel_options_with_keep_alive: list[tuple[str, Union[str, int]]] = [
            ("grpc.keepalive_time_ms", 50000),
            ("grpc.keepalive_timeout_ms", 5000),
            ("grpc.keepalive_permit_without_calls", 1),
            ("grpc.http2.max_pings_without_data", 10),
        ]
        if grpc_channel_options:
            grpc_channel_options_with_keep_alive.extend(grpc_channel_options)
        self._channel = self._create_channel(
            localhost, grpc_channel_options_with_keep_alive, channel_credentials, api_key
        )
        self._context_tokens: list[Token] = []
        self.__register_rpcs()

        # This cleanup handler is helpful for clean exiting e.g. if the authentication fails
        def cleanup(self: "Client", *args: Any) -> None:
            try:
                if hasattr(self, "_channel"):
                    self._channel.close()
            except Exception:
                pass

        self._cleanup = cleanup  # store reference to avoid garbage collection
        atexit.register(self._cleanup, self)

    @property
    def channel(self) -> grpc.Channel:
        return self._channel

    @property
    def apiserver_domain(self) -> str:
        return self._apiserver_domain

    @property
    def primary_domain(self) -> Optional[str]:
        return _get_primary_domain_for_apiserver_domain(self._apiserver_domain)

    @property
    def internal(self) -> bool:
        return _is_internal_domain_for_lc_apiserver(self._apiserver_domain)

    def get_token(self) -> str:
        return self._auth0_client.fetch_access_token() if self._auth0_client else ""

    def __enter__(self) -> "Client":
        self._context_tokens.append(_DEFAULT_CLIENT.set(self))
        return self

    def __exit__(self, *exc: Any) -> None:
        _DEFAULT_CLIENT.reset(self._context_tokens.pop())

    def _create_channel(
        self,
        localhost: bool = False,
        grpc_channel_options: Optional[Iterable[tuple[str, Union[str, int]]]] = None,
        channel_credentials: Optional[grpc.ChannelCredentials] = None,
        api_key: Optional[str] = None,
    ) -> grpc.Channel:
        if channel_credentials is None:
            if localhost:
                logger.debug("Using local channel credentials.")
                channel_credentials = grpc.local_channel_credentials()
            else:
                logger.debug("Using SSL channel credentials.")
                channel_credentials = grpc.ssl_channel_credentials()

        # Add authentication metadata
        auth_plugin: AuthenticationPlugin
        if api_key is not None:
            dummy_auth0_client = Auth0Client()  # dummy for type safety
            auth_plugin = AuthenticationPlugin(auth0_client=dummy_auth0_client, api_key=api_key)
        else:
            if self._auth0_client is None:
                raise ValueError("Either api_key or auth0_client must be provided")
            auth_plugin = AuthenticationPlugin(auth0_client=self._auth0_client, api_key=None)
        call_creds = grpc.metadata_call_credentials(auth_plugin)
        composite_creds = grpc.composite_channel_credentials(channel_credentials, call_creds)
        options = grpc_channel_options and list(grpc_channel_options)
        channel = grpc.secure_channel(
            self._target,
            composite_creds,
            options=options,
        )
        intercepted_channel = grpc.intercept_channel(
            channel,
            LoggingInterceptor(),
            RetryInterceptor(),
        )
        return add_instrumentation(
            intercepted_channel, self._target, self.primary_domain, self._auth0_client, api_key
        )

    def __register_rpcs(self) -> None:
        ProjectServiceStub.__init__(self, self._channel)
        MeshServiceStub.__init__(self, self._channel)
        SimulationServiceStub.__init__(self, self._channel)
        GeometryServiceStub.__init__(self, self._channel)
        UploadServiceStub.__init__(self, self._channel)
        SolutionServiceStub.__init__(self, self._channel)
        SimulationTemplateServiceStub.__init__(self, self._channel)
        VisAPIServiceStub.__init__(self, self._channel)
        OutputNodeServiceStub.__init__(self, self._channel)
        OutputDefinitionServiceStub.__init__(self, self._channel)
        StoppingConditionServiceStub.__init__(self, self._channel)
        PipelineServiceStub.__init__(self, self._channel)
        PhysicsAiServiceStub.__init__(self, self._channel)
        InferenceServiceStub.__init__(self, self._channel)
        NamedVariableSetServiceStub.__init__(self, self._channel)
        OnshapeServiceStub.__init__(self, self._channel)
        ProjectUIStateServiceStub.__init__(self, self._channel)
        for name, value in self.__dict__.items():
            if isinstance(value, grpc.UnaryUnaryMultiCallable):
                setattr(self, name, rpc_error(value))


def _is_internal_domain_for_lc_apiserver(domain_name: str) -> bool:
    """Returns true iff the domain is an internal (non-prod) apiserver domain."""
    return re.match(r"apis[\.-].+\.luminarycloud\.com", domain_name) is not None


def _get_primary_domain_for_apiserver_domain(apiserver_domain: str) -> Optional[str]:
    """
    Get the frontend (primary) domain given an apiserver domain
    apis.luminarycloud.com -> app.luminarycloud.com
    apis-foo.int.luminarycloud.com -> foo.int.luminarycloud.com
    """
    if apiserver_domain == "apis.luminarycloud.com":  # prod
        return "app.luminarycloud.com"
    if apiserver_domain == "apis-itar.luminarycloud.com":  # itar-prod
        return "app-itar.luminarycloud.com"
    elif _is_internal_domain_for_lc_apiserver(apiserver_domain):
        return re.sub(r"^apis[-\.]{1}", "", apiserver_domain)
    return None


_DEFAULT_CLIENT = ContextVar("luminarycloud_client", default=Client())
