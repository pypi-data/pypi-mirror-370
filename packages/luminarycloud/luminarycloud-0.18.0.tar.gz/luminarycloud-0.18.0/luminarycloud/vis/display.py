# Copyright 2023-2024 Luminary Cloud, Inc. All Rights Reserved.
import dataclasses as dc
from luminarycloud.enum import Representation, ColorMapPreset, FieldComponent, VisQuantity
from .._proto.api.v0.luminarycloud.vis import vis_pb2
from typing import Optional
import luminarycloud.enum.quantity_type as quantity_type
from .._helpers._code_representation import CodeRepr


@dc.dataclass
class Field(CodeRepr):
    """
    The field controls the field displayed on the object. If the field doesn't
    exist, we show a solid color.

    .. warning:: This feature is experimental and may change or be removed in the future.

    """

    quantity: VisQuantity = VisQuantity.NONE
    """The quantity to color by. Default: NONE."""
    component: FieldComponent = FieldComponent.MAGNITUDE
    """
    The component of the field to use, applicable to vector fields. If the field is a
    scalar, the component field is ignored. Default: MAGNITUDE.
    """

    def __hash__(self) -> int:
        return hash((self.quantity, self.component))

    def _to_proto(self) -> vis_pb2.Field:
        field = vis_pb2.Field()
        field.quantity_typ = self.quantity.value
        if quantity_type._is_vector(self.quantity):
            field.component = self.component.value
        else:
            field.component = vis_pb2.Field.COMPONENT_UNSPECIFIED
        return field

    def _from_proto(self, field: vis_pb2.Field) -> None:
        self.quantity = VisQuantity(field.quantity_typ)
        if quantity_type._is_vector(self.quantity):
            if field.component == vis_pb2.Field.COMPONENT_UNSPECIFIED:
                raise ValueError("vector field must specify a component.")
            else:
                self.component = FieldComponent(field.component)
        # If its a scalar, just ignore the component.

    def _to_code(self, hide_defaults: bool = True, use_tmp_objs: bool = True) -> str:
        # We have to handle this case specially because we need to omit the field
        # component if the quantity is a scalar. Otherwise, it could confuse the user.
        # Also we omit the instantiation line because all classes that use a Field already
        # instantiate a default one in their own constructor. (Hopefully that invariant continues to
        # hold)
        def enum_to_string(val: VisQuantity | FieldComponent) -> str:
            str_val = val.__repr__()
            return str_val.split(": ")[0][1:]

        code = ""
        code += f".quantity = {enum_to_string(self.quantity)}\n"
        if quantity_type._is_vector(self.quantity):
            code += f".component = {enum_to_string(self.component)}\n"
        return code


@dc.dataclass
class DisplayAttributes(CodeRepr):
    """
    Display attributes specify how objects such as meshes, geometries, and
    filters appear in the scene.

    .. warning:: This feature is experimental and may change or be removed in the future.

    """

    visible: bool = True
    """If the object is visible or not. Default: True"""
    # TODO(matt): opacity not hooked up yet.
    opacity: float = 1.0
    """
    How opaque the object is. This is a normalized number between
    0 (i.e., fully transparent) and 1 (i.e., fully opaque). Default: 1
    """
    field: Field = dc.field(default_factory=Field)
    """What field quantity/component to color by, if applicable."""
    representation: Representation = Representation.SURFACE
    """
    how the object is represented in the scene (e.g., surface, surface with
    edges, wireframe or points). Default: surface.
    """

    def _to_proto(self) -> vis_pb2.DisplayAttributes:
        attrs = vis_pb2.DisplayAttributes()
        attrs.visible = self.visible
        attrs.representation = self.representation.value
        attrs.field.CopyFrom(self.field._to_proto())
        return attrs

    def _from_proto(self, attrs: vis_pb2.DisplayAttributes) -> None:
        self.visible = attrs.visible
        self.representation = Representation(attrs.representation)
        self.field._from_proto(attrs.field)


@dc.dataclass
class DataRange(CodeRepr):
    """
    The data range represents a range of values. Ranges are only valid if the
    max value is greater than the or equal to the min_value. The default is
    invalid.

    .. warning:: This feature is experimental and may change or be removed in the future.

    """

    min_value: float = float("inf")
    """The minimum value of the range."""
    max_value: float = float("-inf")
    """The maximum value of the range."""

    def is_valid(self) -> bool:
        return self.max_value >= self.min_value


