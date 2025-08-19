# Copyright 2025 Luminary Cloud, Inc. All Rights Reserved.
from enum import IntEnum
from .._proto.output import output_pb2 as outputpb


class ResidualType(IntEnum):
    """
    Represents a Residual type.

    Attributes
    ----------
    ABSOLUTE
    RELATIVE
    MAX
    MIN
    """

    UNSPECIFIED = outputpb.INVALID_RESIDUAL_TYPE

    ABSOLUTE = outputpb.RESIDUAL_ABSOLUTE
    RELATIVE = outputpb.RESIDUAL_RELATIVE
    MAX = outputpb.RESIDUAL_MAX
    MIN = outputpb.RESIDUAL_MIN
