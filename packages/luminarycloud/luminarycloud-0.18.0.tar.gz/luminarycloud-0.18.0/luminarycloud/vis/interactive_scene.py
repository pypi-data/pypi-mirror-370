# Copyright 2023-2024 Luminary Cloud, Inc. All Rights Reserved.
from .display import DisplayAttributes
from .filters import SurfaceStreamlines, Filter, SurfaceLIC
from .._client import get_default_client
from luminarycloud.enum.vis_enums import EntityType, SceneMode
from typing import TYPE_CHECKING, cast, Union

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


class InteractiveScene:
    """
    The InteractiveScene acts as the bridge between the the Scene and
    the Jupyter widget, handling checking if we have the widget package
    before passing calls to the widget to handle it being an optional
    dependency
    """

    # Using the type causes a circular import error, not sure on best way to resolve.
    # I do want to keep this in a separate file
    def __init__(self, scene: "Scene", mode: SceneMode) -> None:
        if not lcj:
            raise ImportError("InteractiveScene requires luminarycloud[jupyter] to be installed")
        self.widget = lcj.LCVisWidget(scene_mode=mode)
        self._scene = scene
        self.set_scene(scene, False)

    def _ipython_display_(self) -> None:
        """
        When the InteractiveScene is shown in Jupyter we show the underlying widget
        to run the widget's frontend code
        """
        self.widget._ipython_display_()

    def set_scene(self, scene: "Scene", isComparator: bool) -> None:
        # TODO(matt): we could make isCompartor and index so we could compare
        # more than two scenes at once.

        # Import here to avoid circular import issue
        from .visualization import LookAtCamera

        # Display the initial scene we've been given
        # Submit request for the render data URLs we need
        req = vis_pb2.GetRenderDataUrlsRequest()
        req.project_id = scene._project_id
        if scene._entity_type == EntityType.SIMULATION:
            req.entity.simulation.id = scene._solution.simulation_id
            req.entity.simulation.solution_id = scene._solution.id
        elif scene._entity_type == EntityType.MESH:
            req.entity.mesh.id = scene._mesh.id
        elif scene._entity_type == EntityType.GEOMETRY:
            req.entity.geometry.id = scene._geometry.id
        else:
            # Should never hit b/c the Scene would have complained already
            raise TypeError(
                f"Expected Solution, Mesh or Geometry in Scene, got {scene._entity_type}"
            )

        # Validate filter connections and filter params.
        # we don't care about validating anything else that the Scene checks in _create_request
        # for now. We could unify this code more later.
        scene._validate_filter_connections()
        for filter in scene._filters:
            if isinstance(filter, SurfaceStreamlines):
                # Validate surfaces names
                streamlines = cast(SurfaceStreamlines, filter)
                bad_ids = scene._validate_surfaces_and_tags(streamlines._surface_names)
                if len(bad_ids) != 0:
                    raise ValueError(f"SurfaceStreamlines has invalid surfaces: {bad_ids}")
            if isinstance(filter, SurfaceLIC):
                # Validate surfaces names
                lic = cast(SurfaceLIC, filter)
                bad_ids = scene._validate_surfaces_and_tags(lic._surface_names)
                if len(bad_ids) != 0:
                    raise ValueError(f"SurfaceStreamlines has invalid surfaces: {bad_ids}")

            if isinstance(filter, Filter):
                vis_filter: vis_pb2.Filter = filter._to_proto()
                req.filters.append(vis_filter)
            else:
                raise TypeError(f"Expected 'filter', got {type(filter).__name__}")
            if filter.get_parent_id():
                req.filter_connections[filter.get_parent_id()].children_id.append(filter.id)

        # TODO: would be nice to show execution progress of the workspace here,
        # some inline progress bar in the notebook
        resp = get_default_client().GetRenderDataUrls(req)

        # TODO: would be nice to print/report some download progress info
        # This can be done on the app frontend side now that the download
        # is moved there. Matt: this would be a lot of work. The current vis service
        # call used in the backend doesn't use the streaming version. Further, there is
        # a lot of extra code to manage the streaming callbacks.
        self.widget.set_workspace_state(resp, isComparator)

        # Sync display attributes and visibilities for surfaces
        self.set_display_attributes(_SOURCE_FILTER_ID, scene.global_display_attrs)
        for s, v in scene._surface_visibilities.items():
            self.set_surface_visibility(s, v)

        for f in scene._filters:
            self.set_display_attributes(f.id, f.display_attrs)

        # Set any color maps we have. TODO(matt): only a few attributes are connected atm.
        for color_map in scene._color_maps:
            self.set_color_map(color_map)

        # Apply the first camera, if any, in the scene
        # If we don't have an initial camera to use, reset the camera after loading
        # the workspace state
        if len(scene._cameras) > 0:
            self.set_camera(scene._cameras[0])
        else:
            self.reset_camera()

    def set_surface_visibility(self, surface_id: str, visible: bool) -> None:
        self.widget.set_surface_visibility(surface_id, visible)

    def set_surface_color(self, surface_id: str, color: list[float]) -> None:
        self.widget.set_surface_color(surface_id, color)

    def set_display_attributes(self, object_id: str, attrs: DisplayAttributes) -> None:
        self.widget.set_display_attributes(object_id, attrs)

    def reset_camera(self) -> None:
        self.widget.reset_camera()

    def set_camera(self, camera: "LookAtCamera | DirectionalCamera") -> None:
        # Import here to avoid circular import issue
        from .visualization import LookAtCamera

        # Clear any prev camera state
        self.widget.camera_position = []
        self.widget.camera_look_at = []
        self.widget.camera_up = []
        self.widget.camera_pan = []
        if isinstance(camera, LookAtCamera):
            self.widget.camera_position = [
                camera.position[0],
                camera.position[1],
                camera.position[2],
            ]
            self.widget.camera_look_at = [camera.look_at[0], camera.look_at[1], camera.look_at[2]]
            self.widget.camera_up = [camera.up[0], camera.up[1], camera.up[2]]
            self.widget.camera_pan = [camera.pan_x, camera.pan_y, 0]
        else:
            self.widget.set_camera_orientation(camera.direction)

    def set_color_map(self, color_map: "ColorMap") -> None:
        self.widget.set_color_map(color_map)

    def get_camera(self) -> "LookAtCamera":
        # Import here to avoid circular import issue
        from .visualization import LookAtCamera

        camera = LookAtCamera()
        camera.position = self.widget.camera_position
        camera.look_at = self.widget.camera_look_at
        camera.up = self.widget.camera_up
        # Immediately after creation, the widget's camera_pan is empty, so avoid going out of bounds
        # and report 0 which is what it would be anyway
        camera.pan_x = self.widget.camera_pan[0] if self.widget.camera_pan else 0
        camera.pan_y = self.widget.camera_pan[1] if self.widget.camera_pan else 0
        return camera

    def set_triad_visible(self, visible: bool) -> None:
        self.widget.set_triad_visible(visible)

    def add_plane_widget(self) -> "LCVisPlaneWidget":
        return self.widget.add_plane_widget()

    def delete_widget(self, widget: "InteractiveLCVisWidget") -> None:
        self.widget.delete_widget(widget)

    def compare(self, entity: Union["Geometry", "Mesh", "Solution"]) -> None:
        # The entity can be a Geometry, Mesh, or Solution and is checked by the
        # clone method. This can raise error if the scenes are incompatiable.
        # This happens when tags or surface ids aren't shared or if we try to
        # compare two different types of entities.
        comparison_scene = self._scene.clone(entity)
        self.set_scene(comparison_scene, True)
