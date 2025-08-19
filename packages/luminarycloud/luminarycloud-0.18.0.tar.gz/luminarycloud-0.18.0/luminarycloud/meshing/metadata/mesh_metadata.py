from ..._proto.api.v0.luminarycloud.mesh import mesh_pb2 as meshpb
from ..._wrapper import ProtoWrapper, ProtoWrapperBase
from ...types import Vector3


@ProtoWrapper(meshpb.MeshMetadata.MeshStats)
class MeshStats(ProtoWrapperBase):
    """Contains stats about a part of a mesh."""

    n_points: int
    "The number of points."
    n_faces: int
    "The number of faces."
    n_cvs: int
    "The number of control volumes."
    min_coord: Vector3
    "The minimum coordinate."
    max_coord: Vector3
    "The maximum coordinate."

    _proto: meshpb.MeshMetadata.MeshStats


@ProtoWrapper(meshpb.MeshMetadata.Boundary)
class BoundaryMetadata(ProtoWrapperBase):
    """Represents a Mesh object."""

    name: str
    "The name of this mesh boundary."
    stats: MeshStats
    "The stats for this mesh boundary."

    _proto: meshpb.MeshMetadata.Boundary


@ProtoWrapper(meshpb.MeshMetadata.Zone)
class ZoneMetadata(ProtoWrapperBase):
    """Contains info about a zone in a mesh."""

    name: str
    "The name of this mesh zone."
    stats: MeshStats
    "The stats for this mesh zone."
    boundaries: list[BoundaryMetadata]
    "The boundaries in this mesh zone."

    _proto: meshpb.MeshMetadata.Zone


@ProtoWrapper(meshpb.MeshMetadata)
class MeshMetadata(ProtoWrapperBase):
    """Contains info about a Mesh."""

    zones: list[ZoneMetadata]
    "The zones in this mesh."

    _proto: meshpb.MeshMetadata
