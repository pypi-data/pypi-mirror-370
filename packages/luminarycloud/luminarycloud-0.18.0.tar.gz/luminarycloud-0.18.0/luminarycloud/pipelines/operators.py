# Copyright 2025 Luminary Cloud, Inc. All Rights Reserved.
from dataclasses import dataclass

from .core import Operator, OperatorInputs, OperatorOutputs, PipelineOutput
from .parameters import StringPipelineParameter
from ..meshing import MeshGenerationParams


# Concrete PipelineOutput classes, i.e. the things that can "flow" in a Pipeline


class PipelineOutputGeometry(PipelineOutput):
    """A representation of a Geometry in a Pipeline."""

    pass


class PipelineOutputMesh(PipelineOutput):
    """A representation of a Mesh in a Pipeline."""

    pass


class PipelineOutputSimulation(PipelineOutput):
    """A representation of a Simulation in a Pipeline."""

    pass


# Operators


@dataclass
class ReadGeometryOutputs(OperatorOutputs):
    geometry: PipelineOutputGeometry
    """
    The Geometry identified by the given `geometry_id`, in the state it was in when the Pipeline was
    invoked. I.e. the latest GeometryVersion at that moment.
    """


class ReadGeometry(Operator[ReadGeometryOutputs]):
    """
    Reads a Geometry into the Pipeline.

    Parameters
    ----------
    geometry_id : str | StringPipelineParameter
        The ID of the Geometry to retrieve.

    Outputs
    -------
    geometry : PipelineOutputGeometry
        The latest GeometryVersion of the Geometry as of the moment the Pipeline was invoked.

    .. warning:: This feature is experimental and may change or be removed in the future.
    """

    def __init__(
        self,
        *,
        task_name: str | None = None,
        geometry_id: str | StringPipelineParameter,
    ):
        super().__init__(
            task_name,
            {"geometry_id": geometry_id},
            OperatorInputs(self),
            ReadGeometryOutputs._instantiate_for(self),
        )


@dataclass
class ModifyGeometryOutputs(OperatorOutputs):
    geometry: PipelineOutputGeometry
    """The modified Geometry, represented as a new GeometryVersion."""


# TODO: figure out what `mods` actually is. What does the non-pipeline geo mod interface look like?
class ModifyGeometry(Operator[ModifyGeometryOutputs]):
    """
    Modifies a Geometry.

    Parameters
    ----------
    mods : dict
        The modifications to apply to the Geometry.
    geometry : PipelineOutputGeometry
        The Geometry to modify.

    Outputs
    -------
    geometry : PipelineOutputGeometry
        The modified Geometry, represented as a new GeometryVersion.

    .. warning:: This feature is experimental and may change or be removed in the future.
    """

    def __init__(
        self,
        *,
        task_name: str | None = None,
        mods: list[dict],
        geometry: PipelineOutputGeometry,
    ):
        raise NotImplementedError("ModifyGeometry is not implemented yet.")
        super().__init__(
            task_name,
            {"mods": mods},
            OperatorInputs(self, geometry=(PipelineOutputGeometry, geometry)),
            ModifyGeometryOutputs._instantiate_for(self),
        )


@dataclass
class MeshOutputs(OperatorOutputs):
    mesh: PipelineOutputMesh
    """The Mesh generated from the given Geometry."""


class Mesh(Operator[MeshOutputs]):
    """
    Generates a Mesh from a Geometry.

    Parameters
    ----------
    max_cv_count : int
        The maximum number of control volumes to generate.
    geometry : PipelineOutputGeometry
        The Geometry to mesh.

    Outputs
    -------
    mesh : PipelineOutputMesh
        The generated Mesh.

    .. warning:: This feature is experimental and may change or be removed in the future.
    """

    def __init__(
        self,
        *,
        task_name: str | None = None,
        max_cv_count: int,
        geometry: PipelineOutputGeometry,
    ):
        super().__init__(
            task_name,
            {"max_cv_count": max_cv_count},
            OperatorInputs(self, geometry=(PipelineOutputGeometry, geometry)),
            MeshOutputs._instantiate_for(self),
        )

    # TODO: bring back the full MeshGenerationParams, but we need to be able to hydrate it from the
    # pipeline YAML. I can probably bake that logic into PipelineDictable, `from_pipeline_dict` or
    # something.
    # @classmethod
    # def _parse_params(cls, params: dict) -> dict:
    #     return {"mesh_gen_params": MeshGenerationParams.from_pipeline_dict(**params["mesh_gen_params"])}


@dataclass
class SimulateOutputs(OperatorOutputs):
    simulation: PipelineOutputSimulation
    """The Simulation."""


class Simulate(Operator[SimulateOutputs]):
    """
    Runs a Simulation.

    Parameters
    ----------
    sim_template_id : str | StringPipelineParameter
        The ID of the SimulationTemplate to use for the Simulation.
    mesh : PipelineOutputMesh
        The Mesh to use for the Simulation.

    Outputs
    -------
    simulation : PipelineOutputSimulation
        The Simulation.

    .. warning:: This feature is experimental and may change or be removed in the future.
    """

    def __init__(
        self,
        *,
        task_name: str | None = None,
        sim_template_id: str | StringPipelineParameter,
        mesh: PipelineOutputMesh,
    ):
        super().__init__(
            task_name,
            {"sim_template_id": sim_template_id},
            OperatorInputs(self, mesh=(PipelineOutputMesh, mesh)),
            SimulateOutputs._instantiate_for(self),
        )
