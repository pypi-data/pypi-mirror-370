# Copyright 2024 Luminary Cloud, Inc. All Rights Reserved.
from dataclasses import dataclass
from typing import Any
from ._proto.base.base_pb2 import AdFloatType
from ._proto.output import reference_values_pb2 as refvalpb
from ._proto.client import simulation_pb2 as clientpb
from ._helpers import CodeRepr
from .enum import ReferenceValuesType


@dataclass(kw_only=True)
class ReferenceValues(CodeRepr):
    """
    Reference values needed for computing forces, moments and other
    non-dimensional output quantities.
    """

    reference_value_type: ReferenceValuesType = ReferenceValuesType.PRESCRIBE_VALUES
    """
    Method of specification for the reference values used in force and moment
    computations. Default: PRESCRIBE_VALUES
    """

    area_ref: float = 1.0
    "Reference area for computing force and moment coefficients. Default: 1.0"

    length_ref: float = 1.0
    "Reference length for computing moment coefficients. Default: 1.0"

    use_aero_moment_ref_lengths: bool = False
    "Whether to use separate reference lengths for pitching, rolling and yawing moments. Default: False"

    length_ref_pitch: float = 1.0
    "Reference length for computing pitching moment coefficients. Default: 1.0"

    length_ref_roll: float = 1.0
    "Reference length for computing rolling moment coefficients. Default: 1.0"

    length_ref_yaw: float = 1.0
    "Reference length for computing yawing moment coefficients. Default: 1.0"

    p_ref: float = 101325.0
    """
    Absolute static reference pressure for computing force and moment
    coefficients. This value is independent of the simulation reference
    pressure. Default: 101325.0
    """

    t_ref: float = 288.15
    """
    Reference temperature for computing force and moment coefficients.
    Default: 288.15
    """

    v_ref: float = 1.0
    """
    Reference velocity magnitude for computing force and moment coefficients.
    Default: 1.0
    """

    def _to_proto_common(self, proto: Any) -> None:
        # SimulationParam's reference values do not have "reference_value_type".
        proto.area_ref.CopyFrom(AdFloatType(value=self.area_ref))
        proto.length_ref.CopyFrom(AdFloatType(value=self.length_ref))
        proto.use_aero_moment_ref_lengths = self.use_aero_moment_ref_lengths
        proto.length_ref_pitch.CopyFrom(AdFloatType(value=self.length_ref_pitch))
        proto.length_ref_roll.CopyFrom(AdFloatType(value=self.length_ref_roll))
        proto.length_ref_yaw.CopyFrom(AdFloatType(value=self.length_ref_yaw))
        proto.p_ref.CopyFrom(AdFloatType(value=self.p_ref))
        proto.t_ref.CopyFrom(AdFloatType(value=self.t_ref))
        proto.v_ref.CopyFrom(AdFloatType(value=self.v_ref))

    def _to_proto(self) -> refvalpb.ReferenceValues:
        proto = refvalpb.ReferenceValues(reference_value_type=self.reference_value_type.value)
        self._to_proto_common(proto)
        return proto

    def _to_client_proto(self) -> clientpb.ReferenceValues:
        proto = clientpb.ReferenceValues()
        if self.reference_value_type == ReferenceValuesType.PRESCRIBE_VALUES:
            proto.reference_type = clientpb.PRESCRIBE_VALUES
        elif self.reference_value_type == ReferenceValuesType.FARFIELD_VALUES:
            proto.reference_type = clientpb.REFERENCE_FARFIELD_VALUES
        else:
            proto.reference_type = clientpb.INVALID_REFERENCE_TYPE
        self._to_proto_common(proto)
        return proto

    def _from_client_proto(self, proto: clientpb.ReferenceValues) -> None:
        if proto.reference_type == clientpb.PRESCRIBE_VALUES:
            self.reference_value_type = ReferenceValuesType.PRESCRIBE_VALUES
        elif proto.reference_type == clientpb.REFERENCE_FARFIELD_VALUES:
            self.reference_value_type = ReferenceValuesType.FARFIELD_VALUES
        else:
            self.reference_value_type = ReferenceValuesType.UNSPECIFIED
        self.area_ref = proto.area_ref.value
        self.length_ref = proto.length_ref.value
        self.use_aero_moment_ref_lengths = proto.use_aero_moment_ref_lengths
        self.length_ref_pitch = proto.length_ref_pitch.value
        self.length_ref_roll = proto.length_ref_roll.value
        self.length_ref_yaw = proto.length_ref_yaw.value
        self.p_ref = proto.p_ref.value
        self.t_ref = proto.t_ref.value
        self.v_ref = proto.v_ref.value
