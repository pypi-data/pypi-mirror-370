# Copyright 2023-2024 Luminary Cloud, Inc. All Rights Reserved.
from __future__ import annotations

import logging
import re
import uuid
from datetime import datetime
from os import PathLike, path
from typing import TYPE_CHECKING, Any, Dict, List, Optional, Union, Literal

import concurrent

import grpc

import luminarycloud as lc
from luminarycloud._helpers.named_variables import _named_variables_to_proto
from luminarycloud.params.simulation.adjoint_ import Adjoint

from ._client import get_default_client
from ._helpers import (
    create_geometry,
    create_simulation,
    simulation_params_from_json_path,
    timestamp_to_datetime,
    upload_c81_as_json,
    upload_file,
    upload_mesh,
    upload_table_as_json,
)
from ._helpers.warnings import deprecated
from ._proto.api.v0.luminarycloud.geometry import geometry_pb2 as geometrypb
from ._proto.api.v0.luminarycloud.mesh import mesh_pb2 as meshpb
from ._proto.api.v0.luminarycloud.named_variable_set import (
    named_variable_set_pb2 as namedvariablepb,
)
from ._proto.api.v0.luminarycloud.project import project_pb2 as projectpb
from ._proto.api.v0.luminarycloud.simulation import simulation_pb2 as simulationpb
from ._proto.api.v0.luminarycloud.simulation_template import (
    simulation_template_pb2 as simtemplatepb,
)
from ._proto.api.v0.luminarycloud.project_ui_state import (
    project_ui_state_pb2 as projectuistatepb,
)
from ._proto.client import simulation_pb2 as clientpb
from ._proto.table import table_pb2 as tablepb
from ._proto.hexmesh import hexmesh_pb2 as hexmeshpb
from ._proto.upload import upload_pb2 as uploadpb
from ._wrapper import ProtoWrapper, ProtoWrapperBase
from .enum import GPUType, MeshType, TableType
from .meshing import MeshAdaptationParams, MeshGenerationParams
from .simulation_param import SimulationParam
from .tables import RectilinearTable, create_rectilinear_table
from .types import MeshID, ProjectID, SimulationTemplateID, NamedVariableSetID, Expression, LcFloat
from .named_variable_set import get_named_variable_set

if TYPE_CHECKING:
    from .geometry import Geometry
    from .mesh import Mesh
    from .named_variable_set import NamedVariableSet
    from .simulation import Simulation
    from .simulation_template import SimulationTemplate


