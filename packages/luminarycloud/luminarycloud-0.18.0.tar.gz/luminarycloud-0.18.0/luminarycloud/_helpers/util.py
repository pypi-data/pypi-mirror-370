# Copyright 2024 Luminary Cloud, Inc. All Rights Reserved.
import base64
import hashlib
import io
import logging
import os
from os import PathLike
from typing import Iterator, Tuple

import google_crc32c as crc32c

from luminarycloud._proto.file import file_pb2 as filepb

logger = logging.getLogger(__name__)

DEFAULT_CHUNK_SIZE_BYTES = 1024 * 1024


def _chunker(
    stream: io.BufferedIOBase,
    chunk_size: int | None = None,
) -> Iterator[Tuple[int, bytes]]:
    """
    Generator which breaks the stream into chunks.

    Parameters
    ----------
    stream: io.BufferedIOBase
        The stream to chunk
    chunk_size: int
        (Optional) the default chunk size is 1MB

    Yields
    ------
    offset: int
    chunk: bytes
    """
    if chunk_size is None:
        chunk_size = DEFAULT_CHUNK_SIZE_BYTES

    offset = 0
    while True:
        chunk = stream.read(chunk_size)
        bytes_read = len(chunk)
        if bytes_read == 0:
            return
        yield offset, chunk
        if bytes_read < chunk_size:
            return
        offset += bytes_read


def digest_sha256(
    path: PathLike | str,
    *,
    chunk_size: int | None = None,
) -> bytes:
    """
    Computes the sha256 digest of the file at the given path.

    Uses a buffer to avoid loading the entire file into memory.

    Parameters
    ----------
    path: PathLike or str
        The absolute or relative file path
    chunk_size : int
        (Optional) the default is 1MB

    Returns
    -------
    digest: bytes
    """
    with open(path, "rb") as fp:
        m = hashlib.sha256()
        for _, chunk in _chunker(fp, chunk_size):
            m.update(chunk)
    return m.digest()


def digest_crc32c(
    path: PathLike | str,
    *,
    chunk_size: int | None = None,
) -> bytes:
    """
    Computes the crc32c digest of the file at the given path and returns it as
    base64 encoded bytes. This is intended to be used when with the file.proto's
    FileMetadata.

    Uses a buffer to avoid loading the entire file into memory.

    Parameters
    ----------
    path: PathLike or str
        The absolute or relative file path
    chunk_size : int
        (Optional) the default is 1MB

    Returns
    -------
    string
    """
    with open(path, "rb") as fp:
        checksum = crc32c.Checksum()
        for _, chunk in _chunker(fp, chunk_size):
            checksum.update(chunk)
    return base64.b64encode(checksum.digest())


def get_file_metadata(
    file_path: PathLike | str,
) -> filepb.FileMetadata:

    if not os.path.exists(file_path):
        msg = f"File not found: {file_path}"
        logger.error(msg)
        raise FileNotFoundError(msg)

    basename: str = os.path.basename(file_path)
    fparts = basename.split(".", maxsplit=1)
    if len(fparts) < 2:
        msg = f"Filename is missing extension: {basename}"
        logger.error(msg)
        raise ValueError(msg)

    file_name, file_ext = fparts

    return filepb.FileMetadata(
        name=file_name,
        ext=file_ext,
        size=os.path.getsize(file_path),
        sha256_checksum=digest_sha256(file_path),
        crc32c_checksum=digest_crc32c(file_path).decode(),
    )
