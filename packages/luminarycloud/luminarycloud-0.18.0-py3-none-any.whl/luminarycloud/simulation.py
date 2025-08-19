# Copyright 2023-2024 Luminary Cloud, Inc. All Rights Reserved.
import io
from datetime import datetime
from typing import Optional

from ._client import get_default_client
from ._helpers._timestamp_to_datetime import timestamp_to_datetime
from ._helpers._wait_for_simulation import wait_for_simulation
from ._helpers.warnings import deprecated
from ._proto.api.v0.luminarycloud.common import common_pb2 as commonpb
from ._proto.api.v0.luminarycloud.simulation import simulation_pb2 as simulationpb
from ._proto.api.v0.luminarycloud.solution import solution_pb2 as solutionpb
from ._proto.client import simulation_pb2 as clientpb
from ._proto.quantity import quantity_options_pb2 as quantityoptspb
from ._wrapper import ProtoWrapper, ProtoWrapperBase
from .enum import (
    AveragingType,
    CalculationType,
    QuantityType,
    ResidualNormalization,
    SimulationStatus,
    Vector3Component,
)
from .simulation_param import SimulationParam
from .reference_values import ReferenceValues
from .simulation_param import SimulationParam
from .solution import Solution
from .types import MeshID, ProjectID, SimulationID, Vector3Like
from .types.vector3 import _to_vector3_proto


class _DownloadedTextFile(io.StringIO):
    filename: str

    def __init__(self, file_proto: commonpb.File):
        super().__init__(file_proto.full_contents.decode())
        metadata = file_proto.metadata
        self.filename = metadata.name
        if metadata.ext:
            self.filename += "." + metadata.ext


