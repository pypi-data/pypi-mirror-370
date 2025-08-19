# Copyright 2023-2024 Luminary Cloud, Inc. All Rights Reserved.
import dataclasses as dc
from luminarycloud.types import Vector3, Vector3Like
from .._helpers._code_representation import CodeRepr
from .._proto.api.v0.luminarycloud.vis import vis_pb2
from ..types.vector3 import _to_vector3
import math


@dc.dataclass
class Plane(CodeRepr):
    """
    This class defines a plane.

    .. warning:: This feature is experimental and may change or be removed in the future.

    """

    origin: Vector3Like = dc.field(default_factory=lambda: Vector3(x=0, y=0, z=0))
    """A point defined on the plane. Default: [0,0,0]."""
    normal: Vector3Like = dc.field(default_factory=lambda: Vector3(x=1, y=0, z=0))
    """The vector orthogonal to the  plane. Default: [0,1,0]"""

    def _to_proto(self) -> vis_pb2.Plane:
        plane = vis_pb2.Plane()
        plane.origin.CopyFrom(_to_vector3(self.origin)._to_proto())
        plane.normal.CopyFrom(_to_vector3(self.normal)._to_proto())
        return plane

    def _from_proto(self, proto: vis_pb2.Plane) -> None:
        self.origin = Vector3()
        self.origin._from_proto(proto.origin)
        self.normal = Vector3()
        self.normal._from_proto(proto.normal)

    def __repr__(self) -> str:
        return self._to_code_helper(obj_name="plane")


@dc.dataclass
class Box(CodeRepr):
    """
    This class defines a box used for filters such as box clip.

    .. warning:: This feature is experimental and may change or be removed in the future.

    """

    center: Vector3Like = dc.field(default_factory=lambda: Vector3(x=0, y=0, z=0))
    """A point defined at the center of the box. Default: [0,0,0]."""
    lengths: Vector3Like = dc.field(default_factory=lambda: Vector3(x=1, y=1, z=1))
    """The the legnths of each side of the box. Default: [1,1,1]"""
    angles: Vector3Like = dc.field(default_factory=lambda: Vector3(x=0, y=0, z=0))
    """
    The rotation of the box specified in Euler angles (degrees) and applied
    in XYZ ordering. Default: [0,0,0]
    """

    def _to_proto(self) -> vis_pb2.Box:
        box = vis_pb2.Box()
        box.center.CopyFrom(_to_vector3(self.center)._to_proto())
        box.lengths.CopyFrom(_to_vector3(self.lengths)._to_proto())
        # The api interface is in degrees but the backend needs radians
        radians = _to_vector3(self.angles)
        radians.x = radians.x * (math.pi / 180)
        radians.y = radians.y * (math.pi / 180)
        radians.z = radians.z * (math.pi / 180)
        box.angles.CopyFrom(radians._to_proto())
        return box

    def _from_proto(self, proto: vis_pb2.Box) -> None:
        center = Vector3()
        center._from_proto(proto.center)
        self.center = center
        lengths = Vector3()
        lengths._from_proto(proto.lengths)
        self.lengths = lengths
        self.angles = Vector3()
        # Backend units are radians, convert back to degrees
        self.angles.x = proto.angles.x * (180 / math.pi)
        self.angles.y = proto.angles.y * (180 / math.pi)
        self.angles.z = proto.angles.z * (180 / math.pi)

    def __repr__(self) -> str:
        return self._to_code_helper(obj_name="box")


@dc.dataclass
class AABB(CodeRepr):
    """
    This class defines an axis-aligned bounding box used for filters such as SurfaceLICPlane.

    .. warning:: This feature is experimental and may change or be removed in the future.

    """

    min: Vector3Like = dc.field(default_factory=lambda: Vector3(x=0, y=0, z=0))
    """The min point of the axis-aligned box. Default: [0,0,0]."""
    max: Vector3Like = dc.field(default_factory=lambda: Vector3(x=1, y=1, z=1))
    """The max point of the axis-aligned box. Default: [1,1,1]."""

    def is_valid(self) -> bool:
        """
        Check if the AABB is valid. An AABB is valid if min is less than max in all dimensions.
        """
        min = _to_vector3(self.min)
        max = _to_vector3(self.max)
        return min.x <= max.x and min.y <= max.y and min.z <= max.z

    def _to_proto(self) -> vis_pb2.AABB:
        aabb = vis_pb2.AABB()
        aabb.min.CopyFrom(_to_vector3(self.min)._to_proto())
        aabb.max.CopyFrom(_to_vector3(self.max)._to_proto())
        return aabb

    def _from_proto(self, proto: vis_pb2.AABB) -> None:
        min_point = Vector3()
        min_point._from_proto(proto.min)
        self.min = min_point
        max_point = Vector3()
        max_point._from_proto(proto.max)
        self.max = max_point

    def __repr__(self) -> str:
        return self._to_code_helper(obj_name="aabb")
