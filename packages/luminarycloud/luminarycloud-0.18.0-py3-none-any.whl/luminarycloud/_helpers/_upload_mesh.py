# Copyright 2023-2024 Luminary Cloud, Inc. All Rights Reserved.
from email.message import Message
from email.parser import HeaderParser
import io
import logging
import os
import requests
import pathlib
from tempfile import TemporaryDirectory
from typing import cast, Optional, Union
from urllib.parse import urlparse

from luminarycloud._helpers import util
from luminarycloud._helpers.util import _chunker
from .upload import gcs_resumable_upload

from ..enum import MeshType
from luminarycloud._proto.file import file_pb2 as filepb
from .._proto.api.v0.luminarycloud.mesh.mesh_pb2 import Mesh, GetMeshRequest
from .._client import Client
from luminarycloud._proto.upload import upload_pb2 as uploadpb

logger = logging.getLogger(__name__)

_EXTENSION_TO_MESH_TYPE = {
    ".cgns": MeshType.CGNS,
    ".ansys": MeshType.ANSYS,
    ".lcmesh": MeshType.UNSPECIFIED,
}


def _deduce_mesh_type(path: Union[os.PathLike, str]) -> MeshType:
    """
    Deduce mesh type for the file at the given path.

    Currently, only uses the file extension to deduce type.

    Parameters
    ----------
    path: PathLike or str
        The relative or absolute file path of the mesh file.

    Returns
    -------
    MeshType
        The deduced mesh file format type. If the type cannot be deduced, returns
        MeshType.UNSPECIFIED.
    """
    _, file_ext = os.path.splitext(path)
    return _EXTENSION_TO_MESH_TYPE.get(file_ext, MeshType.UNSPECIFIED)


def _upload_mesh_from_path(
    client: Client,
    project_id: str,
    filepath: Union[os.PathLike, str],
    size: int,
    sha256_checksum: bytes,
    crc32c_checksum: bytes,
    mesh_type: MeshType,
    *,
    name: Optional[str] = None,
    scaling: Optional[float] = None,
    do_not_read_zones_openfoam: Optional[bool] = None,
) -> Mesh:
    """
    Upload mesh from a binary stream.

    Parameters
    ----------
    client: Client
        A LuminaryCloud Client (see client.py)
    binary_stream: io.BufferedIOBase
        A fresh read stream of the mesh file to upload
    project_id: str
        The ID of the project to upload the mesh under
    filepath: PathLike or str
        The relative or absolute file path of the mesh file. Must include the
        appropriate filename extension.
    size: int
        The size of the stream to be read
    sha256checksum: bytes
        The SHA256 digest of the mesh file to upload
    crc32c_checksum: bytes
        The CRC32C digest of the mesh file to upload
    mesh_type : MeshType
        The file format of the mesh file.
    name : str, optional
        Name of the mesh resource on Luminary Cloud. Defaults to the
        filename.
    scaling : float, optional
        If set, apply a scaling factor to the mesh.
    do_not_read_zones_openfoam : bool
        (Optional) If true, disables reading cell zones in the polyMesh/cellZones file
        for OpenFOAM meshes. Default false.
    """

    assert size > 0, "stream size must be positive"
    root, file_ext = os.path.splitext(filepath)
    file_name_without_ext = os.path.basename(root)
    file_ext = file_ext.removeprefix(".")
    if len(file_ext) == 0:
        msg = f"File path {filepath} is missing extension."
        logger.error(msg)
        raise ValueError(msg)
    logger.info(f"Uploading mesh with name '{file_name_without_ext}' and extension '{file_ext}'.")

    file_metadata = filepb.FileMetadata(
        name=file_name_without_ext,  # note: this must be the filename without extension
        ext=file_ext,  # note: this must be the extension without the dot
        size=size,
        sha256_checksum=sha256_checksum,
        crc32c_checksum=crc32c_checksum.decode(),
    )
    create_upload_res: uploadpb.CreateUploadReply = client.CreateUpload(
        uploadpb.CreateUploadRequest(
            project_id=project_id,
            file_meta=file_metadata,
            resource_params=uploadpb.ResourceParams(
                mesh_params=uploadpb.MeshParams(
                    mesh_name=name or file_name_without_ext,
                    scaling=scaling if scaling is not None else 1.0,
                    mesh_type=mesh_type.value,
                    do_not_read_zones_openfoam=do_not_read_zones_openfoam or False,
                    # We force disconnect to True here because we are not exposing this parameter.
                    disconnect=True,
                )
            ),
        )
    )
    upload_id = create_upload_res.upload.id
    logger.debug(f"created upload: {upload_id}")

    start_res: uploadpb.StartUploadReply = client.StartUpload(
        uploadpb.StartUploadRequest(upload_id=upload_id, method=uploadpb.METHOD_GCS_RESUMABLE)
    )
    logger.debug(f"started upload")

    gcs_resumable_upload(
        filepath=pathlib.Path(filepath),
        signed_url=start_res.upload.gcs_resumable.signed_url,
        http_headers=start_res.upload.gcs_resumable.http_headers,
    )
    logger.debug(f"successfully uploaded data")

    finish_res: uploadpb.FinishUploadReply = client.FinishUpload(
        uploadpb.FinishUploadRequest(upload_id=upload_id)
    )

    get_mesh_res = client.GetMesh(GetMeshRequest(id=finish_res.mesh_id))
    return get_mesh_res.mesh


