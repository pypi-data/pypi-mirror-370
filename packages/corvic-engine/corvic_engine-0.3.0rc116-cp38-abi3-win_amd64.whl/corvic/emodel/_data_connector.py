from __future__ import annotations

import copy
from collections.abc import Iterable, Sequence
from datetime import UTC, datetime
from typing import Literal, Self, TypeAlias

import sqlalchemy as sa
from sqlalchemy import orm as sa_orm
from sqlalchemy.orm.interfaces import LoaderOption

from corvic import eorm, system, transfer
from corvic.emodel._base_model import NoIdModel, OrgWideStandardModel
from corvic.emodel._pipeline import Pipeline
from corvic.emodel._proto_orm_convert import (
    data_connection_delete_orms,
    data_connection_orm_to_proto,
    data_connection_proto_to_orm,
    data_connector_delete_orms,
    data_connector_orm_to_proto,
    data_connector_proto_to_orm,
    pipeline_data_connection_delete_orms,
    pipeline_data_connection_orm_to_proto,
    pipeline_data_connection_proto_to_orm,
)
from corvic.result import InvalidArgumentError, NotFoundError, Ok
from corvic_generated.model.v1alpha import models_pb2
from corvic_generated.orm.v1 import data_connector_pb2

DataConnectorID: TypeAlias = eorm.DataConnectorID
DataConnectionID: TypeAlias = eorm.DataConnectionID
OrgID: TypeAlias = eorm.OrgID


