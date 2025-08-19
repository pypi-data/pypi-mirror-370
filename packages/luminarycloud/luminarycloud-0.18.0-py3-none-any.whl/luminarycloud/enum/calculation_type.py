# Copyright 2023-2024 Luminary Cloud, Inc. All Rights Reserved.
from enum import IntEnum
from .._proto.api.v0.luminarycloud.simulation import simulation_pb2


class CalculationType(IntEnum):
    """
    Represents a calculation type when calculating surface outputs or defining OutputNodes.

    Attributes
    ----------
    UNSPECIFIED
    AGGREGATE
        Calculate a single value for the surfaces altogether.
    PER_SURFACE
        Calculate a separate value for each surface.
    DIFFERENCE
        Output the difference between the aggregate of all the IN surfaces and the aggregate of all
        the OUT surfaces. Not valid for a GetSimulationSurfaceQuantityOutputRequest, only for use
        in OutputNodes.
    """

    UNSPECIFIED = simulation_pb2.CalculationType.CALCULATION_TYPE_UNSPECIFIED
    AGGREGATE = simulation_pb2.CalculationType.CALCULATION_TYPE_AGGREGATE
    PER_SURFACE = simulation_pb2.CalculationType.CALCULATION_TYPE_PER_SURFACE
    DIFFERENCE = simulation_pb2.CalculationType.CALCULATION_TYPE_DIFFERENCE
