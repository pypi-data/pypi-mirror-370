# Copyright 2025 Luminary Cloud, Inc. All Rights Reserved.
from enum import IntEnum
from .._proto.output import output_pb2 as outputpb


class VolumeReductionType(IntEnum):
    """
    How to reduce a volume output quantity over the domain.

    Attributes
    ----------
    MINIMUM
    MAXIMUM
    AVERAGE
    """

    UNSPECIFIED = outputpb.INVALID_VOLUME_REDUCTION_TYPE

    MINIMUM = outputpb.VOLUME_MINIMUM
    MAXIMUM = outputpb.VOLUME_MAXIMUM
    AVERAGE = outputpb.VOLUME_AVERAGING
