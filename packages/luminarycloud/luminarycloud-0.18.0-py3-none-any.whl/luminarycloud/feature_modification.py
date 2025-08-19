# Copyright 2025 Luminary Cloud, Inc. All Rights Reserved.
from enum import Enum, auto
from typing import Dict, Iterable, List, Optional, cast
from copy import deepcopy

from luminarycloud.types.adfloat import _to_ad_proto, _from_ad_proto
from ._proto.geometry import geometry_pb2 as gpb
from .types import Vector3Like
from .types.vector3 import _to_vector3
from .params.geometry import Shape, Sphere, Cube, Cylinder, Torus, Cone, HalfSphere, Volume
from google.protobuf.internal.containers import RepeatedScalarFieldContainer


class FeatureOperationType(Enum):
    """Enum representing the type of operation in a Feature."""

    IMPORT_GEOMETRY = auto()
    CREATE = auto()
    DELETE = auto()
    UNION = auto()
    SUBTRACTION = auto()
    INTERSECTION = auto()
    CHOP = auto()
    IMPRINT = auto()
    TRANSLATE = auto()
    ROTATE = auto()
    SCALE = auto()
    SHRINKWRAP = auto()
    FARFIELD = auto()
    PATTERN_LINEAR = auto()
    PATTERN_CIRCULAR = auto()
    CONFIGURATIONS = auto()


def _volumes_to_int_list(volumes: Iterable[Volume | int]) -> List[int]:
    """
    Convert a collection of Volume objects or integer IDs to a list of integer IDs.

    Args:
        volumes: Collection of volumes or volume IDs

    Returns:
        List of integer IDs

    Raises:
        TypeError: If any item in volumes is not a Volume object or integer
    """
    result = []
    for v in volumes:
        if isinstance(v, Volume):
            result.append(int(v.id))
        elif isinstance(v, int):
            result.append(v)
        else:
            raise TypeError(f"Unsupported type for volume: {type(v)}")
    return result


def get_operation_type(feature: gpb.Feature) -> FeatureOperationType:
    """
    Determine which type of operation is active in a gpb.Feature object.

    Args:
        feature: A gpb.Feature object

    Returns:
        The FeatureOperationType enum value representing the active operation

    Raises:
        ValueError: If the feature has no operation set or has an unknown operation type
    """
    operation = feature.WhichOneof("operation")
    if operation is None:
        raise ValueError("No operation set on feature")

    # Base operation map for simple one-to-one mappings
    base_operation_map = {
        "import_geometry": FeatureOperationType.IMPORT_GEOMETRY,
        "create": FeatureOperationType.CREATE,
        "delete": FeatureOperationType.DELETE,
        "imprint": FeatureOperationType.IMPRINT,
        "shrinkwrap": FeatureOperationType.SHRINKWRAP,
        "farfield": FeatureOperationType.FARFIELD,
        "configurations": FeatureOperationType.CONFIGURATIONS,
    }

    # Handle boolean operations
    if operation == "boolean":
        bool_op = feature.boolean.WhichOneof("op")
        if bool_op == "reg_union":
            return FeatureOperationType.UNION
        elif bool_op == "reg_subtraction":
            return FeatureOperationType.SUBTRACTION
        elif bool_op == "reg_intersection":
            return FeatureOperationType.INTERSECTION
        elif bool_op == "reg_chop":
            return FeatureOperationType.CHOP
        else:
            raise ValueError(f"Unknown boolean operation type: {bool_op}")

    # Handle transform operations
    elif operation == "transform":
        transform_op = feature.transform.WhichOneof("t")
        if transform_op == "translation":
            return FeatureOperationType.TRANSLATE
        elif transform_op == "rotation":
            return FeatureOperationType.ROTATE
        elif transform_op == "scaling":
            return FeatureOperationType.SCALE
        else:
            raise ValueError(f"Unknown transform operation type: {transform_op}")

    # Handle pattern operations
    elif operation == "pattern":
        pattern_type = feature.pattern.direction.WhichOneof("type")
        if pattern_type == "linear_spacing":
            return FeatureOperationType.PATTERN_LINEAR
        elif pattern_type == "circular_distribution":
            return FeatureOperationType.PATTERN_CIRCULAR
        else:
            raise ValueError(f"Unknown pattern type: {pattern_type}")

    # Handle simple operations
    elif operation in base_operation_map:
        return base_operation_map[operation]

    # If we get here, it's an unknown operation type
    raise ValueError(f"Unknown operation type: {operation}")


