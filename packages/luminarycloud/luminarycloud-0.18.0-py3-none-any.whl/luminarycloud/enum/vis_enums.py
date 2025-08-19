from typing import cast
from ..enum import quantity_type
from .._proto.api.v0.luminarycloud.vis import vis_pb2
from enum import IntEnum, Enum
from .._proto.quantity import quantity_options_pb2 as quantityoptspb
from .._proto.quantity import quantity_pb2 as quantitypb


class VisQuantity(IntEnum):
    """
    The visualization quantity. This is a subset of all quantities.

    .. warning:: This feature is experimental and may change or be removed in the future.

    """

    NONE = quantitypb.INVALID_QUANTITY_TYPE
    ABSOLUTE_PRESSURE = quantitypb.ABSOLUTE_PRESSURE
    PRESSURE = quantitypb.PRESSURE
    DENSITY = quantitypb.DENSITY
    TEMPERATURE = quantitypb.TEMPERATURE
    MACH = quantitypb.MACH
    Q_CRITERION = quantitypb.Q_CRITERION
    VELOCITY = quantitypb.VELOCITY
    WALL_SHEAR_STRESS = quantitypb.WALL_SHEAR_STRESS
    EDDY_VISCOSITY = quantitypb.EDDY_VISCOSITY
    VISCOSITY = quantitypb.VISCOSITY
    SA_VARIABLE = quantitypb.SA_VARIABLE
    TKE = quantitypb.TKE
    OMEGA = quantitypb.OMEGA
    GAMMA = quantitypb.GAMMA
    RE_THETA = quantitypb.RE_THETA
    N_TILDE = quantitypb.N_TILDE
    Y_PLUS = quantitypb.Y_PLUS
    RE_ROUGHNESS = quantitypb.RE_ROUGHNESS
    MASS_FLUX = quantitypb.MASS_FLUX
    HEAT_FLUX = quantitypb.HEAT_FLUX
    ENERGY_FLUX = quantitypb.ENERGY_FLUX
    HEAT_TRANSFER_COEFFICIENT = quantitypb.HEAT_TRANSFER_COEFFICIENT
    GRID_VELOCITY = quantitypb.GRID_VELOCITY
    # Derived fields
    RELATIVE_VELOCITY = quantitypb.RELATIVE_VELOCITY
    RELATIVE_MACH = quantitypb.RELATIVE_MACH
    PRESSURE_COEFFICIENT = quantitypb.PRESSURE_COEFFICIENT
    TOTAL_PRESSURE = quantitypb.TOTAL_PRESSURE
    TOTAL_PRESSURE_COEFFICIENT = quantitypb.TOTAL_PRESSURE_COEFFICIENT
    TOTAL_TEMPERATURE = quantitypb.TOTAL_TEMPERATURE
    SKIN_FRICTION_COEFFICIENT = quantitypb.SKIN_FRICTION_COEFFICIENT
    # Adjoint
    ADJOINT_RE_THETA = quantitypb.ADJOINT_RE_THETA
    ADJOINT_N_TILDE = quantitypb.ADJOINT_N_TILDE
    SENSITIVITY = quantitypb.SENSITIVITY
    NORMAL_SENSITIVITY = quantitypb.NORMAL_SENSITIVITY
    SMOOTHED_NORMAL_SENSITIVITY = quantitypb.SMOOTHED_NORMAL_SENSITIVITY
    # Time averaged
    MACH_TIME_AVERAGE = quantitypb.MACH_TIME_AVERAGE
    VELOCITY_TIME_AVERAGE = quantitypb.VELOCITY_TIME_AVERAGE
    TEMPERATURE_TIME_AVERAGE = quantitypb.TEMPERATURE_TIME_AVERAGE
    DENSITY_TIME_AVERAGE = quantitypb.DENSITY_TIME_AVERAGE
    PRESSURE_TIME_AVERAGE = quantitypb.PRESSURE_TIME_AVERAGE
    RELATIVE_VELOCITY_TIME_AVERAGE = quantitypb.RELATIVE_VELOCITY_TIME_AVERAGE
    VELOCITY_MAGNITUDE_TIME_AVERAGE = quantitypb.VELOCITY_MAGNITUDE_TIME_AVERAGE
    EDDY_VISCOSITY_TIME_AVERAGE = quantitypb.EDDY_VISCOSITY_TIME_AVERAGE
    VISCOSITY_TIME_AVERAGE = quantitypb.VISCOSITY_TIME_AVERAGE
    WALL_SHEAR_STRESS_TIME_AVERAGE = quantitypb.WALL_SHEAR_STRESS_TIME_AVERAGE
    Y_PLUS_TIME_AVERAGE = quantitypb.Y_PLUS_TIME_AVERAGE
    SA_VARIABLE_TIME_AVERAGE = quantitypb.SA_VARIABLE_TIME_AVERAGE
    PRESSURE_COEFFICIENT_TIME_AVERAGE = quantitypb.PRESSURE_COEFFICIENT_TIME_AVERAGE
    TOTAL_PRESSURE_TIME_AVERAGE = quantitypb.TOTAL_PRESSURE_TIME_AVERAGE
    TOTAL_TEMPERATURE_TIME_AVERAGE = quantitypb.TOTAL_TEMPERATURE_TIME_AVERAGE
    MASS_FLUX_TIME_AVERAGE = quantitypb.MASS_FLUX_TIME_AVERAGE
    Q_CRITERION_TIME_AVERAGE = quantitypb.Q_CRITERION_TIME_AVERAGE
    HEAT_FLUX_TIME_AVERAGE = quantitypb.HEAT_FLUX_TIME_AVERAGE


