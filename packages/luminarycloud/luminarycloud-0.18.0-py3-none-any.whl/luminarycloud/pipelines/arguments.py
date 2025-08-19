# Copyright 2025 Luminary Cloud, Inc. All Rights Reserved.
from typing import Any, Type

from .core import PipelineParameter


class _NVS(PipelineParameter):
    @classmethod
    def _represented_type(cls) -> Type:
        return str

    @classmethod
    def _type_name(cls) -> str:
        return "Named Variable Set"

    def _validate(self) -> None:
        if self.name != "$named-variable-set":
            raise ValueError(
                "The Named Variable Set PipelineParameter must be named '$named-variable-set'"
            )

    def _add_to_params(self, params: dict) -> None:
        raise ValueError(
            "The NamedVariableSet parameter cannot be used explicitly in a Pipeline. It can only be used in PipelineArgs."
        )

    def _is_valid_value(self, value: Any) -> bool:
        return isinstance(value, str) and value.startswith("namedvarset-")


ArgNamedVariableSet = _NVS("$named-variable-set")
"""
This can be used in a PipelineArgs params list to add a Named Variable Set column to the args table.
There must be zero or one of these in a PipelineArgs params list.
"""

# The types that are allowed as PipelineArgs values. This is a union of all concrete
# PipelineParameters' "represented types".
PipelineArgValueType = str | int | float | bool


class PipelineArgsRow:
    def __init__(self, args: "PipelineArgs", row_values: list[PipelineArgValueType]):
        self.args = args
        self.row_values = row_values
        self._validate()

    def _validate(self) -> None:
        if len(self.row_values) != len(self.args.params):
            raise ValueError(
                f"PipelineArgs row wrong size. Expected {len(self.args.params)}, got {len(self.row_values)}"
            )
        for i, v in enumerate(self.row_values):
            param = self.args.params[i]
            if not param._is_valid_value(v):
                raise ValueError(f"PipelineArgs value {v} is invalid for parameter {param}")

    def value_for(self, param_name: str) -> PipelineArgValueType:
        return self.row_values[self.args.column_for(param_name)]

    def has_column_for(self, param_name: str) -> bool:
        return self.args.has_column_for(param_name)

    def __str__(self) -> str:
        s = "PipelineArgsRow("
        for i, v in enumerate(self.row_values):
            s += f"{self.args.params[i].name}={repr(v)}, "
        s += ")"
        return s


class PipelineArgs:
    def __init__(self, params: list[PipelineParameter], args: list[list[PipelineArgValueType]]):
        self.params = params
        self._param_index_by_name = {p.name: i for i, p in enumerate(params)}
        self._validate_params()
        self.rows = [PipelineArgsRow(self, arg) for arg in args]

    def has_column_for(self, param_name: str) -> bool:
        return param_name in self._param_index_by_name

    def column_for(self, param_name: str) -> int:
        if not self.has_column_for(param_name):
            raise ValueError(f'Parameter "{param_name}" not found')
        return self._param_index_by_name[param_name]

    def _validate_params(self) -> None:
        has_nvs = False
        seen_param_names = set()
        for p in self.params:
            if isinstance(p, _NVS):
                if has_nvs:
                    raise ValueError(
                        "There can be at most one Named Variable Set column in a PipelineArgs"
                    )
                has_nvs = True
            else:
                if p.name in seen_param_names:
                    raise ValueError(f'There is more than one parameter named "{p.name}"')
                seen_param_names.add(p.name)

    def __str__(self) -> str:
        return (
            f"PipelineArgs(param_names={[p.name for p in self.params]}, row_count={len(self.rows)})"
        )
