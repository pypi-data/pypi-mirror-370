# Copyright 2023-2024 Luminary Cloud, Inc. All Rights Reserved.
import zstandard as zstd
import csv
import json
from .vis_util import _download_file, _InternalToken, generate_id, _get_status
from ..enum import ExtractStatusType, EntityType
from typing import Tuple, cast, Union
from abc import ABC, abstractmethod
from .._proto.api.v0.luminarycloud.vis import vis_pb2
from .primitives import Plane
from ..types.vector3 import _to_vector3, Vector3Like, Vector3
from .._client import get_default_client
import logging
from ..solution import Solution
from ..geometry import Geometry
from ..mesh import Mesh, get_mesh, get_mesh_metadata
from ..simulation import get_simulation
from .._helpers._get_project_id import _get_project_id
from .display import DisplayAttributes
from time import sleep, time
from luminarycloud.params.simulation.physics.fluid.boundary_conditions import Farfield
from .._helpers._code_representation import CodeRepr
from ..types import SimulationID
from collections import defaultdict


logger = logging.getLogger(__name__)


class DataExtract(ABC, CodeRepr):
    """
    This is the base class for all data extracts. Each derived extract class
    is responsible for providing a _to_proto method to convert to a filter
    protobuf.

    Attributes
    ----------
    id: str
        A automatically generated uniqiue filter id.

    .. warning:: This feature is experimental and may change or be removed in the future.
    """

    def __init__(self, id: str) -> None:
        self.id = id
        self._parent_id: str = ""

    @abstractmethod
    def _to_proto(self) -> vis_pb2.Filter:
        pass


class IntersectionCurve(DataExtract):
    """

    Generate line data by computing intersections between solution surfaces and a slice plane.

    Extracts 1D curves where surfaces intersect the specified cutting plane, preserving
    solution field values at intersection points.

    .. warning:: This feature is experimental and may change or be removed in the future.

    Attributes:
    -----------
    plane : Plane
        The slice plane.
    name : str
        A user provided name for the filter.
    """

    def __init__(self, name: str = "") -> None:
        super().__init__(generate_id("intersection-curve"))
        self.name = name
        self._surface_names: list[str] = []
        self._plane = Plane()
        self.label: str = ""

    @property
    def plane(self) -> Plane:
        return self._plane

    @plane.setter
    def plane(self, new_plane: Plane) -> None:
        if not isinstance(new_plane, Plane):
            raise TypeError(f"Expected 'Plane', got {type(new_plane).__name__}")
        self._plane = new_plane

    def add_surface(self, id: str) -> None:
        """
        Add a surface to compute the intersection curve on. Adding no
        surfaces indicates that all surfaces will be used. The id can
        either be a tag or explicit surface id. These values will be
        validated by the DataExtractor before sending the request.

        Parameters
        ----------
        id: str
            A surface id or a tag id.
        """
        if not isinstance(id, str):
            raise TypeError(f"Expected 'str', got {type(id).__name__}")
        self._surface_names.append(id)

    def _surfaces(self) -> list[str]:
        """
        Returns the current list of surfaces.
        """
        return self._surface_names

    def _to_proto(self) -> vis_pb2.Filter:
        vis_filter = vis_pb2.Filter()
        vis_filter.id = self.id
        vis_filter.name = self.name
        vis_filter.intersection_curve.label = self.label

        for id in self._surface_names:
            vis_filter.intersection_curve.surfaces.append(id)

        vis_filter.intersection_curve.plane.CopyFrom(self._plane._to_proto())
        return vis_filter

    def _from_proto(self, vis_filter: vis_pb2.Filter) -> None:
        self.id = vis_filter.id
        self.name = vis_filter.name
        self.label = vis_filter.intersection_curve.label
        self._surface_names = list(vis_filter.intersection_curve.surfaces)
        self._plane = Plane()
        self._plane._from_proto(vis_filter.intersection_curve.plane)

    def _to_code(self, hide_defaults: bool = True, use_tmp_objs: bool = True) -> str:
        code = super()._to_code(hide_defaults=hide_defaults)
        # We need to explicity write the code for the surfaces since its
        # technically a private variable.
        for s in self._surface_names:
            code += f".add_surface('{s}')\n"
        return code


