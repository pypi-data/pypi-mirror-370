# Copyright 2024 Luminary Cloud, Inc. All Rights Reserved.
# type: ignore

from functools import wraps
from typing import TypeVar

from google.protobuf.message import Message
from luminarycloud._proto.client import simulation_pb2 as clientpb
from luminarycloud._helpers.defaults import _reset_defaults

_P = TypeVar("P", bound=Message)


def _monkey_patch(cls: type[_P]) -> type[_P]:
    """
    Monkey patch the given class to set proto defaults on __init__.

    We use this to monkey patch the generated raw protos for client
    params so that they are populated with default values.
    """

    __class__ = cls
    init = cls.__init__

    @wraps(cls.__init__, assigned=["__signature__"])
    def init_with_defaults(self, *args, **kwargs):
        super().__init__()
        _reset_defaults(self)
        init(self, *args, **kwargs)

    cls.__init__ = init_with_defaults


_monkey_patch(clientpb.SimulationParam)
_monkey_patch(clientpb.FrameTransforms)
_monkey_patch(clientpb.VolumeMaterialRelationship)
_monkey_patch(clientpb.VolumePhysicsRelationship)
_monkey_patch(clientpb.BoundaryLayerProfile)
_monkey_patch(clientpb.BoundaryConditionsHeat)
_monkey_patch(clientpb.HeatSource)
_monkey_patch(clientpb.SlidingInterfaces)
_monkey_patch(clientpb.PeriodicPair)
_monkey_patch(clientpb.BladeElementAirfoilData)
_monkey_patch(clientpb.BoundaryConditionsFluid)
_monkey_patch(clientpb.PhysicalBehavior)
_monkey_patch(clientpb.PorousBehavior)
_monkey_patch(clientpb.MaterialEntity)
_monkey_patch(clientpb.VolumeEntity)
_monkey_patch(clientpb.MotionData)
_monkey_patch(clientpb.ParticleGroup)
_monkey_patch(clientpb.MonitorPlane)
_monkey_patch(clientpb.Physics)
