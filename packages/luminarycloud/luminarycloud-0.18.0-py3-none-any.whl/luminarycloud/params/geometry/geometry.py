# Copyright 2024 Luminary Cloud, Inc. All Rights Reserved.
from dataclasses import dataclass

from luminarycloud.types import Vector3


@dataclass(frozen=True)
class GeometryEntity:
    """A generic entity in the geometry."""

    geometry_id: str
    id: str
    bbox_min: Vector3
    bbox_max: Vector3


@dataclass(frozen=True)
class Volume(GeometryEntity):
    """A volume in the geometry. This class should never be instantiated directly."""

    _lcn_id: str


@dataclass(frozen=True)
class Surface(GeometryEntity):
    """A surface in the geometry. This class should never be instantiated directly."""

    _native_id: int