@dc.dataclass
class ColorMapAppearance(CodeRepr):
    """
    ColorMapAppearance controls how the color maps appear in the image, including
    visibility, position and size.

    The width, height, and the lower left position of the color map are
    specified in normalized device coordinates. These are values in the [0,1]
    range. For example, the lower left hand coordinate of the image is [0,0], and the
    top right coordinate of the image is [1,1].

    .. warning:: This feature is experimental and may change or be removed in the future.

    """

    visible: bool = True
    """Controls if the color map is displayed or not. Default: True"""
    width: float = 0.034
    """The width of the color map in normalized device coordinates. Default: 0.034"""
    height: float = 0.146
    """The height of the color map in normalized device coordinates. Default: 0.146"""
    text_size: int = 36
    """The text size for the color map legend in pixels. Default: 36"""
    lower_left_x: float = 0.8
    """
    The lower left x position of the color map in normalized device
    coordinates. Default: 0.8
    """
    lower_left_y: float = 0.8
    """
    The lower left y position of the color map in normalized device
    coordinates. Default: 0.8
    """


@dc.dataclass
class ColorMap(CodeRepr):
    """
    The color map allows user control over how field values are mapped to
    colors. Color maps are assigned to fields (e.g., the quantity and component)
    and not individual display attributes. This means that there can only ever
    be one color map per field/component combination (e.g., velocity-magnitude
    or velocity-x). Any display attribute in the scene (i.e., filter display
    attributes or global display attributes) that maps to this color map will be
    color in the same manner.

    .. warning:: This feature is experimental and may change or be removed in the future.

    """

    field: Field = dc.field(default_factory=Field)
    """The field and component this color map applies to."""
    preset: ColorMapPreset = ColorMapPreset.JET
    """
    The color map preset to use. This defines the colors used in the color
    map. Default is 'JET'.
    """
    data_range: DataRange = dc.field(default_factory=DataRange)
    """
    An optional data range to use for the color map. The user must explicity
    set the data ranges. If not set explicitly, the fields global data range
    is used. For comparing multiple results, either with different solutions
    in the same simulation or with different simulations, its highly
    recommended that a range is provided so the color scales are the same
    between the resulting images. Default: is an invalid data range.
    """
    discretize: bool = False
    """
    Use discrete color bins instead of a continuous range. When True,
    'n_colors' indicates how many discrete bins to use. Default: False.
    """
    n_colors: int = 8
    """
    How many discrete bins to use when discretize is True. Valid n_colors
    values are [1, 256]. Default: 8.
    """
    appearance: Optional[ColorMapAppearance] = None
    """
    This attribute controls how the color map annotation appears in the image, including
    location, size, and visibility. When the scene is set to automatic color maps, these
    attributes are automatically populated unless overridden. When setting the appearance,
    the user is responsible for setting all values.
    """

    def _to_proto(self) -> vis_pb2.ColorMap:
        res: vis_pb2.ColorMap = vis_pb2.ColorMap()
        res.field.CopyFrom(self.field._to_proto())
        res.name = self.preset.value
        res.discretize = self.discretize
        res.n_colors = self.n_colors
        if self.data_range.is_valid():
            res.range.max = self.data_range.max_value
            res.range.min = self.data_range.min_value

        if not self.appearance:
            res.visible = True
        elif not isinstance(self.appearance, ColorMapAppearance):
            raise TypeError(f"Expected 'ColorMapAppearance', got {type(self.appearance).__name__}")
        else:
            res.visible = self.appearance.visible
            res.width = self.appearance.width
            res.height = self.appearance.height
            res.lower_left_anchor_location.x = self.appearance.lower_left_x
            res.lower_left_anchor_location.y = self.appearance.lower_left_y
            res.text_size = self.appearance.text_size
        return res

    def _from_proto(self, color_map: vis_pb2.ColorMap) -> None:
        self.field._from_proto(color_map.field)

        if color_map.HasField("range"):
            self.data_range = DataRange(
                min_value=color_map.range.min,
                max_value=color_map.range.max,
            )

        self.preset = ColorMapPreset(color_map.name)

        if color_map.HasField("discretize"):
            self.discretize = color_map.discretize
        if color_map.HasField("n_colors"):
            self.n_colors = color_map.n_colors

        self.appearance = ColorMapAppearance()
        if color_map.HasField("visible"):
            self.appearance.visible = color_map.visible
        l_typ = color_map.WhichOneof("location")
        if l_typ == "lower_left_anchor_location":
            self.appearance.lower_left_x = color_map.lower_left_anchor_location.x
            self.appearance.lower_left_y = color_map.lower_left_anchor_location.y
        if color_map.HasField("text_size"):
            self.appearance.text_size = int(color_map.text_size)
        if color_map.HasField("width"):
            self.appearance.width = color_map.width
        if color_map.HasField("height"):
            self.appearance.height = color_map.height
