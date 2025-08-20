import datetime
from collections.abc import Awaitable, Callable, Sequence
from typing import Any, Protocol, TypeVar

import sqlalchemy as sa
import sqlalchemy.orm as sa_orm
from google.protobuf import timestamp_pb2

from corvic import eorm, orm, transfer
from corvic.result import InternalError, InvalidArgumentError, Ok
from corvic_generated.model.v1alpha import models_pb2
from corvic_generated.orm.v1 import feature_view_pb2


class _ModelBelongsToOrgProto(transfer.ProtoModel, Protocol):
    org_id: str


class _ModelBelongsToRoomProto(_ModelBelongsToOrgProto, Protocol):
    room_id: str


class _ModelHasIdBelongsToOrgProto(
    transfer.ProtoHasIdModel, _ModelBelongsToOrgProto, Protocol
):
    pass


class _ModelHasIdBelongsToRoomProto(
    transfer.ProtoHasIdModel, _ModelBelongsToRoomProto, Protocol
):
    pass


ProtoBelongsToOrgT = TypeVar("ProtoBelongsToOrgT", bound=_ModelBelongsToOrgProto)
ProtoBelongsToRoomT = TypeVar("ProtoBelongsToRoomT", bound=_ModelBelongsToRoomProto)
ProtoHasIdBelongsToOrgT = TypeVar(
    "ProtoHasIdBelongsToOrgT", bound=_ModelHasIdBelongsToOrgProto
)
ProtoHasIdBelongsToRoomT = TypeVar(
    "ProtoHasIdBelongsToRoomT", bound=_ModelHasIdBelongsToRoomProto
)


class _OrmBelongsToOrgModel(transfer.OrmModel, Protocol):
    org_id: sa_orm.Mapped[eorm.OrgID | None]


class _OrmBelongsToRoomModel(_OrmBelongsToOrgModel, Protocol):
    room_id: sa_orm.Mapped[eorm.RoomID | None]


class _OrmHasIdBelongsToOrgModel(
    transfer.OrmHasIdModel[transfer.OrmIdT], _OrmBelongsToOrgModel, Protocol
):
    pass


class _OrmHasIdBelongsToRoomModel(
    _OrmHasIdBelongsToOrgModel[transfer.OrmIdT], _OrmBelongsToRoomModel, Protocol
):
    pass


OrmBelongsToOrgT = TypeVar("OrmBelongsToOrgT", bound=_OrmBelongsToOrgModel)
OrmBelongsToRoomT = TypeVar("OrmBelongsToRoomT", bound=_OrmBelongsToRoomModel)
OrmHasIdBelongsToOrgT = TypeVar(
    "OrmHasIdBelongsToOrgT", bound=_OrmHasIdBelongsToOrgModel[Any]
)
OrmHasIdBelongsToRoomT = TypeVar(
    "OrmHasIdBelongsToRoomT", bound=_OrmHasIdBelongsToRoomModel[Any]
)


def _orm_id_to_str(id: eorm.ID | None):
    if id:
        return str(id)
    return ""


def timestamp_orm_to_proto(
    timestamp_orm: datetime.datetime | None,
) -> timestamp_pb2.Timestamp | None:
    if timestamp_orm is not None:
        timestamp_proto = timestamp_pb2.Timestamp()
        timestamp_proto.FromDatetime(timestamp_orm)
    else:
        timestamp_proto = None
    return timestamp_proto


async def resource_orm_to_proto(resource_orm: eorm.Resource) -> models_pb2.Resource:
    pipeline_input_name = ""
    pipeline_id = ""
    pipeline_ref: (
        eorm.PipelineInput | None
    ) = await resource_orm.awaitable_attrs.pipeline_ref
    if pipeline_ref:
        pipeline_input_name = pipeline_ref.name
        pipeline_id = _orm_id_to_str(pipeline_ref.pipeline_id)
    return models_pb2.Resource(
        id=_orm_id_to_str(resource_orm.id),
        name=resource_orm.name,
        description=resource_orm.description,
        mime_type=resource_orm.mime_type,
        url=resource_orm.url,
        md5=resource_orm.md5,
        size=resource_orm.size,
        etag=resource_orm.etag,
        original_modified_at_time=timestamp_orm_to_proto(
            resource_orm.original_modified_at_time
        ),
        data_connection_id=_orm_id_to_str(resource_orm.data_connection_id),
        original_path=resource_orm.original_path,
        room_id=_orm_id_to_str(resource_orm.room_id),
        org_id=_orm_id_to_str(resource_orm.org_id),
        recent_events=[resource_orm.latest_event] if resource_orm.latest_event else [],
        is_terminal=bool(resource_orm.is_terminal),
        pipeline_id=pipeline_id,
        pipeline_input_name=pipeline_input_name,
        created_at=timestamp_orm_to_proto(resource_orm.created_at),
    )


