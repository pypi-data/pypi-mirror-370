# Copyright 2025 Luminary Cloud, Inc. All Rights Reserved.
from enum import IntEnum
from .._proto.output import output_pb2 as outputpb


class SpaceAveragingType(IntEnum):
    """
    How to average a spatial quantity over a surface.

    Attributes
    ----------
    MASS_FLOW
    AREA
    NO_AVERAGING
    """

    UNSPECIFIED = outputpb.INVALID_SPACE_AVERAGING_TYPE

    MASS_FLOW = outputpb.SPACE_MASS_FLOW_AVERAGING
    AREA = outputpb.SPACE_AREA_AVERAGING
    NO_AVERAGING = outputpb.SPACE_NO_AVERAGING
