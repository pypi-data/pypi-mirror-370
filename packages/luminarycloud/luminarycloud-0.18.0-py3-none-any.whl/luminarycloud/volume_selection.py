# Copyright 2023-2025 Luminary Cloud, Inc. All Rights Reserved.
from __future__ import annotations

import logging
from os import PathLike
from typing import TYPE_CHECKING, Iterable, Iterator, Optional
from uuid import uuid4

from luminarycloud._helpers import util
from luminarycloud._helpers.upload import upload_file
from luminarycloud._proto.api.v0.luminarycloud.geometry import (
    geometry_pb2 as geometrypb,
)
from luminarycloud._proto.upload import upload_pb2 as uploadpb
from luminarycloud.types.adfloat import _from_ad_proto, _to_ad_proto

from ._client import get_default_client
from ._proto.base import base_pb2 as basepb
from ._proto.cad import boolean_pb2 as booleanpb
from ._proto.cad import transformation_pb2 as transformationpb
from ._proto.geometry import geometry_pb2 as gpb
from .params.geometry import (
    Cone,
    Cube,
    Cylinder,
    HalfSphere,
    Shape,
    Sphere,
    Torus,
    Volume,
)
from .types import Matrix3, Vector3, Vector3Like
from .types.vector3 import _to_vector3

if TYPE_CHECKING:
    from .geometry import Geometry

logger = logging.getLogger(__name__)


