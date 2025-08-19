# Copyright 2023-2024 Luminary Cloud, Inc. All Rights Reserved.
from datetime import datetime
from os import PathLike
from copy import deepcopy
from typing import Optional, overload
from difflib import Differ

from .enum import (
    TableType,
)
from ._helpers.warnings import deprecated
from ._client import get_default_client
from ._helpers._simulation_params_from_json import simulation_params_from_json_path
from ._helpers._timestamp_to_datetime import timestamp_to_datetime
from ._proto.api.v0.luminarycloud.simulation_template import (
    simulation_template_pb2 as simtemplatepb,
)
from ._proto.client import simulation_pb2 as clientpb
from ._wrapper import ProtoWrapper, ProtoWrapperBase
from .types import SimulationTemplateID, ProjectID
from .tables import RectilinearTable
from .simulation_param import SimulationParam
from .outputs import (
    AnyOutputDefinitionType,
    create_output_definition,
    get_output_definition,
    list_output_definitions,
    update_output_definition,
    delete_output_definition,
    SurfaceAverageOutputDefinition,
    ForceOutputDefinition,
    ResidualOutputDefinition,
    InnerIterationOutputDefinition,
    PointProbeOutputDefinition,
    VolumeReductionOutputDefinition,
    DerivedOutputDefinition,
    StoppingCondition,
    GeneralStoppingConditions,
    list_stopping_conditions,
    get_stopping_condition,
    create_or_update_stopping_condition,
    delete_stopping_condition,
    get_general_stopping_conditions,
    update_general_stopping_conditions,
)


