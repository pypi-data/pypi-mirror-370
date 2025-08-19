# Copyright 2023-2024 Luminary Cloud, Inc. All Rights Reserved.
import logging
import os
import pathlib
from tempfile import TemporaryDirectory
from os import PathLike

from google.protobuf.json_format import MessageToJson

from .upload import upload_file

from luminarycloud._proto.file import file_pb2 as filepb
from .._client import Client
from luminarycloud._proto.upload import upload_pb2 as uploadpb

from luminarycloud._proto.table import table_pb2 as tablepb

logger = logging.getLogger(__name__)


def upload_table_as_json(
    client: Client,
    project_id: str,
    name: str,
    table: tablepb.RectilinearTable,
) -> str:
    """
    Upload a rectilinear table message as json.

    Parameters
    ----------
    client: Client
        A LuminaryCloud Client (see client.py)
    project_id: str
        The ID of the project to upload the table under
    name: str
        Name to use for the uploaded file
    table: RectilinearTable
        The table to upload

    Returns
    -------
    str
        GCS link to uploaded file
    """
    with TemporaryDirectory() as tmpdir:
        json = MessageToJson(table)
        tmp_file_path = os.path.join(tmpdir, name + ".json")

        with open(tmp_file_path, "w") as f:
            f.write(json)

        logger.info("Uploading table.")

        return upload_file(
            client,
            project_id,
            uploadpb.ResourceParams(geometry_params=uploadpb.GeometryParams()),
            pathlib.Path(tmp_file_path),
        )[1].url


def upload_c81_as_json(
    client: Client,
    project_id: str,
    c81: PathLike | str,
) -> str:
    """
    Uploads a c81 table and converts it to RectilinearTable json.

    Parameters
    ----------
    client: Client
        A LuminaryCloud Client (see client.py)
    project_id: str
        The ID of the project to upload the table under
    c81: PathLike or str
        Path to c81 file to upload

    Returns
    -------
    str
        GCS link to converted and uploaded file
    """
    logger.info("Uploading c81.")
    return upload_file(
        client,
        project_id,
        uploadpb.ResourceParams(c81_params=uploadpb.C81Params()),
        pathlib.Path(c81),
    )[1].url
