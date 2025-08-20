"""Corvic system protocols for interacting with storage."""

from __future__ import annotations

import contextlib
import uuid
from collections.abc import Iterator
from typing import Any, BinaryIO, Final, Literal, Protocol

from corvic import eorm
from corvic.result import Error


class DataMisplacedError(Error):
    """Raised when assumptions about data's storage location are violated."""


class BlobClient(Protocol):
    """A Client is the front door for blob store resources."""

    def blob_from_url(self, url: str) -> Blob: ...

    def bucket(self, name: str) -> Bucket: ...


class Blob(Protocol):
    """A Blob is a blob store object that may or may not exist.

    Interface is a subset of google.cloud.storage.Blob's interface
    """

    @property
    def name(self) -> str: ...

    @property
    def physical_name(self) -> str:
        """The name of the blob as stored for cases where it differs from the name."""
        ...

    @property
    def bucket(self) -> Bucket: ...

    @property
    def size(self) -> int | None: ...

    @property
    def md5_hash(self) -> str | None: ...

    @property
    def metadata(self) -> dict[str, Any]: ...

    @metadata.setter
    def metadata(self, value: dict[str, Any]) -> None: ...

    @property
    def content_type(self) -> str: ...

    @content_type.setter
    def content_type(self, value: str) -> None: ...

    def patch(self) -> None: ...

    def reload(self) -> None: ...

    def exists(self) -> bool: ...

    def create_resumable_upload_session(
        self, content_type: str, origin: str | None = None, size: int | None = None
    ) -> str: ...

    @property
    def url(self) -> str: ...

    @contextlib.contextmanager
    def open(self, mode: Literal["rb", "wb"], **kwargs: Any) -> Iterator[BinaryIO]: ...

    def delete(self) -> None: ...

    def upload_from_string(
        self, data: bytes | str, content_type: str = "text/plain"
    ) -> None: ...

    async def generate_signed_url(self, expiration: int) -> str: ...


class Bucket(Protocol):
    """A Bucket is a blob store container for objects.

    Interface is a subset of google.cloud.storage.Bucket's interface.
    """

    @property
    def name(self) -> str: ...

    def blob(self, name: str) -> Blob: ...

    def exists(self) -> bool: ...

    def create(self) -> None: ...

    def list_blobs(self, prefix: str | None = None) -> Iterator[Blob]: ...


class StorageManager:
    """Manages the names of blobs that corvic stores."""

    _blob_client: BlobClient
    _bucket_name: str

    unstructured_prefix: Final[str]
    tabular_prefix: Final[str]
    vector_prefix: Final[str]
    bucket: Final[Bucket]

    def __init__(
        self,
        blob_client: BlobClient,
        *,
        bucket_name: str,
        unstructured_prefix: str,
        tabular_prefix: str,
        vector_prefix: str,
    ):
        self._blob_client = blob_client
        self._bucket_name = bucket_name

        if unstructured_prefix.endswith("/") or tabular_prefix.endswith("/"):
            raise ValueError("prefix should not end with a path separator (/)")

        self.unstructured_prefix = unstructured_prefix
        self.tabular_prefix = tabular_prefix
        self.vector_prefix = vector_prefix

        self.bucket = self._blob_client.bucket(self._bucket_name)

    @staticmethod
    def _render_room_id(room_id: eorm.RoomID) -> str:
        return f"{int(str(room_id)):016}"

    def blob_from_url(self, url: str):
        return self._blob_client.blob_from_url(url)

    def make_tabular_blob(
        self, room_id: eorm.RoomID, suffix: str | None = None
    ) -> Blob:
        if suffix:
            name = f"{self._render_room_id(room_id)}/{suffix}"
        else:
            name = f"{self._render_room_id(room_id)}/{uuid.uuid4()}"
        return self.bucket.blob(f"{self.tabular_prefix}/{name}")

    def make_unstructured_blob(
        self, room_id: eorm.RoomID, suffix: str | None = None
    ) -> Blob:
        if suffix:
            name = f"{self._render_room_id(room_id)}/{suffix}"
        else:
            name = f"{self._render_room_id(room_id)}/{uuid.uuid4()}"
        return self.bucket.blob(f"{self.unstructured_prefix}/{name}")

    def make_vector_blob(self, room_id: eorm.RoomID, suffix: str | None = None) -> Blob:
        if suffix:
            name = f"{self._render_room_id(room_id)}/{suffix}"
        else:
            name = f"{self._render_room_id(room_id)}/{uuid.uuid4()}"
        return self.bucket.blob(f"{self.vector_prefix}/{name}")

    def get_tabular_blob_from_blob_name(self, blob_name: str) -> Blob:
        return self.bucket.blob(f"{self.tabular_prefix}/{blob_name}")

    def get_unstructured_blob_from_blob_name(self, blob_name: str) -> Blob:
        return self.bucket.blob(f"{self.unstructured_prefix}/{blob_name}")

    def get_vector_blob_from_blob_name(self, blob_name: str) -> Blob:
        return self.bucket.blob(f"{self.vector_prefix}/{blob_name}")

    def tabular_prefix_for_room_id(self, room_id: eorm.RoomID) -> str:
        return f"{self.tabular_prefix}/{self._render_room_id(room_id)}"

    def unstructured_prefix_for_room_id(self, room_id: eorm.RoomID) -> str:
        return f"{self.unstructured_prefix}/{self._render_room_id(room_id)}"

    def vector_prefix_for_room_id(self, room_id: eorm.RoomID) -> str:
        return f"{self.vector_prefix}/{self._render_room_id(room_id)}"
