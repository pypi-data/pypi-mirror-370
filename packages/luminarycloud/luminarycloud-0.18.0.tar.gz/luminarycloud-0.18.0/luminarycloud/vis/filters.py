from luminarycloud.types import Vector3, Vector3Like
from ..types.vector3 import _to_vector3
from luminarycloud.enum import (
    VisQuantity,
    StreamlineDirection,
    SurfaceStreamlineMode,
    FieldComponent,
)
import luminarycloud.enum.quantity_type as quantity_type
from .._proto.api.v0.luminarycloud.vis import vis_pb2
from abc import ABC, abstractmethod
from .display import Field, DisplayAttributes
from typing import List, Any, cast
from .primitives import Box, Plane, AABB
from .vis_util import generate_id
from .._helpers._code_representation import CodeRepr


class Filter(ABC, CodeRepr):
    """
    This is the base class for all filters. Each derived filter class
    is responsible for providing a _to_proto method to convert to a filter
    protobuf.

    Attributes
    ----------
    id: str
        A automatically generated uniqiue filter id.

    .. warning:: This feature is experimental and may change or be removed in the future.
    """

    def __init__(self, id: str) -> None:
        self.display_attrs = DisplayAttributes()
        self.id = id
        self._parent_id: str = ""

    @abstractmethod
    def _to_proto(self) -> vis_pb2.Filter:
        pass

    @abstractmethod
    def _from_proto(self, filter: vis_pb2.Filter) -> None:
        pass

    def set_parent(self, filter: Any) -> None:
        """
        Set this filter's parent filter. This controls what data the filter uses
        as input.  Filters can be chained into a DAG. If no parent is set, then
        this filter uses the original dataset.

        Parameters
        ----------
        filter: Filter
            The filter to use as the parent.
        """
        if not isinstance(filter, Filter):
            raise TypeError(f"Expected 'Filter', got {type(filter).__name__}")
        f = cast(Filter, filter)
        self._parent_id = f.id

    def reset_parent(self) -> None:
        """
        Reset the parent of this filter to the original dataset.
        """
        self._parent_id = ""

    def get_parent_id(self) -> str:
        """
        Returns the filter's parent id. An empty string will be returned if
        there is no parent.
        """
        return self._parent_id


class Slice(Filter):
    """
    The slice filter is used to extract a cross-section of a 3D dataset by
    slicing it with a plane.

    .. warning:: This feature is experimental and may change or be removed in the future.

    Attributes:
    -----------
    plane : Plane
        The slice plane.
    name : str
        A user provided name for the filter.
    project_vectors: bool
        When true, vector fields will be projected onto the plane of the slice. This is often
        useful for visualizing vector fields by removing the vector components in the normal
        direction of the plane. Default: False
    display_attrs : DisplayAttributes
        Specifies this filter's appearance.
    """

    def __init__(self, name: str = "") -> None:
        super().__init__(generate_id("slice-"))
        self._plane = Plane()
        self._project_vectors: bool = False
        self.name = name

    @property
    def plane(self) -> Plane:
        return self._plane

    @plane.setter
    def plane(self, new_plane: Plane) -> None:
        if not isinstance(new_plane, Plane):
            raise TypeError(f"Expected 'Plane', got {type(new_plane).__name__}")
        self._plane = new_plane

    @property
    def project_vectors(self) -> bool:
        return self._project_vectors

    @project_vectors.setter
    def project_vectors(self, new_project_vectors: bool) -> None:
        if not isinstance(new_project_vectors, bool):
            raise TypeError(f"Expected 'bool', got {type(new_project_vectors).__name__}")
        self._project_vectors = new_project_vectors

    def _to_proto(self) -> vis_pb2.Filter:
        vis_filter = vis_pb2.Filter()
        vis_filter.id = self.id
        vis_filter.name = self.name
        vis_filter.slice.plane.CopyFrom(self.plane._to_proto())
        vis_filter.slice.project_vectors = self.project_vectors
        return vis_filter

    def _from_proto(self, filter: vis_pb2.Filter) -> None:
        typ = filter.WhichOneof("value")
        if typ != "slice":
            raise TypeError(f"Expected 'slice', got {typ}")
        self.id = filter.id
        self.name = filter.name
        self.project_vectors = filter.slice.project_vectors
        self.plane = Plane()
        self.plane._from_proto(filter.slice.plane)


class Isosurface(Filter):
    """
    Isosurface is used to evaluate scalar fields at constant values, known as
    isovalues. In volumes, isosurface produces surfaces, and in surfaces,
    isosurface produces lines (isolines). Isosurface is also known as contouring
    and as level-sets.

    .. warning:: This feature is experimental and may change or be removed in the future.

    Attributes:
    -----------
    field: Field
        The scalar field to evaluate.
    isovalues: List[float]
        A list of isovalues to evaluate.
    name : str
        A user provided name for the filter.
    display_attrs : DisplayAttributes
        Specifies this filter's appearance.
    """

    def __init__(self, name: str = "") -> None:
        super().__init__(generate_id("contour-"))
        self.isovalues: List[float] = []
        self.field: Field = Field()
        self.name = name

    def _to_proto(self) -> vis_pb2.Filter:
        if not isinstance(self.isovalues, List):
            raise TypeError(f"Expected 'List', got {type(self.isovalues).__name__}")

        if not all(isinstance(x, (int, float)) for x in self.isovalues):
            raise TypeError("Isosurface: all isovalues must be numbers")
        if len(self.isovalues) == 0:
            raise ValueError("Isosurface: isovalue must be non-empty")

        if self.field.quantity == VisQuantity.NONE:
            raise ValueError("Isosurface: field can't be None")

        vis_filter = vis_pb2.Filter()
        vis_filter.id = self.id
        vis_filter.name = self.name
        vis_filter.contour.field.quantity_typ = self.field.quantity.value
        if not quantity_type._is_vector(self.field.quantity):
            vis_filter.contour.field.component = vis_pb2.Field.COMPONENT_UNSPECIFIED
        else:
            vis_filter.contour.field.component = self.field.component.value
        for val in self.isovalues:
            vis_filter.contour.iso_values.append(val)
        return vis_filter

    def _from_proto(self, filter: vis_pb2.Filter) -> None:
        typ = filter.WhichOneof("value")
        if typ != "contour":
            raise TypeError(f"Expected 'contour', got {typ}")
        self.id = filter.id
        self.name = filter.name
        self.field.quantity = VisQuantity(filter.contour.field.quantity_typ)
        if not quantity_type._is_vector(self.field.quantity):
            # This is a scalar so just set the component to magnitude which is the default.
            self.field.component = FieldComponent.MAGNITUDE
        else:
            self.field.component = FieldComponent(filter.contour.field.component)
        self.isovalues.clear()
        for val in filter.contour.iso_values:
            self.isovalues.append(val)


