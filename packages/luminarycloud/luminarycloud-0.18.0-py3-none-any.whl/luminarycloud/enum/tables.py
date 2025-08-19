# Copyright 2023-2024 Luminary Cloud, Inc. All Rights Reserved.

from enum import IntEnum as _IntEnum

from luminarycloud._proto.table import table_pb2 as _tablepb


class TableType(_IntEnum):
    """
    Types of tables.

    Attributes
    ----------
    MONITOR_POINTS
        List of coordinates, name, and IDs. This type is used to define the position of monitor
        points and point sources.
    RADIAL_DISTRIBUTION
        Thrust, torque, and radial force vs relative radius.
    BLADE_GEOMETRY
        Twist angle, sweep angle, anhedral angle, and relative chord vs relative radius.
    AIRFOIL_PERFORMANCE
        C81 data for an airfoil section.
    PROFILE_BC
        Arbitrary number of columns vs a spatial coordinate or time. This type is also used for
        tabulated heat sources.
    FAN_CURVE
        Pressure rise vs volumetric flow rate.
    CUSTOM_SAMPLE_DOE
        List of design-of-experiment samples.
    TEMP_VARYING
        Material property (e.g. conductivity) vs temperature.
    """

    INVALID = _tablepb.INVALID
    MONITOR_POINTS = _tablepb.MONITOR_POINTS
    RADIAL_DISTRIBUTION = _tablepb.RADIAL_DISTRIBUTION
    BLADE_GEOMETRY = _tablepb.BLADE_GEOMETRY
    AIRFOIL_PERFORMANCE = _tablepb.AIRFOIL_PERFORMANCE
    PROFILE_BC = _tablepb.PROFILE_BC
    FAN_CURVE = _tablepb.FAN_CURVE
    CUSTOM_SAMPLE_DOE = _tablepb.CUSTOM_SAMPLE_DOE
    TEMP_VARYING = _tablepb.TEMP_VARYING
