# Copyright 2025 Luminary Cloud, Inc. All Rights Reserved.
from typing import List, Optional

from .._client import get_default_client
from .._proto.api.v0.luminarycloud.physics_ai import physics_ai_pb2 as physaipb
from .._wrapper import ProtoWrapper, ProtoWrapperBase
from ..types.ids import PhysicsAiModelID, PhysicsAiModelVersionID
from ..enum.physics_ai_lifecycle_state import PhysicsAiLifecycleState


@ProtoWrapper(physaipb.PhysicsAiModelVersion)
class PhysicsAiModelVersion(ProtoWrapperBase):
    """
    Represents a specific version of a Physics AI model.

    .. warning:: This feature is experimental and may change or be removed without notice.
    """

    id: PhysicsAiModelVersionID
    name: str
    lifecycle_state: PhysicsAiLifecycleState
    _proto: physaipb.PhysicsAiModelVersion


@ProtoWrapper(physaipb.PhysicsAiModel)
class PhysicsAiModel(ProtoWrapperBase):
    """
    Represents a Physics AI model with all its versions.

    .. warning:: This feature is experimental and may change or be removed without notice.
    """

    id: PhysicsAiModelID
    name: str
    description: str
    versions: List[PhysicsAiModelVersion]
    _proto: physaipb.PhysicsAiModel

    def get_latest_version(self) -> Optional[PhysicsAiModelVersion]:
        """
        Get the latest version of this model.

        Returns
        -------
        PhysicsAiModelVersion or None
            The first model version, or None if no versions exist.
            Note: Version ordering is now determined by the backend.
        """
        if not self.versions:
            return None
        return self.versions[0] if self.versions else None


def list_pretrained_models() -> List[PhysicsAiModel]:
    """
    List available pretrained Physics AI models.

    .. warning:: This feature is experimental and may change or be removed without notice.

    Returns
    -------
    list[PhysicsAiModel]
        A list of all available pretrained Physics AI models.
    """
    req = physaipb.ListPretrainedModelsRequest()
    res = get_default_client().ListPretrainedModels(req)
    return [PhysicsAiModel(model) for model in res.models]