class PlaneClip(Filter):
    """
    Clip the dataset using a plane. Cells in the direction of the plane normal
    are kept, while the cells in the opposite direction are removed.

    .. warning:: This feature is experimental and may change or be removed in the future.

    Attributes:
    -----------
    plane : Plane
        The plane that defines the clip.
    name : str
        A user provided name for the filter.
    display_attrs (DisplayAttributes)
        Specifies this filters appearance.
    inverted : bool
        Inverts the direction of the clip. If true, cells in the direction of the normal
        are removed. Default: False
    """

    def __init__(self, name: str = "") -> None:
        super().__init__(generate_id("planeClip-"))
        self._plane: Plane = Plane()
        self.name = name
        self.inverted: bool = False

    @property
    def plane(self) -> Plane:
        return self._plane

    @plane.setter
    def plane(self, new_plane: Plane) -> None:
        if not isinstance(new_plane, Plane):
            raise TypeError(f"Expected 'Plane', got {type(new_plane).__name__}")
        self._plane = new_plane

    def _to_proto(self) -> vis_pb2.Filter:
        vis_filter = vis_pb2.Filter()
        vis_filter.id = self.id
        vis_filter.name = self.name
        vis_filter.clip.plane.CopyFrom(self.plane._to_proto())
        vis_filter.clip.inverted = self.inverted
        return vis_filter

    def _from_proto(self, filter: vis_pb2.Filter) -> None:
        typ = filter.WhichOneof("value")
        if typ != "clip":
            raise TypeError(f"Expected 'clip', got {typ}")
        clip_typ = filter.clip.WhichOneof("clip_function")
        if clip_typ != "plane":
            raise TypeError(f"Expected 'plane clip', got {clip_typ}")
        self.id = filter.id
        self.name = filter.name
        self.plane = Plane()
        self.plane._from_proto(filter.clip.plane)
        self.inverted = filter.clip.inverted


class BoxClip(Filter):
    """
    Clip the dataset using a box. Cells inside the box are kept while cells completely outside the
    box are removed.

    .. warning:: This feature is experimental and may change or be removed in the future.

    Attributes:
    -----------
    name : str
        A user provided name for the filter.
    box : Box
        The box definition to clip by.
    display_attrs (DisplayAttributes)
        Specifies this filters appearance.
    inverted: bool
        Inverts the direction of the clip. If true, cells completely inside the box are removed.
        Default : False
    """

    def __init__(self, name: str = "") -> None:
        super().__init__(generate_id("boxClip-"))
        self._box: Box = Box()
        self.name = name
        self.inverted: bool = True

    @property
    def box(self) -> Box:
        return self._box

    @box.setter
    def box(self, new_box: Box) -> None:
        if not isinstance(new_box, Box):
            raise TypeError(f"Expected 'Box', got {type(new_box).__name__}")
        self._box = new_box

    def _to_proto(self) -> vis_pb2.Filter:
        vis_filter = vis_pb2.Filter()
        vis_filter.id = self.id
        vis_filter.name = self.name
        vis_filter.clip.box.CopyFrom(self.box._to_proto())
        vis_filter.clip.inverted = self.inverted
        return vis_filter

    def _from_proto(self, filter: vis_pb2.Filter) -> None:
        typ = filter.WhichOneof("value")
        if typ != "clip":
            raise TypeError(f"Expected 'clip', got {typ}")
        clip_typ = filter.clip.WhichOneof("clip_function")
        if clip_typ != "box":
            raise TypeError(f"Expected 'box', got {clip_typ}")
        self.id = filter.id
        self.name = filter.name
        self.box = Box()
        self.box._from_proto(filter.clip.box)
        self.inverted = filter.clip.inverted


class VectorGlyphs(Filter):
    """
    VectorGlyphs is the base class for the two vector glyph types.
    The full doc strings are located in the derived classes.

    .. warning:: This feature is experimental and may change or be removed in the future.

    """

    def __init__(self, name: str = "") -> None:
        super().__init__(generate_id("vector-"))
        self.name: str = name
        self._sampling_rate: int = 500
        self.quantity: VisQuantity = VisQuantity.VELOCITY

    @property
    def sampling_rate(self) -> int:
        return self._sampling_rate

    @sampling_rate.setter
    def sampling_rate(self, rate: int) -> None:
        if not isinstance(rate, int) and not isinstance(rate, float):
            raise TypeError(f"Sampling rate must be a number, got {type(rate).__name__}")
        if rate < 1:
            raise ValueError("Sampling rate must be a integer > 0")
        self._sampling_rate = rate


