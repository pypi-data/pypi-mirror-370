# Copyright 2023-2024 Luminary Cloud, Inc. All Rights Reserved.
import errno
import logging
import os
from pathlib import Path
import requests
from typing import Any, Iterator, Optional, Union, cast, List

from .file_chunk_stream import FileChunkStream
from .._proto.api.v0.luminarycloud.common import common_pb2 as commonpb
from .._proto.api.v0.luminarycloud.solution.solution_pb2 import (
    GetSolutionSurfaceDataRequest,
    GetSolutionVolumeDataRequest,
    GetSurfaceDeformationTemplateRequest,
    GetSurfaceSensitivityDataRequest,
    GetParameterSensitivityDataRequest,
)
from .._proto.api.v0.luminarycloud.physics_ai.physics_ai_pb2 import (
    GetSolutionDataPhysicsAIRequest,
)
from .._client import Client
from ..enum.quantity_type import QuantityType

logger = logging.getLogger(__name__)


def _get_fetch_url(primary_domain: str, file_id: str) -> str:
    """
    Get the URL for the fetch endpoint given a domain
    and file ID.
    """
    return f"https://{primary_domain}/fetch/{file_id}"


def _iter_file_id(
    client: Client,
    file_id: str,
) -> Iterator[bytes]:
    """
    Iterator for download via the fetch endpoint using a file ID.
    """
    if not client.primary_domain:
        raise ValueError("Client does not support file download.")
    fetch_url = _get_fetch_url(client.primary_domain, file_id)
    headers = {"Authorization": f"Bearer {client.get_token()}"}
    r = requests.get(fetch_url, headers=headers, verify=(not client.internal), stream=True)
    # 4MiB chunk size.  Maybe tune.
    for chunk in r.iter_content(chunk_size=4 * 1024 * 1024):
        yield chunk


def _iter_url(
    client: Client,
    url: str,
) -> Iterator[bytes]:
    """Iterator for download via URL."""
    headers = {}
    # Sometimes we use the gcsproxy to proxy downloads. In that case, the backend requires us to
    # authenticate. However, if we are directly downloading from GCS, we should not expose the auth
    # token to the GCS server.
    if "storage.googleapis.com" not in url:
        headers = {"Authorization": f"Bearer {client.get_token()}"}
    r = requests.get(url, headers=headers, verify=(not client.internal), stream=True)
    # 4MiB chunk size.  Maybe tune.
    for chunk in r.iter_content(chunk_size=4 * 1024 * 1024):
        yield chunk


def _create_file_chunk_stream(
    client: Client, solution_id: str, data_desc: str, file: Any
) -> FileChunkStream:
    if file.signed_url:
        logger.info(f"Begin streaming {data_desc} via signed URL for solution {solution_id}.")
        return FileChunkStream(file.metadata, _iter_url(client, file.signed_url))

    logger.info(f"Begin streaming {data_desc} via fetch URL for solution {solution_id}.")
    return FileChunkStream(file.metadata, _iter_file_id(client, file.file_id))


def download_surface_solution(
    client: Client,
    solution_id: str,
) -> FileChunkStream:
    """
    Returns the download as a file-like object.

    The filename can be retrieved from the `filename` attribute of the returned object.

    Examples
    --------
    >>> with download_surface_solution(client, "your-solution-id") as dl:
    ...     with open(dl.filename, "wb") as fp:
    ...         fp.write(dl.read())
    """

    request = GetSolutionSurfaceDataRequest(id=solution_id)
    response = client.GetSolutionSurfaceData(request)
    return _create_file_chunk_stream(client, solution_id, "surface solution", response.file)


def download_volume_solution(
    client: Client,
    solution_id: str,
    single_precision: bool = False,
) -> FileChunkStream:
    """
    Returns the download as a file-like object.

    The filename can be retrieved from the `filename` attribute of the returned object.

    Parameters
    ----------
    client: Client
        The client to use for the download.
    solution_id: str
        The ID of the solution to download.
    single_precision: bool
        If True, the solution will be downloaded in single precision.
        If False, the solution will be downloaded in double precision.

    Examples
    --------
    >>> with download_volume_solution(client, "your-solution-id") as dl:
    ...     with open(dl.filename, "wb") as fp:
    ...         fp.write(dl.read())
    """

    request = GetSolutionVolumeDataRequest(id=solution_id, single_precision=single_precision)
    response = client.GetSolutionVolumeData(request)
    return _create_file_chunk_stream(client, solution_id, "volume solution", response.file)


