# Copyright 2023-2024 Luminary Cloud, Inc. All Rights Reserved.
import logging
from time import time, sleep
import grpc

from .._proto.api.v0.luminarycloud.mesh.mesh_pb2 import Mesh, GetMeshRequest
from .._client import Client

logger = logging.getLogger(__name__)


def wait_for_mesh(
    client: Client,
    mesh: Mesh,
    *,
    interval_seconds: float = 2,
    timeout_seconds: float = float("inf"),
) -> Mesh.MeshStatus.ValueType:
    """
    Waits for a mesh to be done processing.

    Parameters
    ----------
    client: Client
        A LuminaryCloud Client (see client.py)
    mesh: Mesh
        The mesh to wait for.
    interval_seconds: float
        Number of seconds between polls. Default is 2 seconds.
    timeout_seconds: float
        Number of seconds before the operation times out. Default is infinity.

    Raises
    ------
    TimeoutError
    """
    deadline = time() + timeout_seconds
    while True:
        if time() >= deadline:
            logger.error("`wait_for_mesh` timed out.")
            raise TimeoutError
        # It seems this call sometimes hangs. It seems as well that python gRPC is known to hang
        # in some cases, so we'll add a deadline and catch deadline exceeded errors to retry.
        try:
            response = client.GetMesh(GetMeshRequest(id=mesh.id), timeout=15)
        except grpc.RpcError as e:
            if e.code() == grpc.StatusCode.DEADLINE_EXCEEDED:
                logger.error("Deadline exceeded while waiting for mesh.")
                sleep(max(0, min(interval_seconds, deadline - time())))
                continue
            raise e
        status = response.mesh.status
        if status in [Mesh.MESH_STATUS_COMPLETED, Mesh.MESH_STATUS_FAILED]:
            return status
        sleep(max(0, min(interval_seconds, deadline - time())))