def _update_repeated_field(
    target_field: RepeatedScalarFieldContainer[int], new_values: list[int]
) -> None:
    """Helper function to update a repeated field without using clear().

    Args:
        target_field: The RepeatedScalarFieldContainer[int] protobuf repeated field
        new_values: The new values to set

    This is needed because some versions of protobuf don't support clear() on RepeatedScalarContainer.
    """

    # Delete all existing elements
    while len(target_field) > 0:
        del target_field[0]

    # Add new elements
    target_field.extend(new_values)


def modify_import(
    feature: gpb.Feature,
    geometry_url: Optional[str] = None,
    scaling: Optional[float] = None,
) -> gpb.Modification:
    """
    Modify an import feature with optional new values.
    For any parameter, if None is passed, the existing value is kept.

    Args:
        feature: A gpb.Feature object
        geometry_url: The new geometry URL
        scaling: New scaling factor

    Returns:
        A gpb.Modification object
    """
    if get_operation_type(feature) != FeatureOperationType.IMPORT_GEOMETRY:
        raise ValueError("Feature is not an import operation")

    feature_copy = deepcopy(feature)

    if geometry_url is not None:
        # TODO(chiodi): Handle upload of file here.
        feature_copy.import_geometry.geometry_url = geometry_url

    if scaling is not None:
        feature_copy.import_geometry.scaling.CopyFrom(_to_ad_proto(scaling))

    return gpb.Modification(
        mod_type=gpb.Modification.ModificationType.MODIFICATION_TYPE_UPDATE_FEATURE,
        feature=feature_copy,
    )


def modify_create(
    feature: gpb.Feature,
    shape: Optional[Shape] = None,
) -> gpb.Modification:
    """
    Modify a create feature with a new shape.
    If shape is None, the existing shape is kept.

    Args:
        feature: A gpb.Feature object
        shape: New shape to create (Sphere, Cube, Cylinder, etc.)

    Returns:
        A gpb.Modification object
    """
    if get_operation_type(feature) != FeatureOperationType.CREATE:
        raise ValueError("Feature is not a create operation")

    feature_copy = deepcopy(feature)
    create_op = feature_copy.create

    if shape is not None:
        create_op.ClearField("shape")

        if isinstance(shape, Sphere):
            create_op.sphere.CopyFrom(shape._to_proto())  # type: ignore
        elif isinstance(shape, Cube):
            create_op.box.CopyFrom(shape._to_proto())  # type: ignore
        elif isinstance(shape, Cylinder):
            create_op.cylinder.CopyFrom(shape._to_proto())  # type: ignore
        elif isinstance(shape, Torus):
            create_op.torus.CopyFrom(shape._to_proto())  # type: ignore
        elif isinstance(shape, Cone):
            create_op.cone.CopyFrom(shape._to_proto())  # type: ignore
        elif isinstance(shape, HalfSphere):
            create_op.half_sphere.CopyFrom(shape._to_proto())  # type: ignore
        else:
            raise TypeError(f"Unsupported shape type: {type(shape)}")

    return gpb.Modification(
        mod_type=gpb.Modification.ModificationType.MODIFICATION_TYPE_UPDATE_FEATURE,
        feature=feature_copy,
    )