@ProtoWrapper(projectpb.Project)
class Project(ProtoWrapperBase):
    """Represents a Project object."""

    id: ProjectID
    name: str
    description: str
    storage_usage_bytes: int

    _proto: projectpb.Project

    @property
    def create_time(self) -> datetime:
        return timestamp_to_datetime(self._proto.create_time)

    @property
    def update_time(self) -> datetime:
        return timestamp_to_datetime(self._proto.update_time)

    def update(
        self,
        *,
        name: str = "",
        description: str = "",
    ) -> None:
        """
        Update/Edit project attributes.

        Mutates self.

        Parameters
        ----------
        name : str, optional
            New project name.
        description : str, optional
            New project description.
        """
        req = projectpb.UpdateProjectRequest(
            id=self.id,
            name=name,
            description=description,
        )
        res = get_default_client().UpdateProject(req)
        self._proto = res.project

    def delete(self) -> None:
        """
        Delete the project.
        """
        req = projectpb.DeleteProjectRequest(
            id=self.id,
        )
        get_default_client().DeleteProject(req)

    @property
    def url(self) -> str:
        return f"https://{get_default_client().primary_domain}/project/{self.id}"

    def create_geometry(
        self,
        cad_file_path: PathLike | str | List[PathLike | str],
        *,
        name: Optional[str] = None,
        scaling: Optional[float] = None,
        wait: bool = False,
    ) -> "Geometry":
        """
        Create a new geometry in the project by uploading supported CAD file(s).

        For more information on supported formats and best practices, see:
        https://docs.luminarycloud.com/en/articles/9274255-upload-cad

        Parameters
        ----------
        cad_file_path : PathLike | str | List[PathLike | str]
            Path(s) or URL to the CAD file(s) to upload.

        Other Parameters
        ----------------
        name : str, optional
            Name of the geometry on Luminary Cloud. A default name will be used
            if unset.
        scaling : float, optional
            Scaling to apply to the source CAD file upon import. Defaults to 1.0
            if unset.
        wait : bool, optional
            If set to True, this function will block until the geometry import
            completes. Otherwise, it will return immediately and the import will
            occur in the background. Defaults to False.

        Returns
        -------
        Geometry
            The newly created Geometry.

        Examples
        --------
        Basic usage with a wait parameter to ensure geometry is fully loaded:

        >>> geometry = project.create_geometry("path/to/cad/two_cubes.x_b", name="two cubes", wait=True)
        >>> geometry.check()  # Verify geometry integrity
        (True, [])

        Creating a geometry with a custom name, explicit scaling, and wait parameter to ensure
        geometry is fully loaded:

        >>> geometry = project.create_geometry(
        ...     cad_file_path="path/to/cad/model_name.step",
        ...     name="model_name",
        ...     scaling=1.0,
        ...     wait=True,
        ... )
        """
        _geometry = create_geometry(
            get_default_client(),
            project_id=self.id,
            cad_file_path=cad_file_path,
            name=name,
            scaling=scaling,
            wait=wait,
        )
        return lc.Geometry(_geometry)

    def list_geometries(self) -> "list[Geometry]":
        """
        List all geometries in project.

        Returns
        -------
        list[Geometry]
            A list of all available Geometries in the project.
        """
        req = geometrypb.ListGeometriesRequest(project_id=self.id)
        res: geometrypb.ListGeometriesResponse = get_default_client().ListGeometries(req)
        return [lc.Geometry(g) for g in res.geometries]

    def load_geometry_to_setup(self, geometry: "Geometry") -> None:
        """
        Load a geometry to the setup phase.
        NOTE: this operation is irreversible and deletes all the existing meshes and simulations
        in the project.

        Parameters
        ----------
        geometry : Geometry
            Geometry to load to the setup phase.
        """
        req = projectpb.LoadGeometryToSetupRequest(
            id=self.id,
            geometry_id=geometry.id,
        )
        get_default_client().LoadGeometryToSetup(req)

    def upload_mesh(
        self,
        path: PathLike | str,
        *,
        name: Optional[str] = None,
        scaling: Optional[float] = None,
        mesh_type: Optional[MeshType] = None,
        do_not_read_zones_openfoam: Optional[bool] = None,
    ) -> "Mesh":
        """
        Upload a mesh to the project.

        For more information on supported formats and best practices see:
        https://docs.luminarycloud.com/en/articles/9275233-upload-a-mesh

        Parameters
        ----------
        path : PathLike or str
            Path or URL to the mesh file to upload.

        Other Parameters
        ----------------
        name : str, optional
            Name of the mesh resource on Luminary Cloud. Defaults to the
            filename.
        scaling : float, optional
            If set, apply a scaling factor to the mesh.
        mesh_type : MeshType, optional
            The file format of the mesh file. Required for OpenFOAM format.
        do_not_read_zones_openfoam : bool, default False
            If true, disables reading cell zones in the polyMesh/cellZones file
            for OpenFOAM meshes.
        """
        _mesh = upload_mesh(
            get_default_client(),
            project_id=self.id,
            path=path,
            mesh_type=mesh_type,
            name=name,
            scaling=scaling,
            do_not_read_zones_openfoam=do_not_read_zones_openfoam,
        )
        return lc.Mesh(_mesh)

    @deprecated("Use create_or_get_mesh() instead", "0.10.0")
    def create_mesh(
        self,
        params: MeshAdaptationParams | MeshGenerationParams,
        *,
        name: str,
    ) -> "Mesh":
        """
        Create a new mesh in the project.

        .. deprecated:: 0.10.0
            `create_mesh()` will be removed in v0.11.0, it is replaced by
            `create_or_get_mesh()`.

        Parameters
        ----------
        params : MeshGenerationParams | MeshAdaptationParams
            The parameters to use to create the mesh. If generating a new mesh from an
            existing geometry, use MeshGenerationParams. If adapting a mesh from an existing,
            solution use MeshAdaptationParams.
        name : str
            (Optional) Mesh name. Max 256 characters.
        """

        client = get_default_client()

        req = meshpb.CreateMeshRequest(
            project_id=self.id,
            name=name,
        )

        if isinstance(params, meshpb.MeshGenerationParams):
            req.mesh_generation_params.CopyFrom(params)
        elif isinstance(params, MeshAdaptationParams):
            req.mesh_adaptation_params.CopyFrom(params._to_proto())
        elif isinstance(params, MeshGenerationParams):
            req.mesh_generation_params.CopyFrom(params._to_proto())
            list_geometry_entities_res: geometrypb.ListGeometryEntitiesResponse = (
                client.ListGeometryEntities(
                    geometrypb.ListGeometryEntitiesRequest(geometry_id=params.geometry_id)
                )
            )
            req.mesh_generation_params.volume_params.insert(
                0,
                meshpb.MeshGenerationParams.VolumeParams(
                    min_size=params.min_size,
                    max_size=params.max_size,
                    volumes=[body.lcn_id for body in list_geometry_entities_res.bodies],
                ),
            )
        else:
            raise ValueError("Invalid parameters")

        res: meshpb.CreateMeshResponse = client.CreateMesh(req)
        return lc.Mesh(res.mesh)

    def create_or_get_mesh(
        self,
        params: MeshAdaptationParams | MeshGenerationParams,
        *,
        name: str,
    ) -> "Mesh":
        """
        Create a new mesh in the project, or return an existing mesh with the same parameters
        if it already exists.

        Parameters
        ----------
        params : MeshGenerationParams | MeshAdaptationParams
            The parameters to use to create the mesh. If generating a new mesh from an
            existing geometry, use MeshGenerationParams. If adapting a mesh from an existing,
            solution use MeshAdaptationParams.
        name : str
            Mesh name. Max 256 characters.
        """

        try:
            return self.create_mesh(params, name=name)
        except grpc.RpcError as e:
            if e.code() == grpc.StatusCode.ALREADY_EXISTS:
                message = e.details()
                match = re.search(r"mesh-[a-f0-9-]+$", message)
                if match:
                    existing_mesh_id = match.group(0)
                    req = meshpb.GetMeshRequest(id=existing_mesh_id)
                    res = get_default_client().GetMesh(req)
                    return lc.Mesh(res.mesh)
            raise

    def _create_hex_mesh(
        self,
        names_to_file_paths: Dict[str, Union[PathLike[Any], str]],
        params: hexmeshpb.HexMeshSpec,
        use_internal_wrap: bool = False,
    ) -> "Mesh":
        """
        Creates a hex mesh. Only for internal use.
        """
        client = get_default_client()

        def upload_single_file(name: str, file_path: Union[PathLike[Any], str]) -> tuple[str, str]:
            if not str(file_path).endswith(".stl"):
                raise ValueError(f"File {file_path} must be a .stl file")
            finish_res = upload_file(
                client,
                self.id,
                uploadpb.ResourceParams(geometry_params=uploadpb.GeometryParams()),
                file_path,
            )[1]
            return name, finish_res.url

        names_to_uploaded_file_paths = {}
        with concurrent.futures.ThreadPoolExecutor() as executor:
            future_to_name = {
                executor.submit(upload_single_file, name, file_path): name
                for name, file_path in names_to_file_paths.items()
            }

            for future in concurrent.futures.as_completed(future_to_name):
                try:
                    name, url = future.result()
                    names_to_uploaded_file_paths[name] = url
                except Exception as exc:
                    name = future_to_name[future]
                    raise RuntimeError(f"Upload failed for {name}: {exc}")

        for name, url in names_to_uploaded_file_paths.items():
            params.names_to_file_urls[name] = url

        params.use_wrap = use_internal_wrap

        req = meshpb.CreateHexMeshRequest(project_id=self.id, hex_mesh_config=params)

        res: meshpb.CreateHexMeshResponse = client.CreateHexMesh(req)
        get_mesh_res = client.GetMesh(meshpb.GetMeshRequest(id=res.mesh_id))
        return lc.Mesh(get_mesh_res.mesh)

    def list_meshes(self) -> "list[Mesh]":
        """
        List all meshes in project.
        """
        req = meshpb.ListMeshesRequest(project_id=self.id)
        res = get_default_client().ListMeshes(req)
        return [lc.Mesh(m) for m in res.meshes]

    def create_table(
        self,
        table_type: TableType,
        table_file_path: PathLike | str,
        simulation_template: "SimulationTemplate",
    ) -> RectilinearTable:
        """
        Create a new table in the project and make it available in a simulation template.

        Parameters
        ----------
        table_type : TableType
            The type of table being created, this defines the format expected for the file.
        table_file_path : PathLike or str
            Path to the file (usually a csv or c81 file) with the data used to create the table.
        simulation_template : SimulationTemplate
            Simulation template that is updated with the new table.

        Returns
        -------
        RectilinearTable
            A reference to the created table, which can be used for tabulated simulation parameters.
            For example, profile boundary conditions.
        """
        uploaded_filename = path.basename(table_file_path)
        name = uploaded_filename.rsplit(".", maxsplit=1)[0]
        if table_type == TableType.AIRFOIL_PERFORMANCE:
            url = upload_c81_as_json(get_default_client(), self.id, table_file_path)
        else:
            table = create_rectilinear_table(table_type, table_file_path)
            url = upload_table_as_json(get_default_client(), self.id, name, table)
        if not url:
            raise RuntimeError("The table upload failed.")

        # Update the simulation template with the new table reference.
        params: SimulationParam = simulation_template.get_parameters()
        params._table_references[name] = tablepb.Metadata()
        params._table_references[name].url = url
        params._table_references[name].table_type = table_type.value
        params._table_references[name].uploaded_filename = uploaded_filename
        simulation_template.update(parameters=params)
        # The name is lost in to/from proto conversions so make it equal to the id for consistency.
        return RectilinearTable(id=name, name=name, table_type=table_type)

    def set_surface_deformation(
        self,
        file_path: PathLike | str,
        simulation_param: SimulationParam,
    ) -> None:
        """
        Upload a surface deformation file with global IDs and coordinates of the surface points and
        update the simulation params to use this deformation.

        .. warning:: This feature is experimental and may change or be removed without notice.

        Parameters
        ----------
        file_path : PathLike or str
            Path to the file with deformed coordinates of points.
        simulation_param : SimulationParam
            Simulation parameters that are updated with the deformation.
        """

        # Use the upload ID to identify the file, the backend will then retrieve the URL before
        # calling the solver.
        simulation_param.adjoint = simulation_param.adjoint or Adjoint()
        simulation_param.adjoint.deformed_coords_id = upload_file(
            get_default_client(),
            self.id,
            uploadpb.ResourceParams(surf_deform_params=uploadpb.SurfDeformParams()),
            file_path,
        )[0]

    def create_simulation(
        self,
        mesh_id: MeshID,
        name: str,
        simulation_template_id: str,
        *,
        _named_variable_set_id: Optional[NamedVariableSetID] = None,
        description: str = "",
        batch_processing: bool = True,
        gpu_type: Optional[GPUType] = None,
        gpu_count: Optional[int] = None,
    ) -> "Simulation":
        """
        Create a new simulation.

        Parameters
        ----------
        mesh_id : str
            Mesh ID.
        name : str
            Simulation name. If empty, a default name will be generated.
        simulation_template_id : str
            ID of the SimulationTemplate used to set up the simulation.

        Other Parameters
        ----------------
        description : str, optional
            Simulation description.
        batch_processing : bool, default True
            If True, batch processing will be used for this
            simulation.
            Use Batch Processing on simulations that are not time-sensitive to
            save up to 65% in credits.
        gpu_type : GPUType, optional
            GPU type to use for the simulation.
        gpu_count : int, optional
            Number of GPUs to use for the simulation. Must be specified to a
            positive value if `gpu_type` is specified.
        """

        named_variable_set_version_id: Optional[str] = None
        if _named_variable_set_id is not None:
            named_variable_set = get_named_variable_set(_named_variable_set_id)
            named_variable_set_version_id = named_variable_set._version_id

        _simulation = create_simulation(
            get_default_client(),
            self.id,
            mesh_id,
            name,
            simulation_template_id,
            named_variable_set_version_id=named_variable_set_version_id,
            description=description,
            batch_processing=batch_processing,
            gpu_type=gpu_type,
            gpu_count=gpu_count,
        )
        return lc.Simulation(_simulation)

    def list_simulations(self) -> "list[Simulation]":
        """
        List all simulations in project.
        """
        req = simulationpb.ListSimulationsRequest(project_id=self.id)
        res = get_default_client().ListSimulations(req)
        return [lc.Simulation(s) for s in res.simulations]

    def list_simulation_templates(self) -> "list[SimulationTemplate]":
        """
        List all simulation templates in project. The first one in the list is the "setup" template,
        which is the one that is synced to the Setup tab in the UI.
        """
        req = simtemplatepb.ListSimulationTemplatesRequest(project_id=self.id)
        res = get_default_client().ListSimulationTemplates(req)
        return [lc.SimulationTemplate(s) for s in res.simulation_templates]

    def create_simulation_template(
        self,
        name: str,
        *,
        parameters: Optional[SimulationParam] = None,
        params_json_path: Optional[PathLike | str] = None,
        copy_from: "Optional[SimulationTemplate | SimulationTemplateID | str]" = None,
    ) -> "SimulationTemplate":
        """
        Create a new simulation template object.

        Parameters
        ----------
        name : str
            Human-readable name to identify the template.
            Does not need to be unique. Max 256 characters.

        Other Parameters
        ----------------
        parameters : SimulationParam, optional
            Complete simulation parameters. Ignored if `params_json_path` is set.
        params_json_path : PathLike or str, optional
            Path to local JSON file containing simulation params.
        copy_from : SimulationTemplate or str, optional
            Simulation template to copy. If provided, the new template will be a copy of this one.
            Can pass a SimulationTemplate object or an ID of the template to copy.
        """
        if (
            int(params_json_path is not None)
            + int(parameters is not None)
            + int(copy_from is not None)
            > 1
        ):
            raise ValueError("Only one of parameters, params_json_path, or copy_from can be set")

        param_proto: clientpb.SimulationParam | None = None
        copy_from_id: str | None = None

        if params_json_path is not None:
            param_proto = simulation_params_from_json_path(params_json_path)
        elif parameters is not None:
            param_proto = parameters._to_proto()
        elif copy_from is not None:
            if isinstance(copy_from, lc.SimulationTemplate):
                copy_from_id = copy_from.id
            else:
                copy_from_id = copy_from

        req = simtemplatepb.CreateSimulationTemplateRequest(
            project_id=self.id, name=name, parameters=param_proto, copy_from=copy_from_id
        )
        res = get_default_client().CreateSimulationTemplate(req)
        return lc.SimulationTemplate(res.simulation_template)

    def create_named_variable_set(
        self, name: str, named_variables: dict[str, LcFloat]
    ) -> NamedVariableSet:
        """
        Create a new named variable set.

        .. warning:: This feature is experimental and may change or be removed without notice.
        """
        req = namedvariablepb.CreateNamedVariableSetRequest(
            project_id=self.id,
            name=name,
            named_variables=_named_variables_to_proto(named_variables),
            request_id=str(uuid.uuid4()),
        )
        res: namedvariablepb.CreateNamedVariableSetResponse = (
            get_default_client().CreateNamedVariableSet(req)
        )
        return lc.NamedVariableSet(res.named_variable_set)

    def list_named_variable_sets(self) -> list[NamedVariableSet]:
        """
        .. warning:: This feature is experimental and may change or be removed without notice.
        """
        req = namedvariablepb.ListNamedVariableSetsRequest(project_id=self.id)
        res: namedvariablepb.ListNamedVariableSetsResponse = (
            get_default_client().ListNamedVariableSets(req)
        )
        return [lc.NamedVariableSet(n) for n in res.named_variable_sets]

    def set_active_named_variable_set(self, named_variable_set: NamedVariableSet) -> None:
        """
        This is a purely a construct for setting the active NamedVariableSet in the UI. It does not
        affect any previous or future SDK behavior.

        .. warning:: This feature is experimental and may change or be removed without notice.
        """
        req = projectuistatepb.SetActiveNamedVariableSetRequest(
            project_id=self.id, named_variable_set_id=named_variable_set.id
        )
        get_default_client().SetActiveNamedVariableSet(req)

    def get_active_named_variable_set(self) -> Optional[NamedVariableSet]:
        """
        This is a purely a construct for getting the active NamedVariableSet for a project in the UI.
        It does not affect any previous or future SDK behavior.

        .. warning:: This feature is experimental and may change or be removed without notice.
        """
        req = projectuistatepb.GetActiveNamedVariableSetRequest(project_id=self.id)
        res: projectuistatepb.GetActiveNamedVariableSetResponse = (
            get_default_client().GetActiveNamedVariableSet(req)
        )
        if not res.active_named_variable_set_id:
            return None
        return get_named_variable_set(NamedVariableSetID(res.active_named_variable_set_id))

    def share(self, email: str, role: Literal["viewer", "editor"]) -> None:
        """
        Share the project with a user identified by their email address. This function also allows
        changing the role of the user in the project if the project has already been shared with
        the input user.

        Parameters
        ----------
        email : str
            Email address of the user to share the project with. It must be an email whose domain
            is registered within the allowed domains settings of your company account.
        role : Literal["viewer", "editor"]
            The role to assign to the user in the project. Must be either "viewer" or "editor".
        """
        if not re.match(r"[^@]+@[^@]+\.[^@]+", email):
            raise ValueError(f"Invalid email address: {email}")
        if role not in ["viewer", "editor"]:
            raise ValueError(f"Invalid role: {role}. Must be 'viewer' or 'editor'.")
        roleModel = (
            projectpb.ShareProjectRequest.USER_ROLE_VIEWER
            if role == "viewer"
            else projectpb.ShareProjectRequest.USER_ROLE_EDITOR
        )
        req = projectpb.ShareProjectRequest(id=self.id, email=email, role=roleModel)
        get_default_client().ShareProject(req)

    def unshare(self, email: str) -> None:
        """
        Unshare the project with a user identified by their email address.

        Parameters
        ----------
        email : str
            Email address of the user to unshare the project with. It must be an email whose domain
            must be registered within the allowed domains settings of your company account.
        """
        if not re.match(r"[^@]+@[^@]+\.[^@]+", email):
            raise ValueError(f"Invalid email address: {email}")
        req = projectpb.UnshareProjectRequest(id=self.id, email=email)
        get_default_client().UnshareProject(req)

    def share_with_support(self, message: str = "") -> None:
        """
        Share the project with Luminary Cloud support.

        Parameters
        ----------
        message : str, optional
            Message to include with the support share request.
        """
        req = projectpb.ShareProjectWithSupportRequest(id=self.id, message=message)
        get_default_client().ShareProjectWithSupport(req)

    def unshare_with_support(self) -> None:
        """
        Unshare the project with Luminary Cloud support.
        """
        req = projectpb.UnshareProjectWithSupportRequest(id=self.id)
        get_default_client().UnshareProjectWithSupport(req)


