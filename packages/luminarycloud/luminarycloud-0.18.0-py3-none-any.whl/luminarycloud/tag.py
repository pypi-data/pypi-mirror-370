# Copyright 2023-2024 Luminary Cloud, Inc. All Rights Reserved.

from ._proto.api.v0.luminarycloud.geometry import geometry_pb2 as geometrypb
from ._wrapper import ProtoWrapper, ProtoWrapperBase


@ProtoWrapper(geometrypb.Tag)
class Tag(ProtoWrapperBase):
    """Represents a Tag object."""

    id: str
    "ID of the tag. Can be used to assign boundary conditions and other simulation entities to the tag."
    name: str
    "The name of the tag. The tag name is unique for a given geometry."
    bodies: list[str]
    "The list of body IDs associated with the tag. These IDs are to be used when performing geometry modifications."
    volumes: list[str]
    """The list of volume IDs associated with the tag bodies. These IDs are to be used when the user wants to unroll
    the entities within a tag. This list can be used as input for volume-like simulation settings. It is recommended
    to use directly the tag ID in the assignments instead of manually unrollling the tag entities."""
    surfaces: list[str]
    """The list of surface IDs associated with the tag surfaces. These IDs are to be used when the user wants to unroll
    the entities within a tag. This list can be used as input for volume-like simulation settings. It is recommended
    to use directly the tag ID in the assignments instead of manually unrollling the tag entities."""

    _proto: geometrypb.Tag