def modify_delete(
    feature: gpb.Feature,
    volumes: Optional[List[Volume | int]] = None,
) -> gpb.Modification:
    """
    Modify a delete feature with optional new values.
    For any parameter, if None is passed, the existing value is kept.

    Args:
        feature: A gpb.Feature object
        volumes: List of volumes or volume IDs to delete

    Returns:
        A gpb.Modification object
    """
    if get_operation_type(feature) != FeatureOperationType.DELETE:
        raise ValueError("Feature is not a delete operation")

    feature_copy = deepcopy(feature)
    delete_op = feature_copy.delete

    if delete_op.type != gpb.EntityType.BODY:
        raise ValueError("Only body delete operations currently supported")

    if volumes is not None:
        vol_ids = _volumes_to_int_list(volumes)
        _update_repeated_field(delete_op.ids, vol_ids)

    return gpb.Modification(
        mod_type=gpb.Modification.ModificationType.MODIFICATION_TYPE_UPDATE_FEATURE,
        feature=feature_copy,
    )


def modify_union(
    feature: gpb.Feature,
    volumes: Optional[List[Volume | int]] = None,
) -> gpb.Modification:
    """
    Modify a boolean union feature with optional new body IDs.
    If volumes is None, the existing body IDs are kept.

    Args:
        feature: A gpb.Feature object
        volumes: List of volumes or volume IDs to union

    Returns:
        A gpb.Modification object
    """
    if get_operation_type(feature) != FeatureOperationType.UNION:
        raise ValueError("Feature is not a boolean union operation")

    feature_copy = deepcopy(feature)
    boolean_op = feature_copy.boolean

    if volumes is not None:
        vol_ids = _volumes_to_int_list(volumes)
        _update_repeated_field(boolean_op.reg_union.bodies, vol_ids)

    return gpb.Modification(
        mod_type=gpb.Modification.ModificationType.MODIFICATION_TYPE_UPDATE_FEATURE,
        feature=feature_copy,
    )


def modify_subtraction(
    feature: gpb.Feature,
    volumes: Optional[List[Volume | int]] = None,
    tool_volumes: Optional[List[Volume | int]] = None,
    propagate_tool_tags: Optional[bool] = None,
) -> gpb.Modification:
    """
    Modify a boolean subtraction feature with optional new values.
    For any parameter, if None is passed, the existing value is kept.

    Args:
        feature: A gpb.Feature object
        volumes: List of volumes or volume IDs to subtract from
        tool_volumes: List of volumes or volume IDs to use for subtraction
        propagate_tool_tags: Whether to propagate tool tags

    Returns:
        A gpb.Modification object
    """
    if get_operation_type(feature) != FeatureOperationType.SUBTRACTION:
        raise ValueError("Feature is not a boolean subtraction operation")

    feature_copy = deepcopy(feature)
    boolean_op = feature_copy.boolean
    if volumes is not None:
        vol_ids = _volumes_to_int_list(volumes)
        _update_repeated_field(boolean_op.reg_subtraction.bodies, vol_ids)

    if tool_volumes is not None:
        tool_ids = _volumes_to_int_list(tool_volumes)
        _update_repeated_field(boolean_op.reg_subtraction.tools, tool_ids)

    if propagate_tool_tags is not None:
        boolean_op.reg_subtraction.propagate_tool_tags = propagate_tool_tags

    return gpb.Modification(
        mod_type=gpb.Modification.ModificationType.MODIFICATION_TYPE_UPDATE_FEATURE,
        feature=feature_copy,
    )


def modify_intersection(
    feature: gpb.Feature, volumes: Optional[List[Volume | int]] = None
) -> gpb.Modification:
    """
    Modify a boolean intersection feature with optional new volumes.
    If volumes is None, the existing volumes are kept.

    Args:
        feature: A gpb.Feature object
        volumes: List of volumes or volume IDs to intersect

    Returns:
        A gpb.Modification object
    """
    if get_operation_type(feature) != FeatureOperationType.INTERSECTION:
        raise ValueError("Feature is not a boolean intersection operation")

    feature_copy = deepcopy(feature)
    boolean_op = feature_copy.boolean

    if volumes is not None:
        vol_ids = _volumes_to_int_list(volumes)
        _update_repeated_field(boolean_op.reg_intersection.bodies, vol_ids)

    return gpb.Modification(
        mod_type=gpb.Modification.ModificationType.MODIFICATION_TYPE_UPDATE_FEATURE,
        feature=feature_copy,
    )