# Return the text name for the VisQuantity including the units, as it appears in the UI
def visquantity_text(quantity: VisQuantity) -> str:
    extensions = quantity_type._get_quantity_metadata(cast(quantity_type.QuantityType, quantity))
    text = extensions.text
    if extensions.unit_type != quantityoptspb.UNIT_DIMENSIONLESS:
        text += f" ({extensions.unit})"
    return text


class Representation(IntEnum):
    """
    The representation defines how objects will appear in the scene.

    .. warning:: This feature is experimental and may change or be removed in the future.

    Attributes:
    -----------
    SURFACE
        Show the surface of the object.
    SURFACE_WITH_EDGES
        Show the surface of the object with mesh lines.
    WIREFRAME
        Show only the object's mesh lines.
    POINTS
        Show only the objects points.
    """

    SURFACE = vis_pb2.SURFACE
    SURFACE_WITH_EDGES = vis_pb2.SURFACE_WITH_EDGES
    # TODO(matt): need to hook these up in the image renderer
    WIREFRAME = vis_pb2.WIREFRAME
    POINTS = vis_pb2.POINTS


class FieldComponent(IntEnum):
    """
    Specifies which component of a vector field is used for visualization.
    When using scalars, the component is ignored.

    .. warning:: This feature is experimental and may change or be removed in the future.

    Attributes:
    -----------
    X
        Use the 'x' component.
    Y
        Use the 'y' component.
    Z
        Use the 'z' component.
    MAGNITUDE
        Use the magnitude of the vector.
    """

    X = vis_pb2.Field.COMPONENT_X
    Y = vis_pb2.Field.COMPONENT_Y
    Z = vis_pb2.Field.COMPONENT_Z
    MAGNITUDE = vis_pb2.Field.COMPONENT_MAGNITUDE


class ColorMapPreset(IntEnum):
    """Predefined color map presets."""

    VIRIDIS = vis_pb2.ColorMapName.COLOR_MAP_NAME_VIRIDIS
    TURBO = vis_pb2.ColorMapName.COLOR_MAP_NAME_TURBO
    JET = vis_pb2.ColorMapName.COLOR_MAP_NAME_JET
    WAVE = vis_pb2.ColorMapName.COLOR_MAP_NAME_WAVE
    COOL_TO_WARM = vis_pb2.ColorMapName.COLOR_MAP_NAME_COOL_TO_WARM
    XRAY = vis_pb2.ColorMapName.COLOR_MAP_NAME_XRAY
    PLASMA = vis_pb2.ColorMapName.COLOR_MAP_NAME_PLASMA


class CameraProjection(IntEnum):
    """
    The type of projection used in the camera.

    Attributes
    ----------
    ORTHOGRAPHIC
        A orthographic (i.e., parallel) projection.
    PERSPECTIVE
        A perspective projection.
    """

    ORTHOGRAPHIC = vis_pb2.ORTHOGRAPHIC
    PERSPECTIVE = vis_pb2.PERSPECTIVE


