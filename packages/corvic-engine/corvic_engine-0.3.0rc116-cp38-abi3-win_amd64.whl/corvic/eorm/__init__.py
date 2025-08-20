"""Engine Object-Relational Mappings."""

from __future__ import annotations

from datetime import datetime
from typing import TypeAlias

import sqlalchemy as sa
from sqlalchemy import orm as sa_orm

from corvic import orm
from corvic.orm.func import time_offset
from corvic_generated.orm.v1 import (
    common_pb2,
    data_connector_pb2,
    feature_view_pb2,
    pipeline_pb2,
    space_pb2,
    table_pb2,
)
from corvic_generated.status.v1 import event_pb2

OrgID: TypeAlias = orm.OrgID


class RoomID(orm.BaseIDFromInt):
    """A unique identifier for a room."""


class ResourceID(orm.BaseIDFromInt):
    """A unique identifier for a resource."""


class SourceID(orm.BaseIDFromInt):
    """A unique identifier for a source."""


class PipelineID(orm.BaseIDFromInt):
    """A unique identifier for a pipeline."""


class FeatureViewID(orm.BaseIDFromInt):
    """A unique identifier for a feature view."""


class FeatureViewSourceID(orm.BaseIDFromInt):
    """A unique identifier for a source in a feature view."""


class SpaceID(orm.BaseIDFromInt):
    """A unique identifier for a space."""


class DataConnectorID(orm.BaseIDFromInt):
    """A unique identifier for an data connector."""


class DataConnectionID(orm.BaseIDFromInt):
    """A unique identifier for a data connection."""


orm.Base.registry.update_type_annotation_map(
    {
        # proto  message column types
        common_pb2.BlobUrlList: orm.ProtoMessageDecorator(common_pb2.BlobUrlList()),
        feature_view_pb2.FeatureViewOutput: orm.ProtoMessageDecorator(
            feature_view_pb2.FeatureViewOutput()
        ),
        common_pb2.AgentMessageMetadata: orm.ProtoMessageDecorator(
            common_pb2.AgentMessageMetadata()
        ),
        space_pb2.SpaceParameters: orm.ProtoMessageDecorator(
            space_pb2.SpaceParameters()
        ),
        table_pb2.TableComputeOp: orm.ProtoMessageDecorator(table_pb2.TableComputeOp()),
        table_pb2.NamedTables: orm.ProtoMessageDecorator(table_pb2.NamedTables()),
        common_pb2.RetrievedEntities: orm.ProtoMessageDecorator(
            common_pb2.RetrievedEntities()
        ),
        pipeline_pb2.PipelineTransformation: orm.ProtoMessageDecorator(
            pipeline_pb2.PipelineTransformation()
        ),
        event_pb2.Event: orm.ProtoMessageDecorator(event_pb2.Event()),
        data_connector_pb2.DataConnectorParameters: orm.ProtoMessageDecorator(
            data_connector_pb2.DataConnectorParameters()
        ),
        # ID types
        RoomID: orm.IntIDDecorator(RoomID()),
        ResourceID: orm.IntIDDecorator(ResourceID()),
        SourceID: orm.IntIDDecorator(SourceID()),
        PipelineID: orm.IntIDDecorator(PipelineID()),
        FeatureViewID: orm.IntIDDecorator(FeatureViewID()),
        FeatureViewSourceID: orm.IntIDDecorator(FeatureViewSourceID()),
        SpaceID: orm.IntIDDecorator(SpaceID()),
        DataConnectorID: orm.IntIDDecorator(DataConnectorID()),
        DataConnectionID: orm.IntIDDecorator(DataConnectionID()),
    }
)


class Room(orm.BelongsToOrgMixin, orm.SoftDeleteMixin, orm.Base, kw_only=True):
    """A Room is a logical collection of Documents."""

    __tablename__ = "room"
    __table_args__ = (orm.live_unique_constraint("name", "org_id"),)

    name: sa_orm.Mapped[str] = sa_orm.mapped_column(sa.Text, default=None)
    id: sa_orm.Mapped[RoomID | None] = orm.primary_key_identity_column()

    @property
    def room_key(self):
        return self.name