def download_solution_physics_ai(
    client: Client,
    solution_id: str,
    exclude_surfaces: Optional[List[str]] = None,
    fill_holes: float = -1.0,
    surface_fields_to_keep: Optional[List[QuantityType]] = None,
    volume_fields_to_keep: Optional[List[QuantityType]] = None,
    process_volume: bool = False,
    single_precision: bool = False,
) -> Optional[FileChunkStream]:
    """
    Returns the download as a file-like object, or None if destination_url is provided.

    The filename can be retrieved from the `filename` attribute of the returned object.

    Parameters
    ----------
    client: Client
        The client to use for the download.
    solution_id: str
        The ID of the solution to download.
    exclude_surfaces: Optional[List[str]]
        List of surfaces to exclude from surface solution during physics AI processing.
    fill_holes: float
        Sets the maximum size of the hole to be filled for the STL file, measured as the radius of the bounding circumsphere.
        If fill_holes is negative or zero, no holes will be filled.
    surface_fields_to_keep: List of QuantityType enum values for surface fields to keep in output.
            If None, all available surface fields are included.
    volume_fields_to_keep: List of QuantityType enum values for volume fields to keep in output.
            If None, all available volume fields are included.
    process_volume: bool
        Whether to process volume meshes during physics AI processing.
    single_precision: bool
        If True, the solution will be downloaded in single precision.

    Examples
    --------
    >>> with download_solution_physics_ai(client, "your-solution-id", process_volume=True) as dl:
    ...     with open(dl.filename, "wb") as fp:
    ...         fp.write(dl.read())
    """

    request = GetSolutionDataPhysicsAIRequest(
        solution_id=solution_id,
        exclude_surfaces=exclude_surfaces or [],
        fill_holes=fill_holes,
        surface_fields_to_keep=(
            [x.value for x in surface_fields_to_keep] if surface_fields_to_keep else []
        ),
        volume_fields_to_keep=(
            [x.value for x in volume_fields_to_keep] if volume_fields_to_keep else []
        ),
        process_volume=process_volume,
        single_precision=single_precision,
    )
    response = client.GetSolutionDataPhysicsAI(request)

    return _create_file_chunk_stream(
        client, solution_id, "physics ai processed solution", response.file
    )


def download_surface_deformation_template(
    client: Client,
    solution_id: str,
) -> FileChunkStream:
    """
    Similar to download_surface_solution.
    """
    request = GetSurfaceDeformationTemplateRequest(id=solution_id)
    response = client.GetSurfaceDeformationTemplate(request)
    return _create_file_chunk_stream(
        client, solution_id, "surface deformation template", response.file
    )


def download_surface_sensitivity_data(
    client: Client,
    solution_id: str,
) -> FileChunkStream:
    """
    Similar to download_surface_solution.
    """

    request = GetSurfaceSensitivityDataRequest(id=solution_id)
    response = client.GetSurfaceSensitivityData(request)
    return _create_file_chunk_stream(client, solution_id, "surface sensitivity data", response.file)


def download_parameter_sensitivity_data(
    client: Client,
    solution_id: str,
) -> FileChunkStream:
    """
    Similar to download_surface_solution.
    """

    request = GetParameterSensitivityDataRequest(id=solution_id)
    response = client.GetParameterSensitivityData(request)
    return _create_file_chunk_stream(
        client, solution_id, "parameter sensitivity data", response.file
    )


def save_file(
    file_proto: commonpb.File,
    dest_dir: Union[os.PathLike, str],
    *,
    filename: Optional[str] = None,
) -> None:
    """
    Saves the file to the given directory.

    Parameters
    ----------
    file_proto: commonpb.File
        Contents must be of type full_contents.
    dest_dir: PathLike or str
        The destination directory.
    filename: str
        (Optional) The desired filename. Extension is appended if omitted.

    Raises
    ------
    FileNotFoundError
        If the directory does not exist.
    OSError
        If a file with the same name already exists.

    Examples
    --------
    >>> res = client.GetSimulationSurfaceQuantityOutput(req)
    >>> save_file(res.csv_file, "~/Downloads")
    """
    metadata = file_proto.metadata
    if filename is None:
        filename = metadata.name
    if "." not in filename:
        if len(metadata.ext) > 0:
            filename += "." + metadata.ext

    dest_path = Path(dest_dir) / cast(str, filename)
    if os.path.exists(dest_path):
        err = OSError(errno.EEXIST, "File already exists at location", str(dest_path))
        logger.error("File not found.", exc_info=err)
        raise err

    logger.info(f"Writing file to {dest_path}")
    with open(dest_path, "w+") as fp:
        fp.write(file_proto.full_contents.decode())
