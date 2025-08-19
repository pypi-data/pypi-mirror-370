# Copyright 2024 Luminary Cloud, Inc. All Rights Reserved.
from collections.abc import Callable
from dataclasses import dataclass, field
from logging import getLogger
from os import PathLike
from pprint import pformat
from typing import Optional, TypeVar, cast

from luminarycloud._helpers._simulation_params_from_json import (
    simulation_params_from_json_path,
    simulation_params_from_json_dict,
)
from luminarycloud._proto.client import simulation_pb2 as clientpb
from luminarycloud._proto.client.entity_pb2 import EntityIdentifier
from luminarycloud._proto.output import output_pb2 as outputpb
from luminarycloud._proto.quantity import quantity_options_pb2 as quantityoptspb
from luminarycloud.enum import AveragingType, QuantityType, SpaceAveragingType
from luminarycloud.params.geometry import Volume
from luminarycloud.params.simulation import (
    EntityRelationships,
)
from luminarycloud.params.simulation.adjoint_ import Adjoint
from luminarycloud.params.simulation.entity_relationships.volume_material_relationship_ import (
    VolumeMaterialRelationship,
)
from luminarycloud.params.simulation.entity_relationships.volume_physics_relationship_ import (
    VolumePhysicsRelationship,
)
from luminarycloud.params.simulation.material_entity_ import (
    MaterialEntity,
)
from luminarycloud.params.simulation.physics_ import Physics
from luminarycloud.params.simulation.volume_entity_ import (
    VolumeEntity,
)
from luminarycloud.params.simulation import (
    SimulationParam as _SimulationParam,
)
from luminarycloud.reference_values import ReferenceValues
from luminarycloud.types import Vector3Like
from luminarycloud.types.vector3 import _to_vector3_ad_proto

logger = getLogger(__name__)


