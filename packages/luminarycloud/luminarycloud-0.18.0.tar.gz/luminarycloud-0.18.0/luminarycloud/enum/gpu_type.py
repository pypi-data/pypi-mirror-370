from enum import IntEnum
from .._proto.api.v0.luminarycloud.simulation import simulation_pb2 as simulationpb


class GPUType(IntEnum):
    """
    Represents a GPU type.
    """

    UNSPECIFIED = simulationpb.SimulationOptions.GPU_TYPE_UNSPECIFIED
    V100 = simulationpb.SimulationOptions.GPU_TYPE_V100
    A100 = simulationpb.SimulationOptions.GPU_TYPE_A100
