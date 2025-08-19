from __future__ import annotations

import tarfile
from typing import List, Optional, BinaryIO, cast

from .._client import get_default_client
from .._helpers.download import download_solution_physics_ai as _download_solution_physics_ai
from ..enum.quantity_type import QuantityType


def _download_processed_solution_physics_ai(  # noqa: F841
    solution_id: str,
    exclude_surfaces: Optional[List[str]] = None,
    fill_holes: float = -1.0,
    surface_fields_to_keep: Optional[List[QuantityType]] = None,
    volume_fields_to_keep: Optional[List[QuantityType]] = None,
    process_volume: bool = False,
    single_precision: bool = True,
) -> tarfile.TarFile:
    """
    Download solution data with physics AI processing applied.

    Returns a compressed archive containing processed solution files including
    merged surfaces (VTP/STL) and optionally volume data (VTU).

    .. warning:: This feature is experimental and may change or be removed without notice.

    Args:
        solution_id: ID of the solution to download
        exclude_surfaces: List of surface names to exclude from processing
        fill_holes: Sets the maximum size of the hole to be filled for the STL file, measured as the radius of the bounding circumsphere.
            If fill_holes is negative or zero, no holes will be filled.
        surface_fields_to_keep: List of QuantityType enum values for surface fields to keep in output.
            If None, all available surface fields are included.
        volume_fields_to_keep: List of QuantityType enum values for volume fields to keep in output.
            If None, all available volume fields are included.
        process_volume: Whether to process volume data
        single_precision: Whether to use single precision for floating point fields

    Raises:
        ValueError: If invalid field names are provided
    """

    stream = _download_solution_physics_ai(
        get_default_client(),
        solution_id,
        exclude_surfaces=exclude_surfaces,
        fill_holes=fill_holes,
        surface_fields_to_keep=surface_fields_to_keep,
        volume_fields_to_keep=volume_fields_to_keep,
        process_volume=process_volume,
        single_precision=single_precision,
    )

    assert stream is not None, "Failed to download solution data"
    return tarfile.open(
        name=stream.filename,
        fileobj=cast(BinaryIO, stream),
        mode="r|gz",
    )