class FixedSizeVectorGlyphs(VectorGlyphs):
    """
    Vector Glyphs is a vector field visualization techique that places arrows (e.g., glyphs),
    in the 3D scene that are oriented in the direction of the underlying vector field.
    Fixed size vector glyhs places vector annotations at sampled points in
    meshes that are a fixed size. This filter is only valid on vector fields.
    .. warning:: This feature is experimental and may change or be removed in the future.

    Attributes:
    -----------
    name : str
        A user provided name for the filter.
    sampling_rate : int
        Specifies how many vector glyphs to place. A sampling rate of 1 means that a glyph
        will be placed at every point in the input mesh. A sampling rate of 10 means that glyphs
        are paced at every 10th point. The value must be a integer greater than 1. Default: 500.
    size : float
        The size in world units (meters) of the glyphs.
    display_attrs (DisplayAttributes)
        Specifies this filters appearance.
    quantity: VisQuantity
        The vector field to use for glyph generation. Default: Velocity
    """

    def __init__(self, name: str = "") -> None:
        super().__init__(name)
        self.size: float = 1.0

    def _to_proto(self) -> vis_pb2.Filter:
        vis_filter = vis_pb2.Filter()
        vis_filter.id = self.id
        vis_filter.name = self.name
        vis_filter.glyph.fixed_size_glyphs = self.size
        vis_filter.glyph.n_glyphs = self.sampling_rate
        vis_filter.glyph.sampling_mode = vis_pb2.GLYPH_SAMPLING_MODE_EVERY_NTH
        if not quantity_type._is_vector(self.quantity):
            raise ValueError("FixedSizeVectorGlyphs: field must be a vector type")
        vis_filter.glyph.field.quantity_typ = self.quantity.value
        vis_filter.glyph.field.component = vis_pb2.Field.COMPONENT_UNSPECIFIED
        return vis_filter

    def _from_proto(self, filter: vis_pb2.Filter) -> None:
        typ = filter.WhichOneof("value")
        if typ != "glyph":
            raise TypeError(f"Expected 'glyph', got {typ}")
        glyph_typ = filter.glyph.WhichOneof("glyph_size")
        if glyph_typ != "fixed_size_glyphs":
            raise TypeError(f"Expected 'fixed size', got {typ}")
        self.id = filter.id
        self.name = filter.name
        self.n_glyphs = filter.glyph.n_glyphs
        self.size = filter.glyph.fixed_size_glyphs
        self.sampling_rate = filter.glyph.n_glyphs
        self.quantity = VisQuantity(filter.glyph.field.quantity_typ)


class ScaledVectorGlyphs(VectorGlyphs):
    """
    Vector Glyphs is a vector field visualization techique that places arrows
    (e.g., glyphs), in the 3D scene that are oriented in the direction of the
    underlying vector field.  Scaled vector glyphs changes the size of the
    arrows base on the magnitude of the vector. For example when visualizing the
    velocity field, a glyph where the magnitude is twice the magnitude of
    another glyph will appear twice as large.
    .. warning:: This feature is experimental and may change or be removed in the future.

    Attributes:
    -----------
    name : str
        A user provided name for the filter.
    sampling_rate : int
        Specifies how many vector glyphs to place. A sampling rate of 1 means that a glyph
        will be placed at every point in the input mesh. A sampling rate of 10 means that glyphs
        are paced at every 10th point. The value must be a integer greater than 1. Default: 500.
    scale: float
        The scale applied to the vector glyph. The actual vector glpyh size is the magnitude of the
        vector at the sampled point multiplied by the scale. For example, if the vector magnitude is
        0.5 and the scale is 2 then the resulting world space size is 1 meter. Default: 1.
    display_attrs (DisplayAttributes)
        Specifies this filters appearance.
    quantity: VisQuantity
        The vector field to use for glyph generation. Default: Velocity
    """

    def __init__(self, name: str = "") -> None:
        super().__init__(name)
        self.scale: float = 1.0

    def _to_proto(self) -> vis_pb2.Filter:
        vis_filter = vis_pb2.Filter()
        vis_filter.id = self.id
        vis_filter.name = self.name
        vis_filter.glyph.glyph_scale_size = self.scale
        vis_filter.glyph.n_glyphs = self.sampling_rate
        vis_filter.glyph.sampling_mode = vis_pb2.GLYPH_SAMPLING_MODE_EVERY_NTH
        if not quantity_type._is_vector(self.quantity):
            raise ValueError("ScaledVectorGyph: field must be a vector type")
        vis_filter.glyph.field.quantity_typ = self.quantity.value
        vis_filter.glyph.field.component = vis_pb2.Field.COMPONENT_UNSPECIFIED
        return vis_filter

    def _from_proto(self, filter: vis_pb2.Filter) -> None:
        typ = filter.WhichOneof("value")
        if typ != "glyph":
            raise TypeError(f"Expected 'glyph', got {typ}")
        glyph_typ = filter.glyph.WhichOneof("glyph_size")
        if glyph_typ != "glyph_scale_size":
            raise TypeError(f"Expected 'scaled size', got {typ}")
        self.id = filter.id
        self.name = filter.name
        self.n_glyphs = filter.glyph.n_glyphs
        self.scale = filter.glyph.glyph_scale_size
        self.sampling_rate = filter.glyph.n_glyphs
        self.quantity = VisQuantity(filter.glyph.field.quantity_typ)