def add_named_variables_from_csv(project: Project, csv_path: str) -> list[NamedVariableSet]:
    """
    This function reads named variables from a CSV file and creates corresponding NamedVariableSets in the given project.
    The CSV file should have the following format:
    name, var1, var2, ...
    name1, val1, val2, ...
    name2, val1, val2, ...

    .. warning:: This feature is experimental and may change or be removed without notice.
    """
    import csv

    def is_float(s: str) -> bool:
        try:
            float(s)
            return True
        except ValueError:
            return False

    named_variable_sets = []
    with open(csv_path) as csvfile:
        reader = csv.reader(csvfile)
        header = next(reader)
        keys = [k.strip() for k in header[1:]]
        for row in reader:
            if len(row) != len(keys) + 1:
                logging.warning(
                    f"Skipping row {row} because it has the wrong number of columns ({len(row)} instead of {len(keys) + 1})"
                )
                continue
            name = row[0]
            named_variables: dict[str, LcFloat] = {
                k: float(v.strip()) if is_float(v.strip()) else Expression(v.strip())
                for k, v in zip(keys, row[1:])
            }
            named_variable_sets.append(
                project.create_named_variable_set(name=name, named_variables=named_variables)
            )
            logging.info(f"Created named variable set {name} with {len(named_variables)} variables")
    return named_variable_sets


