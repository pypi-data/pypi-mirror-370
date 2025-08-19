# Copyright 2025 Luminary Cloud, Inc. All Rights Reserved.
from enum import IntEnum
from .._proto.output import output_pb2 as outputpb


class ForceDirectionType(IntEnum):
    """
    Whether a force output's direction is explicit ("custom") or implicit (based on "body
    orientation and flow direction")

    Attributes
    ----------
    CUSTOM
    BODY_ORIENTATION_AND_FLOW_DIR
    """

    UNSPECIFIED = outputpb.INVALID_FORCE_DIRECTION_TYPE

    CUSTOM = outputpb.FORCE_DIRECTION_CUSTOM
    BODY_ORIENTATION_AND_FLOW_DIR = outputpb.FORCE_DIRECTION_BODY_ORIENTATION_AND_FLOW_DIR
