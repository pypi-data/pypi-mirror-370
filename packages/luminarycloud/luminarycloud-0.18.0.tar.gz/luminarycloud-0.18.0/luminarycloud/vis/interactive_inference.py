# Copyright 2025 Luminary Cloud, Inc. All Rights Reserved.
import json
from .._proto.api.v0.luminarycloud.vis import vis_pb2
from .display import DisplayAttributes
from luminarycloud.enum.vis_enums import SceneMode, VisQuantity, Representation, FieldComponent
from luminarycloud.vis import Field
from typing import TYPE_CHECKING
import luminarycloud.enum.quantity_type as quantity_type
from .interactive_scene import InteractiveScene

from .._proto.api.v0.luminarycloud.vis import vis_pb2

if TYPE_CHECKING:
    from .visualization import Scene, LookAtCamera, DirectionalCamera, ColorMap
    from ..geometry import Geometry
    from ..mesh import Mesh
    from ..solution import Solution

try:
    import luminarycloud_jupyter as lcj

    if TYPE_CHECKING:
        from luminarycloud_jupyter import InteractiveLCVisWidget, LCVisPlaneWidget
except ImportError:
    lcj = None


_SOURCE_FILTER_ID = "___LC_SOURCE_FILTER___"

# Global workspace state configuration
# We use this to provide a constructed context to the LCVis widget so that we can visualize
# the surface inference results.
WORKSPACE_STATE_CONFIG = {
    "connections": {_SOURCE_FILTER_ID: []},
    "filters": [
        {
            "id": _SOURCE_FILTER_ID,
            "name": "LcMeshSource",
            "params": {
                "fvm_params": "",
                "url": "dummy",
            },
        }
    ],
    "workspace_params": {"edge_mode": "boundary"},
}


class InteractiveInference(InteractiveScene):
    """
    The InteractiveInference acts as the bridge between the RenderData and
    the Jupyter widget, handling checking if we have the widget package
    before passing calls to the widget to handle it being an optional
    dependency
    """

    def __init__(self, signed_url: str, mode: SceneMode = SceneMode.INLINE) -> None:
        # Initialize the widget directly without calling parent constructor
        # since we don't have a real Scene object and override set_scene anyway
        if not lcj:
            raise ImportError(
                "Interactive visualization requires luminarycloud[jupyter] to be installed"
            )
        self.widget = lcj.LCVisWidget(scene_mode=mode)
        self._scene = None  # Not used in InteractiveInference

        # Do inference-specific setup
        self.set_signed_url(signed_url, False)
        # Known quantities written by inference
        self._valid_quantities = [
            VisQuantity.NONE,
            VisQuantity.PRESSURE,
            VisQuantity.WALL_SHEAR_STRESS,
        ]

    def set_signed_url(self, signed_url: str, isComparator: bool) -> None:
        # TODO(matt): we could make isCompartor an index so we could compare
        # more than two scenes at once.

        # Import here to avoid circular import issue
        from .visualization import LookAtCamera

        WORKSPACE_STATE_CONFIG["filters"][0]["params"]["url"] = signed_url
        resp = vis_pb2.GetRenderDataUrlsResponse()
        resp.urls.filter_ids.append(_SOURCE_FILTER_ID)
        file = resp.urls.data_files.add()
        file.signed_url = signed_url
        resp.urls.data_files.append(file)
        resp.workspace_state = json.dumps(WORKSPACE_STATE_CONFIG)

        self.widget.set_workspace_state(resp, isComparator)

        self.reset_camera()
        self.widget.set_flat_shading(True)

    def get_field_range(self, quantity: VisQuantity) -> list[float]:
        """
        Get the field range for a given quantity.
        """
        if quantity not in self._valid_quantities:
            raise ValueError(
                f"Invalid field quantity: {quantity}. Valid quantities are: {self._valid_quantities}"
            )
        return self.widget.get_field_range(quantity)

    def set_display_field(self, field: Field) -> None:
        if field.quantity not in self._valid_quantities:
            raise ValueError(
                f"Invalid field quantity: {field.quantity}. Valid quantities are: {self._valid_quantities}"
            )
        if not quantity_type._is_vector(field.quantity):
            # We normally handle this on the backend, but we are sending this directly
            # to lcvis, so we need to make sure scalars are set to the X component
            field.component = FieldComponent.X
        attrs = DisplayAttributes()
        attrs.field = field
        attrs.visible = True
        attrs.representation = Representation.SURFACE
        self.widget.set_display_attributes(_SOURCE_FILTER_ID, attrs)

    def get_field_ranges(self) -> dict[str, list[float]]:
        """
        Get the field ranges from the widget.
        """
        return self.widget.field_data_map

    def set_color_map(self, color_map: "ColorMap") -> None:
        if color_map.field.quantity not in self._valid_quantities:
            raise ValueError(
                f"Invalid field quantity: {color_map.field.quantity}. Valid quantities are: {self._valid_quantities}"
            )
        if not quantity_type._is_vector(color_map.field.quantity):
            # We normally handle this on the backend, but we are sending this directly
            # to lcvis, so we need to make sure scalars are set to the X component
            color_map.field.component = FieldComponent.X
        super().set_color_map(color_map)

    def set_scene(self, scene: "Scene", isComparator: bool = False) -> None:
        """
        InteractiveInference does not support setting scenes.
        Use set_signed_url() instead to load inference data.
        """
        raise NotImplementedError(
            "InteractiveInference does not support set_scene(). Use set_signed_url() to load inference data."
        )

    def compare(self, entity) -> None:
        """
        InteractiveInference does not support scene comparison.
        """
        raise NotImplementedError(
            "InteractiveInference does not support compare(). This feature is only available for InteractiveScene."
        )
