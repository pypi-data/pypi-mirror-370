# Copyright 2023-2024 Luminary Cloud, Inc. All Rights Reserved.
from enum import IntEnum
from .._proto.api.v0.luminarycloud.simulation.simulation_pb2 import Simulation


class SimulationStatus(IntEnum):
    """
    Represents the status of a simulation.

    Attributes
    ----------
    UNSPECIFIED
        A well-formed simulation resource will never have this value.
    PENDING
        Denotes that the simulation is waiting to be scheduled.
    ACTIVE
        Denotes that the simulation is running currently.
    COMPLETED
        Denotes that the simulation completed successfully.
    FAILED
        Denotes that the simulation completed in a failed state.
    SUSPENDED
        Denotes that the simulation has been suspended.
    """

    UNSPECIFIED = Simulation.SIMULATION_STATUS_UNSPECIFIED
    PENDING = Simulation.SIMULATION_STATUS_PENDING
    ACTIVE = Simulation.SIMULATION_STATUS_ACTIVE
    COMPLETED = Simulation.SIMULATION_STATUS_COMPLETED
    FAILED = Simulation.SIMULATION_STATUS_FAILED
    SUSPENDED = Simulation.SIMULATION_STATUS_SUSPENDED