class LineSample(DataExtract):
    """

    Generate line data by computing intersections between volumetric data and a line.

    Extracts a 1D curve where the line intersects cell faces with solution field
    values at intersection points.

    .. warning:: This feature is experimental and may change or be removed in the future.

    Attributes:
    -----------
    start: Vector3Like
        The start of the line segment. Defaults to (0, 0, 0).
    end: Vector3Like
        The end of the line segment. Defaults to (1, 0, 0).
    label: str
        A user provided label for the line sample.
    name : str
        A user provided name for the filter.
    """

    def __init__(self, name: str = "") -> None:
        super().__init__(generate_id("line-sample"))
        self.name = name
        self.start: Vector3Like = Vector3(x=0, y=0, z=0)
        self.end: Vector3Like = Vector3(x=1, y=0, z=0)
        self.label: str = ""

    def _to_proto(self) -> vis_pb2.Filter:
        vis_filter = vis_pb2.Filter()
        vis_filter.id = self.id
        vis_filter.name = self.name
        vis_filter.line_sample.label = self.label
        vis_filter.line_sample.start.CopyFrom(_to_vector3(self.start)._to_proto())
        vis_filter.line_sample.end.CopyFrom(_to_vector3(self.end)._to_proto())
        return vis_filter

    def _from_proto(self, vis_filter: vis_pb2.Filter) -> None:
        self.id = vis_filter.id
        self.name = vis_filter.name
        self.label = vis_filter.line_sample.label
        self.start = Vector3()
        self.start._from_proto(vis_filter.line_sample.start)
        self.end = Vector3()
        self.end._from_proto(vis_filter.line_sample.end)


