# Copyright 2024 Luminary Cloud, Inc. All Rights Reserved.

from dataclasses import dataclass
from os import path, PathLike
from typing import Sequence
import csv

from typing import Union

from .enum import TableType, QuantityType
from ._helpers import CodeRepr
from ._proto.table import table_pb2 as tablepb
from ._proto.quantity import quantity_pb2 as quantitypb


def create_rectilinear_table(
    table_type: TableType,
    table_file_path: PathLike | str,
) -> tablepb.RectilinearTable:
    """Read a CSV file and create a RectilinearTable of the desired type."""

    if table_type == TableType.AIRFOIL_PERFORMANCE:
        raise RuntimeError("This function can only be used for CSV files.")

    def has_user_defined_header(table_type: TableType) -> bool:
        """Whether a type can use an arbitrary header or must use one defined by us."""
        return table_type == TableType.PROFILE_BC or table_type == TableType.CUSTOM_SAMPLE_DOE

    def has_axis(table_type: TableType) -> bool:
        """Some types of table do not require an axis, they are just a collection of records."""
        return table_type != TableType.MONITOR_POINTS

    def allow_missing_entries(table_type: TableType) -> bool:
        """Whether the type of table allows missing entries."""
        return table_type == TableType.PROFILE_BC

    def lc_defined_header(table_type: TableType) -> list[Union[int, str]]:
        """Returns the required header (if any) for a type of table."""
        if table_type == TableType.MONITOR_POINTS:
            return [quantitypb.LENGTH, quantitypb.LENGTH, quantitypb.LENGTH, "name", "id"]
        elif table_type == TableType.RADIAL_DISTRIBUTION:
            return [
                quantitypb.RELATIVE_RADIUS,
                quantitypb.THRUST_PROFILE,
                quantitypb.TORQUE_PROFILE,
                quantitypb.RADIAL_FORCE_PROFILE,
            ]
        elif table_type == TableType.BLADE_GEOMETRY:
            return [
                quantitypb.RELATIVE_RADIUS,
                quantitypb.TWIST_ANGLE,
                quantitypb.SWEEP_ANGLE,
                quantitypb.ANHEDRAL_ANGLE,
                quantitypb.RELATIVE_CHORD,
            ]
        elif table_type == TableType.PROFILE_BC:
            return []
        elif table_type == TableType.FAN_CURVE:
            return [quantitypb.VOLUME_FLOW_RATE, quantitypb.PRESSURE_RISE]
        elif table_type == TableType.CUSTOM_SAMPLE_DOE:
            return []
        elif table_type == TableType.TEMP_VARYING:
            return [quantitypb.TEMPERATURE, "quantity"]
        else:
            raise RuntimeError("Unknown type of table.")

    def data_types(table_type: TableType, num_cols: int) -> list[type]:
        """Returns the types expected for the data in each column of the table."""
        if table_type == TableType.MONITOR_POINTS:
            return [float, float, float, str, str]
        else:
            return [float] * num_cols

    rows = []
    with open(table_file_path) as f:
        reader = csv.reader(f)
        rows = [row for row in reader]

    if len(rows) == 0 or len(rows[0]) == 0:
        raise RuntimeError(f"Error parsing file {table_file_path}, empty or wrong format.")

    file_has_header = False
    try:
        float(rows[0][0])
    except ValueError:
        file_has_header = True

    header: Sequence[int | str] = []
    if has_user_defined_header(table_type):
        if file_has_header:
            header = rows[0]
            rows = rows[1:]
        else:
            header = [f"Column {i}" for i in range(len(rows[0]))]
    else:
        header = lc_defined_header(table_type)
        # Ignore user-defined headers.
        if file_has_header:
            rows = rows[1:]
        if len(header) != len(rows[0]):
            raise IndexError(
                f"{len(header)} columns required by the type of table, but {len(rows[0])} provided in file."
            )

    table = tablepb.RectilinearTable()
    table.metadata.table_type = table_type.value
    table.metadata.uploaded_filename = path.basename(table_file_path)

    table.header.allow_missing_entries = allow_missing_entries(table_type)
    if has_axis(table_type):
        table.header.axis_label.append(tablepb.Header.Label())
        first_header = header[0]
        if isinstance(first_header, str):
            table.header.axis_label[-1].name = first_header
        else:
            table.header.axis_label[-1].quantity = QuantityType(first_header).value
        table.axis.append(tablepb.Axis())

    for label in header[has_axis(table_type) :]:
        table.header.record_label.append(tablepb.Header.Label())
        if isinstance(label, str):
            table.header.record_label[-1].name = label
        else:
            table.header.record_label[-1].quantity = QuantityType(label).value

    types = data_types(table_type, len(header))

    for row in rows:
        record = tablepb.Record()
        for i, val in enumerate(row):
            # Axis coordinates are always adfloats and cannot be missing.
            if i == 0 and has_axis(table_type):
                table.axis[0].coordinate.append(tablepb.Axis.Coordinate())
                table.axis[0].coordinate[-1].adfloat.value = float(val)
                continue

            if val == "":
                if allow_missing_entries(table_type):
                    record.entry.append(tablepb.Record.Entry(empty=tablepb.Record.Entry.Empty()))
                    pass
                else:
                    raise ValueError(f"Entry {i} in row {row} is missing.")
                continue

            record.entry.append(tablepb.Record.Entry())
            try:
                if types[i] == float:
                    record.entry[-1].adfloat.value = float(val)
                else:
                    record.entry[-1].string = val
            except ValueError:
                raise ValueError(f"Expected type {types[i]} for entry {i} in row {row}.")
        table.record.append(record)

    return table


@dataclass(kw_only=True)
class RectilinearTable(CodeRepr):
    """Represents an uploaded table."""

    id: str = ""
    name: str = ""
    table_type: TableType = TableType.INVALID


def _param_name_to_table_type(name: str) -> TableType:
    if name == "dynamic_viscosity_table_data" or name == "thermal_conductivity_table_data":
        return TableType.TEMP_VARYING
    if name == "profile_bc_data" or name == "profile_source_data":
        return TableType.PROFILE_BC
    if name == "fan_curve_table_data":
        return TableType.FAN_CURVE
    if name == "blade_element_geometry_data":
        return TableType.BLADE_GEOMETRY
    if name == "actuator_disk_radial_table_data":
        return TableType.RADIAL_DISTRIBUTION
    if name == "airfoil_performance_data":
        return TableType.AIRFOIL_PERFORMANCE
    if name == "particle_positions_table":
        return TableType.MONITOR_POINTS
    raise KeyError(f"Param {name} does not have an associated TableType.")
