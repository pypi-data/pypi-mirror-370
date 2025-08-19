# Copyright 2024 Luminary Cloud, Inc. All Rights Reserved.
from google.protobuf.descriptor import FieldDescriptor
from google.protobuf.message import Message

import luminarycloud._proto.base.base_pb2 as basepb
import luminarycloud._proto.options.options_pb2 as optionspb
from luminarycloud.types.vector3 import _to_vector3_proto


def _reset_defaults(params: Message) -> None:
    for field in params.DESCRIPTOR.fields:
        if field.label == FieldDescriptor.LABEL_REPEATED:
            for nested in getattr(params, field.name):
                _reset_defaults(nested)
        else:
            _set_default(params, field.name)
            if field.message_type is not None:
                _reset_defaults(getattr(params, field.name))


def _set_default(params: Message, name: str) -> None:
    field = params.DESCRIPTOR.fields_by_name[name]
    dfl: optionspb.Value = field.GetOptions().Extensions[optionspb.default_value]
    type = dfl.WhichOneof("typ")
    if type == "boolval":
        setattr(params, name, dfl.boolval)
    elif type == "choice":
        setattr(params, name, dfl.choice)
    elif type == "strval":
        setattr(params, name, dfl.strval)
    elif type == "intval":
        int_param: basepb.Int = getattr(params, name)
        int_param.value = dfl.intval
    elif type == "real":
        real_param: basepb.AdFloatType = getattr(params, name)
        real_param.CopyFrom(dfl.real)
    elif type == "vector3":
        param: basepb.AdVector3 = getattr(params, name)
        param.CopyFrom(dfl.vector3)
    return None