class Threshold(Filter):
    """
    The threshold filter used to remove cells based on a data range. Cells with values
    within the range (i.e., min_value and max_value), are kept. All other cells are removed.

    .. warning:: This feature is experimental and may change or be removed in the future.

    Attributes:
    -----------
    name: str
        A user defined name for this filter.
    field: Field
        The field to used for the threshold. Default: Abosulute Pressure
    min_value:
        The minimum value in the range to keep. Default: 0.0
    max_value:
        The minimum value in the range to keep. Default: 1.0
    smooth: bool
        Boolean flag to control if the entire cell is passed through (False) or
        if the cell is clipped to the value range (True), also known as an
        iso-volume. Default: False
    invert: bool
        Invert the cells kept so that values inside the range are removed.
        Default: False
    strict: bool
        Only keep cells if all point values fall within the range. This option
        is only applicable if smooth is False. When False, if any point is
        within the range the cell is kept. Default: False
    display_attrs : DisplayAttributes
        Specifies this filter's appearance.
    """

    def __init__(self, name: str = "") -> None:
        super().__init__(generate_id("threshold-"))
        self.field: Field = Field()
        self.min_value: float = 0.0
        self.max_value: float = 1.0
        self.smooth: bool = False
        self.strict: bool = False
        self.invert: bool = False
        self.name: str = name

    def _to_proto(self) -> vis_pb2.Filter:
        # type checking
        if not isinstance(self.field, Field):
            raise TypeError(f"Expected 'Field', got {type(self.field).__name__}")
        if not isinstance(self.min_value, (float, int)):
            raise TypeError(f"Expected 'float or int', got {type(self.min_value).__name__}")
        if not isinstance(self.max_value, (float, int)):
            raise TypeError(f"Expected 'float or int', got {type(self.max_value).__name__}")
        if not isinstance(self.smooth, bool):
            raise TypeError(f"Expected 'bool', got {type(self.smooth).__name__}")
        if not isinstance(self.strict, bool):
            raise TypeError(f"Expected 'bool', got {type(self.strict).__name__}")
        if not isinstance(self.invert, bool):
            raise TypeError(f"Expected 'bool', got {type(self.invert).__name__}")
        if self.min_value > self.max_value:
            # Alternatively, we could just swap them for the user.
            raise ValueError(f"Threhold: max value must be greater than the min")
        vis_filter = vis_pb2.Filter()
        vis_filter.id = self.id
        vis_filter.name = self.name
        vis_filter.threshold.range.min = self.min_value
        vis_filter.threshold.range.max = self.max_value
        vis_filter.threshold.field.quantity_typ = self.field.quantity.value
        if not quantity_type._is_vector(self.field.quantity):
            vis_filter.threshold.field.component = vis_pb2.Field.COMPONENT_UNSPECIFIED
        else:
            vis_filter.threshold.field.component = self.field.component.value
        vis_filter.threshold.field.component = self.field.component.value
        vis_filter.threshold.smooth = self.smooth
        vis_filter.threshold.invert = self.invert
        vis_filter.threshold.strict = self.strict
        return vis_filter

    def _from_proto(self, filter: vis_pb2.Filter) -> None:
        typ = filter.WhichOneof("value")
        if typ != "threshold":
            raise TypeError(f"Expected 'threshold', got {typ}")
        self.id = filter.id
        self.name = filter.name
        self.min_value = filter.threshold.range.min
        self.max_value = filter.threshold.range.max
        self.smooth = filter.threshold.smooth
        self.invert = filter.threshold.invert
        self.strict = filter.threshold.strict
        self.field.quantity = VisQuantity(filter.threshold.field.quantity_typ)
        if not quantity_type._is_vector(self.field.quantity):
            # This is a scalar so just set the component to magnitude which is the default.
            self.field.component = FieldComponent.MAGNITUDE
        else:
            self.field.component = FieldComponent(filter.threshold.field.component)


class Streamlines(Filter):
    """
    Streanlines is the base class for all the streamlines filters. Full doc strings
    found in derived classes.

    .. warning:: This feature is experimental and may change or be removed in the future.

    Attributes:
    -----------
    name : str
        A user provided name for the filter.
    display_attrs : DisplayAttributes
        Specifies this filter's appearance.
    """

    def __init__(self, name: str = "") -> None:
        super().__init__(generate_id("streamlines-"))
        self.name: str = name
        self.n_streamlines: int = 100
        self.max_length: float = 10
        self.direction: StreamlineDirection = StreamlineDirection.FORWARD
        self.quantity: VisQuantity = VisQuantity.VELOCITY


class RakeStreamlines(Streamlines):
    """
    Streamlines is a vector field visualization technique that integrates
    massless particles through a vector field forming curves. Streamlines are
    used to visualize and analyze fluid flow patterns (e.g., the velocity
    field), helping to understand how the fluid moves. Streamlines
    can be use used to visualize any vector field contained in the solution.

    RakeStreamlines generates seed particles evenly spaced along a line defined
    by specified start and end points. RakeStreamlines only work with volume
    data.

    .. warning:: This feature is experimental and may change or be removed in the future.

    Attributes:
    -----------
    n_streamlines : int
        The number of seed particles to place on the rake. Default: 100
    max_length: float
        The maximum path length of the particle in meters. Default: 10
    quantity: VisQuantity
        The vector field to use for the particle advection. Default: Velocity
    start: Vector3Like
        The start point of the rake. Default: [0,0,0].
    end: Vector3Like
        The end point point of the rake. Default: [1,0,0].
    name : str
        A user provided name for the filter.
    display_attrs : DisplayAttributes
        Specifies this filter's appearance.
    """

    def __init__(self, name: str = "") -> None:
        super().__init__(name)
        self.start: Vector3Like = Vector3(x=0, y=0, z=0)
        self.end: Vector3Like = Vector3(x=1, y=0, z=0)

    def _to_proto(self) -> vis_pb2.Filter:
        # Type checking
        if not isinstance(self.n_streamlines, int):
            raise TypeError(f"Expected 'int', got {type(self.n_streamlines).__name__}")
        if not isinstance(self.max_length, (float, int)):
            raise TypeError(f"Expected 'float or int', got {type(self.max_length).__name__}")
        if not isinstance(self.quantity, VisQuantity):
            raise TypeError(f"Expected 'VisQuantity', got {type(self.quantity).__name__}")

        vis_filter = vis_pb2.Filter()
        vis_filter.id = self.id
        vis_filter.name = self.name
        vis_filter.streamlines.n_streamlines = self.n_streamlines
        vis_filter.streamlines.max_length = self.max_length
        vis_filter.streamlines.rake.start.CopyFrom(_to_vector3(self.start)._to_proto())
        vis_filter.streamlines.rake.end.CopyFrom(_to_vector3(self.end)._to_proto())
        if not quantity_type._is_vector(self.quantity):
            raise ValueError("RakeStreamlines: field must be a vector type")
        vis_filter.streamlines.field.quantity_typ = self.quantity.value
        return vis_filter

    def _from_proto(self, filter: vis_pb2.Filter) -> None:
        typ = filter.WhichOneof("value")
        if typ != "streamlines":
            raise TypeError(f"Expected 'streamlines', got {typ}")
        s_typ = filter.streamlines.WhichOneof("seed_type")
        if s_typ != "rake":
            raise TypeError(f"Expected 'rake streamlines', got {s_typ}")
        self.id = filter.id
        self.name = filter.name
        self.n_streamlines = filter.streamlines.n_streamlines
        self.max_length = filter.streamlines.max_length

        self.start = Vector3()
        self.start._from_proto(filter.streamlines.rake.start)
        self.end = Vector3()
        self.end._from_proto(filter.streamlines.rake.end)
        self.quantity = VisQuantity(filter.streamlines.field.quantity_typ)


