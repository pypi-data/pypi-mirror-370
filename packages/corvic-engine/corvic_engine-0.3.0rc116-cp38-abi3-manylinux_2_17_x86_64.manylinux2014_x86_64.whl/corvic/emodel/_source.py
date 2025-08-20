"""Sources."""

from __future__ import annotations

import copy
import datetime
import functools
from collections.abc import Iterable, Mapping, Sequence
from typing import Self, TypeAlias

import polars as pl
import sqlalchemy as sa
import sqlalchemy.orm as sa_orm
from sqlalchemy.orm.interfaces import LoaderOption

from corvic import eorm, op_graph, system
from corvic.emodel._base_model import StandardModel
from corvic.emodel._proto_orm_convert import (
    source_delete_orms,
    source_orm_to_proto,
    source_proto_to_orm,
)
from corvic.emodel._resource import Resource, ResourceID
from corvic.result import InvalidArgumentError, NotFoundError, Ok
from corvic.table import Table
from corvic_generated.model.v1alpha import models_pb2

SourceID: TypeAlias = eorm.SourceID
RoomID: TypeAlias = eorm.RoomID
PipelineID: TypeAlias = eorm.PipelineID


def foreign_key(
    referenced_source: SourceID | Source, *, is_excluded: bool = False
) -> op_graph.feature_type.ForeignKey:
    match referenced_source:
        case SourceID():
            return op_graph.feature_type.foreign_key(
                referenced_source, is_excluded=is_excluded
            )
        case Source():
            return op_graph.feature_type.foreign_key(
                referenced_source.id, is_excluded=is_excluded
            )


