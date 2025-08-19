# Copyright 2023-2024 Luminary Cloud, Inc. All Rights Reserved.
from enum import IntEnum
from .._proto.output import reference_values_pb2 as refvalpb


class ReferenceValuesType(IntEnum):
    """
    Method of specification for the reference values used in force and moment computations.

    Attributes
    ----------
    UNSPECIFIED
    PRESCRIBE_VALUES
        The specified reference values will be used.
    FARFIELD_VALUES
        Only the area and length reference values will be used; pressure,
        temperature, and velocity values will be taken from the far field
        boundary specification.
    """

    UNSPECIFIED = refvalpb.REFERENCE_VALUES_INVALID
    PRESCRIBE_VALUES = refvalpb.REFERENCE_PRESCRIBE_VALUES
    FARFIELD_VALUES = refvalpb.REFERENCE_FARFIELD_VALUES
