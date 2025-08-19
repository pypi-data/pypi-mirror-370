# Copyright 2024 Luminary Cloud, Inc. All Rights Reserved.
from dataclasses import dataclass

from luminarycloud.types import Vector3
from luminarycloud._helpers.proto_decorator import proto_decorator
from luminarycloud._proto.cad import shape_pb2 as shapepb


class Shape:
    pass


@dataclass(kw_only=True)
@proto_decorator(shapepb.Sphere)
class Sphere(Shape):
    center: Vector3
    radius: float


@dataclass(kw_only=True)
@proto_decorator(shapepb.SphereShell)
class SphereShell(Shape):
    center: Vector3
    radius: float
    radius_inner: float


@dataclass(kw_only=True)
@proto_decorator(shapepb.HalfSphere)
class HalfSphere(Shape):
    center: Vector3
    radius: float
    normal: Vector3


@dataclass(kw_only=True)
@proto_decorator(shapepb.Cube)
class Cube(Shape):
    min: Vector3
    max: Vector3


@dataclass(kw_only=True)
@proto_decorator(shapepb.OrientedCube)
class OrientedCube(Shape):
    min: Vector3
    max: Vector3
    origin: Vector3
    x_axis: Vector3
    y_axis: Vector3


@dataclass(kw_only=True)
@proto_decorator(shapepb.Cylinder)
class Cylinder(Shape):
    start: Vector3
    end: Vector3
    radius: float


@dataclass(kw_only=True)
@proto_decorator(shapepb.AnnularCylinder)
class AnnularCylinder(Shape):
    start: Vector3
    end: Vector3
    radius: float
    radius_inner: float


@dataclass(kw_only=True)
@proto_decorator(shapepb.Torus)
class Torus(Shape):
    center: Vector3
    normal: Vector3
    major_radius: float
    minor_radius: float


@dataclass(kw_only=True)
@proto_decorator(shapepb.Cone)
class Cone(Shape):
    apex: Vector3
    base_center: Vector3
    base_radius: float
