# Copyright 2023-2024 Luminary Cloud, Inc. All Rights Reserved.
import tarfile
from typing import BinaryIO, Optional, cast, TYPE_CHECKING
from os import PathLike

import luminarycloud as lc

from ._client import get_default_client
from ._helpers.download import (
    download_surface_solution,
    download_volume_solution,
    download_surface_deformation_template,
    download_surface_sensitivity_data,
    download_parameter_sensitivity_data,
)
from ._helpers.file_chunk_stream import FileChunkStream
from ._proto.api.v0.luminarycloud.solution import solution_pb2 as solutionpb
from ._wrapper import ProtoWrapper, ProtoWrapperBase
from .types import SimulationID, SolutionID

if TYPE_CHECKING:
    from .simulation import Simulation


# Helper for some methods of Solution.
def _handle_surface_data_stream(stream: FileChunkStream, dst: Optional[PathLike] = None) -> None:
    data = stream.read().decode()
    with open(dst or stream.filename, "w") as f:
        f.write(data)


@ProtoWrapper(solutionpb.Solution)
class Solution(ProtoWrapperBase):
    """Represents a solution for a simulation."""

    id: SolutionID
    "Solution ID."
    simulation_id: SimulationID
    "Simulation ID of parent"
    iteration: int
    "Iteration index of the solution."
    physical_time: float
    "The physical time, in seconds, of the solution iteration (for transient simulations)."

    _proto: solutionpb.Solution

    def simulation(self) -> "Simulation":
        "Get the simulation that generated this solution."
        return lc.get_simulation(SimulationID(self._proto.simulation_id))

    def download_surface_data(self) -> tarfile.TarFile:
        """
        Download the raw surface data as a gzipped tarball containing .vtu files.

        Returns
        -------
        tarfile.Tarfile

        Examples
        --------
        >>> with solution.download_surface_data() as streaming_tar_file:
        ...     path = f"./surface_data_{solution.id}"
        ...     streaming_tar_file.extractall(path)
        ...     print(f"Extracted files to {path}:")
        ...     print("\\t" + "\\n\\t".join(os.listdir(path)))
        Extracted files to ./surface_data_<solution.id>:
            surface_0_bound_z_minus.vtu
            summary.vtm
            surface_0_bound_airfoil.vtu
            surface_0_bound_z_plus.vtu
            surface_0_bound_farfield.vtu
        """
        stream = download_surface_solution(
            get_default_client(),
            self.id,
        )
        return tarfile.open(
            name=stream.filename,
            fileobj=cast(BinaryIO, stream),
            mode="r|gz",
        )

    def download_volume_data(self, single_precision: bool = False) -> tarfile.TarFile:
        """
        Download volume solution for a completed steady simulation as a gzipped tarball containing .vtu & .vtp files.

        The output may be broken up into multiple .vtu files for large simulations.

        Parameters
        ----------
        single_precision : bool
            If True, outputs floating point fields in single precision. Defaults to False.

        Returns
        -------
        tarfile.Tarfile

        Examples
        --------
        >>> with solution.download_volume_data() as streaming_tar_file:
        ...     path = f"./volume_data_{solution.id}"
        ...     streaming_tar_file.extractall(path)
        ...     print(f"Extracted files to {path}:")
        ...     for root, dirs, filenames in os.walk(path):
        ...         print("\\t" + "\\n\\t".join([os.path.join(root, file) for file in filenames]))
        Extracted files to ./volume_data_<solution.id>:
                ./volume_data_<solution.id>/volume_data_<solution.id>.vtm
                ./volume_data_<solution.id>/volume_data_<solution.id>/volume_data_<solution.id>_1_0.vtp
                ./volume_data_<solution.id>/volume_data_<solution.id>/volume_data_<solution.id>_3_0.vtp
                ./volume_data_<solution.id>/volume_data_<solution.id>/volume_data_<solution.id>_4_0.vtp
                ./volume_data_<solution.id>/volume_data_<solution.id>/volume_data_<solution.id>_2_0.vtp
                ./volume_data_<solution.id>/volume_data_<solution.id>/volume_data_<solution.id>_0_0.vtu
        """
        stream = download_volume_solution(
            get_default_client(),
            self.id,
            single_precision=single_precision,
        )
        return tarfile.open(
            name=stream.filename,
            fileobj=cast(BinaryIO, stream),
            mode="r|gz",
        )

    def download_surface_deformation_template(self, dst: Optional[PathLike] = None) -> None:
        """
        Download the surface deformation template into the destination file or into a default-named
        file. The template has 4 numerical columns [[id], [x], [y], [z]] for the IDs and XYZ
        coordinates of the mesh nodes of the deformation/sensitivity surfaces. Deformation templates
        are created by a simulation if SimulationParam.adjoint.deformed_coords_id is set to
        'template'. The point coordinates in the template can be modified and used in
        Project.set_surface_deformation to create simulations with volume mesh morphing.
        """
        stream = download_surface_deformation_template(get_default_client(), self.id)
        _handle_surface_data_stream(stream, dst)

    def download_surface_sensitivity_data(self, dst: Optional[PathLike] = None) -> None:
        """
        Download the surface sensitivity data associated with an adjoint solution into the
        destination file or into a default-named file. The data consists of 4 numerical columns
        [[id], [df/dx], [df/dy], [df/dz]] for the IDs and sensitivity of the adjoint output with
        respect to the coordinates of the mesh nodes of the deformation/sensitivity surfaces.
        The IDs of the sensitivity data are consistent with the node IDs of the surface deformation.
        """
        stream = download_surface_sensitivity_data(get_default_client(), self.id)
        _handle_surface_data_stream(stream, dst)

    def download_parameter_sensitivity_data(self, dst: Optional[PathLike] = None) -> None:
        """
        Download the parameter sensitivity data associated with an adjoint solution into the
        destination file or into a default-named file. The data consists of parameter names and
        sensitivity values (d "adjoint output" / d "SimulationParam parameter").

        .. warning:: This is a very experimental feature, likely to change in the future in favor of
        including the sensitivities in a SimulationParam object directly.
        """
        stream = download_parameter_sensitivity_data(get_default_client(), self.id)
        _handle_surface_data_stream(stream, dst)
