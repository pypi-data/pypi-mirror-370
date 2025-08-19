# Copyright 2023-2024 Luminary Cloud, Inc. All Rights Reserved.
from enum import IntEnum
from .._proto.api.v0.luminarycloud.geometry import geometry_pb2


class GeometryStatus(IntEnum):
    """
    Represents the status of a geometry.

    Attributes
    ----------
    UNKNOWN
        Status is unknown.
    BUSY
        Geometry is being processed (importing, modifying, or other operations).
    HAS_FEATURE_ERRORS
        Geometry has feature errors, which should be resolved.
    READY_FOR_CHECK
        Geometry has no feature errors and is ready to be checked for meshing validity.
    CHECKING
        Geometry check is currently running to validate the geometry.
    FAILED_CHECK
        Geometry is not well-formed and cannot be used for meshing or
        simulation.
    READY
        Geometry is ready to use for meshing and simulation.
    """

    UNKNOWN = geometry_pb2.Geometry.UNKNOWN
    BUSY = geometry_pb2.Geometry.BUSY
    HAS_FEATURE_ERRORS = geometry_pb2.Geometry.HAS_FEATURE_ERRORS
    READY_FOR_CHECK = geometry_pb2.Geometry.READY_FOR_CHECK
    CHECKING = geometry_pb2.Geometry.CHECKING
    FAILED_CHECK = geometry_pb2.Geometry.FAILED_CHECK
    READY = geometry_pb2.Geometry.READY