class BelongsToRoomMixin(sa_orm.MappedAsDataclass):
    room_id: sa_orm.Mapped[RoomID | None] = sa_orm.mapped_column(
        orm.ForeignKey(Room).make(ondelete="CASCADE"),
        nullable=True,
        default=None,
    )


class DataConnector(orm.BelongsToOrgMixin, orm.Base, kw_only=True):
    """data connectors for cloud storage providers."""

    __tablename__ = "data_connector"
    __table_args__ = (sa.UniqueConstraint("name", "org_id"),)

    id: sa_orm.Mapped[DataConnectorID | None] = orm.primary_key_identity_column()
    name: sa_orm.Mapped[str] = sa_orm.mapped_column(sa.Text, nullable=False)
    parameters: sa_orm.Mapped[data_connector_pb2.DataConnectorParameters | None] = (
        sa_orm.mapped_column(default=None)
    )
    base_path: sa_orm.Mapped[str] = sa_orm.mapped_column(sa.Text, nullable=False)
    secret_key: sa_orm.Mapped[str] = sa_orm.mapped_column(sa.Text, nullable=False)
    last_validation_time: sa_orm.Mapped[datetime | None] = sa_orm.mapped_column(
        sa.DateTime(timezone=True),
        server_default=None,
        default=None,
    )
    last_successful_validation: sa_orm.Mapped[datetime | None] = sa_orm.mapped_column(
        sa.DateTime(timezone=True),
        server_default=None,
        default=None,
    )

    @property
    def connector_key(self):
        return self.name


class DefaultObjects(orm.Base, kw_only=True):
    """Holds the identifiers for default objects."""

    __tablename__ = "default_objects"
    default_org: sa_orm.Mapped[OrgID | None] = sa_orm.mapped_column(
        orm.ForeignKey(orm.Org).make(ondelete="CASCADE"),
        nullable=False,
    )
    default_room: sa_orm.Mapped[RoomID | None] = sa_orm.mapped_column(
        orm.ForeignKey(Room).make(ondelete="CASCADE"), nullable=True, default=None
    )
    version: sa_orm.Mapped[int | None] = orm.primary_key_identity_column(
        type_=orm.INT_PK_TYPE
    )


class Source(orm.BelongsToOrgMixin, BelongsToRoomMixin, orm.Base, kw_only=True):
    """A source."""

    __tablename__ = "source"
    __table_args__ = (sa.UniqueConstraint("name", "room_id"),)

    name: sa_orm.Mapped[str] = sa_orm.mapped_column(sa.Text)
    # protobuf describing the operations required to construct a table
    table_op_graph: sa_orm.Mapped[table_pb2.TableComputeOp] = sa_orm.mapped_column()
    id: sa_orm.Mapped[SourceID | None] = orm.primary_key_identity_column()

    source_files: sa_orm.Mapped[common_pb2.BlobUrlList | None] = sa_orm.mapped_column(
        default=None
    )
    pipeline_ref: sa_orm.Mapped[PipelineOutput | None] = sa_orm.relationship(
        init=False, viewonly=True
    )

    @property
    def source_key(self):
        return self.name


class Pipeline(orm.BelongsToOrgMixin, BelongsToRoomMixin, orm.Base, kw_only=True):
    """A resource to source pipeline."""

    __tablename__ = "pipeline"
    __table_args__ = (sa.UniqueConstraint("name", "room_id"),)

    transformation: sa_orm.Mapped[pipeline_pb2.PipelineTransformation] = (
        sa_orm.mapped_column()
    )
    name: sa_orm.Mapped[str] = sa_orm.mapped_column()
    description: sa_orm.Mapped[str | None] = sa_orm.mapped_column()
    id: sa_orm.Mapped[PipelineID | None] = orm.primary_key_identity_column()

    outputs: sa_orm.Mapped[list[PipelineOutput]] = sa_orm.relationship(
        viewonly=True,
        init=False,
        default_factory=list,
    )


