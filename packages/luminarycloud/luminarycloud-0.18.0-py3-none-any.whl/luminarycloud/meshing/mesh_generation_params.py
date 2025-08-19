# Copyright 2023-2024 Luminary Cloud, Inc. All Rights Reserved.
from dataclasses import dataclass, field
from typing import Sequence

from .._proto.api.v0.luminarycloud.mesh import mesh_pb2 as meshpb
from ..params.geometry import (
    AnnularCylinder,
    Cube,
    Cylinder,
    OrientedCube,
    Shape,
    Sphere,
    SphereShell,
    Surface,
    Volume,
)
from ..types import Vector3
from .sizing_strategy import MaxCount, Minimal, MinimalCount, SizingStrategy, TargetCount
from ..pipeline_util.dictable import PipelineDictable


@dataclass(kw_only=True)
class VolumeMeshingParams(PipelineDictable):
    """Volume meshing parameters."""

    volumes: list[Volume]
    "The volumes to mesh"
    min_size: float
    "The minimum mesh element size in meters; should be > 0.0"
    max_size: float
    "The maximum mesh element size in meters; should be > 0.0"

    def _to_proto(self) -> meshpb.MeshGenerationParams.VolumeParams:
        proto = meshpb.MeshGenerationParams.VolumeParams()
        proto.min_size = self.min_size
        proto.max_size = self.max_size
        proto.volumes.extend(int(volume._lcn_id) for volume in self.volumes)
        return proto


@dataclass(kw_only=True)
class ModelMeshingParams(PipelineDictable):
    """Model meshing parameters."""

    surfaces: Sequence[Surface | str]
    "The surfaces to mesh"

    # Defaults copied from ts/frontend/src/lib/paramDefaults/meshGenerationState.ts
    curvature: float = 8
    "Geometric control of the CAD edges and faces in degrees; should be > 0.0."
    max_size: float = 4.5
    "The maximum mesh element size in meters for elements that are part of the model; should be > 0.0."

    def _to_proto(self) -> meshpb.MeshGenerationParams.ModelParams:
        proto = meshpb.MeshGenerationParams.ModelParams()
        proto.curvature = self.curvature
        proto.max_size = self.max_size
        proto.surfaces.extend(
            surface.id if isinstance(surface, Surface) else surface for surface in self.surfaces
        )
        return proto


@dataclass(kw_only=True)
class BoundaryLayerParams(PipelineDictable):
    """Boundary layer meshing parameters."""

    surfaces: Sequence[Surface | str]
    "The surfaces to mesh"

    # Defaults copied from ts/frontend/src/lib/paramDefaults/meshingMultiPartState.ts
    n_layers: int = 40
    "Maximum number of layers within a boundary layer mesh; should be > 0."
    initial_size: float = 0.000001
    "Size of the mesh layer nearest the boundary surface in meters; should be > 0.0"
    growth_rate: float = 1.2
    "Ratio of size between 2 successive boundary mesh layers; should be >= 1.0."

    def _to_proto(self) -> meshpb.MeshGenerationParams.BoundaryLayerParams:
        proto = meshpb.MeshGenerationParams.BoundaryLayerParams()
        proto.n_layers = self.n_layers
        proto.initial_size = self.initial_size
        proto.growth_rate = self.growth_rate
        proto.surfaces.extend(
            surface.id if isinstance(surface, Surface) else surface for surface in self.surfaces
        )
        return proto


@dataclass(kw_only=True)
class RefinementRegion(PipelineDictable):
    """Refinement region parameters."""

    name: str
    "The name of the refinement region"
    h_limit: float
    "length scale limit in refinement region in meters"
    shape: Shape | None = None
    "The shape of the refinement region"

    def _to_proto(self) -> meshpb.MeshGenerationParams.RefinementRegionParams:
        proto = meshpb.MeshGenerationParams.RefinementRegionParams()
        if not self.name:
            raise ValueError("Refinement region name must be set")
        # We don't let the users set the IDs, so we take the names as the IDs. Prepend the ID with
        # some chars so that the frontend clients can still rely on its uniquess.
        proto.id = f"refinementRegionId{self.name}"
        proto.name = self.name
        proto.h_limit = self.h_limit
        if isinstance(self.shape, Sphere):
            proto.sphere.center.CopyFrom(self.shape.center._to_base_proto())
            proto.sphere.radius = self.shape.radius
        elif isinstance(self.shape, SphereShell):
            proto.sphere_shell.center.CopyFrom(self.shape.center._to_base_proto())
            proto.sphere_shell.radius = self.shape.radius
            proto.sphere_shell.radius_inner = self.shape.radius_inner
        elif isinstance(self.shape, Cube):
            proto.cube.min.CopyFrom(self.shape.min._to_base_proto())
            proto.cube.max.CopyFrom(self.shape.max._to_base_proto())
        elif isinstance(self.shape, OrientedCube):
            proto.oriented_cube.min.CopyFrom(self.shape.min._to_base_proto())
            proto.oriented_cube.max.CopyFrom(self.shape.max._to_base_proto())
            proto.oriented_cube.origin.CopyFrom(self.shape.origin._to_base_proto())
            proto.oriented_cube.x_axis.CopyFrom(self.shape.x_axis._to_base_proto())
            proto.oriented_cube.y_axis.CopyFrom(self.shape.y_axis._to_base_proto())
        elif isinstance(self.shape, Cylinder):
            proto.cylinder.start.CopyFrom(self.shape.start._to_base_proto())
            proto.cylinder.end.CopyFrom(self.shape.end._to_base_proto())
            proto.cylinder.radius = self.shape.radius
        elif isinstance(self.shape, AnnularCylinder):
            proto.annular_cylinder.start.CopyFrom(self.shape.start._to_base_proto())
            proto.annular_cylinder.end.CopyFrom(self.shape.end._to_base_proto())
            proto.annular_cylinder.radius = self.shape.radius
            proto.annular_cylinder.radius_inner = self.shape.radius_inner
        else:
            raise ValueError("Invalid shape")
        return proto


