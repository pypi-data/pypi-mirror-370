# Copyright 2024 Luminary Cloud, Inc. All Rights Reserved.
from dataclasses import dataclass
from luminarycloud._proto.output import output_pb2 as outputpb

from luminarycloud.params.outputs import Output
from luminarycloud.params.enum import ResidualQuantity, ResidualNormalization


@dataclass(kw_only=True)
class ResidualOutput(Output):

    quantity: ResidualQuantity = ResidualQuantity.DENSITY
    normalization: ResidualNormalization = ResidualNormalization.RELATIVE

    def _to_proto(self) -> outputpb.Output:
        _proto = super()._to_proto()
        _proto.quantity = self.quantity.value
        _proto.residual_properties.type = self.normalization.value
        return _proto

    def _from_proto(self, proto: outputpb.Output) -> None:
        super()._from_proto(proto)
        self.quantity = ResidualQuantity(proto.quantity)
        self.normalization = ResidualNormalization(proto.residual_properties.type)