@ProtoWrapper(simtemplatepb.SimulationTemplate)
class SimulationTemplate(ProtoWrapperBase):
    """
    Represents a simulation template object.

    Simulation templates can be used to create simulations with the same parameters.
    However, unlike simulations, the parameters of a simulation template are mutable.
    They can be used to partially set up the parameters of a simulation and then be
    persisted to the Luminary Cloud backend.
    """

    id: SimulationTemplateID
    "Simulation template ID."
    name: str
    "Simulation template name."
    project_id: ProjectID
    "Project this simulation template belongs to."

    _proto: simtemplatepb.SimulationTemplate

    @property
    def create_time(self) -> datetime:
        return timestamp_to_datetime(self._proto.create_time)

    @property
    def update_time(self) -> datetime:
        return timestamp_to_datetime(self._proto.update_time)

    def sync_to_ui(self) -> None:
        """
        Sets this simulation template as the one that is used for the "Setup" tab in the UI.
        """
        req = simtemplatepb.SyncSimulationTemplateToUIRequest(id=self.id)
        get_default_client().SyncSimulationTemplateToUI(req)

    def update(
        self,
        *,
        name: Optional[str] = None,
        parameters: Optional[SimulationParam | PathLike] = None,
        copy_from: "Optional[SimulationTemplate | SimulationTemplateID | str]" = None,
    ) -> None:
        """
        Update simulation template.

        Parameters
        ----------
        name : str, optional
            New project name.
        parameters : SimulationParam or PathLike, optional
            New complete simulation parameters object or path to local JSON file containing
            simulation parameters. In the former case, the input argument is modified to reflect
            changes applied by the backend (server), for example due to presets. Any differences
            between input and result are printed on screen.
        copy_from : SimulationTemplate or SimulationTemplateID or str, optional
            Simulation template to copy. If provided, it will be deep-copied into this simulation
            template. Can pass a SimulationTemplate object or an ID of the template to copy.
        """
        return self._update(name=name, parameters=parameters, copy_from=copy_from)

    def _update(
        self,
        *,
        name: Optional[str] = None,
        parameters: Optional[SimulationParam | clientpb.SimulationParam | PathLike] = None,
        copy_from: "Optional[SimulationTemplate | SimulationTemplateID | str]" = None,
    ) -> None:
        """
        Update simulation template. See `update()` for more details.
        """
        req = simtemplatepb.UpdateSimulationTemplateRequest(id=self.id)

        if name is not None:
            req.name = name

        if parameters is not None:
            if isinstance(parameters, SimulationParam):
                param_proto = parameters._to_proto()
            elif isinstance(parameters, clientpb.SimulationParam):
                param_proto = clientpb.SimulationParam()
                param_proto.CopyFrom(parameters)
            else:
                param_proto = simulation_params_from_json_path(parameters)
            req.parameters.CopyFrom(param_proto)

        if copy_from is not None:
            if isinstance(copy_from, SimulationTemplate):
                req.copy_from = copy_from.id
            elif isinstance(copy_from, str):
                req.copy_from = copy_from
            else:
                raise ValueError(f"Invalid copy_from argument: {copy_from}")

        res: simtemplatepb.UpdateSimulationTemplateResponse = (
            get_default_client().UpdateSimulationTemplate(req)
        )
        self._proto = res.simulation_template

        def print_diff(
            old: clientpb.SimulationParam | SimulationParam,
            new: clientpb.SimulationParam | SimulationParam,
        ) -> None:
            diffs = list(Differ().compare(str(old).split("\n"), str(new).split("\n")))
            has_diffs = False
            for diff in diffs:
                if diff.startswith("-") or diff.startswith("+"):
                    if not has_diffs:
                        print(
                            "The given parameters have been modified, both in memory and server-side, due to presets. The modifications:\n"
                        )
                        has_diffs = True
                    print(diff)

        # Show any inconsistency after the update and update the input argument.
        if isinstance(parameters, SimulationParam):
            old_param = deepcopy(parameters)
            parameters._from_proto(self._proto.parameters)
            print_diff(old_param, parameters)
        elif isinstance(parameters, clientpb.SimulationParam):
            print_diff(parameters, self._proto.parameters)
            parameters.CopyFrom(self._proto.parameters)

    def delete(self) -> None:
        """
        Delete the simulation template.
        """
        req = simtemplatepb.DeleteSimulationTemplateRequest(id=self.id)
        get_default_client().DeleteSimulationTemplate(req)

    def get_parameters(self) -> SimulationParam:
        """
        Returns a copy of the simulation parameters associated with this template.
        """
        return SimulationParam.from_proto(self._proto.parameters)

    @deprecated(
        "Use get_parameters() instead. This method will be removed in a future release.",
    )
    def get_simulation_param(self) -> SimulationParam:
        """
        Returns a copy of the simulation parameters associated with this template.
        """
        return self.get_parameters()

    def list_tables(
        self,
        table_type: Optional[TableType] = None,
    ) -> list[RectilinearTable]:
        """
        Lists the tables available in the simulation template.

        Parameters
        ----------
        table_type : TableType
            (Optional) Filter the list to only include this type of table.

        Returns
        -------
        list[RectilinearTable]
            List of tables.
        """
        res: list[RectilinearTable] = []
        for id, metadata in self._proto.parameters.table_references.items():
            if table_type is None or table_type.value == metadata.table_type:
                res.append(
                    RectilinearTable(
                        id=id,
                        name=metadata.uploaded_filename,
                        table_type=TableType(metadata.table_type),
                    )
                )
        return res

    def list_output_definitions(self) -> list[AnyOutputDefinitionType]:
        """
        List output definitions in this simulation template.
        """
        return list_output_definitions(self.id)

    def get_output_definition(self, id: str) -> AnyOutputDefinitionType:
        """
        Get an output definition.

        Parameters
        ----------
        id : str
            ID of the output definition to retrieve.
        """
        return get_output_definition(self.id, id)

    def delete_output_definition(self, id: str) -> None:
        """
        Delete an output definition.

        Parameters
        ----------
        id : str
            ID of the output definition to delete.
        """
        delete_output_definition(self.id, id)

    @overload
    def create_output_definition(
        self,
        output_definition: SurfaceAverageOutputDefinition,
    ) -> SurfaceAverageOutputDefinition: ...

    @overload
    def create_output_definition(
        self,
        output_definition: ForceOutputDefinition,
    ) -> ForceOutputDefinition: ...

    @overload
    def create_output_definition(
        self,
        output_definition: ResidualOutputDefinition,
    ) -> ResidualOutputDefinition: ...

    @overload
    def create_output_definition(
        self,
        output_definition: InnerIterationOutputDefinition,
    ) -> InnerIterationOutputDefinition: ...

    @overload
    def create_output_definition(
        self,
        output_definition: PointProbeOutputDefinition,
    ) -> PointProbeOutputDefinition: ...

    @overload
    def create_output_definition(
        self,
        output_definition: VolumeReductionOutputDefinition,
    ) -> VolumeReductionOutputDefinition: ...

    @overload
    def create_output_definition(
        self,
        output_definition: DerivedOutputDefinition,
    ) -> DerivedOutputDefinition: ...

    def create_output_definition(
        self, output_definition: AnyOutputDefinitionType
    ) -> AnyOutputDefinitionType:
        """
        Create an output definition in this simulation template.

        Parameters
        ----------
        output_definition : AnyOutputDefinitionType
            Output definition to create.
        """
        return create_output_definition(self.id, output_definition)

    @overload
    def update_output_definition(
        self,
        id: str,
        output_definition: SurfaceAverageOutputDefinition,
    ) -> SurfaceAverageOutputDefinition: ...

    @overload
    def update_output_definition(
        self,
        id: str,
        output_definition: ForceOutputDefinition,
    ) -> ForceOutputDefinition: ...

    @overload
    def update_output_definition(
        self,
        id: str,
        output_definition: ResidualOutputDefinition,
    ) -> ResidualOutputDefinition: ...

    @overload
    def update_output_definition(
        self,
        id: str,
        output_definition: InnerIterationOutputDefinition,
    ) -> InnerIterationOutputDefinition: ...

    @overload
    def update_output_definition(
        self,
        id: str,
        output_definition: PointProbeOutputDefinition,
    ) -> PointProbeOutputDefinition: ...

    @overload
    def update_output_definition(
        self,
        id: str,
        output_definition: VolumeReductionOutputDefinition,
    ) -> VolumeReductionOutputDefinition: ...

    @overload
    def update_output_definition(
        self,
        id: str,
        output_definition: DerivedOutputDefinition,
    ) -> DerivedOutputDefinition: ...

    def update_output_definition(
        self, id: str, output_definition: AnyOutputDefinitionType
    ) -> AnyOutputDefinitionType:
        """
        Update an output definition in this simulation template.

        Parameters
        ----------
        id : str
            ID of the output definition to update.
        output_definition : AnyOutputDefinitionType
            Updated output definition. The ID of this output definition must be present in the set
            of output definitions owned by this simulation template.
        """
        return update_output_definition(self.id, id, output_definition)

    def list_stopping_conditions(self) -> list[StoppingCondition]:
        """
        List all stopping conditions for this simulation template.
        """
        return list_stopping_conditions(self.id)

    def get_stopping_condition(self, id: str) -> StoppingCondition:
        """
        Get a stopping condition from this simulation template.

        Parameters
        ----------
        id : str
            ID of the stopping condition to get.
        """
        return get_stopping_condition(self.id, id)

    def create_or_update_stopping_condition(
        self,
        output_definition_id: str,
        threshold: float,
        start_at_iteration: int | None = None,
        averaging_iterations: int | None = None,
        iterations_to_consider: int | None = None,
    ) -> StoppingCondition:
        """
        Create a stopping condition on an output definition, or update it if the output definition
        already has one.

        While this API will prevent the creation of multiple stopping conditions on the same output
        definition, the UI does not. If this endpoint is invoked with an output definition that has
        multiple stopping conditions, all but one will be deleted, and the remaining one will be
        updated.

        Parameters
        ----------
        output_definition_id : str
            ID of the output definition on which the stopping condition is based.
        threshold : float
            Threshold for the stopping condition.
            For a residual stopping condition, the condition is met when the residual drops below
            this threshold.  For a non-residual-based stopping condition, the condition is met when the
            moving average in the monitored output deviates by less than this percentage of its current
            moving average over the specified number of iterations.
        start_at_iteration : int, optional
            The condition will evaluate to false before this iteration is reached.
        averaging_iterations : int, optional
            Trailing average window length. Number of iterations over which the monitored value is
            averaged before the threshold check is applied.
        iterations_to_consider : int, optional
            Number of (averaged) iterations to consider when determining maximum percent
            deviation from the current value.
        """
        return create_or_update_stopping_condition(
            self.id,
            output_definition_id,
            threshold,
            start_at_iteration,
            averaging_iterations,
            iterations_to_consider,
        )

    def delete_stopping_condition(self, id: str) -> None:
        """
        Delete a stopping condition from this simulation template.

        Parameters
        ----------
        id : str
            ID of the stopping condition to delete.
        """
        return delete_stopping_condition(self.id, id)

    def get_general_stopping_conditions(self) -> GeneralStoppingConditions:
        """
        Get the general stopping conditions for this simulation template.

        .. warning:: This feature is experimental and may change or be removed without notice.
        """
        return get_general_stopping_conditions(self.id)

    def update_general_stopping_conditions(
        self,
        max_iterations: int | None = None,
        max_physical_time: float | None = None,
        max_inner_iterations: int | None = None,
        stop_on_any: bool | None = None,
    ) -> GeneralStoppingConditions:
        """
        Update the general stopping conditions for this simulation template.

        .. warning:: This feature is experimental and may change or be removed without notice.

        Parameters
        ----------
        max_iterations : int, optional
            Maximum number of iterations.
        max_physical_time : float, optional
            Maximum physical time for transient simulations.
        max_inner_iterations : int, optional
            Maximum number of inner iterations for implicit-time transient simulations.
        stop_on_any : bool, optional
            If true, stop the simulation if any stopping condition is met. Else, stop when all
            stopping conditions are met. Default: false.
        """
        return update_general_stopping_conditions(
            self.id, max_iterations, max_physical_time, max_inner_iterations, stop_on_any
        )

    def to_code(self, hide_defaults: bool = True) -> str:
        """
        Returns the python code that generates (from scratch) an identical SimulationTemplate object.
        By default parameters with default values are omitted, this change be changed with
        hide_defaults=False.
        """
        parameters = self.get_parameters()
        param_code = parameters.to_code(hide_defaults)
        code, param_code = param_code.split("\n\n\n")

        # Modify the header note included by SimulationParam.to_code.
        code = code.replace("SimulationParam", "SimulationTemplate")
        code += "\n\n\n"
        code += '# Create a new simulation template or modify the one that is synced with the UI "Setup" tab.\n'
        code += f'project = luminarycloud.get_project("{self.project_id}")\n'
        code += f"template = project.create_simulation_template(name={self.name})\n"
        code += '# TODO(USER): To modify the "Setup" template, uncomment the line below and comment out the line above.\n'
        code += "# template = project.list_simulation_templates()[0] # Setup template\n\n"

        if parameters._table_references:
            code += "# Upload tabular data.\n"
            code += (
                "# TODO(USER): Provide the local file paths (they are not stored by Luminary).\n"
            )
            for name, table in sorted(parameters._table_references.items()):
                table_type = TableType(table.table_type).__repr__().split(": ")[0][1:]
                code += f'project.create_table({table_type}, "path/to/{table.uploaded_filename}", template)\n'
            code += "# This shows the available tables:\n"
            code += "# print(template.list_tables())\n\n"

        code += "# Define the simulation parameters.\n"
        code += param_code
        code += "\n# Update the simulation template with the parameters.\n"
        code += "template.update(parameters=obj)\n\n"

        code += "# Define the outputs for monitoring simulations.\n"
        code += "# This assumes the outputs do not exist yet, to modify an exiting output use\n"
        code += "# update_output_definition instead of create_output_definition, the former\n"
        code += "# requires the definition ID, that is obtained from list_output_definitions.\n"
        output_definitions = self.list_output_definitions()
        for i, definition in enumerate(output_definitions):
            if i == 0:
                code += "output_list = []\n"
            output_code = definition._to_code_helper("new_output", hide_defaults)
            for line in output_code.split("\n"):
                # Omit ID because we are generating for create_output_definition.
                if line and not line.startswith("new_output.id"):
                    code += f"{line}\n"
            code += "output_list.append(template.create_output_definition(new_output))\n\n"

        code += "# Define the basic and output-based stopping conditions.\n"
        gsc = self.get_general_stopping_conditions()
        code += f"template.update_general_stopping_conditions({gsc.max_iterations}, "
        code += f"{gsc.max_physical_time}, {gsc.max_inner_iterations}, {gsc.stop_on_any})\n"

        for i, sc in enumerate(self.list_stopping_conditions()):
            if i == 0:
                code += "\n# Output-based conditions require the ID of the associated output.\n"
            # Find the old output to use the new ID created by create_output_definition.
            for j, od in enumerate(output_definitions):
                if sc.output_definition_id == od.id:
                    code += f"template.create_or_update_stopping_condition(output_list[{j}].id, "
                    code += f"{sc.threshold}, {sc.start_at_iteration}, {sc.averaging_iterations}, "
                    code += f"{sc.iterations_to_consider})\n"
                    break

        return code


def get_simulation_template(id: SimulationTemplateID) -> SimulationTemplate:
    """
    Retrieve a specific simulation template by ID.

    Parameters
    ----------
    id : str
        Simulation template ID.
    """
    req = simtemplatepb.GetSimulationTemplateRequest(id=id)
    res = get_default_client().GetSimulationTemplate(req)
    return SimulationTemplate(res.simulation_template)