async def source_orm_to_proto(source_orm: eorm.Source) -> models_pb2.Source:
    pipeline_ref: (
        eorm.PipelineInput | None
    ) = await source_orm.awaitable_attrs.pipeline_ref
    return models_pb2.Source(
        id=_orm_id_to_str(source_orm.id),
        name=source_orm.name,
        table_op_graph=source_orm.table_op_graph,
        room_id=_orm_id_to_str(source_orm.room_id),
        org_id=_orm_id_to_str(source_orm.org_id),
        pipeline_id=_orm_id_to_str(pipeline_ref.pipeline_id) if pipeline_ref else "",
        created_at=timestamp_orm_to_proto(source_orm.created_at),
    )


async def feature_view_source_orm_to_proto(
    feature_view_source_orm: eorm.FeatureViewSource,
) -> models_pb2.FeatureViewSource:
    source: eorm.Source = await feature_view_source_orm.awaitable_attrs.source
    if feature_view_source_orm.table_op_graph.WhichOneof("op") is not None:
        op = feature_view_source_orm.table_op_graph
    else:
        # some legacy feature views were stored without op graphs fill those
        # with the source's opgraph
        op = source.table_op_graph
    return models_pb2.FeatureViewSource(
        id=_orm_id_to_str(feature_view_source_orm.id),
        room_id=_orm_id_to_str(feature_view_source_orm.room_id),
        source=await source_orm_to_proto(source),
        table_op_graph=op,
        drop_disconnected=feature_view_source_orm.drop_disconnected,
        org_id=_orm_id_to_str(feature_view_source_orm.org_id),
        created_at=timestamp_orm_to_proto(feature_view_source_orm.created_at),
    )


async def feature_view_orm_to_proto(
    feature_view_orm: eorm.FeatureView,
) -> models_pb2.FeatureView:
    return models_pb2.FeatureView(
        id=_orm_id_to_str(feature_view_orm.id),
        name=feature_view_orm.name,
        description=feature_view_orm.description,
        room_id=_orm_id_to_str(feature_view_orm.room_id),
        feature_view_output=await feature_view_orm.awaitable_attrs.feature_view_output,
        feature_view_sources=[
            await feature_view_source_orm_to_proto(fvs)
            for fvs in await feature_view_orm.awaitable_attrs.feature_view_sources
        ],
        org_id=_orm_id_to_str(feature_view_orm.org_id),
        created_at=timestamp_orm_to_proto(feature_view_orm.created_at),
    )


async def pipeline_orm_to_proto(
    pipeline_orm: eorm.Pipeline,
) -> models_pb2.Pipeline:
    return models_pb2.Pipeline(
        id=_orm_id_to_str(pipeline_orm.id),
        name=pipeline_orm.name,
        room_id=_orm_id_to_str(pipeline_orm.room_id),
        source_outputs={
            output_obj.name: await source_orm_to_proto(
                await output_obj.awaitable_attrs.source
            )
            for output_obj in await pipeline_orm.awaitable_attrs.outputs
        },
        pipeline_transformation=pipeline_orm.transformation,
        org_id=_orm_id_to_str(pipeline_orm.org_id),
        description=pipeline_orm.description,
        created_at=timestamp_orm_to_proto(pipeline_orm.created_at),
    )