class Source(StandardModel[SourceID, models_pb2.Source, eorm.Source]):
    """Sources describe how resources should be treated.

    Example:
    >>> Source.from_polars(order_data)
    >>>    .as_dimension_table()
    >>> )
    """

    @classmethod
    def orm_class(cls):
        return eorm.Source

    @classmethod
    def id_class(cls):
        return SourceID

    @classmethod
    async def _orm_to_proto(cls, orm_obj: eorm.Source) -> models_pb2.Source:
        return await source_orm_to_proto(orm_obj)

    @classmethod
    async def _proto_to_orm(
        cls, proto_obj: models_pb2.Source, session: eorm.Session
    ) -> Ok[eorm.Source] | InvalidArgumentError:
        return await source_proto_to_orm(proto_obj, session)

    @classmethod
    async def delete_by_ids(
        cls, ids: Sequence[SourceID], session: eorm.Session
    ) -> Ok[None] | InvalidArgumentError:
        return await source_delete_orms(ids, session)

    @classmethod
    async def from_id(
        cls,
        *,
        source_id: SourceID,
        session: eorm.Session | None = None,
        client: system.Client,
    ) -> Ok[Source] | NotFoundError:
        return (
            await cls.load_proto_for(
                obj_id=source_id,
                client=client,
                existing_session=session,
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
        proto: models_pb2.Source,
        client: system.Client,
    ) -> Source:
        return cls(
            proto_self=proto,
            client=client,
        )

    @classmethod
    def create(
        cls,
        *,
        name: str,
        room_id: RoomID,
        client: system.Client,
    ) -> Ok[Self] | InvalidArgumentError:
        """Create a new source to be populated later."""
        proto_source = models_pb2.Source(
            name=name,
            room_id=str(room_id),
        )
        return Ok(cls(proto_self=proto_source, client=client))

    @classmethod
    def from_resource(
        cls,
        *,
        resource: Resource,
        name: str | None = None,
        room_id: RoomID | None = None,
        client: system.Client,
    ) -> Ok[Source] | system.DataMisplacedError | InvalidArgumentError:
        return cls.from_non_tabular_resource(
            resource=resource,
            name=name,
            room_id=room_id,
            client=client,
        ).and_then(
            lambda new_source: Table.from_parquet_file(
                new_source.client, resource.url
            ).map(lambda table: new_source.with_table(table))
        )

    @classmethod
    def from_non_tabular_resource(
        cls,
        *,
        resource: Resource,
        name: str | None = None,
        room_id: RoomID | None = None,
        client: system.Client,
    ) -> Ok[Self] | InvalidArgumentError:
        """Construct a source for a resource that requires some preprocessing.

        This flavor populates all of the metadata that comes from the resource
        but does not populate table. Callers are expected to populate table later.
        """
        client = client or resource.client
        room_id = room_id or resource.room_id

        proto_source = models_pb2.Source(
            name=name or resource.name,
            room_id=str(room_id),
        )

        return Ok(cls(proto_self=proto_source, client=client))

    # TODO(Patrick): move this into corvic_test
    @classmethod
    async def from_polars(
        cls,
        *,
        name: str,
        dataframe: pl.DataFrame,
        room_id: RoomID,
        client: system.Client,
    ) -> Source:
        """Create a source from a pl.DataFrame.

        Args:
            name: a unique name for this source
            dataframe: a polars DataFrame
            client: use a particular system.Client instead of the default
            room_id: room to associate this source with. Use the default room if None.
        """
        resource = (
            await Resource.from_polars(
                dataframe=dataframe, client=client, room_id=room_id
            ).commit()
        ).unwrap_or_raise()
        return cls.from_resource(
            resource=resource, name=name, client=client, room_id=room_id
        ).unwrap_or_raise()

    def with_table(self, table: Table) -> Source:
        proto_self = copy.deepcopy(self.proto_self)
        proto_self.table_op_graph.CopyFrom(table.op_graph.to_proto())
        return Source(
            proto_self=proto_self,
            client=self.client,
        )

    def with_property_table(self, props: Table) -> Source:
        proto_self = copy.deepcopy(self.proto_self)
        proto_self.prop_table_op_graph.CopyFrom(props.op_graph.to_proto())
        return Source(
            proto_self=proto_self,
            client=self.client,
        )

    @classmethod
    def orm_load_options(cls) -> list[LoaderOption]:
        return [
            sa_orm.selectinload(eorm.Source.pipeline_ref).selectinload(
                eorm.PipelineOutput.source
            ),
        ]

    @classmethod
    async def list(
        cls,
        *,
        room_id: RoomID | None = None,
        limit: int | None = None,
        resource_id: ResourceID | None = None,
        created_before: datetime.datetime | None = None,
        ids: Iterable[SourceID] | None = None,
        existing_session: eorm.Session | None = None,
        client: system.Client,
    ) -> Ok[list[Source]] | NotFoundError | InvalidArgumentError:
        """List sources that exist in storage."""
        additional_query_transform = None

        if resource_id is not None:
            match await Resource.from_id(
                resource_id=resource_id,
                client=client,
            ):
                case NotFoundError():
                    return NotFoundError("resource not found", resource_id=resource_id)
                case Ok(resource):

                    def resource_filter(query: sa.Select[tuple[eorm.Source]]):
                        return query.where(
                            eorm.Source.id.in_(
                                sa.select(eorm.PipelineOutput.source_id)
                                .join(eorm.Pipeline)
                                .join(eorm.PipelineInput)
                                .where(eorm.PipelineInput.resource_id == resource.id)
                            )
                        )

                    additional_query_transform = resource_filter

        match await cls.list_as_proto(
            client=client,
            limit=limit,
            room_id=room_id,
            created_before=created_before,
            ids=ids,
            additional_query_transform=additional_query_transform,
            existing_session=existing_session,
        ):
            case NotFoundError() | InvalidArgumentError() as err:
                return err
            case Ok(protos):
                return Ok(
                    [
                        cls.from_proto(
                            proto=proto,
                            client=client,
                        )
                        for proto in protos
                    ]
                )

    def with_feature_types(
        self, feature_types: Mapping[str, op_graph.FeatureType]
    ) -> Source:
        """Assign a Feature Type to each column in source.

        Args:
            feature_types: Mapping between column name and feature type

        Example:
        >>> with_feature_types(
        >>>        {
        >>>            "id": corvic.emodel.feature_type.primary_key(),
        >>>            "customer_id": corvic.emodel.feature_type.foreign_key(
        >>>                customer_source.id
        >>>            ),
        >>>        },
        >>>    )
        """
        return self.with_table(self.table.update_feature_types(feature_types))

    @functools.cached_property
    def table(self):
        return Table.from_ops(
            self.client, op_graph.op.from_proto(self.proto_self.table_op_graph)
        )

    @functools.cached_property
    def prop_table(self):
        return Table.from_ops(
            self.client, op_graph.op.from_proto(self.proto_self.prop_table_op_graph)
        )

    @property
    def name(self) -> str:
        return self.proto_self.name

    @property
    def pipeline_id(self) -> PipelineID | None:
        return PipelineID(self.proto_self.pipeline_id) or None
