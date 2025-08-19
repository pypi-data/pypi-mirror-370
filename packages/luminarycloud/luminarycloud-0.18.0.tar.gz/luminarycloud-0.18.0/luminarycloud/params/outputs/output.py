# Copyright 2024 Luminary Cloud, Inc. All Rights Reserved.
from abc import abstractmethod
from luminarycloud.params.simulation._lib import ParamGroupWrapper
from luminarycloud._helpers import CodeRepr
from luminarycloud._proto.output import output_pb2 as outputpb


class Output(CodeRepr, ParamGroupWrapper[outputpb.Output]):
    """A quantity that can be extracted from the output of a simulation"""

    name: str = ""

    @abstractmethod
    def _to_proto(self) -> outputpb.Output:
        _proto = outputpb.Output()
        _proto.name = self.name
        return _proto

    @abstractmethod
    def _from_proto(self, proto: outputpb.Output) -> None:
        self.name = proto.name
