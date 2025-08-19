from abc import ABCMeta
from typing import Any, Union
from .._proto.base.base_pb2 import AdFloatType, ExpressionType, FirstOrderAdType, SecondOrderAdType


class AdFloat(float, metaclass=ABCMeta):
    """An immutable float with adjoints/tangents or an expression"""

    pass


class FirstOrderAdFloat(AdFloat):
    """An immutable float with first order adjoints/tangents attached."""

    _tangent: tuple[float, ...]
    _adjoint: tuple[float, ...]

    def __new__(cls: type["FirstOrderAdFloat"], value: float, *_: Any) -> "FirstOrderAdFloat":
        return super().__new__(cls, value)

    def __init__(self, value: float, tangent: tuple[float, ...], adjoint: tuple[float, ...]):
        if isinstance(value, AdFloat):
            raise ValueError("Value cannot be an AdFloat")
        if any(isinstance(t, AdFloat) for t in tangent):
            raise ValueError("Tangent cannot be an AdFloat")
        if any(isinstance(a, AdFloat) for a in adjoint):
            raise ValueError("Adjoint cannot be an AdFloat")
        self._tangent = tuple(float(t) for t in tangent)
        self._adjoint = tuple(float(a) for a in adjoint)

    @property
    def tangent(self) -> tuple[float, ...]:
        return self._tangent

    @property
    def adjoint(self) -> tuple[float, ...]:
        return self._adjoint

    def __eq__(self, other: Any) -> bool:
        if not isinstance(other, FirstOrderAdFloat):
            return False
        return (
            float(self) == float(other)
            and self.tangent == other.tangent
            and self.adjoint == other.adjoint
        )

    @staticmethod
    def _from_proto(proto: FirstOrderAdType) -> "FirstOrderAdFloat":
        return FirstOrderAdFloat(
            proto.value,
            tuple(t for t in proto.tangent),
            tuple(a for a in proto.adjoint),
        )


class SecondOrderAdFloat(AdFloat):
    """An immutable float with second order adjoints/tangents attached."""

    _value: FirstOrderAdFloat
    _tangent: tuple[FirstOrderAdFloat, ...]
    _adjoint: tuple[FirstOrderAdFloat, ...]

    def __new__(cls, value: FirstOrderAdFloat, *_: Any) -> "SecondOrderAdFloat":
        return super().__new__(cls, float(value))

    def __init__(
        self,
        value: FirstOrderAdFloat,
        tangent: tuple[FirstOrderAdFloat, ...],
        adjoint: tuple[FirstOrderAdFloat, ...],
    ):
        if not isinstance(value, FirstOrderAdFloat):
            raise TypeError("Value must be a FirstOrderAdFloat")
        if any(not isinstance(t, FirstOrderAdFloat) for t in tangent):
            raise TypeError("Tangent must be a tuple of FirstOrderAdFloat")
        if any(not isinstance(a, FirstOrderAdFloat) for a in adjoint):
            raise TypeError("Adjoint must be a tuple of FirstOrderAdFloat")
        self._value = value
        self._tangent = tangent
        self._adjoint = adjoint

    @property
    def value(self) -> FirstOrderAdFloat:
        return self._value

    @property
    def tangent(self) -> tuple[FirstOrderAdFloat, ...]:
        return self._tangent

    @property
    def adjoint(self) -> tuple[FirstOrderAdFloat, ...]:
        return self._adjoint

    def __eq__(self, other: Any) -> bool:
        if not isinstance(other, SecondOrderAdFloat):
            return False
        return (
            self._value == other._value
            and self._tangent == other._tangent
            and self._adjoint == other._adjoint
        )

    @staticmethod
    def _from_proto(proto: SecondOrderAdType) -> "SecondOrderAdFloat":
        return SecondOrderAdFloat(
            FirstOrderAdFloat._from_proto(proto.value),
            tuple(FirstOrderAdFloat._from_proto(t) for t in proto.tangent),
            tuple(FirstOrderAdFloat._from_proto(a) for a in proto.adjoint),
        )


class Expression:
    """An expression or value that can be evaluated or used in evaluations."""

    _value: float
    _expression: str

    def __init__(self, expression: str):
        if not expression:
            raise ValueError("Expression cannot be empty")
        self._value = 0.0
        self._expression = expression

    @property
    def expression(self) -> str:
        return self._expression

    @property
    def value(self) -> float:
        return self._value

    def _to_proto(self) -> AdFloatType:
        return AdFloatType(variable=ExpressionType(value=self.value, expression=self.expression))

    @staticmethod
    def _from_proto(proto: AdFloatType) -> "Expression":
        expr = object.__new__(Expression)  # Create a new instance without calling __init__
        expr._value = proto.variable.value
        expr._expression = proto.variable.expression
        return expr

    def __eq__(self, other: Any) -> bool:
        if not isinstance(other, Expression):
            return False
        return self._value == other._value and self._expression == other._expression


LcFloat = Union[float, FirstOrderAdFloat, SecondOrderAdFloat, Expression]


def _to_ad_proto(value: LcFloat) -> AdFloatType:
    """Convert an LcFloat to an AdFloatType proto."""
    if isinstance(value, FirstOrderAdFloat):
        return AdFloatType(
            first_order=FirstOrderAdType(
                value=float(value),
                tangent=value.tangent,
                adjoint=value.adjoint,
            )
        )
    elif isinstance(value, SecondOrderAdFloat):
        return AdFloatType(
            second_order=SecondOrderAdType(
                value=_to_ad_proto(value.value).first_order,
                tangent=[_to_ad_proto(t).first_order for t in value.tangent],
                adjoint=[_to_ad_proto(a).first_order for a in value.adjoint],
            )
        )
    elif isinstance(value, Expression):
        return value._to_proto()
    return AdFloatType(value=float(value))


def _from_ad_proto(proto: AdFloatType) -> LcFloat:
    """Convert an AdFloatType proto to an LcFloat."""
    if proto.HasField("first_order"):
        return FirstOrderAdFloat._from_proto(proto.first_order)
    elif proto.HasField("second_order"):
        return SecondOrderAdFloat._from_proto(proto.second_order)
    elif proto.HasField("value"):
        return float(proto.value)
    elif proto.HasField("variable"):
        return Expression._from_proto(proto)
    # An empty proto evaluates to 0.0
    if not proto.ListFields():
        return 0.0

    raise ValueError("Invalid AdFloatType proto")
