"""Rooms."""

from __future__ import annotations

import copy
from collections.abc import Sequence
from typing import Self, TypeAlias

from corvic import eorm, system
from corvic.emodel._base_model import OrgWideStandardModel
from corvic.emodel._proto_orm_convert import (
    room_delete_orms,
    room_orm_to_proto,
    room_proto_to_orm,
)
from corvic.result import InvalidArgumentError, NotFoundError, Ok
from corvic_generated.model.v1alpha import models_pb2

OrgID: TypeAlias = eorm.OrgID
RoomID: TypeAlias = eorm.RoomID
FeatureViewID: TypeAlias = eorm.FeatureViewID


class Room(OrgWideStandardModel[RoomID, models_pb2.Room, eorm.Room]):
    """Rooms contain conversations and tables."""

    @classmethod
    def orm_class(cls):
        return eorm.Room

    @classmethod
    def id_class(cls):
        return RoomID

    @classmethod
    async def _orm_to_proto(cls, orm_obj: eorm.Room) -> models_pb2.Room:
        return room_orm_to_proto(orm_obj)

    @classmethod
    async def _proto_to_orm(
        cls, proto_obj: models_pb2.Room, session: eorm.Session
    ) -> Ok[eorm.Room] | InvalidArgumentError:
        return await room_proto_to_orm(proto_obj, session)

    @classmethod
    async def delete_by_ids(
        cls, ids: Sequence[RoomID], session: eorm.Session
    ) -> Ok[None] | InvalidArgumentError:
        return await room_delete_orms(ids, session)

    @classmethod
    async def from_id(
        cls,
        *,
        room_id: RoomID,
        session: eorm.Session | None = None,
        client: system.Client,
    ) -> Ok[Room] | NotFoundError | InvalidArgumentError:
        return (
            await cls.load_proto_for(
                obj_id=room_id,
                existing_session=session,
                client=client,
            )
        ).map(
            lambda proto_self: cls.from_proto(
                proto=proto_self,
                client=client,
            )
        )

    @classmethod
    def from_proto(
        cls,
        *,
        proto: models_pb2.Room,
        client: system.Client,
    ) -> Room:
        return cls(proto_self=proto, client=client)

    @classmethod
    def create(
        cls,
        *,
        name: str,
        client: system.Client,
    ):
        return cls(
            client=client,
            proto_self=models_pb2.Room(
                name=name,
            ),
        )

    @classmethod
    async def list(
        cls,
        *,
        client: system.Client,
    ) -> Ok[list[Room]] | InvalidArgumentError | NotFoundError:
        """List rooms that exist in storage."""
        return (await cls.list_as_proto(client=client)).map(
            lambda protos: [
                cls.from_proto(proto=proto, client=client) for proto in protos
            ]
        )

    @property
    def name(self) -> str:
        return self.proto_self.name

    @property
    def room_id(self) -> RoomID:
        return RoomID(self.proto_self.id)

    def with_name(self, name: str) -> Self:
        proto_self = copy.deepcopy(self.proto_self)
        proto_self.name = name
        return self.__class__(
            proto_self=proto_self,
            client=self.client,
        )