@dataclass(kw_only=True, repr=False)
class SimulationParam(_SimulationParam):
    """
    Solver configuration parameters that support multi-physics simulations.

    The structure of these parameters is related to the decision tree of selecting different models,
    boundary conditions, etc. for the simulation.
    Most of these choices are made by picking one class for a given field over a number of
    alternatives. For example:

    >>> import luminarycloud.params.simulation as sim_params
    >>> params = SimulationParam()
    >>> params.physics[0].fluid.turbulence = sim_params.physics.fluid.turbulence.KomegaSst()
    >>> params.physics[0].fluid.turbulence = sim_params.physics.fluid.turbulence.SpalartAllmaras()

    The alternatives are listed in the documentation of each field (turbulence in this case), and
    the (sub)module that provides them is always named after the field.
    Therefore, even without consulting the documentation, it is possible to list the alternatives
    using Python's ``dir`` function, in this case:

    >>> dir(sim_params.physics.fluid.turbulence)

    The alternative classes have different fields, which may again have their own alternative
    classes thereby repeating the pattern and creating the tree structure.
    """

    reference_values: ReferenceValues = field(default_factory=ReferenceValues)
    "Reference values for outputs and stopping conditions."

    entity_relationships: EntityRelationships = field(default_factory=EntityRelationships)
    "Relationships between different entities."

    def _to_proto(self) -> clientpb.SimulationParam:
        _proto = super()._to_proto()
        _proto.reference_values.CopyFrom(self.reference_values._to_client_proto())
        return _proto

    @classmethod
    def from_proto(self, proto: clientpb.SimulationParam) -> "SimulationParam":
        _wrapper = cast(SimulationParam, super().from_proto(proto))
        _wrapper.reference_values._from_client_proto(proto.reference_values)
        return _wrapper

    @classmethod
    def from_json(cls, source: PathLike | dict) -> "SimulationParam":
        if isinstance(source, PathLike):
            return cls.from_proto(simulation_params_from_json_path(source))
        else:
            return cls.from_proto(simulation_params_from_json_dict(source))

    def assign_material(self, material: MaterialEntity, volume: Volume | str) -> None:
        """
        Assigns a material entity to a volume.

        This method links a material entity to a specific volume in the simulation domain.
        If the volume or material entity has not been added to the simulation parameters yet,
        they will be added automatically.

        Parameters
        ----------
        material : MaterialEntity
            The material entity to assign to the volume. This is typically created using
            lc.params.simulation.MaterialEntity.
        volume : Volume | str
            The volume to assign the material to. Can be a Volume object or a string
            representing the volume ID.

        Examples
        --------
        Using volumes from list_tags():

        >>> # Get the fluid volume from tags
        >>> tags = geometry.list_tags()
        >>> # Assume the fluid volume is tagged with "Fluid"
        >>> fluid_volume_tag_name = "Fluid"
        >>> fluid_tag = next(
        ...     (tag for tag in tags if tag.name == fluid_volume_tag_name and tag.volumes), None
        ... )
        >>> if fluid_tag:
        ...     # Assume we want to assign the material to the first volume in the tag
        ...     for fluid_volume in fluid_tag.volumes:
        ...         simulation_param.assign_material(material, fluid_volume)
        >>> else:
        ...     raise ValueError("No fluid volume found")

        Using volumes from list_entities():

        >>> # Get the fluid volume from list_entities()
        >>> surfaces, volumes = geometry.list_entities()
        >>> if volumes:
        ...     # Assume we want to assign the material to the first volume in the list
        ...     fluid_volume_to_assign = volumes[0]
        ...     simulation_param.assign_material(material, fluid_volume_to_assign)
        >>> else:
        ...     raise ValueError("No fluid volume found")
        """
        volume_identifier = EntityIdentifier()
        if isinstance(volume, str):
            volume_identifier.id = volume
        else:
            volume_identifier.id = volume._lcn_id

        volume_material_pairs = self.entity_relationships.volume_material_relationship
        _remove_from_list_with_warning(
            _list=volume_material_pairs,
            _accessor=lambda v: get_id(v.volume_identifier),
            _to_remove=volume_identifier.id,
            _warning_message=lambda v: (
                f"Volume {_stringify_identifier(volume_identifier)} has already been assigned "
                f"material {_stringify_identifier(v.material_identifier)}. Overwriting..."
            ),
        )

        if volume_identifier.id not in (get_id(v.volume_identifier) for v in self.volume_entity):
            volume_entity = VolumeEntity(volume_identifier=volume_identifier)
            self.volume_entity.append(volume_entity)
        if get_id(material.material_identifier) not in (
            get_id(m.material_identifier) for m in self.materials
        ):
            self.materials.append(material)

        volume_material_pairs.append(
            VolumeMaterialRelationship(
                volume_identifier=volume_identifier,
                material_identifier=material.material_identifier,
            )
        )

    def assign_physics(self, physics: Physics, volume: Volume | str) -> None:
        """
        Assigns a physics entity to a volume.

        This method links a physics entity to a specific volume in the simulation domain.
        If the volume or physics entity has not been added to the simulation parameters yet,
        they will be added automatically.

        Parameters
        ----------
        physics : Physics
            The physics entity to assign to the volume. This is typically created using
            lc.params.simulation.Physics.
        volume : Volume | str
            The volume to assign the physics to. Can be a Volume object or a string
            representing the volume ID.

        Examples
        --------
        Using volumes from list_tags():

        >>> # Get the fluid volume from tags
        >>> tags = geometry.list_tags()
        >>> # Assume the fluid volume is tagged with "Fluid"
        >>> fluid_volume_tag_name = "Fluid"
        >>> fluid_tag = next(
        ...     (tag for tag in tags if tag.name == fluid_volume_tag_name and tag.volumes), None
        ... )
        >>> if fluid_tag:
        ...     # Assume we want to assign the physics to the first volume in the tag
        ...     for fluid_volume in fluid_tag.volumes:
        ...         simulation_param.assign_physics(physics, fluid_volume)
        >>> else:
        ...     raise ValueError("No fluid volume found")

        Using volumes from list_entities():

        >>> # Get the fluid volume from list_entities()
        >>> surfaces, volumes = geometry.list_entities()
        >>> if volumes:
        ...     # Assume we want to assign the physics to the first volume in the list
        ...     fluid_volume_to_assign = volumes[0]
        ...     simulation_param.assign_physics(physics, fluid_volume_to_assign)
        >>> else:
        ...     raise ValueError("No fluid volume found")
        """
        if isinstance(volume, str):
            volume_identifier = EntityIdentifier(id=volume)
        else:
            volume_identifier = EntityIdentifier(id=volume._lcn_id)

        volume_physics_pairs = self.entity_relationships.volume_physics_relationship
        _remove_from_list_with_warning(
            _list=volume_physics_pairs,
            _accessor=lambda v: get_id(v.volume_identifier),
            _to_remove=volume_identifier.id,
            _warning_message=lambda v: (
                f"Volume {_stringify_identifier(volume_identifier)} has already been assigned "
                f"physics {_stringify_identifier(v.physics_identifier)}. Overwriting..."
            ),
        )
        _remove_from_list_with_warning(
            _list=volume_physics_pairs,
            _accessor=lambda v: get_id(v.physics_identifier),
            _to_remove=get_id(physics.physics_identifier),
            _warning_message=lambda v: (
                f"Physics {_stringify_identifier(physics.physics_identifier)} has already been "
                f"assigned to volume {_stringify_identifier(v.volume_identifier)}. Overwriting..."
            ),
        )

        if volume_identifier.id not in (get_id(v.volume_identifier) for v in self.volume_entity):
            self.volume_entity.append(VolumeEntity(volume_identifier=volume_identifier))
        if get_id(physics.physics_identifier) not in (
            get_id(p.physics_identifier) for p in self.physics
        ):
            self.physics.append(physics)

        volume_physics_pairs.append(
            VolumePhysicsRelationship(
                volume_identifier=volume_identifier,
                physics_identifier=physics.physics_identifier,
            )
        )

    def configure_adjoint_surface_output(
        self,
        quantity_type: QuantityType,
        surface_ids: list[str],
        *,
        reference_values: ReferenceValues = None,
        frame_id: str = "",
        force_direction: Optional[Vector3Like] = None,
        moment_center: Optional[Vector3Like] = None,
        averaging_type: AveragingType = AveragingType.UNSPECIFIED,
    ) -> None:
        """
        Helper to configure the surface output differentiated by the adjoint solver.
        See Simulation.download_surface_output() for details on the input parameters.

        .. warning:: This feature is experimental and may change or be removed without notice.
        """
        self.adjoint = self.adjoint or Adjoint()
        self.adjoint._output = outputpb.Output()
        self.adjoint._output.quantity = quantity_type.value
        self.adjoint._output.in_surfaces.extend(surface_ids)
        self.adjoint._output.frame_id = frame_id
        if QuantityType._is_average(quantity_type):
            if averaging_type == AveragingType.UNSPECIFIED:
                self.adjoint._output.surface_average_properties.averaging_type = (
                    SpaceAveragingType.NO_AVERAGING.value
                )
            elif averaging_type == AveragingType.AREA:
                self.adjoint._output.surface_average_properties.averaging_type = (
                    SpaceAveragingType.AREA.value
                )
            elif averaging_type == AveragingType.MASS_FLOW:
                self.adjoint._output.surface_average_properties.averaging_type = (
                    SpaceAveragingType.MASS_FLOW.value
                )
        elif QuantityType._is_force(quantity_type):
            self.adjoint._output.force_properties.CopyFrom(
                outputpb.ForceProperties(
                    force_dir_type=(
                        outputpb.FORCE_DIRECTION_BODY_ORIENTATION_AND_FLOW_DIR
                        if quantity_type._has_tag(quantityoptspb.TAG_AUTO_DIRECTION)
                        else outputpb.FORCE_DIRECTION_CUSTOM
                    ),
                    force_direction=(
                        _to_vector3_ad_proto(force_direction) if force_direction else None
                    ),
                    moment_center=_to_vector3_ad_proto(moment_center) if moment_center else None,
                )
            )
        else:
            raise ValueError("Invalid QuantityType.")

        if reference_values is not None:
            self.reference_values = reference_values

    def __repr__(self) -> str:
        return pformat(vars(self), compact=True, sort_dicts=True)

    def to_code(self, hide_defaults: bool = True, use_tmp_objs: bool = True) -> str:
        """
        Returns the python code that generates an identical SimulationParam object.
        This is an automatic representation that does not make use of helper functions like
        assign_material and assign_physics.
        Parameters with default values are omitted by default, with hide_defaults=False, code will
        also be generated for those parameters.
        By default the idiom used to populate lists and maps is to create a temporary object and
        then append or insert, respectively. The alternative, using [] to access items, is used if
        use_tmp_objs=False.
        """
        code = """## NOTE: This is an automatic representation of a SimulationParam object as the
## code that creates (from scratch) an identical object. As such, some parts do
## not match 1 to 1 with hand-written examples.
import luminarycloud
from luminarycloud.types import Vector3
from luminarycloud.tables import RectilinearTable
from luminarycloud.enum import *
from luminarycloud.params.enum import *
from luminarycloud.params import simulation as sim_params
from luminarycloud import outputs, SimulationParam, EntityIdentifier


"""
        code += self._to_code_helper("obj", hide_defaults, use_tmp_objs).replace(
            "luminarycloud.simulation_param.SimulationParam()", "luminarycloud.SimulationParam()", 1
        )
        if self.adjoint.primal_simulation_id != "":
            code += """
# TODO(USER): Select appropriate parameters to configure the adjoint output.
obj.configure_adjoint_output("...")
"""
        return code

    def find_parameter(self, parameter: str) -> None:
        """
        Searches the full output of "to_code(False, False)" for occurrences of "parameter" and prints
        the lines with matches. This is a helper function to assist users in finding, for example,
        how to change farfield conditions, material properties, etc.
        """
        for i, line in enumerate(self.to_code(False, False).split("\n")):
            if parameter.lower() in line.lower():
                print(f"line {i}: {line}")


T = TypeVar("T")
U = TypeVar("U")


def _remove_from_list_with_warning(
    _list: list[T],
    _accessor: Callable[[T], U],
    _to_remove: U,
    _warning_message: Callable[[T], str],
) -> None:
    for i, e in reversed(list(enumerate(_list))):
        if _accessor(e) == _to_remove:
            logger.warning(_warning_message(e))
            _list.pop(i)


def _stringify_identifier(identifier: Optional[EntityIdentifier]) -> str:
    if identifier is None:
        return ""
    if identifier.name:
        return f'"{identifier.name}" ({identifier.id})'
    return f"({identifier.id})"


def get_id(identifier: Optional[EntityIdentifier]) -> str:
    if identifier is None:
        return ""
    return identifier.id
