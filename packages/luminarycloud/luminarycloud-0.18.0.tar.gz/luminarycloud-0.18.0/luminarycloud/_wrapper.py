# Copyright 2023-2024 Luminary Cloud, Inc. All Rights Reserved.
from enum import Enum
from typing import (
    cast,
    Any,
    Callable,
    Generic,
    Iterator,
    Optional,
    SupportsIndex,
    TypeVar,
    NewType,
    get_type_hints,
    get_origin,
    get_args,
)

from google.protobuf.message import Message

from luminarycloud.types.vector3 import Vector3, _to_vector3


# We mainly need this to statically declare to the linter that these
# attributes will eventually exist.
class ProtoWrapperBase:
    _proto: Message

    def __init__(self, proto_type: Optional[Message] = None):
        pass


P = TypeVar("P", bound=Message)
C = TypeVar("C", bound=ProtoWrapperBase)


class ProtoWrapper(Generic[P]):
    """
    A class decorator for classes that wrap a proto message type.

    This class decorator is used to decorate a class C (which inherits from ProtoWrapperBase) that
    wraps a proto message type P.

    The resulting class will take a proto message of type P as an optional argument to its
    constructor, and that proto message will be stored in the _proto attribute of the class
    instance.

    Getters and setters will be created for type-annotated fields of the decorated class C that
    provide access to the corresponding fields of the underlying proto message P.

    These getters and setters have the following behavior:
    - For fields annotated with a ProtoWrapper type, values will be wrapped/unwrapped before/after
    getting/setting the underlying nested proto message.
    - For fields annotated with an Enum type, values will be wrapped/unwrapped before getting/setting
    the underlying enum value.
    - For fields annotated as a List of a ProtoWrapper or Enum type, a getter will provide read-only
    access to a list-like interface to the underlying data, while wrapping/unwrapping the elements
    of the list. This list will only accept instances of the wrapper type as elements.

    NOTE: By "annotated with a(n) X type", we mean that the annotated type must be a class that
    _inherits_ from X. It should be a class that is actually meant to be instantiated.
    For example, IntEnum, despite being a subclass of Enum, should not be used because it is only
    meant to be used as a base class for enums.

    Fields that do not have a name that matches a field in the proto message P will behave as
    normal attributes. Also, it's up to the developer to give the right type annotations to each
    field.

    ---

    For example, if you are decorating the following class:

    class MyClass(ProtoWrapperBase):
        my_field: NestedProto
        my_enum: MyEnum
        my_list: list[NestedProto]
        my_other_field: int

    Then the following lines are equivalent (read third "==" as "does the same thing as"):

    my_class.my_field == NestedProto(my_class._proto.my_field)
    my_class.my_enum == MyEnum(my_class._proto.my_enum)
    my_class.my_list.append(NestedProto()) == my_class._proto.my_list.append(NestedProto())
    my_class.my_other_field == my_class.my_other_field
    """

    def __init__(decorator, proto_type: type[P]):
        decorator.proto_type = proto_type

    def __call__(decorator, cls: type[C]) -> type[C]:
        class _W(cls):  # type: ignore
            def __init__(self, proto: Optional[P] = None):
                if proto is None:
                    proto = decorator.proto_type()
                self._proto = cast(P, proto)

            def __str__(self) -> str:
                return self._proto.__str__()

            def __repr__(self) -> str:
                return self._proto.__repr__()

        # This binds the field name to the getter.
        def getter(field_name: str) -> Any:
            return lambda self: getattr(self._proto, field_name)

        def wrapped_getter(field_name: str, wrapper: type[ProtoWrapperBase]) -> Any:
            return lambda self: wrapper(getattr(self._proto, field_name))

        # This binds the field name to the setter.
        def setter(field_name: str) -> Callable[[C, Any], None]:
            return lambda self, value: setattr(self._proto, field_name, value)

        def wrapped_setter(
            field_name: str, wrapper: type[ProtoWrapperBase]
        ) -> Callable[[C, Any], None]:
            def _set(self: C, value: Any) -> None:
                if not isinstance(value, wrapper):
                    raise TypeError(f"{field_name} should be a {wrapper.__name__}")
                setattr(self._proto, field_name, value._proto)

            return _set

        def list_wrapped_getter(field_name: str, wrapper: type[ProtoWrapperBase]) -> Any:
            return lambda self: RepeatedProtoWrapper(wrapper, getattr(self._proto, field_name))

        # Create getters that access the attributes of the underlying proto.
        type_hints = get_type_hints(cls)

        for field in decorator.proto_type.DESCRIPTOR.fields:
            _type = type_hints.get(field.name, None)
            if _type:
                fget = getter(field.name)
                fset: Optional[Callable[[C, Any], None]] = setter(field.name)
                _origin_type = get_origin(_type)
                if _origin_type is list:
                    _listed_type = get_args(_type)[0]
                    try:
                        if issubclass(_listed_type, Enum) or issubclass(
                            _listed_type, ProtoWrapperBase
                        ):
                            fget = list_wrapped_getter(field.name, _listed_type)
                            fset = None
                    except TypeError:
                        # _listed_type is not a class (e.g., forward reference that couldn't be resolved)
                        # Fall back to basic getter
                        pass
                elif isinstance(_type, NewType):
                    pass
                else:
                    try:
                        if issubclass(_type, Enum) or issubclass(_type, ProtoWrapperBase):
                            fget = wrapped_getter(field.name, _type)
                            fset = wrapped_setter(field.name, _type)
                    except TypeError:
                        # _type is not a class (e.g., forward reference that couldn't be resolved)
                        # Fall back to basic getter
                        pass
                setattr(_W, field.name, property(fget=fget, fset=fset))

        # Preserve the original class annotations in the new class
        class_dict = {}
        if hasattr(cls, "__annotations__"):
            class_dict["__annotations__"] = cls.__annotations__

        W = type(cls.__name__, (_W,), class_dict)
        return cast(type[C], W)


class RepeatedProtoWrapper(Generic[C]):
    """
    A wrapper for a list of proto messages.

    This wrapper is used to wrap/unwrap the elements of a list of proto messages.
    """

    def __init__(self, wrapper: type[C], values: list[Message]):
        self._wrapper = wrapper
        self._values = values

    def __len__(self) -> int:
        return len(self._values)

    def __getitem__(self, key: SupportsIndex) -> C:
        return self._wrapper(self._values[key])

    def __setitem__(self, key: SupportsIndex, value: C) -> None:
        if not isinstance(value, self._wrapper):
            raise TypeError
        self._values[key] = value._proto

    def __delitem__(self, key: SupportsIndex) -> None:
        del self._values[key]

    def __iter__(self) -> Iterator[C]:
        return (self._wrapper(value) for value in self._values)

    def __reversed__(self) -> Iterator[C]:
        return reversed(list(self.__iter__()))

    def append(self, value: C) -> None:
        if not isinstance(value, self._wrapper):
            raise TypeError
        self._values.append(value._proto)