class CameraDirection(IntEnum):
    """
    Directional camera options

    Attributes
    ----------
    X_POSITIVE
        Look down the positive x-axis
    Y_POSITIVE
        Look down the positive y-axis
    Z_POSITIVE
        Look down the positive z-axis
    X_NEGATIVE
        Look down the negative x-axis
    Y_NEGATIVE
        Look down the negative y-axis
    Z_NEGATIVE
        Look down the negative z-axis
    """

    X_POSITIVE = vis_pb2.X_POSITIVE
    Y_POSITIVE = vis_pb2.Y_POSITIVE
    Z_POSITIVE = vis_pb2.Z_POSITIVE
    X_NEGATIVE = vis_pb2.X_NEGATIVE
    Y_NEGATIVE = vis_pb2.Y_NEGATIVE
    Z_NEGATIVE = vis_pb2.Z_NEGATIVE


class RenderStatusType(IntEnum):
    """
    Represents the status of a rendering request.

    .. warning:: This feature is experimental and may change or be removed in the future.

    Attributes
    ----------
    ACTIVE
        The request is currently active and being processed.
    COMPLETED
        The request is complete.
    FAILED
        The request has failed.
    INVALID
        The request is invalid.
    """

    ACTIVE = vis_pb2.Active
    COMPLETED = vis_pb2.Completed
    FAILED = vis_pb2.Failed
    INVALID = vis_pb2.Invalid


ExtractStatusType = RenderStatusType


class EntityType(IntEnum):
    """
    An enum for specifying the source of an image. When listing extracts,
    the user must specify what type of extract they are interested in. This
    enum is only used by the visualization code.

    .. warning:: This feature is experimental and may change or be removed in the future.

    Attributes
    ----------
    SIMULATION
        Specifies a similuation entity (i.e., a result).
    MESH
        Specifies a mesh entity.
    GEOMETRY
        Specifies a geometry entity.

    """

    SIMULATION = 0
    MESH = 1
    GEOMETRY = 2


class StreamlineDirection(IntEnum):
    """
    An enum for specifying the integration direction for streamlines filters.

    .. warning:: This feature is experimental and may change or be removed in the future.

    Attributes
    ----------
    FORWARD
        Integrate streamlines in the direction of the vector field. Use this
        option when you want to see where a particle travels in the vector field
        given an initial position.
    BACKWARDS
        Integrate streamlines in the opposite direction of the vector field. Use this
        option when you want to see where a particle came from in the vector field
        given the final position.
    BOTH
        Integrate streamlines in the both directions in the vector field. Use
        this option whe you want to see both where the particle came from and
        where it travels given an initial position.

    """

    FORWARD = vis_pb2.STREAMLINES_DIRECTION_FORWARD
    BACKWARD = vis_pb2.STREAMLINES_DIRECTION_BACKWARD
    BOTH = vis_pb2.STREAMLINES_DIRECTION_BOTH


class SurfaceStreamlineMode(IntEnum):
    """
    An enum for specifying the streamline behavior for SurfaceStreamlines.

    .. warning:: This feature is experimental and may change or be removed in the future.

    Attributes
    ----------
    ADVECT_ON_SURFACE
        Particle advection is constrained to the surfaces of the mesh.
    ADVECT_IN_VOLUME
        Use points on surfaces to seed particle advection in the volume.
    """

    ADVECT_ON_SURFACE = 0
    ADVECT_IN_VOLUME = 1


class SceneMode(str, Enum):
    """
    An enum for specifying how a scene should be rendered in the UI.

    This enum controls whether the scene appears directly within the notebook output
    or inside a dedicated side panel. This is used by the visualization layer to
    determine the preferred rendering context for a given scene.

    .. warning:: This feature is experimental and may change or be removed in the future.

    Attributes
    ----------
    INLINE
        Render the scene directly in the notebook output.
    SIDE_PANEL
        Render the scene in the side panel for a more focused or persistent view.
    """

    INLINE = "inline"
    SIDE_PANEL = "side_panel"
    FULLSCREEN = "fullscreen"