class ExtractOutput:
    """
    The extract output represents the request to extract data from a solution,
    and is contructed by the DataExtractor class. The operation exectutes
    asyncronously, so the caller must check the status of the data extract. If
    the status is completed, then the resuling data is available for download.

    .. warning:: This class should not be directly instantiated by users.

    .. warning:: This feature is experimental and may change or be removed in the future.

    Attributes:
    -----------
    name: str
        The user provided name of the extract.
    description: str
        The user provided description of the extract.
    status: ExtractStatusType
        The status of the extract (i.e., has it completed or not).
    _extract_id: str
        The unique indentifier of the extract.
    _project_id: str
        The project id associated with the extract.
    _deleted: bool
        Internal flag to track if the extract has been deleted.
    """

    def __init__(self, factory_token: _InternalToken):
        if not isinstance(factory_token, _InternalToken):
            raise ValueError("This class can only be constructed through the Scene class")

        self._extract_id: str = ""
        self._project_id: str = ""
        self.status: ExtractStatusType = ExtractStatusType.INVALID
        self.name: str = ""
        self.description: str = ""
        self._deleted = False

    def _set_data(
        self,
        extract_id: str,
        project_id: str,
        name: str,
        desciption: str,
        status: ExtractStatusType,
    ) -> None:
        self._extract_id = extract_id
        self._project_id = project_id
        self.status = status
        self.name = name
        self.description = desciption

    def __repr__(self) -> str:
        return f"ExtractOutput (Id: {self._extract_id} status: {self.status})"

    def refresh(self) -> "ExtractOutput":
        """
        Refesh the status of the ExtractOutput.

        Returns
        -------
        self
        """
        self._fail_if_deleted()
        self.status = _get_status(self._project_id, self._extract_id)
        return self

    def wait(
        self, interval_seconds: float = 4, timeout_seconds: float = float("inf")
    ) -> ExtractStatusType:
        """
        Wait until the ExtractOutput is completed or failed.

        Parameters
        ----------
        interval : float, optional
            Number of seconds between polls.
        timeout : float, optional
            Number of seconds before timeout.

        Returns
        -------
        ExtractStatusType: Current status of the image extract.
        """
        self._fail_if_deleted()
        deadline = time() + timeout_seconds
        while True:
            self.refresh()

            if self.status in [
                ExtractStatusType.COMPLETED,
                ExtractStatusType.FAILED,
                ExtractStatusType.INVALID,
            ]:
                return self.status
            if time() >= deadline:
                logger.error("`ExtractOutput: wait ` timed out.")
                raise TimeoutError
            sleep(max(-1, min(interval_seconds, deadline - time())))

    def download_data(self) -> list[Tuple[list[list[Union[str, int, float]]], str]]:
        """
        Downloads the resulting data into memory. This is useful
        for plotting data in notebooks.  If that status is not complete, an
        error will be raised.

        Returns:
            A list of results for each extract added to the request. Each result is a tuple
            where the first entry is a in-memory csv file (List[List[Union[str, int, float]]]).
            The first row is the header followed by the data rows. The second entry of the tuple
            is the label provided by the user for the DataExtract.

        .. warning:: This feature is experimental and may change or be removed in the future.

        """
        self._fail_if_deleted()
        self.refresh()
        if self.status != ExtractStatusType.COMPLETED:
            raise Exception("download_data: status not complete.")
        req = vis_pb2.DownloadExtractRequest()
        req.extract_id = self._extract_id
        req.project_id = self._project_id
        res: vis_pb2.DownloadExtractResponse = get_default_client().DownloadExtract(req)

        csv_files: list[Tuple[list[list[Union[str, int, float]]], str]] = []
        if res.HasField("line_data"):
            compressed_buffer = _download_file(res.line_data)
            dctx = zstd.ZstdDecompressor()
            decompressed_size = zstd.frame_content_size(compressed_buffer.getvalue())
            serializedTable = dctx.decompress(
                compressed_buffer.getvalue(), max_output_size=decompressed_size
            )
            line_data = vis_pb2.LineDataExtract()
            # If uncompressed: this is
            # line_data.ParseFromString(line_data_buffer.read())
            line_data.ParseFromString(serializedTable)
            ids = line_data.lines.keys()
            # Each filter(id) produces a set of tables, one per line segment.
            for id in ids:
                header: list[Union[str, float, int]] = []
                tables = line_data.lines[id]
                # One table per line segment. First, figure out the
                # shape of the data and validate what we expect.
                total_rows = 0
                n_cols = 0
                for _, table in enumerate(tables.lines_table):
                    assert len(table.axis) == 1
                    assert len(table.record) == 1
                    n_rows = len(table.axis[0].coordinate)
                    total_rows += n_rows
                    n_cols = len(table.header.record_label)
                    if len(header) == 0:
                        for _, label in enumerate(table.header.record_label):
                            header.append(label.name)
                        # We also have a curve id we need to add.
                        header.append("curve id")
                    # verify what we expect to see
                    assert n_rows * n_cols == len(table.record[0].entry)
                assert len(header) != 0
                assert n_cols != 0
                rows: list[list[Union[str, float, int]]] = []
                rows.append(header)
                for curve_id, table in enumerate(tables.lines_table):
                    n_rows = len(table.axis[0].coordinate)
                    new_rows: list[list[Union[str, float, int]]] = []
                    idx = 0
                    # The the shape of the values are in row-major ordering.
                    for r in range(n_rows):
                        row: list[Union[str, float, int]] = []
                        for c in range(n_cols):
                            row.append(table.record[0].entry[idx].adfloat.value)
                            idx += 1
                        new_rows.append(row)
                    # Now add the curve id to all the rows.
                    for row in new_rows:
                        row.append(curve_id)
                    rows = rows + new_rows
                csv_files.append((rows, line_data.labels[id]))
        return csv_files

    def save_files(self, file_prefix: str, write_labels: bool = False) -> None:
        """
        A helper for downloading and save resulting csv files to the file system. If that status is not
        complete, an error will be raised. csv_files will be of the form {file_prefix}_{index}.csv.
        Optionally, a file will be written containing a list of file names and image labels. Labels
        are an optional field in the DataExtracts.

        .. warning:: This feature is experimental and may change or be removed in the future.

        Parameters
        ----------
        file_prefix: str, required
            The file prefix to save the extract. A file index and  '.csv' will be
            appended to the file names.
        write_labels: bool, optional
            Write a json file containing a list of csv file names and labels,
            if True. The resulting json file is named '{file_prefix}.json' Default: False
        """
        if not file_prefix:
            raise ValueError("file_prefix must be non-empty")

        csv_files = self.download_data()
        names_labels: list[Tuple[str, str]] = []
        counter = 0
        for csv_file in csv_files:
            output_file = f"{file_prefix}_{counter}.csv"
            with open(output_file, "w", newline="") as file:
                writer = csv.writer(file)
                writer.writerows(csv_file[0])
            counter = counter + 1
            names_labels.append((output_file, csv_file[1]))
        if write_labels:
            with open(f"{file_prefix}.json", "w") as json_file:
                json.dump(names_labels, json_file, indent=1)

    def _fail_if_deleted(self) -> None:
        if self._deleted:
            raise ValueError("RenderOutput has been deleted.")

    def delete(self) -> None:
        """Delete the the extracts."""
        self._fail_if_deleted()
        req = vis_pb2.DeleteExtractRequest()
        req.extract_id = self._extract_id
        req.project_id = self._project_id
        get_default_client().DeleteExtract(req)
        self._deleted = True


