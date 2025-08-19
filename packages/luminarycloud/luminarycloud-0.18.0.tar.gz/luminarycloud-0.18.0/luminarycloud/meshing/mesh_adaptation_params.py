from .._proto.api.v0.luminarycloud.mesh import mesh_pb2 as meshpb
from ..types import SimulationID


class MeshAdaptationParams:
    """
    Parameters used to create a new mesh with mesh adaptation.

    .. warning:: This feature is experimental and may change or be removed without notice.

    Attributes
    ----------
    source_simulation_id : str
        (Required) The simluation ID of a previously completed simulation. The
        source simulation will be used to extract the input mesh and mesh
        adaptation sensor from the solution.

    target_cv_count : int
        (Required) Target count of mesh CVs.

    h_ratio : float
        (Required) Boundary layer scaling.

    aspect_ratio : float
        (Optional) Cell aspect ratio limit.
    """

    source_simulation_id: SimulationID
    target_cv_count: int
    h_ratio: float
    aspect_ratio: float

    def __init__(
        self,
        source_simulation_id: str,
        target_cv_count: int,
        h_ratio: float,
        aspect_ratio: float = 0.0,
    ) -> None:
        self.source_simulation_id = SimulationID(source_simulation_id)
        self.target_cv_count = target_cv_count
        self.h_ratio = h_ratio
        self.aspect_ratio = aspect_ratio

    def _to_proto(self) -> meshpb.MeshAdaptationParams:
        return meshpb.MeshAdaptationParams(
            source_simulation_id=self.source_simulation_id,
            target_cv_count=self.target_cv_count,
            h_ratio=self.h_ratio,
            aspect_ratio=self.aspect_ratio,
        )