def modify_chop(
    feature: gpb.Feature,
    volumes: Optional[List[Volume | int]] = None,
    tool_volumes: Optional[List[Volume | int]] = None,
    propagate_tool_tags: Optional[bool] = None,
) -> gpb.Modification:
    """
    Modify a boolean chop feature with optional new values.
    For any parameter, if None is passed, the existing value is kept.

    Args:
        feature: A gpb.Feature object
        volumes: List of volumes or volume IDs to chop
        tool_volumes: List of volumes or volume IDs to use for chopping
        propagate_tool_tags: Whether to propagate tool tags

    Returns:
        A gpb.Modification object
    """
    if get_operation_type(feature) != FeatureOperationType.CHOP:
        raise ValueError("Feature is not a boolean chop operation")

    feature_copy = deepcopy(feature)
    boolean_op = feature_copy.boolean

    if volumes is not None:
        vol_ids = _volumes_to_int_list(volumes)
        _update_repeated_field(boolean_op.reg_chop.bodies, vol_ids)

    if tool_volumes is not None:
        tool_ids = _volumes_to_int_list(tool_volumes)
        _update_repeated_field(boolean_op.reg_chop.tools, tool_ids)

    if propagate_tool_tags is not None:
        boolean_op.reg_chop.propagate_tool_tags = propagate_tool_tags

    return gpb.Modification(
        mod_type=gpb.Modification.ModificationType.MODIFICATION_TYPE_UPDATE_FEATURE,
        feature=feature_copy,
    )


def modify_imprint(
    feature: gpb.Feature,
    behavior: Optional[str] = None,
    volumes: Optional[List[Volume | int]] = None,
) -> gpb.Modification:
    """
    Modify an imprint feature with optional new values.
    For any parameter, if None is passed, the existing value is kept.

    Args:
        feature: A gpb.Feature object
        behavior: Imprint behavior ("IMPRINT_ALL" or "IMPRINT_SELECTED")
        volumes: List of volumes or volume IDs to imprint. Not needed for an Imprint behavior of IMPRINT_ALL

    Returns:
        A gpb.Modification object
    """
    if get_operation_type(feature) != FeatureOperationType.IMPRINT:
        raise ValueError("Feature is not an imprint operation")

    feature_copy = deepcopy(feature)
    imprint_op = feature_copy.imprint

    if behavior is not None:
        behavior_map = {
            "IMPRINT_ALL": gpb.Imprint.ImprintBehavior.IMPRINT_ALL,
            "IMPRINT_SELECTED": gpb.Imprint.ImprintBehavior.IMPRINT_SELECTED,
        }
        if behavior not in behavior_map:
            raise ValueError(
                f"Invalid imprint behavior: {behavior}. Expected one of: {', '.join(behavior_map.keys())}"
            )
        imprint_op.behavior = behavior_map[behavior]

    if volumes is not None and imprint_op.behavior != gpb.Imprint.ImprintBehavior.IMPRINT_ALL:
        vol_ids = _volumes_to_int_list(volumes)
        _update_repeated_field(imprint_op.body, vol_ids)

    if imprint_op.behavior != gpb.Imprint.ImprintBehavior.IMPRINT_ALL and len(imprint_op.body) == 0:
        raise ValueError("No volumes provided for imprint operation")

    return gpb.Modification(
        mod_type=gpb.Modification.ModificationType.MODIFICATION_TYPE_UPDATE_FEATURE,
        feature=feature_copy,
    )