def _data_extract_to_obj_name(extract: DataExtract) -> str:
    """
    Helper function to convert a filter to a code object name used in code gen.
    """
    if not isinstance(extract, DataExtract):
        raise TypeError(f"Expected 'DataExtract', got {type(extract).__name__}")
    if isinstance(extract, LineSample):
        return "line_sample"
    elif isinstance(extract, IntersectionCurve):
        return "intersection_curve"
    else:
        raise TypeError(f"Unknown data extract type: {type(extract).__name__}")


class DataExtractor:
    """
    I extract data from solutions.

    .. warning:: This feature is experimental and may change or be removed in the future.

    """

    def __init__(self, solution: Solution):
        if not isinstance(solution, Solution):
            raise TypeError(f"Expected Solution got {type(solution).__name__}")
        self._solution: Solution = solution
        self._entity_type: EntityType = EntityType.SIMULATION
        self._extracts: list[DataExtract] = []

        # Meshes that are directly uploaded will not have tags.
        self._has_tags: bool = True

        project_id = _get_project_id(solution)
        if not project_id:
            raise ValueError("Unable to get project id from solution")

        self._project_id = project_id

        # Trace each entity all the way back to the geometry so we
        # can accesss the tags, if they are present.
        geom: Geometry | None = None
        simulation = get_simulation(self._solution.simulation_id)
        mesh_meta = get_mesh_metadata(simulation.mesh_id)
        mesh = get_mesh(simulation.mesh_id)
        geo_ver = mesh.geometry_version()
        if geo_ver is None:
            self._has_tags = False
        else:
            geom = geo_ver.geometry()

        self._surface_ids: list[str] = []
        for zone in mesh_meta.zones:
            for bound in zone.boundaries:
                self._surface_ids.append(bound.name)

        self._tag_ids: list[str] = []
        if geom and self._has_tags:
            tags = geom.list_tags()
            for tag in tags:
                self._tag_ids.append(tag.id)

        self.far_field_boundary_ids: list[str] = []

        # Find all the far field surfaces if we can get the params.
        params = simulation.get_parameters()
        for physics in params.physics:
            if physics.fluid:
                for bc in physics.fluid.boundary_conditions:
                    if isinstance(bc, Farfield):
                        for bc_surface in bc.surfaces:
                            self.far_field_boundary_ids.append(bc_surface)

    def _validate_surfaces_and_tags(self, ids: list[str]) -> list[str]:
        """
        Validate a list of ids as either tags or ids. Returns a list of invalid ids. If the
        length of the list is zero, the input list is valid.
        """
        bad_ids: list[str] = []
        for id in ids:
            if id in self._tag_ids:
                continue
            if id not in self._surface_ids:
                bad_ids.append(id)
        return bad_ids

    def surface_ids(self) -> list[str]:
        """Get a list of all the surface ids associated with the solution."""
        return self._surface_ids

    def tag_ids(self) -> list[str]:
        """Get a list of all the tag ids associated with the solution."""
        return self._tag_ids

    def add_data_extract(self, extract: DataExtract) -> None:
        """
        Add a data extract.
        """
        if not isinstance(extract, DataExtract):
            raise TypeError(f"Expected 'Filter', got {type(extract).__name__}")
        self._extracts.append(extract)

    def _create_request(self, name: str, description: str) -> vis_pb2.CreateExtractRequest:
        req = vis_pb2.CreateExtractRequest()

        # We have to add a bunch of dummy params to get the request to go through the same
        # path as filters.
        req.spec.global_display_attributes.CopyFrom(DisplayAttributes()._to_proto())
        req.spec.animation_properties
        req.spec.data_only = True
        for extract in self._extracts:
            if isinstance(extract, IntersectionCurve):
                # Validate surfaces names
                icurve = cast(IntersectionCurve, extract)
                bad_ids = self._validate_surfaces_and_tags(icurve._surface_names)
                if len(bad_ids) != 0:
                    raise ValueError(f"IntersectionCurve has invalid surfaces: {bad_ids}")

            if isinstance(extract, DataExtract):
                vis_filter: vis_pb2.Filter = extract._to_proto()
                req.spec.filters.append(vis_filter)
                # Add dummy display attrs
                req.spec.display_attributes[extract.id].CopyFrom(DisplayAttributes()._to_proto())
            else:
                raise TypeError(f"Expected 'filter', got {type(filter).__name__}")

        req.project_id = self._project_id
        req.spec.entity_type.simulation.id = self._solution.simulation_id
        req.spec.entity_type.simulation.solution_id = self._solution.id
        req.spec.name = name
        req.spec.description = description
        return req

    def create_extracts(self, name: str, description: str) -> ExtractOutput:
        """
        Create a request to extract data from a solution.

        Parameters
        ----------
        name : str
            A short name for the the extracts.
        description : str
           A longer description of the extracts.
        """
        req: vis_pb2.CreateExtractRequest = self._create_request(name=name, description=description)
        res: vis_pb2.CreateExtractResponse = get_default_client().CreateExtract(req)
        extract_output = ExtractOutput(_InternalToken())
        extract_output._set_data(
            extract_id=res.extract.extract_id,
            project_id=self._project_id,
            name=name,
            desciption=description,
            status=ExtractStatusType(res.extract.status),
        )
        return extract_output

    def to_code(self, obj_name: str, include_imports: bool, hide_defaults: bool = True) -> str:
        """
        This function will produce a code string that reproduces the data extractor
        in its current state.

        Parameters
        ----------
        obj_name: str
            the object name of the scene.
        include_imports: bool
            If True, the code will include the necessary imports to run the code. This will be
            set to false if generating scene code as well, since the imports overlap.
        hide_defaults: bool, optional
            If True, the code will make a best effort not include default values for attributes.
        """
        if len(self._extracts) == 0:
            # If we don't have any extracts, we don't need to generate any code.
            return ""

        imports: str = ""
        if include_imports:
            imports += "import luminarycloud as lc\n"
            imports += "import luminarycloud.vis as vis\n"
            imports += "from luminarycloud.types import Vector3\n"
            imports += "from luminarycloud.enum import ExtractStatusType\n"

        # This isn't technically needed, but I think its useful.
        code = "\n# Find the entity to build the scene from\n"
        code += f"simulation = lc.get_simulation('{self._solution.simulation_id}')\n"
        code += "for sol in simulation.list_solutions():\n"
        code += f"    if sol.id == '{self._solution.id}':\n"
        code += f"        solution = sol\n"
        code += f"        break\n"
        code += "data_extractor = vis.DataExtractor(solution)\n"
        code += "\n"

        code += "\n"
        # We can have many of the same type of filter so we need to track how
        # many times we have seen a filter type to create the object name.
        name_map: defaultdict[str, int] = defaultdict(int)
        # Filters can be connected so we need to track what the ids are so we
        # can connected them.
        ids_to_obj_name: dict[str, str] = {}
        for extract in self._extracts:
            # Name objects numerically: slice0, slice1, etc.
            name = _data_extract_to_obj_name(extract)
            obj_name = f"{name}{name_map[obj_name]}"
            name_map[obj_name] += 1
            ids_to_obj_name[extract.id] = obj_name
            code += extract._to_code_helper(obj_name, hide_defaults=hide_defaults)
            code += f"data_extractor.add_data_extract({obj_name})\n"
            code += "\n"

        if include_imports:
            imports += "\n"
        # The code gen is very verbose, so we can do some string replacements
        # since we are importing the luminarycloud.vis package.
        cleanup_list: list[str] = [
            "luminarycloud.vis.data_extraction",
        ]
        for cleanup in cleanup_list:
            code = code.replace(cleanup, "vis")
        # Many classes initialize the attributes, so we don't need to explicitly
        # creat new objects for them. Additionally, its easier to do this here than
        # in the individual classes.
        remove_list: list[str] = [
            "vis.DataRange()",
            "luminarycloud.vis.primitives.Plane()",
            "luminarycloud.vis.primitives.Box()",
        ]
        # Remove entire lines containing any remove_list item
        code_lines = code.splitlines()
        filtered_lines = [
            line
            for line in code_lines
            if not any(remove_item in line for remove_item in remove_list)
        ]
        code = "\n".join(filtered_lines)

        code += "\n"
        code += "extract_output = extractor.create_extracts(name='extract data', description='lonerg description')\n"
        code += "status = extract_output.wait()\n"
        code += "if status == ExtractStatusType.COMPLETED:\n"
        code += "    extract_output.save_files('data_extracts_prefix', True)\n"
        code += "else:\n"
        code += "    print('Data extraction failed ', status)\n"

        return imports + code


