import abc
import contextlib
import copy
import datetime
import functools
from collections.abc import AsyncIterator, Callable, Iterable, Sequence
from typing import Any, Final, Generic, Protocol, Self, TypeVar

import sqlalchemy as sa
import sqlalchemy.orm as sa_orm
import structlog
from google.protobuf import timestamp_pb2
from sqlalchemy.exc import (
    DBAPIError,
    IntegrityError,
)
from sqlalchemy.ext.hybrid import hybrid_property

from corvic import orm, system
from corvic.result import (
    InvalidArgumentError,
    NotFoundError,
    Ok,
    UnavailableError,
)
from corvic.transfer._common_transformations import (
    OrmIdT,
    generate_uncommitted_id_str,
    non_empty_timestamp_to_datetime,
)

_logger = structlog.get_logger()


class OrmModel(Protocol):
    @hybrid_property
    def created_at(self) -> datetime.datetime | None: ...

    @created_at.inplace.expression
    @classmethod
    def _created_at_expression(
        cls,
    ) -> ...: ...


class OrmHasIdModel(OrmModel, Protocol[OrmIdT]):
    id: sa_orm.Mapped[OrmIdT | None]


OrmT = TypeVar("OrmT", bound=OrmModel)
OrmHasIdT = TypeVar("OrmHasIdT", bound=OrmHasIdModel[Any])


class ProtoModel(Protocol):
    created_at: timestamp_pb2.Timestamp


class ProtoHasIdModel(ProtoModel, Protocol):
    id: str


ProtoT = TypeVar("ProtoT", bound=ProtoModel)
ProtoHasIdT = TypeVar("ProtoHasIdT", bound=ProtoHasIdModel)


class HasProtoSelf(Generic[ProtoT], abc.ABC):
    client: Final[system.Client]
    proto_self: Final[ProtoT]

    def __init__(self, *, proto_self: ProtoT, client: system.Client):
        self.proto_self = proto_self
        self.client = client

    @property
    def created_at(self) -> datetime.datetime | None:
        return non_empty_timestamp_to_datetime(self.proto_self.created_at)


class UsesOrmID(Generic[OrmIdT, ProtoHasIdT], HasProtoSelf[ProtoHasIdT]):
    def __init__(self, *, proto_self: ProtoHasIdT, client: system.Client):
        if not proto_self.id:
            proto_self.id = generate_uncommitted_id_str()
        super().__init__(
            proto_self=proto_self,
            client=client,
        )

    @classmethod
    @abc.abstractmethod
    def id_class(cls) -> type[OrmIdT]: ...

    @functools.cached_property
    def id(self) -> OrmIdT:
        return self.id_class().from_str(self.proto_self.id)


class OrmBackedProto(Generic[ProtoT, OrmT], HasProtoSelf[ProtoT]):
    """Base for orm wrappers providing a unified update mechanism."""

    @property
    def created_at(self) -> datetime.datetime | None:
        return non_empty_timestamp_to_datetime(self.proto_self.created_at)

    @classmethod
    @abc.abstractmethod
    def orm_class(cls) -> type[OrmT]: ...

    @classmethod
    @abc.abstractmethod
    async def _orm_to_proto(cls, orm_obj: OrmT) -> ProtoT: ...

    @classmethod
    @abc.abstractmethod
    async def _proto_to_orm(
        cls, proto_obj: ProtoT, session: orm.Session
    ) -> Ok[OrmT] | InvalidArgumentError: ...

    @classmethod
    async def _generate_query_results(
        cls, query: sa.Select[tuple[OrmT]], session: orm.Session
    ) -> AsyncIterator[OrmT]:
        it = await session.stream_scalars(query)
        while True:
            try:
                async for obj in it:
                    yield obj
            except Exception:
                _logger.exception(
                    "omitting model from list: " + "failed to parse database entry",
                )
            else:
                break

    @classmethod
    def orm_load_options(cls) -> list[sa_orm.interfaces.LoaderOption]:
        """Overridable method to pass extra orm specific transformations."""
        return []

    @classmethod
    async def list_as_proto(
        cls,
        *,
        limit: int | None = None,
        created_before: datetime.datetime | None = None,
        additional_query_transform: Callable[
            [sa.Select[tuple[OrmT]]], sa.Select[tuple[OrmT]]
        ]
        | None = None,
        existing_session: orm.Session | None = None,
        client: system.Client,
    ) -> Ok[list[ProtoT]] | NotFoundError | InvalidArgumentError:
        """List sources that exist in storage."""
        orm_class = cls.orm_class()
        async with (
            contextlib.nullcontext(existing_session)
            if existing_session
            else orm.Session(client.sa_engine) as session
        ):
            query = sa.select(orm_class).order_by(sa.desc(orm_class.created_at))
            if limit is not None:
                if limit < 0:
                    return InvalidArgumentError("limit cannot be negative")
                query = query.limit(limit)
            if created_before:
                query = query.filter(orm_class.created_at < created_before)
            if additional_query_transform:
                query = additional_query_transform(query)
            extra_orm_loaders = cls.orm_load_options()
            if extra_orm_loaders:
                query = query.options(*extra_orm_loaders)
            return Ok(
                [
                    await cls._orm_to_proto(val)
                    async for val in cls._generate_query_results(query, session)
                ]
            )

    async def commit(self) -> Ok[Self] | InvalidArgumentError | UnavailableError:
        """Store this object in the database at its id or a newly allocated id.

        This overwrites the entry at id in the database so that future readers will see
        this object. One of `id` or `derived_from_id` cannot be empty or None.
        """
        async with orm.Session(self.client.sa_engine) as session:
            try:
                new_orm_self = (
                    await self._proto_to_orm(self.proto_self, session)
                ).unwrap_or_raise()
                await session.flush()
                await session.refresh(new_orm_self)
                new_proto_self = self.__class__(
                    client=self.client,
                    proto_self=await self._orm_to_proto(new_orm_self),
                )
                await session.commit()
            except DBAPIError as err:
                return orm.dbapi_error_to_result(err)
            return Ok(new_proto_self)

    async def add_to_session(
        self, session: orm.Session
    ) -> Ok[None] | InvalidArgumentError | UnavailableError:
        """Like commit, but just calls session.flush to check for database errors.

        This adds the updated object to a transaction in session. Unlike commit
        this will not return the updated object because some values may not be known
        until the wrapped transaction commits.
        """
        try:
            _ = (await self._proto_to_orm(self.proto_self, session)).unwrap_or_raise()
            await session.flush()
        # TODO(thunt): Possibly separate out DatabaseError into a precondition error
        except DBAPIError as err:
            return orm.dbapi_error_to_result(err)
        return Ok(None)