# TODO(ayush): deprecated: remove this once we shift to using DataConnection.
class PipelineDataConnection(
    orm.BelongsToOrgMixin, BelongsToRoomMixin, orm.Base, kw_only=True
):
    """Pipeline data connection."""

    __tablename__ = "pipeline_data_connection"

    pipeline_id: sa_orm.Mapped[PipelineID] = orm.primary_key_foreign_column(
        orm.ForeignKey(Pipeline).make(ondelete="CASCADE")
    )
    data_connector_id: sa_orm.Mapped[DataConnectorID] = orm.primary_key_foreign_column(
        orm.ForeignKey(DataConnector).make()
    )
    data_connector: sa_orm.Mapped[DataConnector] = sa_orm.relationship(
        viewonly=True, init=False
    )

    prefix: sa_orm.Mapped[str]
    glob: sa_orm.Mapped[str]
    last_ingestion_time: sa_orm.Mapped[datetime | None] = sa_orm.mapped_column(
        sa.DateTime(timezone=True),
        server_default=None,
        default=None,
    )
    last_successful_ingestion_time: sa_orm.Mapped[datetime | None] = (
        sa_orm.mapped_column(
            sa.DateTime(timezone=True),
            server_default=None,
            default=None,
        )
    )
    interval_seconds: sa_orm.Mapped[int | None] = sa_orm.mapped_column(
        sa.Integer,
        default=None,
    )
    watermark_time: sa_orm.Mapped[datetime | None] = sa_orm.mapped_column(
        sa.DateTime(timezone=True),
        server_default=None,
        default=None,
    )


class DataConnection(orm.BelongsToOrgMixin, BelongsToRoomMixin, orm.Base, kw_only=True):
    """Data Connection for Pipeline."""

    __tablename__ = "data_connection"
    __table_args__ = (sa.UniqueConstraint("pipeline_id", "data_connector_id"),)

    id: sa_orm.Mapped[DataConnectionID | None] = orm.primary_key_identity_column()
    pipeline_id: sa_orm.Mapped[PipelineID] = sa_orm.mapped_column(
        orm.ForeignKey(Pipeline).make(ondelete="CASCADE"),
        nullable=False,
    )
    data_connector_id: sa_orm.Mapped[DataConnectorID] = sa_orm.mapped_column(
        orm.ForeignKey(DataConnector).make(),
    )
    data_connector: sa_orm.Mapped[DataConnector] = sa_orm.relationship(
        viewonly=True, init=False
    )

    prefix: sa_orm.Mapped[str]
    glob: sa_orm.Mapped[str]
    last_ingestion_time: sa_orm.Mapped[datetime | None] = sa_orm.mapped_column(
        sa.DateTime(timezone=True),
        server_default=None,
        default=None,
    )
    last_successful_ingestion_time: sa_orm.Mapped[datetime | None] = (
        sa_orm.mapped_column(
            sa.DateTime(timezone=True),
            server_default=None,
            default=None,
        )
    )
    interval_seconds: sa_orm.Mapped[int | None] = sa_orm.mapped_column(
        sa.Integer,
        default=None,
    )
    watermark_time: sa_orm.Mapped[datetime | None] = sa_orm.mapped_column(
        sa.DateTime(timezone=True),
        server_default=None,
        default=None,
    )