class VolumeSelection:
    """
    Represents a selection of volumes on which geometry modification operations can be performed.

    When a modification is applied, the selection is updated as volumes are created and/or deleted.
    Newly created volumes are added to the selection, while deleted volumes are removed from the
    selection. This allows for chaining modifications together easily.

    Examples
    --------
    >>> s = geometry.select_volumes([])
    >>> s.create_shape(
    ...     lc.params.geometry.Sphere(radius=1.0, center=lc.types.Vector3(0, 0, 0)),
    ... )
    >>> s.translate(lc.types.Vector3(1, 0, 0))
    >>> s.tag("sphere")

    >>> s = geometry.select_volumes() # select all
    >>> s.union()
    >>> a = s.volumes()

    >>> s.clear()
    >>> s.import_cad("/path/to/cube.cgns")
    >>> s.translate(lc.types.Vector3(1, 0, 1))
    >>> b = s.volumes()

    >>> s.clear()
    >>> s.select(a)
    >>> s.subtract(b)
    """

    def __init__(self, geometry: "Geometry", volumes: list[Volume | int]):
        self.__geometry = geometry
        self.__volume_ids = set()
        for v in volumes:
            if isinstance(v, Volume):
                self.__volume_ids.add(int(v.id))
            elif isinstance(v, int):
                self.__volume_ids.add(v)
            else:
                raise TypeError(f"Unsupported type for volume selection: {type(v)}")

    def select(self, volumes: Iterable[Volume]) -> None:
        """Add volumes to the selection."""
        self.__volume_ids |= set(int(v.id) for v in volumes)

    def unselect(self, volumes: Iterable[Volume]) -> None:
        """Remove volumes from the selection."""
        for v in volumes:
            if not isinstance(v, Volume):
                raise TypeError(f"Unsupported type: {type(v)}")
            self.__volume_ids.discard(int(v.id))

    def select_all(self) -> None:
        """Select all volumes in the geometry."""
        self.__volume_ids = set(int(b.id) for b in self.__list_entities().bodies)

    def clear(self) -> None:
        """Clear the selection."""
        self.__volume_ids.clear()

    def __iter__(self) -> Iterator[Volume]:
        """
        Return an iterator over the selected volumes.
        """
        res = self.__list_entities()
        for b in res.bodies:
            if b.id in self.__volume_ids:
                yield Volume(
                    geometry_id=self.__geometry.id,
                    id=str(b.id),
                    _lcn_id=str(b.lcn_id),
                    bbox_min=Vector3(b.bbox_min.x, b.bbox_min.y, b.bbox_min.z),
                    bbox_max=Vector3(b.bbox_max.x, b.bbox_max.y, b.bbox_max.z),
                )

    def volumes(self) -> list[Volume]:
        """
        Return a list of the selected volumes.
        """
        return list(self)

    def import_cad(
        self,
        cad_file_path: PathLike,
        *,
        scaling: float = 1.0,
        feature_name: str = "Import CAD",
    ) -> None:
        """
        Import a CAD file into the geometry. Add the imported volumes to the selection.

        Parameters
        ----------
        cad_file_path : PathLike
            The path to the CAD file to import.
        scaling : float
            The scaling factor to apply to the CAD file.
        feature_name : str
            The name of the feature. This is not a tag name.
        """
        cad_file_meta = util.get_file_metadata(cad_file_path)
        logger.debug(
            f"Uploading file {cad_file_meta.name}.{cad_file_meta.ext} to import into geometry {self.__geometry.id}"
            + f"size: {cad_file_meta.size} bytes, sha256: {str(cad_file_meta.sha256_checksum)}, "
            + f"crc32c: {cad_file_meta.crc32c_checksum}"
        )

        finish_res = upload_file(
            get_default_client(),
            self.__geometry._proto.project_id,
            uploadpb.ResourceParams(geometry_params=uploadpb.GeometryParams()),
            cad_file_path,
        )[1]
        cad_url = finish_res.url

        feature = gpb.Feature(feature_name=feature_name)
        feature.import_geometry.CopyFrom(
            gpb.ImportGeometry(
                geometry_url=cad_url,
                scaling=_to_ad_proto(scaling),
            )
        )
        self.__create_feature(feature)

    def delete(self, *, feature_name: str = "Delete") -> None:
        """
        Delete the selected volumes.

        Parameters
        ----------
        feature_name : str
            The name of the feature.
        """
        self.__create_feature(
            gpb.Feature(
                feature_name=feature_name,
                delete=gpb.Delete(
                    type=gpb.EntityType.BODY,
                    ids=self.__volume_ids,
                ),
            )
        )

    def union(self, *, feature_name: str = "Union") -> None:
        """
        Merge the selected volumes.

        The original volumes are removed.

        Parameters
        ----------
        feature_name : str
            The name of the feature.
        """
        self.__create_feature(
            gpb.Feature(
                feature_name=feature_name,
                boolean=gpb.Boolean(
                    reg_union=booleanpb.RegularUnion(
                        bodies=self.__volume_ids,
                    )
                ),
            )
        )

    def subtract(
        self,
        tool_volumes: Iterable[Volume],
        *,
        propagate_tags: bool = False,
        feature_name: str = "Subtract",
    ) -> None:
        """
        Boolean subtract the tool volumes from the selected volumes.

        The selected volumes are modified in-place, and the tool volumes are removed.

        Parameters
        ----------
        tool_volumes : Iterable[Volume]
            The volumes to subtract from the selected volumes.
        propagate_tags : bool
            Whether to propagate the tool volume tags to the surfaces created by the subtraction.
        feature_name : str
            The name of the feature.
        """
        self.__create_feature(
            gpb.Feature(
                feature_name=feature_name,
                boolean=gpb.Boolean(
                    reg_subtraction=booleanpb.RegularSubtraction(
                        bodies=self.__volume_ids,
                        tools=[int(v.id) for v in tool_volumes],
                        propagate_tool_tags=propagate_tags,
                    )
                ),
            )
        )

    def intersection(self, *, feature_name: str = "Intersection") -> None:
        """
        Create an intersection of the selected volumes.

        The original volumes are removed.

        Parameters
        ----------
        feature_name : str
            The name of the feature.
        """
        self.__create_feature(
            gpb.Feature(
                feature_name=feature_name,
                boolean=gpb.Boolean(
                    reg_intersection=booleanpb.RegularIntersection(
                        bodies=self.__volume_ids,
                    )
                ),
            )
        )

    def chop(
        self,
        tool_volumes: Iterable[Volume],
        *,
        propagate_tags: bool = False,
        feature_name: str = "Chop",
    ) -> None:
        """
        Chop the selected volumes with the tool volumes.

        The tool volumes are removed, and the original volumes are replaced with the result
        of the chop.

        Parameters
        ----------
        tool_volumes : Iterable[Volume]
            The volumes to chop the selected volumes with.
        propagate_tags : bool
            Whether to propagate the tool volume tags to the surfaces created by the chop.
        feature_name : str
            The name of the feature.
        """
        self.__create_feature(
            gpb.Feature(
                feature_name=feature_name,
                boolean=gpb.Boolean(
                    reg_chop=booleanpb.RegularChop(
                        bodies=self.__volume_ids,
                        tools=[int(v.id) for v in tool_volumes],
                        propagate_tool_tags=propagate_tags,
                    )
                ),
            )
        )

    def translate(self, displacement: Vector3Like, *, feature_name: str = "Translate") -> None:
        """
        Translate the selected volumes.

        The selected volumes are modified in-place.

        Parameters
        ----------
        displacement : Vector3Like
            The displacement to translate the selected volumes by.
        feature_name : str
            The name of the feature.
        """
        displacement = _to_vector3(displacement)
        self.__create_feature(
            gpb.Feature(
                feature_name=feature_name,
                transform=gpb.Transform(
                    body=self.__volume_ids,
                    translation=transformationpb.Translation(
                        vector=basepb.Vector3(
                            x=displacement.x,
                            y=displacement.y,
                            z=displacement.z,
                        ),
                    ),
                ),
            )
        )

    def rotate(
        self,
        angle: float,
        axis: Vector3Like,
        origin: Vector3Like,
        *,
        feature_name: str = "Rotate",
    ) -> None:
        """
        Rotate the selected volumes.

        The selected volumes are modified in-place.

        Parameters
        ----------
        angle : float
            The angle to rotate the selected volumes by, in degrees.
        axis : Vector3Like
            The axis to rotate the selected volumes around.
        origin : Vector3Like
            The origin to rotate the selected volumes around.
        feature_name : str
            The name of the feature.
        """
        axis = _to_vector3(axis)
        origin = _to_vector3(origin)
        self.__create_feature(
            gpb.Feature(
                feature_name=feature_name,
                transform=gpb.Transform(
                    body=self.__volume_ids,
                    rotation=transformationpb.Rotation(
                        angle=angle,
                        arbitrary=transformationpb.AnchoredVector3(
                            origin=basepb.Vector3(
                                x=origin.x,
                                y=origin.y,
                                z=origin.z,
                            ),
                            direction=basepb.Vector3(
                                x=axis.x,
                                y=axis.y,
                                z=axis.z,
                            ),
                        ),
                    ),
                ),
            )
        )

    def scale(
        self,
        factor: float,
        origin: Vector3Like,
        *,
        feature_name: str = "Scale",
    ) -> None:
        """
        Isotropically scale the selected volumes.

        The selected volumes are modified in-place.

        Parameters
        ----------
        factor : float
            The scaling factor.
        origin : Vector3Like
            The origin to scale the selected volumes from.
        feature_name : str
            The name of the feature.
        """
        origin = _to_vector3(origin)
        self.__create_feature(
            gpb.Feature(
                feature_name=feature_name,
                transform=gpb.Transform(
                    body=self.__volume_ids,
                    scaling=transformationpb.Scaling(
                        isotropic=factor,
                        arbitrary=basepb.Vector3(
                            x=origin.x,
                            y=origin.y,
                            z=origin.z,
                        ),
                    ),
                ),
            )
        )

    def transform(
        self,
        transform: Matrix3,
        translation: Vector3Like,
        *,
        feature_name: str = "Transform",
    ) -> None:
        """
        Transform the selected volumes.

        The selected volumes are modified in-place.

        Parameters
        ----------
        transform : Matrix3
            The linear transformation to apply to the selected volumes.
        translation : Vector3Like
            The translation to apply to the selected volumes.
        feature_name : str
            The name of the feature.
        """
        translation = _to_vector3(translation)
        self.__create_feature(
            gpb.Feature(
                feature_name=feature_name,
                transform=gpb.Transform(
                    body=self.__volume_ids,
                    matrix=transformationpb.AugmentedMatrix(
                        affine=transform._to_proto(),
                        translation=basepb.Vector3(
                            x=translation.x,
                            y=translation.y,
                            z=translation.z,
                        ),
                    ),
                ),
            )
        )

    def shrinkwrap(
        self,
        resolution_min: Optional[float] = None,
        resolution_max: Optional[float] = None,
        tool: Optional[Iterable[Volume]] = None,
        *,
        feature_name: str = "Shrinkwrap",
    ) -> None:
        """
        Shrinkwrap the selected volumes.

        Parameters
        ----------
        resolution_min : float, optional
            The minimum resolution to shrinkwrap the selected volumes to.
        resolution_max : float, optional
            The maximum resolution to shrinkwrap the selected volumes to.
        tool : VolumeSelection, optional
            The tool volume selection to subtract from self in the shrinkwrap operation.
        feature_name : str
            The name of the feature.
        """
        if resolution_min is not None and resolution_max is not None:
            if resolution_min > resolution_max:
                raise ValueError("resolution_min must be less than or equal to resolution_max.")
            if resolution_min == resolution_max:
                mode = gpb.ShrinkwrapMode.UNIFORM
            else:
                mode = gpb.ShrinkwrapMode.MINMAX
        elif resolution_min is not None or resolution_max is not None:
            raise ValueError(
                "Either both resolution_min and resolution_max must be provided, or neither."
            )
        else:
            mode = gpb.ShrinkwrapMode.AUTOMATIC

        tool_ids = []
        if tool is not None:
            tool_ids = [int(v.id) for v in tool]

        self.__create_feature(
            gpb.Feature(
                feature_name=feature_name,
                shrinkwrap=gpb.Shrinkwrap(
                    body=self.__volume_ids,
                    resolution_min=(resolution_min or 0.0),
                    resolution_max=(resolution_max or 0.0),
                    resolution_uniform=(resolution_min or 0.0),
                    tool=tool_ids,
                    mode=mode,
                ),
            )
        )

    def linear_pattern(
        self,
        vector: Vector3Like,
        quantity: int,
        *,
        feature_name: str = "Linear Pattern",
    ) -> None:
        """
        Repeat the selected volumes evenly along a vector.

        Parameters
        ----------
        vector : Vector3Like
            The vector to repeat the selected volumes along.
        quantity : int
            The number of times to repeat the selected volumes.
        feature_name : str
            The name of the feature.
        """
        vector = _to_vector3(vector)
        self.__create_feature(
            gpb.Feature(
                feature_name=feature_name,
                pattern=gpb.Pattern(
                    body=self.__volume_ids,
                    direction=gpb.Pattern.Direction(
                        linear_spacing=transformationpb.Translation(
                            vector=basepb.Vector3(
                                x=vector.x,
                                y=vector.y,
                                z=vector.z,
                            ),
                        ),
                        quantity=quantity,
                    ),
                ),
            )
        )

    def linear_pattern_with_vector_magnitude(
        self,
        vector: Vector3Like,
        magnitude: float,
        quantity: int,
        *,
        feature_name: str = "Linear Pattern",
    ) -> None:
        """
        Repeat the selected volumes evenly along a vector defined by a direction and its
        magnitude.

        Parameters
        ----------
        vector : Vector3Like
            Direction of the vector to repeat the selected volumes along. It will be normalized.
        magnitude : float
            The magnitude of the vector.
        quantity : int
            The number of times to repeat the selected volumes.
        feature_name : str
            The name of the feature.
        """
        return self.linear_pattern(
            vector=[vector[i] * magnitude for i in range(3)],
            quantity=quantity,
            feature_name=feature_name,
        )

    def circular_pattern(
        self,
        angle: float,
        axis: Vector3Like,
        origin: Vector3Like,
        quantity: int,
        *,
        feature_name: str = "Circular Pattern",
    ) -> None:
        """
        Repeat the selected volumes evenly along a circular arc.

        Parameters
        ----------
        angle : float
            The angle of the circular arc, in degrees. If the angle is 360, the volumes are evenly
            distributed around a full circle.
        axis : Vector3Like
            The axis of the circular arc.
        origin : Vector3Like
            The origin of the circular arc.
        quantity : int
            The number of times to repeat the selected volumes.
        feature_name : str
            The name of the feature.
        """
        axis = _to_vector3(axis)
        origin = _to_vector3(origin)
        self.__create_feature(
            gpb.Feature(
                feature_name=feature_name,
                pattern=gpb.Pattern(
                    body=self.__volume_ids,
                    direction=gpb.Pattern.Direction(
                        circular_distribution=gpb.Pattern.Direction.Circular(
                            rotation=transformationpb.Rotation(
                                angle=angle,
                                arbitrary=transformationpb.AnchoredVector3(
                                    origin=basepb.Vector3(
                                        x=origin.x,
                                        y=origin.y,
                                        z=origin.z,
                                    ),
                                    direction=basepb.Vector3(
                                        x=axis.x,
                                        y=axis.y,
                                        z=axis.z,
                                    ),
                                ),
                            ),
                            full=(angle == 360.0),  # set to true if angle is exactly 360
                        ),
                        quantity=quantity,
                    ),
                ),
            )
        )

    def create_shape(
        self,
        shape: Shape,
        *,
        feature_name: Optional[str] = None,
    ) -> None:
        """
        Create a simple shape in the geometry.

        The resulting volume is added to selected volumes.

        Parameters
        ----------
        shape : Shape
            The shape to create.
        feature_name : str
            The name of the feature. Not the name of the created shape.
        """
        if feature_name is None:
            feature_name = f"Create {shape.__class__.__name__}"

        params = gpb.Create()
        if isinstance(shape, Sphere):
            params.sphere.CopyFrom(shape._to_proto())  # type: ignore
        elif isinstance(shape, Cube):
            params.box.CopyFrom(shape._to_proto())  # type: ignore
        elif isinstance(shape, Cylinder):
            params.cylinder.CopyFrom(shape._to_proto())  # type: ignore
        elif isinstance(shape, Torus):
            params.torus.CopyFrom(shape._to_proto())  # type: ignore
        elif isinstance(shape, Cone):
            params.cone.CopyFrom(shape._to_proto())  # type: ignore
        elif isinstance(shape, HalfSphere):
            params.half_sphere.CopyFrom(shape._to_proto())  # type: ignore
        else:
            raise TypeError(f"Unsupported shape type: {type(shape)}")
        self.__create_feature(
            gpb.Feature(
                feature_name=feature_name,
                create=params,
            )
        )

    def tag(self, name: str) -> None:
        """Tag the selected volumes."""
        req = geometrypb.ModifyGeometryRequest(
            geometry_id=self.__geometry.id,
            modification=gpb.Modification(
                mod_type=gpb.Modification.MODIFICATION_TYPE_CREATE_TAG,
                create_or_update_tag=gpb.CreateOrUpdateTag(
                    name=name,
                    bodies=self.__volume_ids,
                ),
            ),
        )
        get_default_client().ModifyGeometry(req)

    def __list_entities(self) -> geometrypb.ListGeometryEntitiesResponse:
        return get_default_client().ListGeometryEntities(
            geometrypb.ListGeometryEntitiesRequest(geometry_id=self.__geometry.id)
        )

    def __create_feature(self, feature: gpb.Feature) -> None:
        before = set(int(b.id) for b in self.__list_entities().bodies)
        feature.id = str(uuid4())
        req = geometrypb.ModifyGeometryRequest(
            geometry_id=self.__geometry.id,
            modification=gpb.Modification(
                mod_type=gpb.Modification.MODIFICATION_TYPE_CREATE_FEATURE,
                feature=feature,
            ),
        )
        res: geometrypb.ModifyGeometryResponse = get_default_client().ModifyGeometry(req)
        after = set(int(v.id) for v in res.volumes)

        self.__volume_ids |= after - before
        self.__volume_ids -= before - after

    def __len__(self) -> int:
        return len(self.__volume_ids)
