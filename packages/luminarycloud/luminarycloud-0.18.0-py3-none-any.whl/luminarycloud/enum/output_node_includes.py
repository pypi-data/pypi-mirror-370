# Copyright 2025 Luminary Cloud, Inc. All Rights Reserved.
from enum import IntEnum
from .._proto.frontend.output import output_pb2 as feoutputpb


class OutputNodeIncludes(IntEnum):
    """
    Values that can be included in an output node.

    Attributes
    ----------
    BASE
    TIME_AVERAGE
    COEFFICIENT
    COEFFICIENT_TIME_AVERAGE
    RESIDUAL
    MAX_DEV
    INNER
    """

    UNSPECIFIED = feoutputpb.INVALID_OUTPUT_INCLUDE

    BASE = feoutputpb.OUTPUT_INCLUDE_BASE
    TIME_AVERAGE = feoutputpb.OUTPUT_INCLUDE_TIME_AVERAGE
    COEFFICIENT = feoutputpb.OUTPUT_INCLUDE_COEFFICIENT
    COEFFICIENT_TIME_AVERAGE = feoutputpb.OUTPUT_INCLUDE_COEFFICIENT_TIME_AVERAGE
    RESIDUAL = feoutputpb.OUTPUT_INCLUDE_RESIDUAL
    MAX_DEV = feoutputpb.OUTPUT_INCLUDE_MAX_DEV
    INNER = feoutputpb.OUTPUT_INCLUDE_INNER
