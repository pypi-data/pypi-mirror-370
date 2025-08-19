# Copyright 2023-2024 Luminary Cloud, Inc. All Rights Reserved.
import io
from collections.abc import Iterable
from typing import Any, Optional

from .._proto.api.v0.luminarycloud.common.common_pb2 import FileMetadata


class FileChunkStream(io.BufferedIOBase):
    """
    File-like object with an underlying iterable of chunks (bytes).

    Implements https://docs.python.org/3/library/io.html#io.BufferedIOBase.
    File metadata can be accessed via the `filename` and `size` attributes.
    """

    def __init__(
        self,
        metadata: FileMetadata,
        chunks: Iterable[bytes],
    ):
        self._chunks = chunks.__iter__()
        self._metadata = metadata
        self._buffer = io.BytesIO()

    @property
    def filename(self) -> str:
        _filename = self._metadata.name
        if self._metadata.ext:
            _filename += "." + self._metadata.ext
        return _filename

    @property
    def size(self) -> int:
        return self._metadata.size

    def _load_next_chunk(self) -> None:
        next_chunk = next(self._chunks)
        self._buffer = io.BytesIO(next_chunk)

    def read1(self, size: Optional[int] = None) -> Any:  # -> "bytes-like"
        if size is None:
            size = -1
        bytes_read = self._buffer.read(size)
        if len(bytes_read) > 0:
            return bytes_read
        try:
            self._load_next_chunk()
            return self._buffer.read(size)
        except StopIteration:
            return b""

    def readinto1(self, b: Any) -> int:  # b: "bytes-like"
        data = self.read1(len(b))
        num_read = len(data)
        b[:num_read] = data
        return num_read

    def readinto(self, b: Any) -> int:  # b: "bytes-like"
        i = 0
        while i < len(b):
            data = self.read1(len(b) - i)
            if len(data) == 0:
                break
            j = i + len(data)
            b[i:j] = data
            i = j
        return i

    def read(self, size: Optional[int] = None) -> Any:  # -> "bytes-like"
        if size is None:
            size = -1
        if size < 0:
            b = bytearray()
            while True:
                chunk = self.read1()
                if len(chunk) == 0:
                    return b
                b.extend(chunk)
        else:
            b = bytearray(size)
            self.readinto(b)
            return b
