# Copyright 2023-2024 Luminary Cloud, Inc. All Rights Reserved.
from enum import IntEnum
from .._proto.api.v0.luminarycloud.simulation.simulation_pb2 import (
    GetSimulationGlobalResidualsRequest,
)


class ResidualNormalization(IntEnum):
    """
    Represents a normalization method for residuals.

    Attributes
    ----------
    UNSPECIFIED
    ABSOLUTE
    RELATIVE
    """

    UNSPECIFIED = GetSimulationGlobalResidualsRequest.RESIDUAL_NORMALIZATION_UNSPECIFIED
    ABSOLUTE = GetSimulationGlobalResidualsRequest.RESIDUAL_NORMALIZATION_ABSOLUTE
    RELATIVE = GetSimulationGlobalResidualsRequest.RESIDUAL_NORMALIZATION_RELATIVE
