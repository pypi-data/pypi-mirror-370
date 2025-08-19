# Copyright 2025 Luminary Cloud, Inc. All rights reserved.
from enum import IntEnum
from .._proto.base import base_pb2 as basepb


class Vector3Component(IntEnum):
    """
    Components of a 3-D vector.
    Attributes
    ----------
    UNSPECIFIED
    X
    Y
    Z
    """

    UNSPECIFIED = basepb.VECTOR_3_COMPONENT_INVALID
    X = basepb.VECTOR_3_COMPONENT_X
    Y = basepb.VECTOR_3_COMPONENT_Y
    Z = basepb.VECTOR_3_COMPONENT_Z