async def space_orm_to_proto(space_orm: eorm.Space) -> models_pb2.Space:
    return models_pb2.Space(
        id=_orm_id_to_str(space_orm.id),
        name=space_orm.name,
        description=space_orm.description,
        room_id=_orm_id_to_str(space_orm.room_id),
        space_parameters=space_orm.parameters,
        feature_view=await feature_view_orm_to_proto(
            await space_orm.awaitable_attrs.feature_view
        ),
        auto_sync=space_orm.auto_sync if space_orm.auto_sync is not None else False,
        org_id=_orm_id_to_str(space_orm.org_id),
        created_at=timestamp_orm_to_proto(space_orm.created_at),
    )


def room_orm_to_proto(room_orm: eorm.Room) -> models_pb2.Room:
    return models_pb2.Room(
        id=_orm_id_to_str(room_orm.id),
        name=room_orm.name,
        org_id=_orm_id_to_str(room_orm.org_id),
        created_at=timestamp_orm_to_proto(room_orm.created_at),
    )


def data_connector_orm_to_proto(
    data_connector_orm: eorm.DataConnector,
) -> models_pb2.DataConnector:
    return models_pb2.DataConnector(
        id=_orm_id_to_str(data_connector_orm.id),
        name=data_connector_orm.name,
        org_id=_orm_id_to_str(data_connector_orm.org_id),
        parameters=data_connector_orm.parameters,
        base_path=data_connector_orm.base_path,
        secret_key=data_connector_orm.secret_key,
        created_at=timestamp_orm_to_proto(data_connector_orm.created_at),
        last_validation_time=timestamp_orm_to_proto(
            data_connector_orm.last_validation_time
        ),
        last_successful_validation=timestamp_orm_to_proto(
            data_connector_orm.last_successful_validation
        ),
    )


async def pipeline_data_connection_orm_to_proto(
    orm_obj: eorm.PipelineDataConnection,
) -> models_pb2.PipelineDataConnection:
    return models_pb2.PipelineDataConnection(
        pipeline_id=_orm_id_to_str(orm_obj.pipeline_id),
        data_connector=data_connector_orm_to_proto(
            await orm_obj.awaitable_attrs.data_connector
        ),
        room_id=_orm_id_to_str(orm_obj.room_id),
        org_id=_orm_id_to_str(orm_obj.org_id),
        prefix=orm_obj.prefix,
        glob=orm_obj.glob,
        created_at=timestamp_orm_to_proto(orm_obj.created_at),
        last_ingestion_time=timestamp_orm_to_proto(orm_obj.last_ingestion_time),
        last_successful_ingestion_time=timestamp_orm_to_proto(
            orm_obj.last_successful_ingestion_time
        ),
        interval_seconds=orm_obj.interval_seconds,
        watermark_time=timestamp_orm_to_proto(orm_obj.watermark_time),
    )


async def data_connection_orm_to_proto(
    orm_obj: eorm.DataConnection,
) -> models_pb2.DataConnection:
    return models_pb2.DataConnection(
        id=_orm_id_to_str(orm_obj.id),
        pipeline_id=_orm_id_to_str(orm_obj.pipeline_id),
        data_connector=data_connector_orm_to_proto(
            await orm_obj.awaitable_attrs.data_connector
        ),
        room_id=_orm_id_to_str(orm_obj.room_id),
        org_id=_orm_id_to_str(orm_obj.org_id),
        prefix=orm_obj.prefix,
        glob=orm_obj.glob,
        created_at=timestamp_orm_to_proto(orm_obj.created_at),
        last_ingestion_time=timestamp_orm_to_proto(orm_obj.last_ingestion_time),
        last_successful_ingestion_time=timestamp_orm_to_proto(
            orm_obj.last_successful_ingestion_time
        ),
        interval_seconds=orm_obj.interval_seconds,
        watermark_time=timestamp_orm_to_proto(orm_obj.watermark_time),
    )


async def add_orm_org_mixin_to_session(
    orm_obj: OrmHasIdBelongsToOrgT,
    proto_obj: _ModelHasIdBelongsToOrgProto,
    id_class: type[transfer.OrmIdT],
    session: eorm.Session,
) -> Ok[OrmHasIdBelongsToOrgT] | orm.InvalidORMIdentifierError:
    match transfer.translate_orm_id(proto_obj.id, id_class):
        case Ok(orm_id):
            orm_obj.id = orm_id
        case orm.InvalidORMIdentifierError() as err:
            return err
    if proto_obj.org_id:
        org_id = eorm.OrgID(proto_obj.org_id)
        match org_id.to_db():
            case Ok():
                orm_obj.org_id = org_id
            case orm.InvalidORMIdentifierError() as err:
                return err
        orm_obj.org_id = org_id
    if not orm_obj.id:
        session.add(orm_obj)
    else:
        orm_obj = await session.merge(orm_obj)
    return Ok(orm_obj)


