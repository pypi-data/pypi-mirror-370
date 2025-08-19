# Copyright 2024 Luminary Cloud, Inc. All Rights Reserved.
from luminarycloud._proto.api.v0.luminarycloud.geometry import geometry_pb2 as geometrypb
from luminarycloud._proto.upload import upload_pb2 as uploadpb
from luminarycloud.types.adfloat import _to_ad_proto
from os import PathLike
from .._client import Client
from .upload import upload_file
from typing import List, Optional
from luminarycloud._helpers import util
import uuid
import random
import time
import tempfile
import zipfile
from pathlib import Path

import logging

logger = logging.getLogger(__name__)


def _create_zip(file_paths: List[PathLike | str]) -> Path:
    """Create ZIP file."""

    zip_path = Path(tempfile.mktemp(suffix=".zip"))

    with zipfile.ZipFile(zip_path, "w") as zf:
        for file_path in file_paths:
            path = Path(file_path)
            zf.write(path, path.name)  # Flatten structure

    return zip_path


def _create_geometry_from_url(
    client: Client,
    project_id: str,
    url: str,
    name: str,
    web_geometry_id: str,
    scaling: Optional[float],
    wait: bool,
) -> geometrypb.Geometry:
    """Create geometry from already-uploaded URL (shared logic)."""

    if scaling is None:
        # default to no scaling
        scaling = 1.0

    create_geo_res: geometrypb.CreateGeometryResponse = client.CreateGeometry(
        geometrypb.CreateGeometryRequest(
            project_id=project_id,
            name=name,
            url=url,
            web_geometry_id=web_geometry_id,
            scaling=_to_ad_proto(scaling),
            wait=False,
            request_id=str(uuid.uuid4()),
        )
    )
    geo = create_geo_res.geometry

    # Prefer polling on the client than waiting on the server (although waiting on the server
    # notifies the clients potentially faster).
    if wait:
        last_version_id = ""
        while not last_version_id:
            jitter = random.uniform(0.5, 1.5)
            time.sleep(2 + jitter)
            req = geometrypb.GetGeometryRequest(geometry_id=create_geo_res.geometry.id)
            res_geo: geometrypb.GetGeometryResponse = client.GetGeometry(req)
            geo = res_geo.geometry
            last_version_id = geo.last_version_id

    logger.info(f"created geometry {geo.name} ({geo.id})")
    return geo


def _create_geometry_from_multiple_files(
    client: Client,
    cad_file_paths: List[PathLike | str],
    project_id: str,
    *,
    name: Optional[str] = None,
    scaling: Optional[float] = None,
    wait: bool = False,
) -> geometrypb.Geometry:
    """
    Create geometry from multiple files using frontend's proven pattern.

    Creates a ZIP file and uploads using meshParams (not geometryParams)
    to leverage existing FileSetManifest infrastructure.
    """

    # Create ZIP file (simple, no validation - like single-file)
    zip_path = _create_zip(cad_file_paths)

    try:
        # Upload ZIP using meshParams
        finish_res = upload_file(
            client,
            project_id,
            uploadpb.ResourceParams(mesh_params=uploadpb.MeshParams(scaling=scaling or 1.0)),
            zip_path,
        )[1]

        # Create geometry from uploaded ZIP URL
        return _create_geometry_from_url(
            client,
            project_id,
            finish_res.url,
            name or "Multi-file Geometry",
            "",
            scaling,
            wait,
        )
    finally:
        # Clean up ZIP
        zip_path.unlink()


def create_geometry(
    client: Client,
    cad_file_path: PathLike | str | List[PathLike | str],
    project_id: str,
    *,
    name: Optional[str] = None,
    scaling: Optional[float] = None,
    wait: bool = False,
) -> geometrypb.Geometry:
    """
    Create a geometry from single or multiple CAD files.
    """

    # Route to appropriate handler based on input type
    if isinstance(cad_file_path, (list, tuple)) and len(cad_file_path) > 1:
        # Multi-file: use mesh upload pattern (like frontend)
        return _create_geometry_from_multiple_files(
            client, cad_file_path, project_id, name=name, scaling=scaling, wait=wait
        )

    # Single file: existing logic
    single_path = cad_file_path[0] if isinstance(cad_file_path, (list, tuple)) else cad_file_path
    return _create_geometry_from_single_file(
        client, single_path, project_id, name=name, scaling=scaling, wait=wait
    )


def _create_geometry_from_single_file(
    client: Client,
    cad_file_path: PathLike | str,
    project_id: str,
    *,
    name: Optional[str] = None,
    scaling: Optional[float] = None,
    wait: bool = False,
) -> geometrypb.Geometry:
    """Create geometry from single file."""

    # TODO(onshape): Document this publicly when we release
    cad_file_path_str = str(cad_file_path)
    if "https://" in cad_file_path_str and ".onshape.com" in cad_file_path_str:
        if name is None:
            # Onshape will fill in an empty string with the document - element name
            name = ""

        web_geometry_reply = client.UploadWebGeometry(
            uploadpb.UploadWebGeometryRequest(
                project_id=project_id,
                url=cad_file_path_str,
            )
        )
        url = ""
        web_geometry_id = web_geometry_reply.web_geometry_id
    else:
        cad_file_meta = util.get_file_metadata(cad_file_path)
        logger.info(
            f"creating geometry in {project_id} by uploading file: {cad_file_meta.name}.{cad_file_meta.ext}, "
            + f"size: {cad_file_meta.size} bytes, sha256: {str(cad_file_meta.sha256_checksum)}, "
            + f"crc32c: {cad_file_meta.crc32c_checksum}"
        )

        finish_res = upload_file(
            client,
            project_id,
            uploadpb.ResourceParams(geometry_params=uploadpb.GeometryParams()),
            cad_file_path,
        )[1]
        url = finish_res.url
        web_geometry_id = ""

        if name is None:
            # if the caller did not provide a name, use the file name
            name = cad_file_meta.name

    return _create_geometry_from_url(client, project_id, url, name, web_geometry_id, scaling, wait)