def create_project(
    name: str,
    description: str = "",
) -> Project:
    """
    Create a project owned by the user.

    Parameters
    ----------
    name : str
        Project name.
    description : str
        Project description.
    """
    req = projectpb.CreateProjectRequest(name=name, description=description)
    res = get_default_client().CreateProject(req)
    return Project(res.project)


def get_project(
    id: ProjectID,
) -> Project:
    """
    Get a specific project by ID.

    Parameters
    ----------
    id : str
        Project ID.
    """
    req = projectpb.GetProjectRequest(id=id)
    res = get_default_client().GetProject(req)
    return Project(res.project)


@deprecated("Use iterate_projects() instead.", "0.10.1")
def list_projects() -> list[Project]:
    """
    List projects accessible by the user.

    .. deprecated:: 0.10.1
        `list_projects()` will be removed in v0.11.0, it is replaced by
        `iterate_projects()` because the latter provides a more efficient
        way to fetch projects.
    """
    return list(iterate_projects())


class ProjectIterator:
    """Iterator class for projects that provides length hint."""

    def __init__(self, page_size: int):
        self._page_size: int = page_size
        self._page_token: str = ""
        self._total_count: Optional[int] = None
        self._current_page: Optional[list[projectpb.Project]] = None
        self._client = get_default_client()
        self._iterated_count: int = 0

    def __iter__(self) -> "ProjectIterator":
        return self

    def __next__(self) -> Project:
        if self._current_page is None:
            self._fetch_next_page()

        # _current_page really can't be None here, but this assertion is needed to appease mypy
        assert self._current_page is not None

        if len(self._current_page) == 0:
            if not self._page_token:
                raise StopIteration
            self._fetch_next_page()

        self._iterated_count += 1

        return Project(self._current_page.pop(0))

    def _fetch_next_page(self) -> None:
        req = projectpb.ListProjectsRequest(page_size=self._page_size, page_token=self._page_token)
        res = self._client.ListProjects(req)

        self._current_page = list(res.projects)
        self._page_token = res.next_page_token

        # Set length hint on first fetch if available
        if self._total_count is None:
            self._total_count = res.total_count or 0

    def __length_hint__(self) -> int:
        if self._total_count is None:
            # Fetch first page to get total size if not already fetched
            if self._current_page is None:
                self._fetch_next_page()
        return max(0, (self._total_count or 0) - self._iterated_count)


def iterate_projects(page_size: int = 50) -> ProjectIterator:
    """
    Iterate over all projects accessible by the user.

    The projects are fetched lazily in batches using pagination to optimize memory usage and API
    calls.

    Parameters
    ----------
    page_size : int, optional
        Number of projects to fetch per page. Defaults to 50, max is 500.

    Returns
    -------
    ProjectIterator
        An iterator that yields Project objects one at a time.

    Examples
    --------
    Fetch all projects and filter them for large ones.
    (Somewhat contrived example, such filtering should really be done on the server side.)

    >>> large_projects = [p for p in iterate_projects() if p.storage_usage_bytes > 100e6]
    [Project(...), Project(...)]

    Lazily fetch projects.
    (A batch size of 2 is a bad idea in real-world usage, but it helps demonstrate the lazy
    fetching.)

    >>> my_projects = iterate_projects(batch_size=2) # no network request has been made yet
    >>> next(my_projects) # first page of projects is fetched, first project is returned
    Project(...)
    >>> next(my_projects) # second project is returned from memory
    Project(...)
    >>> next(my_projects) # second page of projects is fetched, third project is returned
    Project(...)
    >>> next(my_projects) # if there areno more projects, this call raises StopIteration
    """
    return ProjectIterator(page_size)