async def add_orm_room_mixin_to_session(
    orm_obj: OrmHasIdBelongsToRoomT,
    proto_obj: _ModelHasIdBelongsToRoomProto,
    id_class: type[transfer.OrmIdT],
    session: eorm.Session,
) -> Ok[OrmHasIdBelongsToRoomT] | orm.InvalidORMIdentifierError:
    room_id = eorm.RoomID(proto_obj.room_id)
    match room_id.to_db():
        case Ok():
            pass
        case orm.InvalidORMIdentifierError() as err:
            return err
    orm_obj.room_id = eorm.RoomID(proto_obj.room_id)
    return await add_orm_org_mixin_to_session(orm_obj, proto_obj, id_class, session)


async def _resource_pipeline_to_orm(
    proto_obj: models_pb2.Resource, orm_obj: eorm.Resource, session: eorm.Session
) -> Ok[None] | InvalidArgumentError:
    if proto_obj.pipeline_id:
        match transfer.translate_orm_id(proto_obj.pipeline_id, eorm.PipelineID):
            case orm.InvalidORMIdentifierError() as err:
                return err
            case Ok(pipeline_id):
                pass
        if not pipeline_id:
            return InvalidArgumentError("resource's pipeline cannot be anonymous")
        await session.flush()
        if not orm_obj.id:
            raise InternalError("internal assertion did not hold")
        pipeline_input = eorm.PipelineInput(
            resource_id=orm_obj.id,
            name=proto_obj.pipeline_input_name,
            pipeline_id=pipeline_id,
            room_id=orm_obj.room_id,
        )
        if orm_obj.org_id:
            pipeline_input.org_id = orm_obj.org_id
        orm_obj.pipeline_ref = await session.merge(pipeline_input)
    return Ok(None)


async def resource_proto_to_orm(
    proto_obj: models_pb2.Resource, session: eorm.Session
) -> Ok[eorm.Resource] | InvalidArgumentError:
    data_connection_id = None
    if proto_obj.data_connection_id:
        match transfer.translate_orm_id(
            proto_obj.data_connection_id, eorm.DataConnectionID
        ):
            case orm.InvalidORMIdentifierError() as err:
                return err
            case Ok(data_connection_id):
                pass
    orm_obj = eorm.Resource(
        name=proto_obj.name,
        description=proto_obj.description,
        mime_type=proto_obj.mime_type,
        md5=proto_obj.md5,
        url=proto_obj.url,
        size=proto_obj.size,
        etag=proto_obj.etag,
        original_modified_at_time=proto_obj.original_modified_at_time.ToDatetime(
            datetime.UTC
        ),
        data_connection_id=data_connection_id,
        original_path=proto_obj.original_path,
        latest_event=proto_obj.recent_events[-1] if proto_obj.recent_events else None,
        is_terminal=proto_obj.is_terminal,
    )
    match await add_orm_room_mixin_to_session(
        orm_obj, proto_obj, eorm.ResourceID, session
    ):
        case InvalidArgumentError() as err:
            return err
        case Ok(orm_obj):
            pass

    match await _resource_pipeline_to_orm(proto_obj, orm_obj, session):
        case InvalidArgumentError() as err:
            return err
        case Ok(None):
            return Ok(orm_obj)


async def _ensure_id(
    proto_obj: transfer.ProtoHasIdT,
    proto_to_orm: Callable[
        [transfer.ProtoHasIdT, eorm.Session],
        Awaitable[Ok[transfer.OrmHasIdT] | InvalidArgumentError],
    ],
    id_type: type[transfer.OrmIdT],
    session: eorm.Session,
) -> Ok[transfer.OrmIdT] | orm.InvalidORMIdentifierError | InvalidArgumentError:
    match transfer.translate_orm_id(proto_obj.id, id_type):
        case orm.InvalidORMIdentifierError() as err:
            return err
        case Ok(orm_id):
            if orm_id:
                return Ok(orm_id)
    match await proto_to_orm(proto_obj, session):
        case orm.InvalidORMIdentifierError() | InvalidArgumentError() as err:
            return err
        case Ok(orm_obj):
            await session.flush()
            if not orm_obj.id:
                raise InternalError("internal assertion did not hold")
            return Ok(orm_obj.id)