def modify_translate(
    feature: gpb.Feature,
    volumes: Optional[List[Volume | int]] = None,
    displacement: Optional[Vector3Like] = None,
    keep: Optional[bool] = None,
) -> gpb.Modification:
    """
    Modify a transform translate feature with optional new values.
    For any parameter, if None is passed, the existing value is kept.

    Args:
        feature: A gpb.Feature object
        volumes: List of volumes or volume IDs to transform
        displacement: The displacement vector [x, y, z]
        keep: Whether to keep the original bodies

    Returns:
        A gpb.Modification object
    """
    if get_operation_type(feature) != FeatureOperationType.TRANSLATE:
        raise ValueError("Feature is not a translate transform operation")

    feature_copy = deepcopy(feature)
    transform_op = feature_copy.transform

    if volumes is not None:
        vol_ids = _volumes_to_int_list(volumes)
        _update_repeated_field(transform_op.body, vol_ids)

    if displacement is not None:
        vec = _to_vector3(displacement)
        transform_op.translation.vector.x = vec.x
        transform_op.translation.vector.y = vec.y
        transform_op.translation.vector.z = vec.z

    if keep is not None:
        transform_op.keep = keep

    return gpb.Modification(
        mod_type=gpb.Modification.ModificationType.MODIFICATION_TYPE_UPDATE_FEATURE,
        feature=feature_copy,
    )


def modify_rotate(
    feature: gpb.Feature,
    volumes: Optional[List[Volume | int]] = None,
    angle: Optional[float] = None,
    axis: Optional[Vector3Like] = None,
    origin: Optional[Vector3Like] = None,
    keep: Optional[bool] = None,
) -> gpb.Modification:
    """
    Modify a transform rotate feature with optional new values.
    For any parameter, if None is passed, the existing value is kept.

    Args:
        feature: A gpb.Feature object
        volumes: List of volumes or volume IDs to transform
        angle: Rotation angle in degrees
        axis: Rotation axis vector [x, y, z]
        origin: Rotation origin point [x, y, z]
        keep: Whether to keep the original bodies

    Returns:
        A gpb.Modification object
    """
    if get_operation_type(feature) != FeatureOperationType.ROTATE:
        raise ValueError("Feature is not a rotate transform operation")

    feature_copy = deepcopy(feature)
    transform_op = feature_copy.transform

    if volumes is not None:
        vol_ids = _volumes_to_int_list(volumes)
        _update_repeated_field(transform_op.body, vol_ids)

    # Update existing rotation
    if angle is not None:
        transform_op.rotation.angle = angle

    if axis is not None:
        axis_vec = _to_vector3(axis)
        transform_op.rotation.arbitrary.direction.x = axis_vec.x
        transform_op.rotation.arbitrary.direction.y = axis_vec.y
        transform_op.rotation.arbitrary.direction.z = axis_vec.z

    if origin is not None:
        origin_vec = _to_vector3(origin)
        transform_op.rotation.arbitrary.origin.x = origin_vec.x
        transform_op.rotation.arbitrary.origin.y = origin_vec.y
        transform_op.rotation.arbitrary.origin.z = origin_vec.z

    if keep is not None:
        transform_op.keep = keep

    return gpb.Modification(
        mod_type=gpb.Modification.ModificationType.MODIFICATION_TYPE_UPDATE_FEATURE,
        feature=feature_copy,
    )


