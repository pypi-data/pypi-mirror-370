# Copyright 2023-2024 Luminary Cloud, Inc. All Rights Reserved.
from dataclasses import dataclass, field

from .._proto.base import base_pb2 as basepb
from .vector3 import Vector3


@dataclass
class Matrix3:
    """Represents a 3x3 matrix."""

    a: Vector3 = field(default_factory=Vector3)
    b: Vector3 = field(default_factory=Vector3)
    c: Vector3 = field(default_factory=Vector3)

    def _to_proto(self) -> basepb.Matrix3:
        return basepb.Matrix3(
            a=basepb.Vector3(x=self.a.x, y=self.a.y, z=self.a.z),
            b=basepb.Vector3(x=self.b.x, y=self.b.y, z=self.b.z),
            c=basepb.Vector3(x=self.c.x, y=self.c.y, z=self.c.z),
        )

    def _from_proto(self, proto: basepb.Matrix3) -> None:
        self.a = Vector3(x=proto.a.x, y=proto.a.y, z=proto.a.z)
        self.b = Vector3(x=proto.b.x, y=proto.b.y, z=proto.b.z)
        self.c = Vector3(x=proto.c.x, y=proto.c.y, z=proto.c.z)