def list_data_extracts(solution: Solution) -> list[ExtractOutput]:
    """
    Lists all previously created data extract associated with a project and a solution.

    .. warning:: This feature is experimental and may change or be removed in the future.

    Parameters
    ----------
    project_id : str
        The project id to query.
    entity : Geometry | Mesh | Solution
        Specifies what types of rendering extracts to list(e.g., geometry, mesh or solution).

    """

    # Find out what we are working on.
    if not isinstance(solution, Solution):
        raise TypeError(f"Expected Solution got {type(solution).__name__}")

    entity_type = EntityType.SIMULATION
    project_id = _get_project_id(solution)
    if not project_id:
        raise ValueError("Unable to get project id from solution")

    req = vis_pb2.ListExtractsRequest()
    req.project_id = project_id

    sim_entity = cast(Solution, solution)
    req.entity.simulation.id = sim_entity.simulation_id
    req.entity.simulation.solution_id = sim_entity.id

    # We are requesting data not images
    req.data_only = True
    res: vis_pb2.ListExtractsResponse = get_default_client().ListExtracts(req)

    results: list[ExtractOutput] = []
    for extract in res.extracts:
        result = ExtractOutput(_InternalToken())
        result._set_data(
            extract_id=extract.extract_id,
            project_id=extract.project_id,
            name=extract.name,
            desciption=extract.description,
            status=ExtractStatusType(extract.status),
        )
        # This need to be fixed on the backend, but manually refreshing works for now.
        result.refresh()
        results.append(result)

    return results