def modify_scale(
    feature: gpb.Feature,
    volumes: Optional[List[Volume | int]] = None,
    scale_factor: Optional[float] = None,
    origin: Optional[Vector3Like] = None,
    keep: Optional[bool] = None,
) -> gpb.Modification:
    """
    Modify a transform scale feature with optional new values.
    For any parameter, if None is passed, the existing value is kept.

    Args:
        feature: A gpb.Feature object
        volumes: List of volumes or volume IDs to transform
        scale_factor: Uniform scaling factor
        origin: Scaling origin point [x, y, z]
        keep: Whether to keep the original bodies

    Returns:
        A gpb.Modification object
    """
    if get_operation_type(feature) != FeatureOperationType.SCALE:
        raise ValueError("Feature is not a scale transform operation")

    feature_copy = deepcopy(feature)
    transform_op = feature_copy.transform

    if volumes is not None:
        vol_ids = _volumes_to_int_list(volumes)
        _update_repeated_field(transform_op.body, vol_ids)

    if scale_factor is not None:
        transform_op.scaling.isotropic = scale_factor

    if origin is not None:
        origin_vec = _to_vector3(origin)
        transform_op.scaling.arbitrary.x = origin_vec.x
        transform_op.scaling.arbitrary.y = origin_vec.y
        transform_op.scaling.arbitrary.z = origin_vec.z

    if keep is not None:
        transform_op.keep = keep

    return gpb.Modification(
        mod_type=gpb.Modification.ModificationType.MODIFICATION_TYPE_UPDATE_FEATURE,
        feature=feature_copy,
    )


def modify_shrinkwrap(
    feature: gpb.Feature,
    volumes: Optional[List[Volume | int]] = None,
    tool_volumes: Optional[List[Volume | int]] = None,
    mode: Optional[str] = None,
    resolution_min: Optional[float] = None,
    resolution_max: Optional[float] = None,
    resolution_uniform: Optional[float] = None,
) -> gpb.Modification:
    """
    Modify a shrinkwrap feature with optional new values.
    For any parameter, if None is passed, the existing value is kept.

    Args:
        feature: A gpb.Feature object
        volumes: List of volumes or volume IDs to shrinkwrap
        tool_volumes: List of volumes or volume IDs to use as tools
        mode: Shrinkwrap mode ("AUTOMATIC", "MINMAX", or "UNIFORM")
        resolution_min: Minimum resolution
        resolution_max: Maximum resolution
        resolution_uniform: Uniform resolution

    Returns:
        A gpb.Modification object
    """
    if get_operation_type(feature) != FeatureOperationType.SHRINKWRAP:
        raise ValueError("Feature is not a shrinkwrap operation")

    feature_copy = deepcopy(feature)
    shrinkwrap_op = feature_copy.shrinkwrap

    if volumes is not None:
        vol_ids = _volumes_to_int_list(volumes)
        _update_repeated_field(shrinkwrap_op.body, vol_ids)

    if tool_volumes is not None:
        tool_ids = _volumes_to_int_list(tool_volumes)
        _update_repeated_field(shrinkwrap_op.tool, tool_ids)

    if mode is not None:
        mode_map = {
            "AUTOMATIC": gpb.ShrinkwrapMode.AUTOMATIC,
            "MINMAX": gpb.ShrinkwrapMode.MINMAX,
            "UNIFORM": gpb.ShrinkwrapMode.UNIFORM,
        }
        if mode not in mode_map:
            raise ValueError(
                f"Invalid shrinkwrap mode: {mode}. Expected one of: {', '.join(mode_map.keys())}"
            )
        shrinkwrap_op.mode = mode_map[mode]

    if resolution_min is not None:
        shrinkwrap_op.resolution_min = resolution_min

    if resolution_max is not None:
        shrinkwrap_op.resolution_max = resolution_max

    if resolution_uniform is not None:
        shrinkwrap_op.resolution_uniform = resolution_uniform

    return gpb.Modification(
        mod_type=gpb.Modification.ModificationType.MODIFICATION_TYPE_UPDATE_FEATURE,
        feature=feature_copy,
    )


