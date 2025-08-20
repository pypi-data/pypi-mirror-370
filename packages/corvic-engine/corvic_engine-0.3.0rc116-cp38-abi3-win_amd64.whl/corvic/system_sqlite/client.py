"""Sqlite backed system client."""

import contextlib
import dataclasses
import logging
import pathlib
import sqlite3
import tempfile
from collections.abc import Iterator
from pathlib import Path
from typing import Protocol, Self, cast

import aiosqlite
import duckdb
import sqlalchemy as sa
from sqlalchemy import event
from sqlalchemy.ext import asyncio as sa_async

import corvic.context
import corvic.eorm
import corvic.system
from corvic.result import NotFoundError
from corvic.system_sqlite.fs_blob_store import FSBlobClient
from corvic.system_sqlite.staging import DuckDBStaging

UNSTRUCTURED_PREFIX = "unstructured_data"
TABULAR_PREFIX = "tabular_data"
VECTOR_PREFIX = "vectors"


@contextlib.contextmanager
def _context_requester_org_id_is(value: str | corvic.eorm.OrgID) -> Iterator[None]:
    old_requester = corvic.context.get_requester()
    new_requester = corvic.context.Requester(org_id=str(value))
    corvic.context.update_context(new_requester=new_requester)
    yield
    corvic.context.update_context(new_requester=old_requester)


@contextlib.contextmanager
def _context_requester_org_is_superuser() -> Iterator[None]:
    with _context_requester_org_id_is(corvic.context.SUPERUSER_ORG_ID):
        yield


@event.listens_for(sa.Engine, "connect")
def set_sqlite_pragma(
    dbapi_connection: sa.AdaptedConnection | sqlite3.Connection | None, _
) -> None:
    """Tell sqlite to respect foreign key constraints.

    By default, sqlite doesn't check foreign keys. It can though if you tell it to.
    Postresql always does
    """
    if isinstance(dbapi_connection, sqlite3.Connection) or (
        dbapi_connection
        and hasattr(dbapi_connection, "driver_connection")
        and isinstance(dbapi_connection.driver_connection, aiosqlite.Connection)
    ):
        cursor = cast(sqlite3.Connection, dbapi_connection).cursor()
        _ = cursor.execute("PRAGMA foreign_keys=ON;")
        cursor.close()


async def _initialize_db_from_empty(engine: sa_async.AsyncEngine):
    """Initialize uninitialized database.

    To setup a real database, use the database migration process. However, the SQL there
    is Postgres-specific. This initialization process is at the ORM level so it will
    work for any compatible backend, assuming no state needs to be migrated.
    """
    with _context_requester_org_is_superuser():
        async with sa_async.AsyncSession(engine) as session:
            new_org = corvic.eorm.Org(id=corvic.eorm.OrgID("default_org"))
            session.add(new_org)

            await session.commit()

            new_org_id = await new_org.awaitable_attrs.id
            new_room = corvic.eorm.Room(name="default_room")
            new_room.org_id = new_org_id
            session.add(new_room)

            await session.commit()

            new_default_entry = corvic.eorm.DefaultObjects(
                default_org=new_org_id,
                default_room=await new_room.awaitable_attrs.id,
            )
            session.add(new_default_entry)

            await session.commit()


async def _get_default_org_id(engine: sa_async.AsyncEngine):
    async with corvic.eorm.Session(engine) as session:
        defaults_row = (
            await session.scalars(
                sa.select(corvic.eorm.DefaultObjects)
                .order_by(corvic.eorm.DefaultObjects.version.desc())
                .limit(1)
            )
        ).one_or_none()
        if not defaults_row:
            raise NotFoundError("defaults table was uninitialized")
        return defaults_row.default_org


class StagingDBMaker(Protocol):
    """Staging DB maker."""

    def __call__(
        self, storage_manager: corvic.system.StorageManager
    ) -> corvic.system.StagingDB: ...