def _is_valid_upload_url(path: Union[os.PathLike, str]) -> bool:
    parsed = urlparse(str(path))
    return parsed.scheme in ("http", "https")


def upload_mesh_from_local_file(
    client: Client,
    project_id: str,
    path: Union[os.PathLike, str],
    *,
    name: Optional[str] = None,
    scaling: Optional[float] = None,
    mesh_type: Optional[MeshType] = None,
    do_not_read_zones_openfoam: Optional[bool] = None,
) -> Mesh:
    """
    Upload a mesh from a local file.

    The mesh file format is inferred from the filename extension.
    For supported formats, see: https://docs.luminarycloud.com/en/articles/9275233-upload-a-mesh

    Parameters
    ----------
    client: Client
        A LuminaryCloud Client (see client.py)
    project_id: str
        The ID of the project to upload the mesh under
    path: PathLike or str
        The relative or absolute file path of the mesh file to upload.
    name : str, optional
        Name of the mesh resource on Luminary Cloud. Defaults to the
        filename.
    scaling : float, optional
        If set, apply a scaling factor to the mesh.
    mesh_type : MeshType
        (Optional) The file format of the mesh file.
    do_not_read_zones_openfoam : bool
        (Optional) If true, disables reading cell zones in the polyMesh/cellZones file
        for OpenFOAM meshes. Default false.
    """
    if not os.path.exists(path):
        logger.error("File not found.")
        raise FileNotFoundError

    if mesh_type is None:
        mesh_type = _deduce_mesh_type(path)

    return _upload_mesh_from_path(
        client,
        project_id,
        path,
        os.path.getsize(path),
        util.digest_sha256(path),
        util.digest_crc32c(path),
        mesh_type,
        name=name,
        scaling=scaling,
        do_not_read_zones_openfoam=do_not_read_zones_openfoam,
    )