class Resource(orm.BelongsToOrgMixin, BelongsToRoomMixin, orm.Base, kw_only=True):
    """A Resource is a reference to some durably stored file.

    E.g., a document could be a PDF file, an image, or a text transcript of a
    conversation
    """

    __tablename__ = "resource"

    name: sa_orm.Mapped[str] = sa_orm.mapped_column(sa.Text)
    mime_type: sa_orm.Mapped[str] = sa_orm.mapped_column(sa.Text)
    url: sa_orm.Mapped[str] = sa_orm.mapped_column(sa.Text)
    md5: sa_orm.Mapped[str] = sa_orm.mapped_column(sa.CHAR(32), nullable=True)
    size: sa_orm.Mapped[int] = sa_orm.mapped_column(nullable=True)
    original_path: sa_orm.Mapped[str] = sa_orm.mapped_column(nullable=True)
    description: sa_orm.Mapped[str] = sa_orm.mapped_column(nullable=True)
    etag: sa_orm.Mapped[str | None] = sa_orm.mapped_column(
        sa.Text, nullable=True, default=None
    )
    original_modified_at_time: sa_orm.Mapped[datetime | None] = sa_orm.mapped_column(
        sa.DateTime(timezone=True),
        server_default=None,
        default=None,
    )
    data_connection_id: sa_orm.Mapped[DataConnectionID | None] = sa_orm.mapped_column(
        orm.ForeignKey(DataConnection).make(ondelete="SET NULL"),
        nullable=True,
        default=None,
    )
    id: sa_orm.Mapped[ResourceID | None] = orm.primary_key_identity_column()
    latest_event: sa_orm.Mapped[event_pb2.Event | None] = sa_orm.mapped_column(
        default=None, nullable=True
    )
    is_terminal: sa_orm.Mapped[bool | None] = sa_orm.mapped_column(
        default=None, nullable=True
    )
    pipeline_ref: sa_orm.Mapped[PipelineInput | None] = sa_orm.relationship(
        init=False, viewonly=True
    )


class PipelineInput(orm.BelongsToOrgMixin, BelongsToRoomMixin, orm.Base, kw_only=True):
    """Pipeline input resources."""

    __tablename__ = "pipeline_input"
    __table_args__ = (sa.UniqueConstraint("name", "pipeline_id"),)

    resource: sa_orm.Mapped[Resource] = sa_orm.relationship(viewonly=True, init=False)
    name: sa_orm.Mapped[str]
    """A name the pipeline uses to refer to this input."""

    pipeline_id: sa_orm.Mapped[PipelineID] = orm.primary_key_foreign_column(
        orm.ForeignKey(Pipeline).make(ondelete="CASCADE")
    )
    resource_id: sa_orm.Mapped[ResourceID] = orm.primary_key_foreign_column(
        orm.ForeignKey(Resource).make(ondelete="CASCADE")
    )


class PipelineOutput(orm.BelongsToOrgMixin, BelongsToRoomMixin, orm.Base, kw_only=True):
    """Objects for tracking pipeline output sources."""

    __tablename__ = "pipeline_output"
    __table_args__ = (sa.UniqueConstraint("name", "pipeline_id"),)

    source: sa_orm.Mapped[Source] = sa_orm.relationship(viewonly=True, init=False)
    name: sa_orm.Mapped[str]
    """A name the pipeline uses to refer to this output."""

    pipeline_id: sa_orm.Mapped[PipelineID] = orm.primary_key_foreign_column(
        orm.ForeignKey(Pipeline).make(ondelete="CASCADE")
    )
    source_id: sa_orm.Mapped[SourceID] = orm.primary_key_foreign_column(
        orm.ForeignKey(Source).make(ondelete="CASCADE")
    )


class FeatureView(
    orm.SoftDeleteMixin,
    orm.BelongsToOrgMixin,
    BelongsToRoomMixin,
    orm.Base,
    kw_only=True,
):
    """A FeatureView is a logical collection of sources used by various spaces."""

    __tablename__ = "feature_view"
    __table_args__ = (orm.live_unique_constraint("name", "room_id"),)

    id: sa_orm.Mapped[FeatureViewID | None] = orm.primary_key_identity_column()
    name: sa_orm.Mapped[str] = sa_orm.mapped_column(sa.Text, default=None)
    description: sa_orm.Mapped[str] = sa_orm.mapped_column(sa.Text, default="")

    feature_view_output: sa_orm.Mapped[feature_view_pb2.FeatureViewOutput | None] = (
        sa_orm.mapped_column(default_factory=feature_view_pb2.FeatureViewOutput)
    )

    @property
    def feature_view_key(self):
        return self.name

    feature_view_sources: sa_orm.Mapped[list[FeatureViewSource]] = sa_orm.relationship(
        viewonly=True,
        init=False,
        default_factory=list,
    )