async def pipeline_proto_to_orm(  # noqa: C901
    proto_obj: models_pb2.Pipeline, session: eorm.Session
) -> Ok[eorm.Pipeline] | orm.InvalidORMIdentifierError | InvalidArgumentError:
    orm_obj = eorm.Pipeline(
        name=proto_obj.name,
        transformation=proto_obj.pipeline_transformation,
        description=proto_obj.description,
    )
    if proto_obj.org_id:
        orm_obj.org_id = eorm.OrgID(proto_obj.org_id)
    match await add_orm_room_mixin_to_session(
        orm_obj, proto_obj, eorm.PipelineID, session
    ):
        case Ok(orm_obj):
            pass
        case orm.InvalidORMIdentifierError() as err:
            return err
    await session.flush()

    if not orm_obj.id:
        raise InternalError("internal assertion did not hold")

    outputs = list[eorm.PipelineOutput]()
    for name, val in proto_obj.source_outputs.items():
        match await _ensure_id(val, source_proto_to_orm, eorm.SourceID, session):
            case orm.InvalidORMIdentifierError() | InvalidArgumentError() as err:
                return err
            case Ok(source_id):
                pass
        outputs.append(
            eorm.PipelineOutput(
                source_id=source_id,
                name=name,
                pipeline_id=orm_obj.id,
                room_id=orm_obj.room_id,
            )
        )

    if proto_obj.org_id:
        org_id = orm.OrgID(proto_obj.org_id)
        for obj in outputs:
            obj.org_id = org_id
    for obj in outputs:
        await session.merge(obj)
    return Ok(orm_obj)


async def source_proto_to_orm(
    proto_obj: models_pb2.Source, session: eorm.Session
) -> Ok[eorm.Source] | orm.InvalidORMIdentifierError | InvalidArgumentError:
    orm_obj = eorm.Source(
        name=proto_obj.name,
        table_op_graph=proto_obj.table_op_graph,
    )
    return await add_orm_room_mixin_to_session(
        orm_obj, proto_obj, eorm.SourceID, session
    )


async def space_proto_to_orm(
    proto_obj: models_pb2.Space, session: eorm.Session
) -> Ok[eorm.Space] | orm.InvalidORMIdentifierError | InvalidArgumentError:
    match await _ensure_id(
        proto_obj.feature_view, feature_view_proto_to_orm, eorm.FeatureViewID, session
    ):
        case orm.InvalidORMIdentifierError() | InvalidArgumentError() as err:
            return err
        case Ok(feature_view_id):
            pass

    if not feature_view_id:
        raise InternalError("internal assertion did not hold")

    orm_obj = eorm.Space(
        name=proto_obj.name,
        description=proto_obj.description,
        feature_view_id=feature_view_id,
        parameters=proto_obj.space_parameters,
        auto_sync=proto_obj.auto_sync,
    )
    return await add_orm_room_mixin_to_session(
        orm_obj, proto_obj, eorm.SpaceID, session
    )