@dataclass(kw_only=True)
class MeshGenerationParams(PipelineDictable):
    """Mesh generation parameters."""

    geometry_id: str
    "The ID of the geometry to generate a mesh for"
    sizing_strategy: SizingStrategy = field(default_factory=MaxCount)
    "The sizing strategy to use"

    # Defaults copied from ts/frontend/src/lib/paramDefaults/meshGenerationState.ts
    min_size: float = 0.0001
    "The default minimum mesh element size in meters; should be > 0.0"
    max_size: float = 512
    "The default maximum mesh element size in meters; should be > 0.0"
    body_x_axis: Vector3 = field(default_factory=lambda: Vector3(1, 0, 0))
    "The x-axis of the body"
    body_y_axis: Vector3 = field(default_factory=lambda: Vector3(0, 1, 0))
    "The y-axis of the body"
    proximity_layers: int = 1
    "The number of proximity layers"
    add_refinement: bool = False
    "If true, automatically adds a refinement region around the body"

    volume_meshing_params: list[VolumeMeshingParams] = field(default_factory=list)
    "Custom meshing parameters for volumes. Overrides default meshing parameters."
    model_meshing_params: list[ModelMeshingParams] = field(default_factory=list)
    "Custom meshing parameters for models. Overrides default meshing parameters."
    boundary_layer_params: list[BoundaryLayerParams] = field(default_factory=list)
    "Custom meshing parameters for boundary layers. Overrides default meshing parameters."
    refinement_regions: list[RefinementRegion] = field(default_factory=list)
    "Refinement regions"

    use_wrap: bool = False
    "If true, falls back to using an approximation of the surfaces to mesh. This may ignore some of the parameters. Experimental and may be removed in the future."

    def _to_proto(self) -> meshpb.MeshGenerationParams:
        proto = meshpb.MeshGenerationParams(
            meshing_mode=meshpb.MeshGenerationParams.MeshingMode(
                default=meshpb.MeshGenerationParams.MeshingMode.Default()
            )
        )

        if isinstance(self.sizing_strategy, (MinimalCount, Minimal)):
            proto.mesh_complexity_params.type = (
                meshpb.MeshGenerationParams.MeshComplexityParams.ComplexityType.MIN
            )
            proto.meshing_mode.base.SetInParent()
        elif isinstance(self.sizing_strategy, TargetCount):
            proto.mesh_complexity_params.type = (
                meshpb.MeshGenerationParams.MeshComplexityParams.ComplexityType.TARGET
            )
            proto.mesh_complexity_params.target_cells = self.sizing_strategy.target_count
        elif isinstance(self.sizing_strategy, MaxCount):
            proto.mesh_complexity_params.type = (
                meshpb.MeshGenerationParams.MeshComplexityParams.ComplexityType.MAX
            )
            proto.mesh_complexity_params.limit_max_cells = int(self.sizing_strategy.max_count)
        else:
            raise ValueError("Invalid sizing strategy")

        proto.geometry_id = self.geometry_id
        proto.body_x_axis.CopyFrom(self.body_x_axis._to_ad_proto())
        proto.body_y_axis.CopyFrom(self.body_y_axis._to_ad_proto())
        proto.add_refinement = self.add_refinement
        proto.proximity_layers = self.proximity_layers

        proto.volume_params.extend(p._to_proto() for p in self.volume_meshing_params)
        proto.model_params.extend(p._to_proto() for p in self.model_meshing_params)
        proto.bl_params.extend(p._to_proto() for p in self.boundary_layer_params)
        proto.refine_params.extend(p._to_proto() for p in self.refinement_regions)

        proto.use_wrap = self.use_wrap

        rr_ids = [rr.id for rr in proto.refine_params]
        rr_ids_set = set(rr_ids)
        if len(rr_ids) != len(rr_ids_set):
            # We set the RR IDs as their names. That's why we show "names" in the error message.
            raise ValueError("Refinement region names must be unique")

        return proto
