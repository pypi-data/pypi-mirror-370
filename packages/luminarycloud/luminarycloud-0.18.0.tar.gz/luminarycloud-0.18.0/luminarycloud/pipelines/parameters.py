# Copyright 2025 Luminary Cloud, Inc. All Rights Reserved.
from .core import PipelineParameter
from typing import Type


class StringPipelineParameter(PipelineParameter):
    """
    A String Pipeline Parameter can replace a hard-coded string in Pipeline operator arguments to
    allow its value to be set when the Pipeline is invoked.
    """

    @classmethod
    def _represented_type(cls) -> Type:
        return str

    @classmethod
    def _type_name(cls) -> str:
        return "string"


class FloatPipelineParameter(PipelineParameter):
    """
    A Float Pipeline Parameter can replace a hard-coded float in Pipeline operator arguments to
    allow its value to be set when the Pipeline is invoked.
    """

    @classmethod
    def _represented_type(cls) -> Type:
        return float

    @classmethod
    def _type_name(cls) -> str:
        return "float"


class IntPipelineParameter(PipelineParameter):
    """
    An Int Pipeline Parameter can replace a hard-coded int in Pipeline operator arguments to
    allow its value to be set when the Pipeline is invoked.
    """

    @classmethod
    def _represented_type(cls) -> Type:
        return int

    @classmethod
    def _type_name(cls) -> str:
        return "int"


class BoolPipelineParameter(PipelineParameter):
    """
    A Bool Pipeline Parameter can replace a hard-coded bool in Pipeline operator arguments to
    allow its value to be set when the Pipeline is invoked.
    """

    @classmethod
    def _represented_type(cls) -> Type:
        return bool

    @classmethod
    def _type_name(cls) -> str:
        return "bool"
