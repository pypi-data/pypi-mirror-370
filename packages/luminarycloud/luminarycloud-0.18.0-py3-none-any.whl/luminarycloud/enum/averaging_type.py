# Copyright 2023-2024 Luminary Cloud, Inc. All Rights Reserved.
from enum import IntEnum
from .._proto.api.v0.luminarycloud.simulation import simulation_pb2 as simulationpb


class AveragingType(IntEnum):
    """
    Represents an averaging method used to compute average surface quantities.

    Attributes
    ----------
    UNSPECIFIED
    AREA
        Average using the area of each face divided by the total area.
    MASS_FLOW
        Average using the mass flow at each face divided by the total mass flow.
    """

    UNSPECIFIED = simulationpb.AVERAGING_TYPE_UNSPECIFIED
    AREA = simulationpb.AVERAGING_TYPE_AREA
    MASS_FLOW = simulationpb.AVERAGING_TYPE_MASS_FLOW