async def feature_view_proto_to_orm(
    proto_obj: models_pb2.FeatureView, session: eorm.Session
) -> Ok[eorm.FeatureView] | orm.InvalidORMIdentifierError | InvalidArgumentError:
    orm_obj = eorm.FeatureView(
        name=proto_obj.name,
        description=proto_obj.description,
    )
    if proto_obj.org_id:
        orm_obj.org_id = eorm.OrgID(proto_obj.org_id)
    match await add_orm_room_mixin_to_session(
        orm_obj, proto_obj, eorm.FeatureViewID, session
    ):
        case Ok(orm_obj):
            pass
        case orm.InvalidORMIdentifierError() as err:
            return err
    await session.flush()

    if not orm_obj.id or not orm_obj.room_id:
        raise InternalError("internal assertion did not hold")

    new_fv_sources = list[eorm.FeatureViewSource]()
    for fvs in proto_obj.feature_view_sources:
        match await _feature_view_source_proto_to_orm(
            fvs, orm_obj.room_id, orm_obj.id, session
        ):
            case orm.InvalidORMIdentifierError() | InvalidArgumentError() as err:
                return err
            case Ok(fvs_orm):
                new_fv_sources.append(fvs_orm)

    old_to_new_source_id = dict[str, str]()
    for old_fvs, new_fvs in zip(
        proto_obj.feature_view_sources, new_fv_sources, strict=True
    ):
        if old_fvs.source.id != str(new_fvs.source_id):
            old_to_new_source_id[old_fvs.source.id] = str(new_fvs.source_id)

    orm_obj.feature_view_output = (
        feature_view_pb2.FeatureViewOutput(
            relationships=[
                feature_view_pb2.FeatureViewRelationship(
                    start_source_id=old_to_new_source_id.get(
                        old_rel.start_source_id, old_rel.start_source_id
                    ),
                    end_source_id=old_to_new_source_id.get(
                        old_rel.end_source_id, old_rel.end_source_id
                    ),
                )
                for old_rel in proto_obj.feature_view_output.relationships
            ],
            output_sources=[
                feature_view_pb2.OutputSource(
                    source_id=old_to_new_source_id.get(
                        old_output_source.source_id, old_output_source.source_id
                    )
                )
                for old_output_source in proto_obj.feature_view_output.output_sources
            ],
        )
        if old_to_new_source_id
        else proto_obj.feature_view_output
    )
    orm_obj = await session.merge(orm_obj)
    return Ok(orm_obj)


async def _feature_view_source_proto_to_orm(
    proto_obj: models_pb2.FeatureViewSource,
    room_id: eorm.RoomID,
    feature_view_id: eorm.FeatureViewID,
    session: eorm.Session,
) -> Ok[eorm.FeatureViewSource] | orm.InvalidORMIdentifierError | InvalidArgumentError:
    match await _ensure_id(
        proto_obj.source, source_proto_to_orm, eorm.SourceID, session
    ):
        case orm.InvalidORMIdentifierError() | InvalidArgumentError() as err:
            return err
        case Ok(source_id):
            pass

    proto_obj.room_id = proto_obj.room_id or str(room_id)
    orm_obj = eorm.FeatureViewSource(
        table_op_graph=proto_obj.table_op_graph,
        drop_disconnected=proto_obj.drop_disconnected,
        source_id=source_id,
        feature_view_id=feature_view_id,
    )
    return await add_orm_room_mixin_to_session(
        orm_obj, proto_obj, eorm.FeatureViewSourceID, session
    )


async def room_proto_to_orm(
    proto_obj: models_pb2.Room, session: eorm.Session
) -> Ok[eorm.Room] | orm.InvalidORMIdentifierError | InvalidArgumentError:
    orm_obj = eorm.Room(name=proto_obj.name)
    return await add_orm_org_mixin_to_session(orm_obj, proto_obj, eorm.RoomID, session)


async def data_connector_proto_to_orm(
    proto_obj: models_pb2.DataConnector, session: eorm.Session
) -> Ok[eorm.DataConnector] | InvalidArgumentError:
    orm_obj = eorm.DataConnector(
        name=proto_obj.name,
        parameters=proto_obj.parameters,
        base_path=proto_obj.base_path,
        secret_key=proto_obj.secret_key,
        last_validation_time=proto_obj.last_validation_time.ToDatetime(),
        last_successful_validation=proto_obj.last_successful_validation.ToDatetime(),
    )
    return await add_orm_org_mixin_to_session(
        orm_obj, proto_obj, eorm.DataConnectorID, session
    )


