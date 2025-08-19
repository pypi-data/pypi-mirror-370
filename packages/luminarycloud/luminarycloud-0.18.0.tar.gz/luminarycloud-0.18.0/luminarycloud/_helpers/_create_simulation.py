# Copyright 2023-2024 Luminary Cloud, Inc. All Rights Reserved.
import logging
from typing import Optional

from .._proto.api.v0.luminarycloud.simulation.simulation_pb2 import (
    Simulation,
    SimulationOptions,
    CreateSimulationRequest,
)
from .._client import Client
from ..enum import GPUType

logger = logging.getLogger(__name__)


def create_simulation(
    client: Client,
    project_id: str,
    mesh_id: str,
    name: str,
    simulation_template_id: str,
    *,
    named_variable_set_version_id: Optional[str] = None,
    description: str = "",
    batch_processing: bool = True,
    gpu_type: Optional[GPUType] = None,
    gpu_count: Optional[int] = None,
) -> Simulation:

    logger.debug(f"Calling gRPC CreateSimulation with project_id {project_id}, mesh_id {mesh_id}")
    response = client.CreateSimulation(
        CreateSimulationRequest(
            project_id=project_id,
            mesh_id=mesh_id,
            simulation_template_id=simulation_template_id,
            named_variable_set_version_id=named_variable_set_version_id or "",
            name=name,
            description=description,
            simulation_options=SimulationOptions(
                batch_processing=batch_processing,
                gpu_type=gpu_type.value if gpu_type is not None else GPUType.UNSPECIFIED.value,
                gpu_count=gpu_count or 0,
            ),
        )
    )
    return response.simulation
