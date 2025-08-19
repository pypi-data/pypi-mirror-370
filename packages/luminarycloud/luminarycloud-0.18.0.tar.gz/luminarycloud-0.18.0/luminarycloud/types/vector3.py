# Copyright 2023-2024 Luminary Cloud, Inc. All Rights Reserved.
from dataclasses import dataclass
from typing import TypeAlias, Iterator

from .._proto.api.v0.luminarycloud.common import common_pb2 as commonpb
from .._proto.base.base_pb2 import AdVector3, Vector3 as Vector3Proto
from .adfloat import (
    _to_ad_proto as _float_to_ad_proto,
    _from_ad_proto as _float_from_ad_proto,
)
from ..pipeline_util.dictable import PipelineDictable


@dataclass
class Vector3(PipelineDictable):
    """Represents a 3-dimensional vector.

    Supports direct component access, indexing, iteration, and conversion to numpy arrays.

    Examples:
        >>> from luminarycloud.types import Vector3
        >>> v = Vector3(1.0, 2.0, 3.0)
        >>> v.x, v.y, v.z  # Direct component access
        (1.0, 2.0, 3.0)
        >>> v[0]  # Access by index
        1.0
        >>> list(v)  # Iterate over components
        [1.0, 2.0, 3.0]
        >>> import numpy as np
        >>> np.array(v)  # Convert to numpy array
        array([1., 2., 3.])
    """

    x: float = 0.0
    y: float = 0.0
    z: float = 0.0

    def _to_proto(self) -> commonpb.Vector3:
        return commonpb.Vector3(x=self.x, y=self.y, z=self.z)

    def _from_proto(self, proto: commonpb.Vector3) -> None:
        self.x = proto.x
        self.y = proto.y
        self.z = proto.z

    def _to_ad_proto(self) -> AdVector3:
        advector = AdVector3()
        advector.x.CopyFrom(_float_to_ad_proto(self.x))
        advector.y.CopyFrom(_float_to_ad_proto(self.y))
        advector.z.CopyFrom(_float_to_ad_proto(self.z))
        return advector

    def _to_base_proto(self) -> Vector3Proto:
        return Vector3Proto(x=self.x, y=self.y, z=self.z)

    def _from_ad_proto(self, proto: AdVector3) -> None:
        self.x = _float_from_ad_proto(proto.x)
        self.y = _float_from_ad_proto(proto.y)
        self.z = _float_from_ad_proto(proto.z)

    @classmethod
    def from_ad_proto(cls, proto: AdVector3) -> "Vector3":
        vector = cls()
        vector._from_ad_proto(proto)
        return vector

    def __getitem__(self, index: int) -> float:
        return [self.x, self.y, self.z][index]

    def __setitem__(self, index: int, value: float) -> None:
        if index == 0:
            self.x = value
        elif index == 1:
            self.y = value
        elif index == 2:
            self.z = value
        else:
            raise IndexError(f"Index {index} out of bounds for Vector3")

    def __iter__(self) -> Iterator[float]:
        """Enable iteration over the vector components."""
        yield self.x
        yield self.y
        yield self.z

    def __len__(self) -> int:
        """Return the number of components in the vector."""
        return 3


Vector3Like: TypeAlias = Vector3 | list[float] | tuple[float, float, float]  # type: ignore


def _to_vector3(value: Vector3Like) -> Vector3:
    if isinstance(value, Vector3):
        return value
    elif isinstance(value, list) or isinstance(value, tuple):
        assert len(value) == 3
        return Vector3(value[0], value[1], value[2])
    else:
        raise TypeError(f"Not a valid Vector3Like: {type(value)}")


def _to_vector3_proto(value: Vector3Like) -> commonpb.Vector3:
    return _to_vector3(value)._to_proto()


def _to_vector3_ad_proto(value: Vector3Like) -> AdVector3:
    return _to_vector3(value)._to_ad_proto()