async def pipeline_data_connection_proto_to_orm(
    proto_obj: models_pb2.PipelineDataConnection, session: eorm.Session
) -> Ok[eorm.PipelineDataConnection] | InvalidArgumentError:
    match transfer.translate_nongenerated_orm_id(
        proto_obj.pipeline_id, eorm.PipelineID
    ):
        case eorm.InvalidORMIdentifierError() as err:
            return err
        case Ok(pipeline_id):
            pass
    match transfer.translate_nongenerated_orm_id(
        proto_obj.data_connector.id, eorm.DataConnectorID
    ):
        case eorm.InvalidORMIdentifierError() as err:
            return err
        case Ok(data_connector_id):
            pass
    match transfer.translate_nongenerated_orm_id(proto_obj.room_id, eorm.RoomID):
        case eorm.InvalidORMIdentifierError() as err:
            return err
        case Ok(room_id):
            pass
    orm_obj = eorm.PipelineDataConnection(
        pipeline_id=pipeline_id,
        data_connector_id=data_connector_id,
        prefix=proto_obj.prefix,
        glob=proto_obj.glob,
        room_id=room_id,
        last_ingestion_time=proto_obj.last_ingestion_time.ToDatetime(datetime.UTC),
        last_successful_ingestion_time=proto_obj.last_successful_ingestion_time.ToDatetime(
            datetime.UTC
        ),
        interval_seconds=proto_obj.interval_seconds,
        watermark_time=proto_obj.watermark_time.ToDatetime(datetime.UTC),
    )
    orm_obj = await session.merge(orm_obj)
    return Ok(orm_obj)


async def data_connection_proto_to_orm(
    proto_obj: models_pb2.DataConnection, session: eorm.Session
) -> Ok[eorm.DataConnection] | InvalidArgumentError:
    match transfer.translate_nongenerated_orm_id(
        proto_obj.pipeline_id, eorm.PipelineID
    ):
        case eorm.InvalidORMIdentifierError() as err:
            return err
        case Ok(pipeline_id):
            pass
    match transfer.translate_nongenerated_orm_id(
        proto_obj.data_connector.id, eorm.DataConnectorID
    ):
        case eorm.InvalidORMIdentifierError() as err:
            return err
        case Ok(data_connector_id):
            pass
    match transfer.translate_nongenerated_orm_id(proto_obj.room_id, eorm.RoomID):
        case eorm.InvalidORMIdentifierError() as err:
            return err
        case Ok(room_id):
            pass
    orm_obj = eorm.DataConnection(
        pipeline_id=pipeline_id,
        data_connector_id=data_connector_id,
        prefix=proto_obj.prefix,
        glob=proto_obj.glob,
        room_id=room_id,
        last_ingestion_time=proto_obj.last_ingestion_time.ToDatetime(datetime.UTC),
        last_successful_ingestion_time=proto_obj.last_successful_ingestion_time.ToDatetime(
            datetime.UTC
        ),
        interval_seconds=proto_obj.interval_seconds,
        watermark_time=proto_obj.watermark_time.ToDatetime(datetime.UTC),
    )
    return await add_orm_org_mixin_to_session(
        orm_obj, proto_obj, eorm.DataConnectionID, session
    )


async def source_delete_orms(
    orm_ids: Sequence[eorm.SourceID],
    session: eorm.Session,
) -> Ok[None] | InvalidArgumentError:
    feat_view_refs = list(
        await session.scalars(
            sa.select(eorm.FeatureViewSource.id)
            .where(eorm.FeatureViewSource.source_id.in_(orm_ids))
            .limit(1)
        )
    )

    if feat_view_refs:
        return InvalidArgumentError(
            "cannot delete a source that still has feature views"
        )
    await session.execute(sa.delete(eorm.Source).where(eorm.Source.id.in_(orm_ids)))
    return Ok(None)


async def pipeline_delete_orms(
    ids: Sequence[eorm.PipelineID], session: eorm.Session
) -> Ok[None] | InvalidArgumentError:
    source_ids = [
        val[0]
        for val in await session.execute(
            sa.select(eorm.Source.id).where(
                eorm.Source.id.in_(
                    sa.select(eorm.PipelineOutput.source_id).where(
                        eorm.PipelineOutput.pipeline_id.in_(ids)
                    )
                )
            )
        )
        if val[0] is not None
    ]
    match await source_delete_orms(source_ids, session):
        case InvalidArgumentError() as err:
            return err
        case Ok():
            pass

    await session.execute(
        sa.delete(eorm.Resource).where(
            eorm.Resource.id.in_(
                sa.select(eorm.PipelineInput.resource_id)
                .join(eorm.Pipeline)
                .where(eorm.Pipeline.id.in_(ids))
            )
        )
    )
    await session.execute(sa.delete(eorm.Pipeline).where(eorm.Pipeline.id.in_(ids)))
    return Ok(None)


