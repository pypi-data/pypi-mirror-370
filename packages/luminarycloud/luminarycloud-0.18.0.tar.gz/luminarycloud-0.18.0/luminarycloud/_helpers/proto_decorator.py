# Copyright 2025 Luminary Cloud, Inc. All Rights Reserved.
from typing import (
    Generic,
    TypeVar,
    get_type_hints,
    get_origin,
)

from google.protobuf.message import Message

from luminarycloud.types import Vector3

P = TypeVar("P", bound=Message)
C = TypeVar("C")


class proto_decorator(Generic[P]):
    """
    A decorator that adds a `to_proto` method to a class.

    NOTE: only works for primitive and basepb.Vector3 fields right now.
    """

    proto_type: type[P]

    def __init__(decorator, proto_type: type[P]):
        decorator.proto_type = proto_type

    def __call__(decorator, cls: type[C]) -> type[C]:
        type_hints = get_type_hints(cls)
        fields = decorator.proto_type.DESCRIPTOR.fields

        def _to_proto(self: type[C]) -> P:
            proto = decorator.proto_type()
            for field in fields:
                _type = type_hints.get(field.name, None)
                if _type:
                    value = getattr(self, field.name)
                    if issubclass(_type, Vector3):
                        vector_proto = getattr(proto, field.name)
                        vector_proto.x = value.x
                        vector_proto.y = value.y
                        vector_proto.z = value.z
                    else:
                        setattr(proto, field.name, value)
            return proto

        setattr(cls, "_to_proto", _to_proto)
        return cls
