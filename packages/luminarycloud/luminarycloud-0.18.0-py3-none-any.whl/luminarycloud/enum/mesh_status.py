# Copyright 2023-2024 Luminary Cloud, Inc. All Rights Reserved.
from enum import IntEnum
from .._proto.api.v0.luminarycloud.mesh.mesh_pb2 import Mesh


class MeshStatus(IntEnum):
    """
    Represents the status of a mesh.

    Attributes
    ----------
    UNSPECIFIED
        A well-formed mesh resource will never have this value.
    CREATING
        Mesh is being created.
    COMPLETED
        Mesh was created successfully and can be used to create simulations.
    FAILED
        Mesh was not created successfully and is unusable.
    """

    UNSPECIFIED = Mesh.MESH_STATUS_UNSPECIFIED
    CREATING = Mesh.MESH_STATUS_CREATING
    COMPLETED = Mesh.MESH_STATUS_COMPLETED
    FAILED = Mesh.MESH_STATUS_FAILED
