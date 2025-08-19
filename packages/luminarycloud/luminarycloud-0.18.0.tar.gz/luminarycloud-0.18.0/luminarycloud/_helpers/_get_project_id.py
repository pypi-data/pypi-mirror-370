from ..simulation import get_simulation
from ..geometry import Geometry
from ..solution import Solution
from ..mesh import Mesh


def _get_project_id(entity: Geometry | Solution | Mesh) -> str | None:
    """
    A helper function to get the project id from various entities.
    Returns the project id or None if the entity type is unknown.

    Parameters
    ----------
    entiry: Geometry | Solution | Mesh
        The entity to get the project id from.
    """
    if isinstance(entity, Solution):
        solution: Solution = entity
        sim = get_simulation(solution.simulation_id)
        return sim.project_id
    elif isinstance(entity, Mesh):
        mesh: Mesh = entity
        return mesh.project_id
    elif isinstance(entity, Geometry):
        geometry: Geometry = entity
        project = geometry.project()
        return project.id
    else:
        return None