def _spec_to_data_extractor(spec: vis_pb2.ExtractSpec) -> DataExtractor:
    entity = spec.entity_type.WhichOneof("entity")
    if entity == "simulation":
        sim_id = SimulationID(spec.entity_type.simulation.id)
        sim = get_simulation(sim_id)
        sols = sim.list_solutions()
        found = False
        for sol in sols:
            if sol.id == spec.entity_type.simulation.solution_id:
                extractor = DataExtractor(sol)
                found = True
                break
        if not found:
            raise ValueError("Error: could not find the solution")
    else:
        raise ValueError("Error: only solutions are supported for data extraction")

    try:
        _ = extractor  # check to see if this is bound
    except NameError:
        raise ValueError(f"Error: could not create scene from entity")

    filter_ids: list[str] = []
    for filter in spec.filters:
        filter_ids.append(filter.id)
        typ = filter.WhichOneof("value")
        pfilter: DataExtract | None = None
        if typ == "line_sample":
            pfilter = LineSample("")
        elif typ == "intersection_curve":
            pfilter = IntersectionCurve("")
        else:
            # Don't complain about vis filters that are not data extracts.
            # If the extractor has no filters, it will return an empty string
            # from the to_code path.
            continue

        assert pfilter is not None, "Internal error: filter type not set"
        pfilter._from_proto(filter)
        extractor.add_data_extract(pfilter)

    return extractor
