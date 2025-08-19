# Copyright 2025 Luminary Cloud, Inc. All Rights Reserved.
from typing import List, Optional

from .._client import get_default_client
from .._proto.api.v0.luminarycloud.physics_ai import physics_ai_pb2 as physaipb
from .._wrapper import ProtoWrapper, ProtoWrapperBase
from ..types.ids import PhysicsAiArchitectureID, PhysicsAiArchitectureVersionID
from ..enum.physics_ai_lifecycle_state import PhysicsAiLifecycleState


@ProtoWrapper(physaipb.PhysicsAiArchitectureVersion)
class PhysicsAiArchitectureVersion(ProtoWrapperBase):
    """
    Represents a specific version of a Physics AI architecture.

    .. warning:: This feature is experimental and may change or be removed without notice.
    """

    id: PhysicsAiArchitectureVersionID
    name: str
    changelog: str
    lifecycle_state: PhysicsAiLifecycleState
    _proto: physaipb.PhysicsAiArchitectureVersion


@ProtoWrapper(physaipb.PhysicsAiArchitecture)
class PhysicsAiArchitecture(ProtoWrapperBase):
    """
    Represents a Physics AI architecture with all its versions.

    .. warning:: This feature is experimental and may change or be removed without notice.
    """

    id: PhysicsAiArchitectureID
    name: str
    description: str
    versions: List[PhysicsAiArchitectureVersion]
    _proto: physaipb.PhysicsAiArchitecture

    def get_latest_version(self) -> Optional[PhysicsAiArchitectureVersion]:
        """
        Get the latest version of this architecture based on name.

        Returns
        -------
        PhysicsAiArchitectureVersion or None
            The first architecture version, or None if no versions exist.
            Note: Version ordering is now determined by the backend.
        """
        if not self.versions:
            return None
        return self.versions[0] if self.versions else None


def list_architectures() -> List[PhysicsAiArchitecture]:
    """
    List available Physics AI architectures for model training.

    .. warning:: This feature is experimental and may change or be removed without notice.

    Returns
    -------
    list[PhysicsAiArchitecture]
        A list of all available Physics AI architectures.
    """
    req = physaipb.ListArchitecturesRequest()
    res = get_default_client().ListArchitectures(req)
    return [PhysicsAiArchitecture(arch) for arch in res.architectures]