async def resource_delete_orms(
    ids: Sequence[eorm.ResourceID],
    session: eorm.Session,
) -> Ok[None] | InvalidArgumentError:
    pipeline_refs = list(
        await session.execute(
            sa.select(eorm.PipelineInput.pipeline_id)
            .where(eorm.PipelineInput.resource_id.in_(ids))
            .limit(1)
        )
    )

    if pipeline_refs:
        return InvalidArgumentError(
            "sources exist that reference resources to be deleted"
        )
    await session.execute(sa.delete(eorm.Resource).where(eorm.Resource.id.in_(ids)))
    return Ok(None)


async def feature_view_source_delete_orms(
    ids: Sequence[eorm.FeatureViewSourceID], session: eorm.Session
) -> Ok[None] | InvalidArgumentError:
    feat_view_refs = list(
        await session.execute(
            sa.select(eorm.FeatureView.id)
            .where(
                eorm.FeatureView.id.in_(
                    sa.select(eorm.FeatureViewSource.feature_view_id).where(
                        eorm.FeatureViewSource.id.in_(ids)
                    )
                )
            )
            .limit(1)
        )
    )
    if feat_view_refs:
        return InvalidArgumentError(
            "feature views exist that reference feature_view_sources to be deleted"
        )

    await session.execute(
        sa.delete(eorm.FeatureViewSource).where(eorm.FeatureViewSource.id.in_(ids))
    )
    return Ok(None)


async def feature_view_delete_orms(
    ids: Sequence[eorm.FeatureViewID], session: eorm.Session
) -> Ok[None] | InvalidArgumentError:
    space_refs = list(
        await session.execute(
            sa.select(eorm.Space.id).where(eorm.Space.feature_view_id.in_(ids))
        )
    )
    if space_refs:
        return InvalidArgumentError(
            "spaces exist that reference feature_views to be deleted"
        )
    await session.execute(
        sa.delete(eorm.FeatureView).where(eorm.FeatureView.id.in_(ids))
    )
    return Ok(None)


async def space_delete_orms(
    ids: Sequence[eorm.SpaceID], session: eorm.Session
) -> Ok[None] | InvalidArgumentError:
    await session.execute(sa.delete(eorm.Space).where(eorm.Space.id.in_(ids)))
    return Ok(None)


async def room_delete_orms(
    ids: Sequence[eorm.RoomID], session: eorm.Session
) -> Ok[None] | InvalidArgumentError:
    source_refs = list(
        await session.scalars(
            sa.select(eorm.Source).where(eorm.Source.room_id.in_(ids)).limit(1)
        )
    )
    if source_refs:
        return InvalidArgumentError("cannot delete a room that still has sources")

    await session.execute(sa.delete(eorm.Room).where(eorm.Room.id.in_(ids)))
    return Ok(None)


async def data_connector_delete_orms(
    ids: Sequence[eorm.DataConnectorID],
    session: eorm.Session,
) -> Ok[None] | InvalidArgumentError:
    _ = await session.execute(
        sa.delete(eorm.DataConnector).where(eorm.DataConnector.id.in_(ids))
    )
    return Ok(None)


async def pipeline_data_connection_delete_orms(
    pipeline_id: eorm.PipelineID,
    data_connector_id: eorm.DataConnectorID,
    session: eorm.Session,
) -> Ok[None] | InvalidArgumentError:
    _ = await session.execute(
        sa.delete(eorm.PipelineDataConnection).where(
            sa.and_(
                eorm.PipelineDataConnection.pipeline_id == pipeline_id,
                eorm.PipelineDataConnection.data_connector_id == data_connector_id,
            )
        )
    )
    return Ok(None)


async def data_connection_delete_orms(
    ids: Sequence[eorm.DataConnectionID],
    session: eorm.Session,
) -> Ok[None] | InvalidArgumentError:
    _ = await session.execute(
        sa.delete(eorm.DataConnection).where(eorm.DataConnection.id.in_(ids))
    )
    return Ok(None)
