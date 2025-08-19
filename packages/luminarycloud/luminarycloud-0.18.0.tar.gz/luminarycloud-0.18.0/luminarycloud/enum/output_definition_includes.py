# Copyright 2025 Luminary Cloud, Inc. All Rights Reserved.
from enum import IntEnum
from .._proto.frontend.output import output_pb2 as feoutputpb


class OutputDefinitionIncludes(IntEnum):
    """
    Values that can be included in an output definition.

    Attributes
    ----------
    BASE
        The output value itself.
    TIME_AVERAGE
        A moving average of the output value.
    COEFFICIENT
        The coefficient of the output value (only valid for forces and moments).
    COEFFICIENT_TIME_AVERAGE
        A moving average of the coefficient of the output value (only valid for forces and moments).
    MAX_DEV
        The moving average of the output value that is used for convergence monitoring.
    """

    UNSPECIFIED = feoutputpb.INVALID_OUTPUT_INCLUDE

    BASE = feoutputpb.OUTPUT_INCLUDE_BASE
    TIME_AVERAGE = feoutputpb.OUTPUT_INCLUDE_TIME_AVERAGE
    COEFFICIENT = feoutputpb.OUTPUT_INCLUDE_COEFFICIENT
    COEFFICIENT_TIME_AVERAGE = feoutputpb.OUTPUT_INCLUDE_COEFFICIENT_TIME_AVERAGE
    MAX_DEV = feoutputpb.OUTPUT_INCLUDE_MAX_DEV
