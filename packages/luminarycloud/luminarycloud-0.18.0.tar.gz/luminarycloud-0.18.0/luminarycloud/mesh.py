# Copyright 2023-2024 Luminary Cloud, Inc. All Rights Reserved.
from datetime import datetime

from typing_extensions import TYPE_CHECKING

import luminarycloud as lc

from ._client import get_default_client
from ._helpers._timestamp_to_datetime import timestamp_to_datetime
from ._helpers._wait_for_mesh import wait_for_mesh
from ._proto.api.v0.luminarycloud.mesh import mesh_pb2 as meshpb
from ._wrapper import ProtoWrapper, ProtoWrapperBase
from .enum import MeshStatus
from .geometry_version import GeometryVersion, get_geometry_version
from .meshing.metadata import MeshMetadata
from .types import MeshID, ProjectID

if TYPE_CHECKING:
    from .project import Project


@ProtoWrapper(meshpb.Mesh)
class Mesh(ProtoWrapperBase):
    """Represents a Mesh object."""

    id: MeshID
    "Mesh ID."
    name: str
    "Mesh name."
    status: MeshStatus
    "Mesh status. May not reflect the current status."
    project_id: ProjectID
    "ID of the project containing this mesh."

    _proto: meshpb.Mesh

    @property
    def create_time(self) -> datetime:
        return timestamp_to_datetime(self._proto.create_time)

    def project(self) -> "Project":
        """
        Get the project this mesh belongs to.
        """
        return lc.get_project(ProjectID(self._proto.project_id))

    def geometry_version(self) -> GeometryVersion | None:
        """
        Get the geometry version associated with this mesh.

        Returns
        -------
        GeometryVersion | None
            The geometry version associated with this mesh, or None if the mesh has no geometry version.
        """
        if self._proto.geometry_version_id == "":
            return None
        return get_geometry_version(self._proto.geometry_version_id)

    def update(
        self,
        *,
        name: str = "",
    ) -> None:
        """
        Update mesh attributes.

        Mutates self.

        Parameters
        ----------
        name : str
            New mesh name, maximum length of 256 characters.
        """
        req = meshpb.UpdateMeshRequest(
            id=self.id,
            name=name,
        )
        res: meshpb.UpdateMeshResponse = get_default_client().UpdateMesh(req)
        self._proto = res.mesh

    def wait(
        self,
        *,
        interval_seconds: float = 5,
        timeout_seconds: float = float("inf"),
    ) -> MeshStatus:
        """
        Wait until the mesh has either completed or failed processing.

        Parameters
        ----------
        interval_seconds : float, optional
            Number of seconds between polls. Default is 5 seconds.
        timeout_seconds : float, optional
            Number of seconds before timeout.

        Returns
        -------
        luminarycloud.enum.MeshStatus
            Current status of the mesh.
        """
        wait_for_mesh(
            get_default_client(),
            self._proto,
            interval_seconds=interval_seconds,
            timeout_seconds=timeout_seconds,
        )
        self._proto = get_mesh(self.id)._proto
        return self.status

    def refresh(self) -> "Mesh":
        """
        Sync the Mesh object with the backend.

        Returns
        -------
        Mesh
            Updated mesh consistent with the backend.
        """
        self._proto = get_mesh(self.id)._proto
        return self

    def delete(self) -> None:
        """
        Delete the mesh.
        """
        req = meshpb.DeleteMeshRequest(
            id=self.id,
        )
        get_default_client().DeleteMesh(req)

    def get_metadata(self) -> MeshMetadata:
        """
        Get the metadata for this mesh.
        """
        return get_mesh_metadata(self.id)

    def to_code(self) -> str:
        """
        Returns the Python code that recreates this mesh.

        Examples:
        --------
        >>> mesh = lc.get_mesh("mesh-123")
        >>> python_code = mesh.to_code()
        >>> print(python_code)
        """
        req = meshpb.GetMeshGenerationSdkCodeRequest(id=self.id)
        res: meshpb.GetMeshGenerationSdkCodeResponse = (
            get_default_client().GetMeshGenerationSdkCode(req)
        )
        return res.sdk_code


def get_mesh(id: MeshID) -> Mesh:
    """
    Get a specific mesh with the given ID.

    Parameters
    ----------
    id : str
        Mesh ID.
    """
    req = meshpb.GetMeshRequest(id=id)
    res = get_default_client().GetMesh(req)
    return Mesh(res.mesh)


def get_mesh_metadata(id: MeshID) -> MeshMetadata:
    """
    Returns the mesh metadata for the mesh with the given ID.

    Parameters
    ----------
    id : str
        Mesh ID.
    """
    res: meshpb.GetMeshMetadataResponse = get_default_client().GetMeshMetadata(
        meshpb.GetMeshMetadataRequest(id=id)
    )
    return MeshMetadata(res.mesh_metadata)