class FeatureViewSource(
    orm.BelongsToOrgMixin, BelongsToRoomMixin, orm.Base, kw_only=True
):
    """A source inside of a feature view."""

    __tablename__ = "feature_view_source"

    table_op_graph: sa_orm.Mapped[table_pb2.TableComputeOp] = sa_orm.mapped_column()
    feature_view_id: sa_orm.Mapped[FeatureViewID] = sa_orm.mapped_column(
        orm.ForeignKey(FeatureView).make(ondelete="CASCADE"),
        nullable=False,
    )
    id: sa_orm.Mapped[FeatureViewSourceID | None] = orm.primary_key_identity_column()
    drop_disconnected: sa_orm.Mapped[bool] = sa_orm.mapped_column(default=False)
    # this should be legal but pyright complains that it makes Source depend
    # on itself
    source_id: sa_orm.Mapped[SourceID] = sa_orm.mapped_column(
        orm.ForeignKey(Source).make(ondelete="CASCADE"),
        nullable=False,
        default=None,
    )
    source: sa_orm.Mapped[Source] = sa_orm.relationship(
        init=True, viewonly=True, default=None
    )


class Space(orm.BelongsToOrgMixin, BelongsToRoomMixin, orm.Base, kw_only=True):
    """A space is a named evaluation of space parameters."""

    __tablename__ = "space"
    __table_args__ = (sa.UniqueConstraint("name", "room_id"),)

    id: sa_orm.Mapped[SpaceID | None] = orm.primary_key_identity_column()
    name: sa_orm.Mapped[str] = sa_orm.mapped_column(sa.Text, default=None)
    description: sa_orm.Mapped[str] = sa_orm.mapped_column(sa.Text, default="")

    feature_view_id: sa_orm.Mapped[FeatureViewID] = sa_orm.mapped_column(
        orm.ForeignKey(FeatureView).make(ondelete="CASCADE"),
        nullable=False,
        default=None,
    )
    parameters: sa_orm.Mapped[space_pb2.SpaceParameters | None] = sa_orm.mapped_column(
        default=None
    )
    auto_sync: sa_orm.Mapped[bool | None] = sa_orm.mapped_column(default=None)
    feature_view: sa_orm.Mapped[FeatureView] = sa_orm.relationship(
        init=False,
        default=None,
        viewonly=True,
    )

    @property
    def space_key(self):
        return self.name


ID = (
    orm.ID
    | DataConnectionID
    | DataConnectorID
    | FeatureViewID
    | FeatureViewSourceID
    | PipelineID
    | ResourceID
    | RoomID
    | SourceID
    | SpaceID
)

# These are part of the public interface, exposing them here so that
# users don't have to import orm anytime they import eorm
Base: TypeAlias = orm.Base
Org: TypeAlias = orm.Org
Session: TypeAlias = orm.Session

InvalidORMIdentifierError: TypeAlias = orm.InvalidORMIdentifierError
RequestedObjectsForNobodyError: TypeAlias = orm.RequestedObjectsForNobodyError

__all__ = [
    "Base",
    "DefaultObjects",
    "DataConnection",
    "DataConnectionID",
    "DataConnector",
    "DataConnectorID",
    "FeatureView",
    "FeatureViewID",
    "FeatureViewSource",
    "FeatureViewSourceID",
    "ID",
    "InvalidORMIdentifierError",
    "OrgID",
    "PipelineID",
    "PipelineInput",
    "PipelineOutput",
    "RequestedObjectsForNobodyError",
    "Resource",
    "ResourceID",
    "Room",
    "RoomID",
    "Session",
    "Source",
    "SourceID",
    "Space",
    "SpaceID",
    "time_offset",
]