class DataConnector(
    OrgWideStandardModel[DataConnectorID, models_pb2.DataConnector, eorm.DataConnector],
):
    """Data Connector Model."""

    @classmethod
    def orm_class(cls):
        return eorm.DataConnector

    @classmethod
    def id_class(cls):
        return DataConnectorID

    @classmethod
    async def _orm_to_proto(
        cls, orm_obj: eorm.DataConnector
    ) -> models_pb2.DataConnector:
        return data_connector_orm_to_proto(orm_obj)

    @classmethod
    async def _proto_to_orm(
        cls, proto_obj: models_pb2.DataConnector, session: eorm.Session
    ) -> Ok[eorm.DataConnector] | InvalidArgumentError:
        return await data_connector_proto_to_orm(proto_obj, session)

    @classmethod
    async def delete_by_ids(
        cls, ids: Sequence[DataConnectorID], session: eorm.Session
    ) -> Ok[None] | InvalidArgumentError:
        return await data_connector_delete_orms(ids, session)

    @property
    def name(self) -> str:
        return self.proto_self.name

    @property
    def provider(self) -> Literal["s3", "azure-blob", "gcs"] | None:
        match self.proto_self.parameters.WhichOneof("credentials"):
            case "azure_blob_credentials":
                return "azure-blob"
            case "s3_credentials":
                return "s3"
            case "gcs_credentials":
                return "gcs"
            case _:
                return None

    @property
    def parameters(
        self,
    ) -> (
        data_connector_pb2.AzureBlobCredentials
        | data_connector_pb2.S3Credentials
        | data_connector_pb2.GCSCredentials
        | None
    ):
        match self.provider:
            case "azure-blob":
                return self.azure_blob_credentials
            case "s3":
                return self.s3_credentials
            case "gcs":
                return self.gcs_credentials
            case None:
                return None

    @property
    def azure_blob_credentials(
        self,
    ) -> data_connector_pb2.AzureBlobCredentials | None:
        if self.proto_self.parameters.HasField("azure_blob_credentials"):
            return self.proto_self.parameters.azure_blob_credentials
        return None

    @property
    def s3_credentials(
        self,
    ) -> data_connector_pb2.S3Credentials | None:
        if self.proto_self.parameters.HasField("s3_credentials"):
            return self.proto_self.parameters.s3_credentials
        return None

    @property
    def gcs_credentials(
        self,
    ) -> data_connector_pb2.GCSCredentials | None:
        if self.proto_self.parameters.HasField("gcs_credentials"):
            return self.proto_self.parameters.gcs_credentials
        return None

    @property
    def base_path(self) -> str:
        return self.proto_self.base_path

    @property
    def secret_key(self) -> str:
        return self.proto_self.secret_key

    @property
    def last_validation_time(self) -> datetime | None:
        return transfer.non_empty_timestamp_to_datetime(
            self.proto_self.last_validation_time
        )

    @property
    def last_successful_validation(self) -> datetime | None:
        return transfer.non_empty_timestamp_to_datetime(
            self.proto_self.last_successful_validation
        )

    @property
    def is_validated(self) -> bool:
        return (
            self.last_successful_validation is not None
            and self.last_validation_time is not None
            and self.last_successful_validation >= self.last_validation_time
        )

    @classmethod
    def create(
        cls,
        *,
        name: str,
        parameters: data_connector_pb2.DataConnectorParameters,
        base_path: str,
        secret_key: str,
        client: system.Client,
    ):
        return cls(
            proto_self=models_pb2.DataConnector(
                name=name,
                parameters=parameters,
                base_path=base_path,
                secret_key=secret_key,
            ),
            client=client,
        )

    @classmethod
    async def list(
        cls,
        *,
        limit: int | None = None,
        created_before: datetime | None = None,
        ids: Iterable[DataConnectorID] | None = None,
        existing_session: eorm.Session | None = None,
        client: system.Client,
    ) -> Ok[list[Self]] | NotFoundError | InvalidArgumentError:
        """List access models."""
        match await cls.list_as_proto(
            limit=limit,
            created_before=created_before,
            ids=ids,
            existing_session=existing_session,
            client=client,
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

    @classmethod
    def from_proto(
        cls,
        *,
        proto: models_pb2.DataConnector,
        client: system.Client,
    ) -> Self:
        return cls(
            proto_self=proto,
            client=client,
        )

    @classmethod
    async def from_id(
        cls,
        *,
        data_connector_id: DataConnectorID,
        session: eorm.Session | None = None,
        client: system.Client,
    ) -> Ok[Self] | NotFoundError:
        return (
            await cls.load_proto_for(
                obj_id=data_connector_id,
                client=client,
                existing_session=session,
            )
        ).map(
            lambda proto_self: cls.from_proto(
                proto=proto_self,
                client=client,
            )
        )

    def with_name(self, name: str) -> DataConnector:
        proto_self = copy.deepcopy(self.proto_self)
        proto_self.name = name
        return DataConnector(
            proto_self=proto_self,
            client=self.client,
        )

    def with_parameters(
        self, parameters: data_connector_pb2.DataConnectorParameters
    ) -> DataConnector:
        proto_self = copy.deepcopy(self.proto_self)
        proto_self.parameters.CopyFrom(parameters)
        return DataConnector(
            proto_self=proto_self,
            client=self.client,
        )

    def with_base_path(self, base_path: str) -> DataConnector:
        proto_self = copy.deepcopy(self.proto_self)
        proto_self.base_path = base_path
        return DataConnector(
            proto_self=proto_self,
            client=self.client,
        )

    def with_secret_key(self, secret_key: str) -> DataConnector:
        proto_self = copy.deepcopy(self.proto_self)
        proto_self.secret_key = secret_key
        return DataConnector(
            proto_self=proto_self,
            client=self.client,
        )

    def with_last_validation_time(
        self, last_validation_time: datetime
    ) -> DataConnector:
        proto_self = copy.deepcopy(self.proto_self)
        proto_self.last_validation_time.FromDatetime(last_validation_time)
        return DataConnector(
            proto_self=proto_self,
            client=self.client,
        )

    def with_last_successful_validation(
        self, last_successful_validation: datetime
    ) -> DataConnector:
        proto_self = copy.deepcopy(self.proto_self)
        proto_self.last_successful_validation.FromDatetime(last_successful_validation)
        return DataConnector(
            proto_self=proto_self,
            client=self.client,
        )


def _ready_for_ingestion(
    query: sa.Select[tuple[eorm.PipelineDataConnection]]
    | sa.Select[tuple[eorm.DataConnection]],
    orm_class: type[eorm.PipelineDataConnection | eorm.DataConnection],
) -> (
    sa.Select[tuple[eorm.PipelineDataConnection]]
    | sa.Select[tuple[eorm.DataConnection]]
):
    time_now = datetime.now(tz=UTC)
    return (
        query.where(
            orm_class.interval_seconds.is_not(None),
            (orm_class.interval_seconds > 0),
        )
        .where(
            eorm.time_offset(
                orm_class.last_ingestion_time,
                orm_class.interval_seconds,
            )
            < time_now
        )
        .distinct()
        .order_by(orm_class.created_at.desc())
    )


class PipelineDataConnection(
    NoIdModel[models_pb2.PipelineDataConnection, eorm.PipelineDataConnection]
):
    """A connection to a DataConnector object with connection parameters."""

    @classmethod
    def orm_class(cls):
        return eorm.PipelineDataConnection

    @classmethod
    async def _orm_to_proto(
        cls, orm_obj: eorm.PipelineDataConnection
    ) -> models_pb2.PipelineDataConnection:
        return await pipeline_data_connection_orm_to_proto(orm_obj)

    @classmethod
    async def _proto_to_orm(
        cls, proto_obj: models_pb2.PipelineDataConnection, session: eorm.Session
    ) -> Ok[eorm.PipelineDataConnection] | InvalidArgumentError:
        return await pipeline_data_connection_proto_to_orm(proto_obj, session)

    @classmethod
    def orm_load_options(cls) -> list[LoaderOption]:
        return [
            sa_orm.selectinload(eorm.PipelineDataConnection.data_connector),
        ]

    @classmethod
    def create(
        cls,
        *,
        pipeline: Pipeline,
        data_connector: DataConnector,
        prefix: str,
        glob: str,
        interval_seconds: int | None = None,
        client: system.Client,
    ) -> Self:
        proto_self = models_pb2.PipelineDataConnection(
            pipeline_id=str(pipeline.id),
            data_connector=data_connector.proto_self,
            room_id=str(pipeline.room_id),
            org_id=str(pipeline.org_id),
            prefix=prefix,
            glob=glob,
            interval_seconds=interval_seconds,
        )
        return cls(proto_self=proto_self, client=client)

    @classmethod
    async def list(
        cls,
        *,
        pipeline_id: eorm.PipelineID | None = None,
        data_connector_id: eorm.DataConnectorID | None = None,
        ready_for_ingestion: bool = False,
        limit: int | None = None,
        created_before: datetime | None = None,
        existing_session: eorm.Session | None = None,
        client: system.Client,
    ) -> Ok[list[Self]] | NotFoundError | InvalidArgumentError:
        """List access models."""

        def query_transform(query: sa.Select[tuple[eorm.PipelineDataConnection]]):
            if pipeline_id:
                query = query.where(
                    eorm.PipelineDataConnection.pipeline_id == pipeline_id
                )
            if data_connector_id:
                query = query.where(
                    eorm.PipelineDataConnection.data_connector_id == data_connector_id
                )
            if ready_for_ingestion:
                query = _ready_for_ingestion(query, eorm.PipelineDataConnection)  # pyright: ignore[reportAssignmentType]
            return query

        match await cls.list_as_proto(
            client=client,
            limit=limit,
            created_before=created_before,
            existing_session=existing_session,
            additional_query_transform=query_transform,
        ):
            case NotFoundError() | InvalidArgumentError() as err:
                return err
            case Ok(protos):
                return Ok(
                    [cls.from_proto(proto=proto, client=client) for proto in protos]
                )

    @classmethod
    def from_proto(
        cls,
        *,
        proto: models_pb2.PipelineDataConnection,
        client: system.Client,
    ) -> Self:
        return cls(
            proto_self=proto,
            client=client,
        )

    @classmethod
    async def from_pipeline_id(
        cls,
        *,
        pipeline_id: eorm.PipelineID,
        data_connector_id: eorm.DataConnectorID | None = None,
        client: system.Client,
        session: eorm.Session | None = None,
    ) -> Ok[list[Self]] | NotFoundError | InvalidArgumentError:
        def _modify_query(
            query: sa.Select[tuple[eorm.PipelineDataConnection]],
        ) -> sa.Select[tuple[eorm.PipelineDataConnection]]:
            query = query.where(eorm.PipelineDataConnection.pipeline_id == pipeline_id)
            if data_connector_id:
                query = query.where(
                    eorm.PipelineDataConnection.data_connector_id == data_connector_id
                )
            return query

        return (
            await cls.list_as_proto(
                client=client,
                existing_session=session,
                additional_query_transform=_modify_query,
            )
        ).map(lambda protos: [cls(proto_self=proto, client=client) for proto in protos])

    async def delete(self, session: eorm.Session) -> Ok[None] | InvalidArgumentError:
        return await pipeline_data_connection_delete_orms(
            pipeline_id=self.pipeline_id,
            data_connector_id=self.data_connector.id,
            session=session,
        )

    @property
    def pipeline_id(self) -> eorm.PipelineID:
        return eorm.PipelineID(self.proto_self.pipeline_id)

    @property
    def data_connector(self) -> DataConnector:
        return DataConnector(
            proto_self=self.proto_self.data_connector, client=self.client
        )

    @property
    def prefix(self) -> str:
        return self.proto_self.prefix

    @property
    def glob(self) -> str:
        return self.proto_self.glob

    @property
    def last_ingestion_time(self) -> datetime | None:
        return transfer.non_empty_timestamp_to_datetime(
            self.proto_self.last_ingestion_time
        )

    @property
    def last_successful_ingestion_time(self) -> datetime | None:
        return transfer.non_empty_timestamp_to_datetime(
            self.proto_self.last_successful_ingestion_time
        )

    @property
    def interval_seconds(self) -> int | None:
        return (
            self.proto_self.interval_seconds
            if self.proto_self.interval_seconds != 0
            else None
        )

    @property
    def watermark_time(self) -> datetime | None:
        return transfer.non_empty_timestamp_to_datetime(self.proto_self.watermark_time)

    def with_last_ingestion_time(
        self, last_ingestion_time: datetime
    ) -> PipelineDataConnection:
        proto_self = copy.copy(self.proto_self)
        proto_self.last_ingestion_time.FromDatetime(last_ingestion_time)
        return PipelineDataConnection(
            proto_self=proto_self,
            client=self.client,
        )

    def with_last_successful_ingestion_time(
        self, last_successful_ingestion_time: datetime
    ) -> PipelineDataConnection:
        proto_self = copy.copy(self.proto_self)
        proto_self.last_successful_ingestion_time.FromDatetime(
            last_successful_ingestion_time
        )
        return PipelineDataConnection(
            proto_self=proto_self,
            client=self.client,
        )

    def with_interval_seconds(self, interval_seconds: int) -> PipelineDataConnection:
        proto_self = copy.copy(self.proto_self)
        proto_self.interval_seconds = interval_seconds
        return PipelineDataConnection(
            proto_self=proto_self,
            client=self.client,
        )

    def with_watermark_time(self, watermark_time: datetime) -> PipelineDataConnection:
        proto_self = copy.copy(self.proto_self)
        proto_self.watermark_time.FromDatetime(watermark_time)
        return PipelineDataConnection(
            proto_self=proto_self,
            client=self.client,
        )


class DataConnection(
    OrgWideStandardModel[
        DataConnectionID, models_pb2.DataConnection, eorm.DataConnection
    ]
):
    """A connection to a DataConnector object with connection parameters."""

    @classmethod
    def id_class(cls):
        return DataConnectionID

    @classmethod
    def orm_class(cls):
        return eorm.DataConnection

    @classmethod
    async def _orm_to_proto(
        cls, orm_obj: eorm.DataConnection
    ) -> models_pb2.DataConnection:
        return await data_connection_orm_to_proto(orm_obj)

    @classmethod
    async def _proto_to_orm(
        cls, proto_obj: models_pb2.DataConnection, session: eorm.Session
    ) -> Ok[eorm.DataConnection] | InvalidArgumentError:
        return await data_connection_proto_to_orm(proto_obj, session)

    @classmethod
    def orm_load_options(cls) -> list[LoaderOption]:
        return [
            sa_orm.selectinload(eorm.DataConnection.data_connector),
        ]

    @classmethod
    def create(
        cls,
        *,
        pipeline: Pipeline,
        data_connector: DataConnector,
        prefix: str,
        glob: str,
        interval_seconds: int | None = None,
        client: system.Client,
    ) -> Self:
        proto_self = models_pb2.DataConnection(
            pipeline_id=str(pipeline.id),
            data_connector=data_connector.proto_self,
            room_id=str(pipeline.room_id),
            org_id=str(pipeline.org_id),
            prefix=prefix,
            glob=glob,
            interval_seconds=interval_seconds,
        )
        return cls(proto_self=proto_self, client=client)

    @classmethod
    async def list(
        cls,
        *,
        pipeline_id: eorm.PipelineID | None = None,
        data_connector_id: eorm.DataConnectorID | None = None,
        ready_for_ingestion: bool = False,
        limit: int | None = None,
        created_before: datetime | None = None,
        ids: Iterable[DataConnectionID] | None = None,
        existing_session: eorm.Session | None = None,
        client: system.Client,
    ) -> Ok[list[Self]] | NotFoundError | InvalidArgumentError:
        """List DataConnections."""

        def query_transform(query: sa.Select[tuple[eorm.DataConnection]]):
            if pipeline_id:
                query = query.where(eorm.DataConnection.pipeline_id == pipeline_id)
            if data_connector_id:
                query = query.where(
                    eorm.DataConnection.data_connector_id == data_connector_id
                )
            if ready_for_ingestion:
                query = _ready_for_ingestion(query, eorm.DataConnection)  # pyright: ignore[reportAssignmentType]

            return query

        match await cls.list_as_proto(
            client=client,
            limit=limit,
            created_before=created_before,
            ids=ids,
            existing_session=existing_session,
            additional_query_transform=query_transform,
        ):
            case NotFoundError() | InvalidArgumentError() as err:
                return err
            case Ok(protos):
                return Ok(
                    [cls.from_proto(proto=proto, client=client) for proto in protos]
                )

    @classmethod
    def from_proto(
        cls,
        *,
        proto: models_pb2.DataConnection,
        client: system.Client,
    ) -> Self:
        return cls(
            proto_self=proto,
            client=client,
        )

    @classmethod
    async def from_pipeline_id(
        cls,
        *,
        pipeline_id: eorm.PipelineID,
        data_connector_id: eorm.DataConnectorID | None = None,
        client: system.Client,
        session: eorm.Session | None = None,
    ) -> Ok[list[Self]] | NotFoundError | InvalidArgumentError:
        def _modify_query(
            query: sa.Select[tuple[eorm.DataConnection]],
        ) -> sa.Select[tuple[eorm.DataConnection]]:
            query = query.where(eorm.DataConnection.pipeline_id == pipeline_id)
            if data_connector_id:
                query = query.where(
                    eorm.DataConnection.data_connector_id == data_connector_id
                )
            return query

        return (
            await cls.list_as_proto(
                client=client,
                existing_session=session,
                additional_query_transform=_modify_query,
            )
        ).map(lambda protos: [cls(proto_self=proto, client=client) for proto in protos])

    @classmethod
    async def from_id(
        cls,
        *,
        data_connection_id: DataConnectionID,
        session: eorm.Session | None = None,
        client: system.Client,
    ) -> Ok[Self] | NotFoundError:
        return (
            await cls.load_proto_for(
                obj_id=data_connection_id,
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
    async def delete_by_ids(
        cls, ids: Sequence[DataConnectionID], session: eorm.Session
    ) -> Ok[None] | InvalidArgumentError:
        return await data_connection_delete_orms(ids, session)

    @property
    def pipeline_id(self) -> eorm.PipelineID:
        return eorm.PipelineID(self.proto_self.pipeline_id)

    @property
    def data_connector(self) -> DataConnector:
        return DataConnector(
            proto_self=self.proto_self.data_connector, client=self.client
        )

    @property
    def prefix(self) -> str:
        return self.proto_self.prefix

    @property
    def glob(self) -> str:
        return self.proto_self.glob

    @property
    def last_ingestion_time(self) -> datetime | None:
        return transfer.non_empty_timestamp_to_datetime(
            self.proto_self.last_ingestion_time
        )

    @property
    def last_successful_ingestion_time(self) -> datetime | None:
        return transfer.non_empty_timestamp_to_datetime(
            self.proto_self.last_successful_ingestion_time
        )

    @property
    def interval_seconds(self) -> int | None:
        return (
            self.proto_self.interval_seconds
            if self.proto_self.interval_seconds != 0
            else None
        )

    @property
    def watermark_time(self) -> datetime | None:
        return transfer.non_empty_timestamp_to_datetime(self.proto_self.watermark_time)

    def with_last_ingestion_time(self, last_ingestion_time: datetime) -> DataConnection:
        proto_self = copy.copy(self.proto_self)
        proto_self.last_ingestion_time.FromDatetime(last_ingestion_time)
        return DataConnection(
            proto_self=proto_self,
            client=self.client,
        )

    def with_last_successful_ingestion_time(
        self, last_successful_ingestion_time: datetime
    ) -> DataConnection:
        proto_self = copy.copy(self.proto_self)
        proto_self.last_successful_ingestion_time.FromDatetime(
            last_successful_ingestion_time
        )
        return DataConnection(
            proto_self=proto_self,
            client=self.client,
        )

    def with_interval_seconds(self, interval_seconds: int) -> DataConnection:
        proto_self = copy.copy(self.proto_self)
        proto_self.interval_seconds = interval_seconds
        return DataConnection(
            proto_self=proto_self,
            client=self.client,
        )

    def with_watermark_time(self, watermark_time: datetime) -> DataConnection:
        proto_self = copy.copy(self.proto_self)
        proto_self.watermark_time.FromDatetime(watermark_time)
        return DataConnection(
            proto_self=proto_self,
            client=self.client,
        )