@ProtoWrapper(simulationpb.Simulation)
class Simulation(ProtoWrapperBase):
    """Represents a simulation object."""

    id: SimulationID
    "Simulation ID."
    name: str
    "Simulation name."
    description: str
    "Simulation description."
    status: SimulationStatus
    "Simulation status. May not reflect current status."
    mesh_id: MeshID
    "ID of the simulation mesh."
    project_id: ProjectID
    "ID of the project containing this simulation."

    _proto: simulationpb.Simulation

    @property
    def create_time(self) -> datetime:
        return timestamp_to_datetime(self._proto.create_time)

    @property
    def update_time(self) -> datetime:
        return timestamp_to_datetime(self._proto.update_time)

    def update(
        self,
        *,
        name: str = None,
    ) -> None:
        """
        Update/Edit simulation attributes.

        Mutates self.

        Parameters
        ----------
        name : str, optional
            New project name.
        """
        req = simulationpb.UpdateSimulationRequest(
            id=self.id,
            name=name,
        )
        res = get_default_client().UpdateSimulation(req)
        self._proto = res.simulation

    def wait(
        self,
        *,
        print_residuals: bool = False,
        interval_seconds: float = 5,
        timeout_seconds: float = float("inf"),
    ) -> SimulationStatus:
        """
        Wait until the simulation is completed, failed, or suspended.

        Parameters
        ----------
        print_residuals : bool, optional
            If true, residual values for the latest completed iteration will be printed.
            Frequency is based on interval_seconds.
        interval : float, optional
            Number of seconds between polls.
        timeout : float, optional
            Number of seconds before timeout.

        Returns
        -------
        luminarycloud.enum.SimulationStatus
            Current status of the simulation.
        """
        wait_for_simulation(
            get_default_client(),
            self._proto,
            print_residuals=print_residuals,
            interval_seconds=interval_seconds,
            timeout_seconds=timeout_seconds,
        )
        self._proto = get_simulation(self.id)._proto
        return self.status

    def refresh(self) -> "Simulation":
        """
        Sync the Simulation object with the backend.

        Returns
        -------
        Simulation
            Updated simulation consistent with the backend.
        """
        self._proto = get_simulation(self.id)._proto
        return self

    def download_global_residuals(
        self,
        normalization: ResidualNormalization = ResidualNormalization.RELATIVE,
    ) -> _DownloadedTextFile:
        """
        Download global residuals in csv format.

        Parameters
        ----------
        normalization : ResidualNormalization, optional
            The type of normalization to use. Default is relative normalization.

        Returns
        -------
        io.StringIO
            Stream of text. The filename can be retrieved from the "filename" attribute of the
            object.

        Examples
        --------
        Create a Pandas dataframe:

        >>> from luminarycloud.enum import ResidualType
        >>> import pandas as pd
        >>> with simulation.download_global_residuals() as dl:
        ...     residuals_df = pd.read_csv(dl)

        Save to disk:

        >>> with download_global_residuals() as dl:
        ...     with open(dl.filename, "wb") as fp:
        ...         fp.write(dl.read())
        """
        req = simulationpb.GetSimulationGlobalResidualsRequest(
            id=self.id,
            residual_normalization=normalization.value,
        )
        res = get_default_client().GetSimulationGlobalResiduals(req)
        return _DownloadedTextFile(res.csv_file)

    def download_surface_output(
        self,
        quantity_type: QuantityType,
        surface_ids: list[str],
        *,
        reference_values: ReferenceValues = None,
        calculation_type: CalculationType = CalculationType.AGGREGATE,
        frame_id: str = "",
        force_direction: Optional[Vector3Like] = None,
        moment_center: Optional[Vector3Like] = None,
        averaging_type: AveragingType = AveragingType.UNSPECIFIED,
        vector_component: Vector3Component = Vector3Component.UNSPECIFIED,
    ) -> _DownloadedTextFile:
        """
        Downloads surface outputs (e.g. lift, drag, ...) in csv format.

        Parameters
        ----------
        quantity_type : luminarycloud.enum.QuantityType
            Surface quantity type to compute (e.g. lift, drag).
        surface_ids : list of str
            List of names of the surfaces to compute the quantities for.
            Should have at least one element.

        Other Parameters
        ----------------
        reference_values : ReferenceValues, optional
            Reference values used for computing forces, moments and
            other non-dimensional output quantities. If not provided, default
            reference values will be used.
        calculation_type : CalculationType, optional
            Whether the calculation should be done for all the surfaces together or each surface
            individually. Default is AGGREGATE.
        frame_id: str, optional
            The ID of the reference frame that this output should be
            reported in for "force" quantity types.
        force_direction : Vector3Like, optional
            The direction of the query component for "force" quantity types.
            Required for certain quantity types.
        moment_center : Vector3Like, optional
            The center of moment for "force" quantity types.
            Required for certain quantity types. Ignored if not applicable.
        averaging_type : AveragingType, optional
            The averaging method used to compute "surface average" quantity types.
            Ignored if not applicable.
        vector_component : Vector3Component, optional
            For 3-vector quantity types (e.g. `QuantityType.VELOCITY`), the component of the vector to extract.
            Ignored for scalar quantity types.

        Returns
        -------
        io.StringIO
            Stream of text. The filename can be retrieved from the "filename" attribute of the
            object.

        Examples
        --------
        Create a Pandas dataframe:

        >>> from luminarycloud.enum import QuantityType
        >>> import pandas as pd
        >>> with simulation.download_surface_output(QuantityType.LIFT, ["0/bound/airfoil"], frame_id="body_frame_id") as dl:
        ...     outputs_df = pd.read_csv(dl)

        Save to disk:

        >>> with simulation.download_surface_output(QuantityType.LIFT, ["0/bound/airfoil"]) as dl:
        ...     with open(dl.filename, "w") as fp:
        ...         fp.write(dl.read())
        """
        if quantity_type._has_tag(quantityoptspb.TAG_COEFFICIENT) and reference_values is None:
            print("WARNING: Quantity is a coefficient but reference values were not specified.")
        req = simulationpb.GetSimulationSurfaceQuantityOutputRequest(
            id=self.id,
            quantity_type=quantity_type.value,
            surface_ids=surface_ids,
            calculation_type=calculation_type.value,
            reference_values=(
                reference_values._to_proto() if reference_values else ReferenceValues()._to_proto()
            ),
            frame_id=frame_id,
            force_direction=_to_vector3_proto(force_direction) if force_direction else None,
            moment_center=_to_vector3_proto(moment_center) if moment_center else None,
            averaging_type=averaging_type.value,
            vector_component=vector_component.value,
        )
        res = get_default_client().GetSimulationSurfaceQuantityOutput(req)
        return _DownloadedTextFile(res.csv_file)

    def delete(self) -> None:
        """
        Delete the simulation.

        The simulation will be stopped first if running. This operation cannot be reverted and all
        the simulation data will be deleted as part of this request.
        """
        req = simulationpb.DeleteSimulationRequest(id=self.id)
        get_default_client().DeleteSimulation(req)

    def suspend(self) -> None:
        """
        Suspend the simulation.
        """
        req = simulationpb.SuspendSimulationRequest(id=self.id)
        get_default_client().SuspendSimulation(req)

    def list_solutions(self) -> list[Solution]:
        """
        List all solutions for this simulation in ascending order of iteration.
        """
        req = solutionpb.ListSolutionsRequest(simulation_id=self.id)
        res = get_default_client().ListSolutions(req)
        return [Solution(s) for s in res.solutions]

    def get_parameters(self) -> SimulationParam:
        """
        Returns the simulation parameters associated with this simulation to allow customization of
        the parameters.
        """
        req = simulationpb.GetSimulationParametersRequest(id=self.id)
        return SimulationParam.from_proto(get_default_client().GetSimulationParameters(req))

    @deprecated(
        "Use get_parameters() instead. This method will be removed in a future release.",
    )
    def get_simulation_param(self) -> SimulationParam:
        return self.get_parameters()

    # This is used by the assistant for the SDK Code shown in the Results tab.
    def _to_code(self) -> str:
        return f"""# This code shows how to modify the parameters of the current simulation to create a new one.
import luminarycloud as lc

current_simulation = lc.get_simulation("{self.id}")
params = current_simulation.get_parameters()

# TODO(USER): Modify the parameters.
# You can use params.find_parameter to help you find the parameters you wish to modify.
# params.find_parameter("mach")
# Alternatively, the Simulation SDK Code shown in the Setup tab, shows how to create the
# entire params object from scratch. The following line produces a similar result.
# print(params.to_code())

project = lc.get_project("{self.project_id}")
# Modify the setup (synced with UI), or an existing template, or create a new one.
template = project.list_simulation_templates()[0]
# template = lc.get_simulation_template("...")
# template = project.create_simulation_template("New Template")

template.update(parameters=params)

# NOTE: This starts a new simulation.
# This uses the mesh from the current simulation, you can use project.list_meshes() to find
# other meshes available in the project.
simulation = project.create_simulation(current_simulation.mesh_id, "New Simulation", template.id)
# Waiting for the simulation to finish is optional.
status = simulation.wait()
"""


def get_simulation(id: SimulationID) -> Simulation:
    """
    Retrieve a specific simulation by ID.

    Parameters
    ----------
    id : str
        Simulation ID.
    """
    req = simulationpb.GetSimulationRequest(id=id)
    res = get_default_client().GetSimulation(req)
    return Simulation(res.simulation)
