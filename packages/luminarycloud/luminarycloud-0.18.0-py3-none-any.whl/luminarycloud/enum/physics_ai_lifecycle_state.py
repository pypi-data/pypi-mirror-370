# Copyright 2025 Luminary Cloud, Inc. All Rights Reserved.
from enum import IntEnum
from .._proto.api.v0.luminarycloud.physics_ai.physics_ai_pb2 import (
    PhysicsAiLifecycleState as PhysicsAiLifecycleStatePb,
)


class PhysicsAiLifecycleState(IntEnum):
    """
    Represents the lifecycle state of a Physics AI resource (architecture or model version).

    Attributes
    ----------
    UNSPECIFIED
        Default value, should not be used in practice.
    DEVELOPMENT
        Not ready for general use.
    ACTIVE
        Available for new training jobs.
    DEPRECATED
        Can still serve inference, but not used for new training.
    RETIRED
        Archived; no training or inference support.
    """

    UNSPECIFIED = PhysicsAiLifecycleStatePb.LIFECYCLE_STATE_UNSPECIFIED
    DEVELOPMENT = PhysicsAiLifecycleStatePb.LIFECYCLE_STATE_DEVELOPMENT
    ACTIVE = PhysicsAiLifecycleStatePb.LIFECYCLE_STATE_ACTIVE
    DEPRECATED = PhysicsAiLifecycleStatePb.LIFECYCLE_STATE_DEPRECATED
    RETIRED = PhysicsAiLifecycleStatePb.LIFECYCLE_STATE_RETIRED