def modify_farfield(
    feature: gpb.Feature,
    shape: Optional[Shape] = None,
    volumes: Optional[List[Volume | int]] = None,
    keep_source_bodies: Optional[bool] = None,
    keep_tool_bodies: Optional[bool] = None,
    propagate_tool_tags: Optional[bool] = None,
) -> gpb.Modification:
    """
    Modify a farfield feature with optional new values.
    For any parameter, if None is passed, the existing value is kept.

    Args:
        feature: A gpb.Feature object
        shape: The shape to create for the farfield
        volumes: List of volumes or volume IDs to subtract
        keep_source_bodies: Whether to keep source bodies
        keep_tool_bodies: Whether to keep tool bodies
        propagate_tool_tags: Whether to propagate tool tags

    Returns:
        A gpb.Modification object
    """
    if get_operation_type(feature) != FeatureOperationType.FARFIELD:
        raise ValueError("Feature is not a farfield operation")

    feature_copy = deepcopy(feature)
    farfield_op = feature_copy.farfield

    if shape is not None:
        create_op = gpb.Create()
        if isinstance(shape, Sphere):
            create_op.sphere.CopyFrom(shape._to_proto())  # type: ignore
        elif isinstance(shape, Cube):
            create_op.box.CopyFrom(shape._to_proto())  # type: ignore
        elif isinstance(shape, Cylinder):
            create_op.cylinder.CopyFrom(shape._to_proto())  # type: ignore
        elif isinstance(shape, Torus):
            create_op.torus.CopyFrom(shape._to_proto())  # type: ignore
        elif isinstance(shape, Cone):
            create_op.cone.CopyFrom(shape._to_proto())  # type: ignore
        elif isinstance(shape, HalfSphere):
            create_op.half_sphere.CopyFrom(shape._to_proto())  # type: ignore
        else:
            raise TypeError(f"Unsupported shape type: {type(shape)}")
        farfield_op.create.CopyFrom(create_op)

    if volumes is not None:
        vol_ids = _volumes_to_int_list(volumes)
        _update_repeated_field(farfield_op.bodies, vol_ids)

    if keep_source_bodies is not None:
        farfield_op.keep_source_bodies = keep_source_bodies

    if keep_tool_bodies is not None:
        farfield_op.keep_tool_bodies = keep_tool_bodies

    if propagate_tool_tags is not None:
        farfield_op.propagate_tool_tags = propagate_tool_tags

    return gpb.Modification(
        mod_type=gpb.Modification.ModificationType.MODIFICATION_TYPE_UPDATE_FEATURE,
        feature=feature_copy,
    )


def modify_linear_pattern(
    feature: gpb.Feature,
    volumes: Optional[List[Volume | int]] = None,
    direction: Optional[Vector3Like] = None,
    quantity: Optional[int] = None,
    symmetric: Optional[bool] = None,
) -> gpb.Modification:
    """
    Modify a linear pattern feature with optional new values.
    For any parameter, if None is passed, the existing value is kept.

    Args:
        feature: A gpb.Feature object
        volumes: List of volumes or volume IDs to pattern
        direction: Direction vector [x, y, z]
        quantity: Number of instances
        symmetric: Whether the pattern is symmetric

    Returns:
        A gpb.Modification object
    """
    if get_operation_type(feature) != FeatureOperationType.PATTERN_LINEAR:
        raise ValueError("Feature is not a linear pattern operation")

    feature_copy = deepcopy(feature)
    pattern_op = feature_copy.pattern

    if volumes is not None:
        vol_ids = _volumes_to_int_list(volumes)
        _update_repeated_field(pattern_op.body, vol_ids)

    if direction is not None:
        # Update existing linear pattern direction
        dir_vec = _to_vector3(direction)
        pattern_op.direction.linear_spacing.vector.x = dir_vec.x
        pattern_op.direction.linear_spacing.vector.y = dir_vec.y
        pattern_op.direction.linear_spacing.vector.z = dir_vec.z

    if quantity is not None:
        pattern_op.direction.quantity = quantity

    if symmetric is not None:
        pattern_op.direction.symmetric = symmetric

    return gpb.Modification(
        mod_type=gpb.Modification.ModificationType.MODIFICATION_TYPE_UPDATE_FEATURE,
        feature=feature_copy,
    )