class HasIdOrmBackedProto(
    Generic[OrmIdT, ProtoHasIdT, OrmHasIdT],
    UsesOrmID[OrmIdT, ProtoHasIdT],
    OrmBackedProto[ProtoHasIdT, OrmHasIdT],
):
    @classmethod
    @abc.abstractmethod
    async def delete_by_ids(
        cls, ids: Sequence[OrmIdT], session: orm.Session
    ) -> Ok[None] | InvalidArgumentError: ...

    @classmethod
    async def load_proto_for(
        cls,
        *,
        obj_id: OrmIdT,
        existing_session: orm.Session | None = None,
        client: system.Client,
        **extra_kwargs: Any,
    ) -> Ok[ProtoHasIdT] | NotFoundError:
        """Create a model object by loading it from the database."""
        async with (
            contextlib.nullcontext(existing_session)
            if existing_session
            else orm.Session(client.sa_engine) as session
        ):
            orm_self = await session.get(
                cls.orm_class(), obj_id, options=cls.orm_load_options(**extra_kwargs)
            )
            if orm_self is None:
                return NotFoundError("object with given id does not exist", id=obj_id)
            proto_self = await cls._orm_to_proto(orm_self, **extra_kwargs)
        return Ok(proto_self)

    async def delete(self) -> Ok[Self] | NotFoundError | InvalidArgumentError:
        async with orm.Session(
            self.client.sa_engine, expire_on_commit=False, autoflush=False
        ) as session:
            try:
                match await self.delete_by_ids([self.id], session):
                    case InvalidArgumentError() as err:
                        return err
                    case Ok(None):
                        pass
                await session.commit()
            except IntegrityError as exc:
                return InvalidArgumentError.from_(exc)

            new_proto_self = copy.copy(self.proto_self)
            new_proto_self.id = ""

            return Ok(
                self.__class__(
                    client=self.client,
                    proto_self=new_proto_self,
                )
            )

    @classmethod
    async def list_as_proto(
        cls,
        *,
        limit: int | None = None,
        created_before: datetime.datetime | None = None,
        ids: Iterable[OrmIdT] | None = None,
        additional_query_transform: Callable[
            [sa.Select[tuple[OrmHasIdT]]], sa.Select[tuple[OrmHasIdT]]
        ]
        | None = None,
        existing_session: orm.Session | None = None,
        client: system.Client,
    ) -> Ok[list[ProtoHasIdT]] | NotFoundError | InvalidArgumentError:
        def query_transform(
            query: sa.Select[tuple[OrmHasIdT]],
        ) -> sa.Select[tuple[OrmHasIdT]]:
            if ids:
                query = query.where(cls.orm_class().id.in_(ids))
            if additional_query_transform:
                query = additional_query_transform(query)
            return query

        return await super().list_as_proto(
            client=client,
            limit=limit,
            created_before=created_before,
            additional_query_transform=query_transform,
            existing_session=existing_session,
        )
