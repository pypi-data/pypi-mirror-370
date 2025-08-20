import datetime
from collections.abc import Callable, Iterable
from typing import Generic

import sqlalchemy as sa

from corvic import eorm, system, transfer
from corvic.emodel._proto_orm_convert import (
    OrmBelongsToRoomT,
    OrmHasIdBelongsToOrgT,
    OrmHasIdBelongsToRoomT,
    ProtoBelongsToOrgT,
    ProtoBelongsToRoomT,
    ProtoHasIdBelongsToOrgT,
    ProtoHasIdBelongsToRoomT,
)
from corvic.result import (
    InvalidArgumentError,
    NotFoundError,
    Ok,
)


def _make_room_filter_query_transfrom(
    room_id: eorm.RoomID | None,
    existing_transform: Callable[
        [sa.Select[tuple[transfer.OrmT]]], sa.Select[tuple[transfer.OrmT]]
    ]
    | None,
):
    def query_transform(
        query: sa.Select[tuple[transfer.OrmT]],
    ) -> sa.Select[tuple[transfer.OrmT]]:
        if room_id:
            query = query.filter_by(room_id=room_id)
        if existing_transform:
            query = existing_transform(query)
        return query

    if room_id:
        return query_transform
    return existing_transform


class OrmBackedModel(
    Generic[transfer.ProtoT, transfer.OrmT],
    transfer.OrmBackedProto[transfer.ProtoT, transfer.OrmT],
):
    @classmethod
    async def list_as_proto(
        cls,
        *,
        limit: int | None = None,
        room_id: eorm.RoomID | None = None,
        created_before: datetime.datetime | None = None,
        additional_query_transform: Callable[
            [sa.Select[tuple[transfer.OrmT]]], sa.Select[tuple[transfer.OrmT]]
        ]
        | None = None,
        existing_session: eorm.Session | None = None,
        client: system.Client,
    ) -> Ok[list[transfer.ProtoT]] | NotFoundError | InvalidArgumentError:
        return await super().list_as_proto(
            client=client,
            limit=limit,
            created_before=created_before,
            additional_query_transform=_make_room_filter_query_transfrom(
                room_id, additional_query_transform
            ),
            existing_session=existing_session,
        )


class HasIdOrmBackedModel(
    Generic[transfer.OrmIdT, transfer.ProtoHasIdT, transfer.OrmHasIdT],
    transfer.HasIdOrmBackedProto[
        transfer.OrmIdT, transfer.ProtoHasIdT, transfer.OrmHasIdT
    ],
):
    @classmethod
    async def list_as_proto(
        cls,
        *,
        limit: int | None = None,
        room_id: eorm.RoomID | None = None,
        created_before: datetime.datetime | None = None,
        ids: Iterable[transfer.OrmIdT] | None = None,
        additional_query_transform: Callable[
            [sa.Select[tuple[transfer.OrmHasIdT]]], sa.Select[tuple[transfer.OrmHasIdT]]
        ]
        | None = None,
        existing_session: eorm.Session | None = None,
        client: system.Client,
    ) -> Ok[list[transfer.ProtoHasIdT]] | NotFoundError | InvalidArgumentError:
        return await super().list_as_proto(
            client=client,
            limit=limit,
            created_before=created_before,
            ids=ids,
            additional_query_transform=_make_room_filter_query_transfrom(
                room_id, additional_query_transform
            ),
            existing_session=existing_session,
        )


class BelongsToOrgModelMixin(
    Generic[ProtoBelongsToOrgT], transfer.HasProtoSelf[ProtoBelongsToOrgT]
):
    """Base for orm wrappers with org mixin providing a unified update mechanism."""

    @property
    def org_id(self) -> eorm.OrgID:
        return eorm.OrgID().from_str(self.proto_self.org_id)


class BelongsToRoomModelMixin(
    Generic[ProtoBelongsToRoomT], transfer.HasProtoSelf[ProtoBelongsToRoomT]
):
    """Base for orm wrappers with room mixin providing a unified update mechanism."""

    @property
    def room_id(self) -> eorm.RoomID:
        return eorm.RoomID().from_str(self.proto_self.room_id)


class OrgWideStandardModel(
    Generic[transfer.OrmIdT, ProtoHasIdBelongsToOrgT, OrmHasIdBelongsToOrgT],
    BelongsToOrgModelMixin[ProtoHasIdBelongsToOrgT],
    HasIdOrmBackedModel[
        transfer.OrmIdT, ProtoHasIdBelongsToOrgT, OrmHasIdBelongsToOrgT
    ],
):
    """Base for most models, though the lion's share are StandardModels.

    Most models are typically referenced by an ID, and belong to an org.
    """


class StandardModel(
    Generic[transfer.OrmIdT, ProtoHasIdBelongsToRoomT, OrmHasIdBelongsToRoomT],
    BelongsToRoomModelMixin[ProtoHasIdBelongsToRoomT],
    OrgWideStandardModel[
        transfer.OrmIdT, ProtoHasIdBelongsToRoomT, OrmHasIdBelongsToRoomT
    ],
):
    """Base for most models.

    Like OrgWideStandardModel, but more specific. The majority of models belong to a
    room.
    """


class NoIdModel(
    Generic[ProtoBelongsToRoomT, OrmBelongsToRoomT],
    BelongsToRoomModelMixin[ProtoBelongsToRoomT],
    BelongsToOrgModelMixin[ProtoBelongsToRoomT],
    transfer.OrmBackedProto[ProtoBelongsToRoomT, OrmBelongsToRoomT],
):
    """Like StandardModel, but for objects that are not usually referenced by ID."""