def modify_circular_pattern(
    feature: gpb.Feature,
    volumes: Optional[List[Volume | int]] = None,
    angle: Optional[float] = None,
    axis: Optional[Vector3Like] = None,
    origin: Optional[Vector3Like] = None,
    quantity: Optional[int] = None,
    symmetric: Optional[bool] = None,
    full_rotation: Optional[bool] = None,
) -> gpb.Modification:
    """
    Modify a circular pattern feature with optional new values.
    For any parameter, if None is passed, the existing value is kept.

    Args:
        feature: A gpb.Feature object
        volumes: List of volumes or volume IDs to pattern
        angle: Rotation angle in degrees
        axis: Rotation axis vector [x, y, z]
        origin: Rotation origin point [x, y, z]
        quantity: Number of instances
        symmetric: Whether the pattern is symmetric
        full_rotation: Whether it's a full 360-degree rotation

    Returns:
        A gpb.Modification object
    """
    if get_operation_type(feature) != FeatureOperationType.PATTERN_CIRCULAR:
        raise ValueError("Feature is not a circular pattern operation")

    feature_copy = deepcopy(feature)
    pattern_op = feature_copy.pattern

    if volumes is not None:
        vol_ids = _volumes_to_int_list(volumes)
        _update_repeated_field(pattern_op.body, vol_ids)

    if quantity is not None:
        pattern_op.direction.quantity = quantity

    if symmetric is not None:
        pattern_op.direction.symmetric = symmetric

    circular = pattern_op.direction.circular_distribution

    if angle is not None:
        circular.rotation.angle = angle

    if axis is not None:
        axis_vec = _to_vector3(axis)
        circular.rotation.arbitrary.direction.x = axis_vec.x
        circular.rotation.arbitrary.direction.y = axis_vec.y
        circular.rotation.arbitrary.direction.z = axis_vec.z

    if origin is not None:
        origin_vec = _to_vector3(origin)
        circular.rotation.arbitrary.origin.x = origin_vec.x
        circular.rotation.arbitrary.origin.y = origin_vec.y
        circular.rotation.arbitrary.origin.z = origin_vec.z

    if full_rotation is not None:
        circular.full = full_rotation

    return gpb.Modification(
        mod_type=gpb.Modification.ModificationType.MODIFICATION_TYPE_UPDATE_FEATURE,
        feature=feature_copy,
    )


def modify_configurations(
    feature: gpb.Feature,
    configurations: Optional[Dict[str, List[Volume | int]]] = None,
    active: Optional[str] = None,
) -> gpb.Modification:
    """
    Modify a configurations feature with optional new values.
    For any parameter, if None is passed, the existing value is kept.

    Args:
        feature: A gpb.Feature object
        configurations: Dictionary mapping configuration names to lists of volumes or volume IDs
        active: Name of the active configuration

    Returns:
        A gpb.Modification object
    """
    if get_operation_type(feature) != FeatureOperationType.CONFIGURATIONS:
        raise ValueError("Feature is not a configurations operation")

    feature_copy = deepcopy(feature)
    configurations_op = feature_copy.configurations
    # Replace only if there were new configs
    if configurations is not None and len(configurations) > 0:
        existing_keys = list(configurations_op.configuration.keys())
        # Delete all old configurations
        for key in existing_keys:
            configurations_op.configuration.pop(key)

        # Add new configurations
        for name, vols in configurations.items():
            config = gpb.Configurations.Configuration()
            vol_ids = _volumes_to_int_list(vols)
            config.body.extend(vol_ids)
            configurations_op.configuration[name].CopyFrom(config)

    available_configs = set(configurations_op.configuration.keys())
    if active is not None:
        if active not in available_configs:
            raise ValueError(
                f"Active configuration '{active}' not found in provided configurations"
            )
        configurations_op.active = active

    return gpb.Modification(
        mod_type=gpb.Modification.ModificationType.MODIFICATION_TYPE_UPDATE_FEATURE,
        feature=feature_copy,
    )
