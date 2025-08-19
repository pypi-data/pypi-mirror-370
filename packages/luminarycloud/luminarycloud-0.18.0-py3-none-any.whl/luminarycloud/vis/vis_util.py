# Copyright 2023-2024 Luminary Cloud, Inc. All Rights Reserved.
import io
import requests
import string, random
import luminarycloud._proto.api.v0.luminarycloud.common.common_pb2 as common_pb2
from ..enum.vis_enums import RenderStatusType, VisQuantity
from .._proto.api.v0.luminarycloud.vis import vis_pb2
from .._client import get_default_client


def generate_id(prefix: str) -> str:
    return prefix + "".join(random.choices(string.ascii_lowercase, k=24))


class _InternalToken:
    """Marker class to control instantiation access for vis outputs."""

    pass


def _download_file(file: common_pb2.File) -> "io.BytesIO":
    buffer = io.BytesIO()
    if file.signed_url:
        response = requests.get(file.signed_url, stream=True)
        response.raise_for_status()
        for chunk in response.iter_content(chunk_size=8192):
            buffer.write(chunk)
    elif file.full_contents:
        buffer.write(file.full_contents)
    else:
        raise Exception("file respose contains no data.")
    # Reset buffer position to the beginning for reading
    buffer.seek(0)
    return buffer


def _get_status(project_id: str, extract_id: str) -> RenderStatusType:
    """
    Get a previously created set of render outputs by project and extract id. This
    can be used by both extracts and images since the status type is just an alias.

    .. warning:: This feature is experimental and may change or be removed in the future.

    Parameters
    ----------
    project_id : str
        The project id to of the extract.
    extract_id: str
        The id to of the extract.

    """
    req = vis_pb2.GetExtractRequest()
    req.extract_id = extract_id
    req.project_id = project_id
    res: vis_pb2.GetExtractResponse = get_default_client().GetExtract(req)
    return RenderStatusType(res.extract.status)