class GridStreamlines(Streamlines):
    """
    Streamlines is a vector field visualization technique that integrates
    massless particles through a vector field forming curves. Streamlines are
    used to visualize and analyze fluid flow patterns (e.g., the velocity
    field), helping to understand how the fluid moves. Streamlines
    can be use used to visualize any vector field contained in the solution.

    GridStreamlines generates seed particles arranged in a 2D grid pattern
    inside the volume. GridStreamlines only work with volume data.

    The grid is defined by a center point and two vectors that define the u
    (rake_direction) and v (seed_direction) directions of the grid. It's
    recommended that the rake_direction and seed_direction vectors are
    orthogonal to each other, but it's not required. Rakes (sets of seed
    particles) are generated in the rake_direction. Seed particles are
    distributed along the seed_direction. The rake spacing controls the distance
    between the rakes, and the seed spacing controls the distance between the
    seed particles along the rake.

    For example, if the rake vector is [1,0,0] and the seed vector is [0,1,0],
    then the rakes will be generated in the x direction and the seed particles
    will be generated in the y direction. Lets say we want to create a grid of
    of 4x4 particles that is 8 meters wide and 2 meters tall. The rake spacing
    would be 2 meters / 4 = 0.5 meters, and the seed spacing would be 8 meters /
    4 = 2 meters.

    .. warning:: This feature is experimental and may change or be removed in the future.

    Attributes:
    -----------
    max_length: float
        The maximum path length of the particle in meters. Default: 10
    quantity: VisQuantity
        The vector field to use for the particle advection. Default: Velocity
    rake_direction: Vector3Like
        The vector defining the u direction of the grid along which the rakes are placed.
        Default: [1,0,0].
    seed_direction: Vector3Like
        The vector defining the v direction of the grid along which the seed particles are placed.
        Default: [0,1,0].
    center: Vector3Like
        The center point of the grid. Default: [0,0,0].
    rake_res: int
        The number of rake lines to generate in the u direction. Default: 2.
    seed_res: int
        The number of seed particles to generate in the v direction. Default: 10.
    rake_spacing: float
        The spacing between the rake lines in meters. Default: 0.5.
    seed_spacing: float
        The spacing between the seed particles in meters. Default: 0.1.
    name : str
        A user provided name for the filter.
    display_attrs : DisplayAttributes
        Specifies this filter's appearance.
    """

    def __init__(self, name: str = "") -> None:
        super().__init__(name)
        self.rake_direction: Vector3Like = Vector3(x=1, y=0, z=0)
        self.seed_direction: Vector3Like = Vector3(x=0, y=1, z=0)
        self.center: Vector3Like = Vector3(x=0, y=0, z=0)
        self.rake_res: int = 2
        self.seed_res: int = 10
        self.rake_spacing: float = 0.5
        self.seed_spacing: float = 0.1

    def _to_proto(self) -> vis_pb2.Filter:
        # Type checking
        if not isinstance(self.max_length, (float, int)):
            raise TypeError(f"Expected 'float or int', got {type(self.max_length).__name__}")
        if not isinstance(self.quantity, VisQuantity):
            raise TypeError(f"Expected 'VisQuantity', got {type(self.quantity).__name__}")
        if not isinstance(self.rake_res, int):
            raise TypeError(f"Expected 'int', got {type(self.rake_res).__name__}")
        if not isinstance(self.seed_res, int):
            raise TypeError(f"Expected 'int', got {type(self.seed_res).__name__}")
        if not isinstance(self.rake_spacing, (float, int)):
            raise TypeError(f"Expected 'float or int', got {type(self.rake_spacing).__name__}")
        if not isinstance(self.seed_spacing, (float, int)):
            raise TypeError(f"Expected 'float or int', got {type(self.seed_spacing).__name__}")

        vis_filter = vis_pb2.Filter()
        vis_filter.id = self.id
        vis_filter.name = self.name
        vis_filter.streamlines.max_length = self.max_length
        vis_filter.streamlines.grid.center.CopyFrom(_to_vector3(self.center)._to_proto())
        vis_filter.streamlines.grid.u_vec.CopyFrom(_to_vector3(self.rake_direction)._to_proto())
        vis_filter.streamlines.grid.v_vec.CopyFrom(_to_vector3(self.seed_direction)._to_proto())
        vis_filter.streamlines.grid.rake_res = self.rake_res
        vis_filter.streamlines.grid.seed_res = self.seed_res
        vis_filter.streamlines.grid.rake_spacing = self.rake_spacing
        vis_filter.streamlines.grid.seed_spacing = self.seed_spacing

        if not quantity_type._is_vector(self.quantity):
            raise ValueError("GridStreamlines: field must be a vector type")
        vis_filter.streamlines.field.quantity_typ = self.quantity.value
        return vis_filter

    def _from_proto(self, filter: vis_pb2.Filter) -> None:
        typ = filter.WhichOneof("value")
        if typ != "streamlines":
            raise TypeError(f"Expected 'streamlines', got {typ}")
        s_typ = filter.streamlines.WhichOneof("seed_type")
        if s_typ != "grid":
            raise TypeError(f"Expected 'grid streamlines', got {s_typ}")
        self.id = filter.id
        self.name = filter.name
        self.n_streamlines = filter.streamlines.n_streamlines
        self.max_length = filter.streamlines.max_length

        self.center = Vector3()
        self.center._from_proto(filter.streamlines.grid.center)
        self.rake_direction = Vector3()
        self.rake_direction._from_proto(filter.streamlines.grid.u_vec)
        self.seed_direction = Vector3()
        self.seed_direction._from_proto(filter.streamlines.grid.v_vec)
        self.rake_res = filter.streamlines.grid.rake_res
        self.seed_res = filter.streamlines.grid.seed_res
        self.rake_spacing = filter.streamlines.grid.rake_spacing
        self.seed_spacing = filter.streamlines.grid.seed_spacing
        self.quantity = VisQuantity(filter.streamlines.field.quantity_typ)