class Client(corvic.system.Client):
    """Client for the sqlite system implementation."""

    def __init__(  # noqa: PLR0913
        self,
        sqlite_file: pathlib.Path,
        *,
        vector_column_names_to_sizes: dict[str, int] | None,
        keep_blob_state_after_delete: bool,
        use_umap_embedding_visualization: bool,
        staging_db_maker: StagingDBMaker | None,
        bucket_name: str | None,
        fs_blob_data_dir_name: str | None,
        text_embedder: corvic.system.TextEmbedder | None,
        image_embedder: corvic.system.ImageEmbedder | None,
    ):
        self._sa_engine = sa_async.create_async_engine(
            f"sqlite+aiosqlite:///{sqlite_file}",
        )
        if keep_blob_state_after_delete:
            self._blob_client = FSBlobClient(
                sqlite_file.parent / (fs_blob_data_dir_name or "corvic_blob_data")
            )
        else:
            self._tempdir = tempfile.TemporaryDirectory()  # cleaned up on client gc
            self._blob_client = FSBlobClient(Path(self._tempdir.name))

        # Choice of default bucket name is arbitrary
        bucket = self._blob_client.bucket(bucket_name or "localhost")
        if not bucket.exists():
            bucket.create()

        self._storage_manager = corvic.system.StorageManager(
            self._blob_client,
            bucket_name=bucket.name,
            unstructured_prefix=UNSTRUCTURED_PREFIX,
            tabular_prefix=TABULAR_PREFIX,
            vector_prefix=VECTOR_PREFIX,
        )
        duck_db_conn = duckdb.connect(":memory:")
        if staging_db_maker:
            self._staging_db = staging_db_maker(self.storage_manager)
        else:
            self._staging_db = DuckDBStaging(
                self._storage_manager,
                duck_db_conn,
                vector_column_names_to_sizes
                or corvic.system.DEFAULT_VECTOR_COLUMN_NAMES_TO_SIZES,
            )
        self._text_embedder = (
            text_embedder if text_embedder else corvic.system.RandomTextEmbedder()
        )
        self._image_embedder = (
            image_embedder if image_embedder else corvic.system.CombinedImageEmbedder()
        )
        self._executor = corvic.system.ValidateFirstExecutor(
            corvic.system.InMemoryExecutor(
                self._staging_db,
                self._storage_manager,
                self._text_embedder,
                self._image_embedder,
                corvic.system.UmapDimensionReducer()
                if use_umap_embedding_visualization
                else corvic.system.TruncateDimensionReducer(),
            )
        )

    @classmethod
    async def make(  # noqa: PLR0913
        cls,
        sqlite_file: pathlib.Path,
        *,
        vector_column_names_to_sizes: dict[str, int] | None = None,
        keep_blob_state_after_delete=False,
        use_umap_embedding_visualization=True,
        staging_db_maker: StagingDBMaker | None = None,
        bucket_name: str | None = None,
        fs_blob_data_dir_name: str | None = None,
        text_embedder: corvic.system.TextEmbedder | None = None,
        image_embedder: corvic.system.ImageEmbedder | None = None,
    ) -> Self:
        logging.getLogger("aiosqlite").setLevel(logging.WARNING)
        sqlite_file_exists = sqlite_file.exists()
        client = cls(
            sqlite_file=sqlite_file,
            vector_column_names_to_sizes=vector_column_names_to_sizes,
            keep_blob_state_after_delete=keep_blob_state_after_delete,
            use_umap_embedding_visualization=use_umap_embedding_visualization,
            staging_db_maker=staging_db_maker,
            bucket_name=bucket_name,
            fs_blob_data_dir_name=fs_blob_data_dir_name,
            text_embedder=text_embedder,
            image_embedder=image_embedder,
        )
        async with client.sa_engine.begin() as conn:
            await conn.run_sync(corvic.eorm.Base.metadata.create_all)
            if not sqlite_file_exists:
                await _initialize_db_from_empty(client.sa_engine)

        # when using the system_sqlite client the caller almost always
        # does not care about org. So set the org preemptively to the default
        # org.
        corvic.context.update_context(
            new_requester=dataclasses.replace(
                corvic.context.get_requester(),
                org_id=str(await _get_default_org_id(client.sa_engine)),
            )
        )
        return client

    @property
    def blob_client(self) -> FSBlobClient:
        return self._blob_client

    @property
    def storage_manager(self) -> corvic.system.StorageManager:
        return self._storage_manager

    @property
    def sa_engine(self) -> sa_async.AsyncEngine:
        return self._sa_engine

    @property
    def staging_db(self) -> corvic.system.StagingDB:
        return self._staging_db

    @property
    def executor(self) -> corvic.system.OpGraphExecutor:
        return self._executor

    @property
    def text_embedder(self) -> corvic.system.TextEmbedder:
        return self._text_embedder

    @property
    def image_embedder(self) -> corvic.system.ImageEmbedder:
        return self._image_embedder