def upload_mesh_from_url(
    client: Client,
    project_id: str,
    url: str,
    *,
    timeout: int = 5,
    name: Optional[str] = None,
    scaling: Optional[float] = None,
    mesh_type: Optional[MeshType] = None,
    do_not_read_zones_openfoam: Optional[bool] = None,
) -> Mesh:
    """
    Upload a mesh from a URL.

    The mesh file format is inferred from the filename extension.
    For supported formats, see: https://docs.luminarycloud.com/en/articles/9275233-upload-a-mesh

    Parameters
    ----------
    client: Client
        A LuminaryCloud Client (see client.py)
    project_id: str
        The ID of the project to upload the mesh under
    url: str
        The url of the mesh file.
    timeout: int, optional
        Timeout (in seconds) for the download request.
    name : str, optional
        Name of the mesh resource on Luminary Cloud. Defaults to the
        filename.
    scaling : float, optional
        If set, apply a scaling factor to the mesh.
    mesh_type: MeshType, optional
        The file format of the mesh file.
    do_not_read_zones_openfoam : bool, optional
        If true, disables reading cell zones in the polyMesh/cellZones file
        for OpenFOAM meshes. Default false.
    """

    logger.debug("Creating temporary directory.")
    with TemporaryDirectory() as tmpdir:
        logger.debug(f"Created temporary directory: {tmpdir}")
        logger.debug("Initiating download request.")
        with requests.get(url, stream=True, timeout=timeout) as r:
            r = cast(requests.Response, r)
            r.raise_for_status()
            logger.debug("Successfully started streaming download.")
            try:
                header = r.headers["Content-Disposition"]
                msg = Message()
                msg["Content-Disposition"] = header
                value = msg.get_content_disposition()
                params = dict(
                    msg.get_params(header="content-disposition")[1:]
                )  # [1:] skips the main value
                if value != "attachment":
                    raise Exception("Expected header Content-Disposition: attachment")
                filename = params["filename"]
                logger.debug(f"Got filename from Content-Disposition header: {filename}")
            except Exception as e:
                logger.warning("Failed to get filename from headers.", exc_info=e)
                filename = os.path.basename(urlparse(url).path)
                logger.debug(f"Got filename from basename of download URL: {filename}")
            filepath = os.path.join(tmpdir, filename)
            logger.debug(f"Creating file: {filepath}.")
            with open(filepath, "wb") as f:
                logger.debug(f"Writing stream to file: {filepath}")
                for chunk in r.iter_content(chunk_size=util.DEFAULT_CHUNK_SIZE_BYTES):
                    f.write(chunk)
        return upload_mesh_from_local_file(
            client,
            project_id,
            filepath,
            name=name,
            scaling=scaling,
            mesh_type=mesh_type,
            do_not_read_zones_openfoam=do_not_read_zones_openfoam,
        )


def upload_mesh(
    client: Client,
    project_id: str,
    path: Union[os.PathLike, str],
    *,
    name: Optional[str] = None,
    scaling: Optional[float] = None,
    mesh_type: Optional[MeshType] = None,
    do_not_read_zones_openfoam: Optional[bool] = None,
) -> Mesh:
    """
    Upload a mesh from a local file or a URL.

    Parameters
    ----------
    client: Client
        A LuminaryCloud Client (see client.py)
    project_id: str
        The ID of the project to upload the mesh under
    path: PathLike or str
        The URL or file path of the mesh file to upload.
    name : str, optional
        Name of the mesh resource on Luminary Cloud. Defaults to the
        filename.
    scaling : float, optional
        If set, apply a scaling factor to the mesh.
    mesh_type : MeshType, optional
        The file format of the mesh file.
    do_not_read_zones_openfoam : bool, optional
        If true, disables reading cell zones in the polyMesh/cellZones file
        for OpenFOAM meshes. Default false.
    """
    if _is_valid_upload_url(path):
        logger.info(f"Attempting to upload mesh from URL: {path}")
        return upload_mesh_from_url(
            client,
            project_id,
            str(path),
            name=name,
            scaling=scaling,
            mesh_type=mesh_type,
            do_not_read_zones_openfoam=do_not_read_zones_openfoam,
        )
    else:
        logger.info(f"Attempting to upload mesh from local file: {path}")
        return upload_mesh_from_local_file(
            client,
            project_id,
            path,
            name=name,
            scaling=scaling,
            mesh_type=mesh_type,
            do_not_read_zones_openfoam=do_not_read_zones_openfoam,
        )