class SurfaceStreamlines(Streamlines):
    """
    Streamlines is a vector field visualization technique that integrates
    massless particles through a vector field forming curves. Streamlines are
    used to visualize and analyze fluid flow patterns (e.g., the velocity
    field), helping to understand how the fluid moves. Streamlines
    can be use used to visualize any vector field contained in the solution.


    Surface streamlines has two different modes:
        - ADVECT_ON_SURFACE: constrain particles to the surfaces of the mesh.
        - ADVECT_IN_VOLUME: use surface points to seed volumetric streamlines.

    The advection mode also effects what fields can be used. For example, velocity is zero
    on walls, so when useing ADVECT_ON_SURFACE use a field that has non-zero
    values such as wall shear stress.

    Example use cases for ADVECT_IN_VOLUME:
        - placing seeds on an inlet surface and integrating in the forwared direction.
        - placing seeds on an outlet surface and integrating in the backward direction.
        - placing seeds on the tires of a car or on the wing of an airplane.

    Example use cases for ADVECT_ON_SURFACE:
        - Understanding forces on walls such as wall shear stress.

    .. warning:: This feature is experimental and may change or be removed in the future.

    Attributes:
    -----------
    mode: SurfaceStreamlinesMode
        Specifies whether to advect particles on the surface or in the volume.
        Default: ADVECT_IN_VOLUME
    sampling_rate : int
        Specifies how frequently to place seeds on the surface points. A
        sampling rate of 1 means that a seed particle will be placed at every
        point on the surfaces. A sampling rate of 10 means that are paced at
        every 10th point. The value must be a integer greater than 1. Default:
        100.
    offset: float
        User provided offset. Particles placed directly on the surface have a
        chance of leaving the volume immediately. Set the offset to place seed
        particles further into the volume based on the surface normal.  Default: 0.0
    max_length: float
        The maximum path length of the particle in meters. Default: 10
    quantity: VisQuantity
        The vector field to use for the particle advection. Default: Velocity
    name : str
        A user provided name for the filter.
    display_attrs : DisplayAttributes
        Specifies this filter's appearance.
    """

    def __init__(self, name: str = "") -> None:
        super().__init__(name)
        self.offset: float = 0.0
        self._surface_names: List[str] = []
        self.sampling_rate = 100
        self.mode: SurfaceStreamlineMode = SurfaceStreamlineMode.ADVECT_IN_VOLUME

    def add_surface(self, id: str) -> None:
        """
        Add a surface to generate seed points from.

        Parameters
        ----------
        id: str
            A surface id or a tag id.
        """
        if not isinstance(id, str):
            raise TypeError(f"Expected 'str', got {type(id).__name__}")
        self._surface_names.append(id)

    def _surfaces(self) -> List[str]:
        """
        Returns the current list of surfaces.
        """
        return self._surface_names

    def _to_proto(self) -> vis_pb2.Filter:
        # Type checking
        if not isinstance(self.n_streamlines, int):
            raise TypeError(f"Expected 'int', got {type(self.n_streamlines).__name__}")
        if not isinstance(self.max_length, (float, int)):
            raise TypeError(f"Expected 'float or int', got {type(self.max_length).__name__}")
        if not isinstance(self.offset, (float, int)):
            raise TypeError(f"Expected 'float or int', got {type(self.offset).__name__}")
        if not isinstance(self.quantity, VisQuantity):
            raise TypeError(f"Expected 'VisQuantity', got {type(self.quantity).__name__}")
        if not isinstance(self.mode, SurfaceStreamlineMode):
            raise TypeError(f"Expected 'SurfaceStreamlinesMode', got {type(self.mode).__name__}")

        vis_filter = vis_pb2.Filter()
        vis_filter.id = self.id
        vis_filter.name = self.name
        vis_filter.streamlines.max_length = self.max_length
        vis_filter.streamlines.surface.offset = self.offset
        project = False
        # Prevent common mistakes that cause confusion.
        if self.mode == SurfaceStreamlineMode.ADVECT_ON_SURFACE:
            if self.quantity == VisQuantity.VELOCITY:
                raise ValueError(
                    "SurfacesStreamines: velocity is 0 on surfaces and will produce no data"
                )
            project = True
        elif self.quantity == VisQuantity.WALL_SHEAR_STRESS:
            raise ValueError(
                "SurfacesStreamines: wall shear stress is 0 in the volume and will produce no data "
            )

        vis_filter.streamlines.surface.project_on_surface = project
        if len(self._surface_names) == 0:
            raise ValueError("SurfaceStreamlines: need at least one surfaces specified.")
        for id in self._surface_names:
            vis_filter.streamlines.surface.surface_names.append(id)
        if not quantity_type._is_vector(self.quantity):
            raise ValueError("SurfaceStreamlines: quantity must be a vector type")
        vis_filter.streamlines.field.quantity_typ = self.quantity.value
        return vis_filter

    def _from_proto(self, filter: vis_pb2.Filter) -> None:
        typ = filter.WhichOneof("value")
        if typ != "streamlines":
            raise TypeError(f"Expected 'streamlines', got {typ}")
        s_typ = filter.streamlines.WhichOneof("seed_type")
        if s_typ != "surface":
            raise TypeError(f"Expected 'surface streamlines', got {s_typ}")
        self.id = filter.id
        self.name = filter.name
        self.max_length = filter.streamlines.max_length
        self.offset = filter.streamlines.surface.offset
        self._surface_names.clear()
        for s in filter.streamlines.surface.surface_names:
            self._surface_names.append(s)
        self.quantity = VisQuantity(filter.streamlines.field.quantity_typ)

    def _to_code(self, hide_defaults: bool = True, use_tmp_objs: bool = True) -> str:
        code = super()._to_code(hide_defaults=hide_defaults)
        # We need to explicity write the code for the surfaces since its
        # technically a private variable.
        for s in self._surface_names:
            code += f".add_surface('{s}')\n"
        return code


class SurfaceLIC(Filter):
    """
    A Surface Line Integral Convolution (LIC) filter is used to depict the flow
    direction and structure of vector fields (such as velocity) on surfaces. It
    enhances the perception of complex flow patterns by convolving noise
    textures along streamlines, making it easier to visually interpret the
    behavior of fluid flow on boundaries or surfaces in a simulation.

    The input is a list of surfaces. If none are specified, all are used. The
    surface LIC outputs grey scale colors on the specified surfaces. When the
    display attributes quantity is not None, the field colors are blended with
    the grey scale colors.

    Note: surface LIC computes on the same surfaces of the solution. If the surfaces in
    the global display attributes are not hidden, the surface LIC will not be visible since
    the existing surfaces are occluding it.

    .. warning:: This feature is experimental and may change or be removed in the future.

    Attributes:
    -----------
    quantity: VisQuantity
        Specifies the field used to advect particles for the surface LIC.
        Default: WALL_SHEER_STRESS
    contrast: float
        Contrast controls the contrast of the resuting surface LIC. Valid values
        are in the [0.2, 3.0] range. Lower values means less contrast and
        higher values mean more contrast. Default: 1
    """

    def __init__(self, name: str = "") -> None:
        super().__init__(generate_id("surface-lic-"))
        self.name = name
        self.contrast: float = 1.0
        self._surface_names: List[str] = []
        self.quantity: VisQuantity = VisQuantity.WALL_SHEAR_STRESS

    def add_surface(self, id: str) -> None:
        """
        Add a surface to compute the surface LIC on. Adding no
        surfaces indicates that all surfaces will be used.

        Parameters
        ----------
        id: str
            A surface id or a tag id.
        """
        if not isinstance(id, str):
            raise TypeError(f"Expected 'str', got {type(id).__name__}")
        self._surface_names.append(id)

    def _surfaces(self) -> List[str]:
        """
        Returns the current list of surfaces.
        """
        return self._surface_names

    def _to_proto(self) -> vis_pb2.Filter:
        vis_filter = vis_pb2.Filter()
        vis_filter.id = self.id
        vis_filter.name = self.name
        # Prevent common mistakes that cause confusion. The only current option
        # is to be on a surface, so no velocity.
        if not isinstance(self.quantity, VisQuantity):
            raise TypeError(f"Expected 'VisQuantity', got {type(self.quantity).__name__}")
        if self.quantity == VisQuantity.VELOCITY:
            raise ValueError("SurfaceLIC: velocity is 0 on surfaces and will produce no data")
        if not isinstance(self.contrast, (int, float)):
            raise TypeError(f"Expected 'int or float', got {type(self.contrast).__name__}")
        if self.contrast < 0.2 or self.contrast > 3.0:
            raise ValueError("SurfaceLIC: contrast must be between 0.2 and 3.0")

        for id in self._surface_names:
            vis_filter.surface_lic.geometry.surface_names.append(id)
        if len(self._surface_names) == 0:
            # we need to make sure that the geometry is populated.
            geometry = vis_pb2.SurfaceLICGeomtery()
            vis_filter.surface_lic.geometry.CopyFrom(geometry)

        vis_filter.surface_lic.field.quantity_typ = self.quantity.value
        vis_filter.surface_lic.contrast = self.contrast
        return vis_filter

    def _from_proto(self, filter: vis_pb2.Filter) -> None:
        typ = filter.WhichOneof("value")
        if typ != "surface_lic":
            raise TypeError(f"Expected 'surface lic', got {typ}")
        l_typ = filter.surface_lic.WhichOneof("lic_type")
        if l_typ != "geometry":
            # there is only one type of surface lic currently.
            raise TypeError(f"Expected geometry', got {l_typ}")
        self.id = filter.id
        self.name = filter.name
        self.contrast = filter.surface_lic.contrast
        self._surface_names = []
        for s in filter.surface_lic.geometry.surface_names:
            self._surface_names.append(s)
        if not quantity_type._is_vector(self.quantity):
            raise ValueError("SurfaceLIC: quantity must be a vector type")
        self.quantity = VisQuantity(filter.surface_lic.field.quantity_typ)

    def _to_code(self, hide_defaults: bool = True, use_tmp_objs: bool = True) -> str:
        code = super()._to_code(hide_defaults=hide_defaults)
        # We need to explicity write the code for the surfaces since its
        # technically a private variable.
        for s in self._surface_names:
            code += f".add_surface('{s}')\n"
        return code


class SurfaceLICPlane(Filter):
    """
    A Surface Line Integral Convolution (LIC) filter is used to depict the flow
    direction and structure of vector fields (such as velocity) on surfaces. It
    enhances the perception of complex flow patterns by convolving noise
    textures along streamlines, making it easier to visually interpret the
    behavior of fluid flow on boundaries or surfaces in a simulation.

    This filter extracts a plane clipped by an axis-aligned bounding box (AABB) from
    the volume solution and computes the surface LIC on the plane.
    The surface LIC outputs the values as grayscale colors on the specified
    plane. When the display attributes quantity is not None, the field colors
    are blended with the grayscale colors.

    .. warning:: This feature is experimental and may change or be removed in the future.

    Attributes:
    -----------
    quantity: VisQuantity
        Specifies the field used to advect particles for the surface LIC.
        Default: VELOCITY
    contrast: float
        Contrast controls the contrast of the resuting surface LIC. Valid values
        are in the [0.2, 3.0] range. Lower values means less contrast and
        higher values mean more contrast. Default: 1
    plane: Plane
        The plane to extract from the volume solution.
    clip_box: AABB
        The axis-aligned bounding box (AABB) to clip the plane with. This is
        useful to limit the area of the plane to a specific region of interest.
    """

    def __init__(self, name: str = "") -> None:
        super().__init__(generate_id("surface-lic-"))
        self.name = name
        self.contrast: float = 1.0
        self.quantity: VisQuantity = VisQuantity.VELOCITY
        self.plane: Plane = Plane()
        self.clip_box: AABB = AABB()

    def _to_proto(self) -> vis_pb2.Filter:
        vis_filter = vis_pb2.Filter()
        vis_filter.id = self.id
        vis_filter.name = self.name
        if not isinstance(self.quantity, VisQuantity):
            raise TypeError(f"Expected 'VisQuantity', got {type(self.quantity).__name__}")
        if self.quantity == VisQuantity.WALL_SHEAR_STRESS:
            raise ValueError(
                "SurfaceLICPlane: wall shear stress is 0 in the volume and will produce no data"
            )
        if not isinstance(self.contrast, (int, float)):
            raise TypeError(f"Expected 'int or float', got {type(self.contrast).__name__}")
        if self.contrast < 0.2 or self.contrast > 3.0:
            raise ValueError("SurfaceLICPlane: contrast must be between 0.2 and 3.0")
        if not isinstance(self.plane, Plane):
            raise TypeError(f"Expected 'Plane', got {type(self.plane).__name__}")
        if not isinstance(self.clip_box, AABB):
            raise TypeError(f"Expected 'AABB', got {type(self.clip_box).__name__}")

        vis_filter.surface_lic.plane.plane.CopyFrom(self.plane._to_proto())
        vis_filter.surface_lic.plane.clip_box.CopyFrom(self.clip_box._to_proto())
        vis_filter.surface_lic.field.quantity_typ = self.quantity.value
        vis_filter.surface_lic.contrast = self.contrast
        return vis_filter

    def _from_proto(self, filter: vis_pb2.Filter) -> None:
        typ = filter.WhichOneof("value")
        if typ != "surface_lic":
            raise TypeError(f"Expected 'surface lic', got {typ}")
        l_typ = filter.surface_lic.WhichOneof("lic_type")
        if l_typ != "plane":
            raise TypeError(f"Expected 'plane', got {l_typ}")
        self.id = filter.id
        self.name = filter.name
        self.contrast = filter.surface_lic.contrast
        self.plane._from_proto(filter.surface_lic.plane.plane)
        self.clip_box._from_proto(filter.surface_lic.plane.clip_box)
        if not quantity_type._is_vector(self.quantity):
            raise ValueError("SurfaceLICPlane: quantity must be a vector type")
        self.quantity = VisQuantity(filter.surface_lic.field.quantity_typ)


def _filter_to_obj_name(filter: Filter) -> str:
    """
    Helper function to convert a filter to a code object name used in code gen.
    """
    if not isinstance(filter, Filter):
        raise TypeError(f"Expected 'Filter', got {type(filter).__name__}")
    if isinstance(filter, Slice):
        return "slice"
    elif isinstance(filter, Isosurface):
        return "isosurface"
    elif isinstance(filter, PlaneClip):
        return "plane_clip"
    elif isinstance(filter, BoxClip):
        return "box_clip"
    elif isinstance(filter, FixedSizeVectorGlyphs):
        return "fixed_size_vector_glyphs"
    elif isinstance(filter, ScaledVectorGlyphs):
        return "scaled_vector_glyphs"
    elif isinstance(filter, Threshold):
        return "threshold"
    elif isinstance(filter, RakeStreamlines):
        return "rake_streamlines"
    elif isinstance(filter, GridStreamlines):
        return "grid_streamlines"
    elif isinstance(filter, SurfaceStreamlines):
        return "surface_streamlines"
    elif isinstance(filter, SurfaceLIC):
        return "surface_lic"
    elif isinstance(filter, SurfaceLICPlane):
        return "surface_lic_plane"
    else:
        raise TypeError(f"Unknown filter type: {type(filter).__name__}")
