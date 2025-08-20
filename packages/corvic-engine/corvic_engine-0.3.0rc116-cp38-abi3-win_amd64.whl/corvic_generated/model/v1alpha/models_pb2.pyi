from corvic_generated.orm.v1 import data_connector_pb2 as _data_connector_pb2
from corvic_generated.orm.v1 import feature_view_pb2 as _feature_view_pb2
from corvic_generated.orm.v1 import pipeline_pb2 as _pipeline_pb2
from corvic_generated.orm.v1 import space_pb2 as _space_pb2
from corvic_generated.orm.v1 import table_pb2 as _table_pb2
from corvic_generated.status.v1 import event_pb2 as _event_pb2
from google.protobuf import timestamp_pb2 as _timestamp_pb2
from google.protobuf.internal import containers as _containers
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from typing import ClassVar as _ClassVar, Iterable as _Iterable, Mapping as _Mapping, Optional as _Optional, Union as _Union

DESCRIPTOR: _descriptor.FileDescriptor

class Room(_message.Message):
    __slots__ = ("id", "name", "org_id", "created_at")
    ID_FIELD_NUMBER: _ClassVar[int]
    NAME_FIELD_NUMBER: _ClassVar[int]
    ORG_ID_FIELD_NUMBER: _ClassVar[int]
    CREATED_AT_FIELD_NUMBER: _ClassVar[int]
    id: str
    name: str
    org_id: str
    created_at: _timestamp_pb2.Timestamp
    def __init__(self, id: _Optional[str] = ..., name: _Optional[str] = ..., org_id: _Optional[str] = ..., created_at: _Optional[_Union[_timestamp_pb2.Timestamp, _Mapping]] = ...) -> None: ...

class Resource(_message.Message):
    __slots__ = ("id", "name", "description", "mime_type", "url", "size", "md5", "original_path", "etag", "original_modified_at_time", "data_connection_id", "room_id", "org_id", "pipeline_id", "pipeline_input_name", "recent_events", "is_terminal", "created_at")
    ID_FIELD_NUMBER: _ClassVar[int]
    NAME_FIELD_NUMBER: _ClassVar[int]
    DESCRIPTION_FIELD_NUMBER: _ClassVar[int]
    MIME_TYPE_FIELD_NUMBER: _ClassVar[int]
    URL_FIELD_NUMBER: _ClassVar[int]
    SIZE_FIELD_NUMBER: _ClassVar[int]
    MD5_FIELD_NUMBER: _ClassVar[int]
    ORIGINAL_PATH_FIELD_NUMBER: _ClassVar[int]
    ETAG_FIELD_NUMBER: _ClassVar[int]
    ORIGINAL_MODIFIED_AT_TIME_FIELD_NUMBER: _ClassVar[int]
    DATA_CONNECTION_ID_FIELD_NUMBER: _ClassVar[int]
    ROOM_ID_FIELD_NUMBER: _ClassVar[int]
    ORG_ID_FIELD_NUMBER: _ClassVar[int]
    PIPELINE_ID_FIELD_NUMBER: _ClassVar[int]
    PIPELINE_INPUT_NAME_FIELD_NUMBER: _ClassVar[int]
    RECENT_EVENTS_FIELD_NUMBER: _ClassVar[int]
    IS_TERMINAL_FIELD_NUMBER: _ClassVar[int]
    CREATED_AT_FIELD_NUMBER: _ClassVar[int]
    id: str
    name: str
    description: str
    mime_type: str
    url: str
    size: int
    md5: str
    original_path: str
    etag: str
    original_modified_at_time: _timestamp_pb2.Timestamp
    data_connection_id: str
    room_id: str
    org_id: str
    pipeline_id: str
    pipeline_input_name: str
    recent_events: _containers.RepeatedCompositeFieldContainer[_event_pb2.Event]
    is_terminal: bool
    created_at: _timestamp_pb2.Timestamp
    def __init__(self, id: _Optional[str] = ..., name: _Optional[str] = ..., description: _Optional[str] = ..., mime_type: _Optional[str] = ..., url: _Optional[str] = ..., size: _Optional[int] = ..., md5: _Optional[str] = ..., original_path: _Optional[str] = ..., etag: _Optional[str] = ..., original_modified_at_time: _Optional[_Union[_timestamp_pb2.Timestamp, _Mapping]] = ..., data_connection_id: _Optional[str] = ..., room_id: _Optional[str] = ..., org_id: _Optional[str] = ..., pipeline_id: _Optional[str] = ..., pipeline_input_name: _Optional[str] = ..., recent_events: _Optional[_Iterable[_Union[_event_pb2.Event, _Mapping]]] = ..., is_terminal: bool = ..., created_at: _Optional[_Union[_timestamp_pb2.Timestamp, _Mapping]] = ...) -> None: ...

class Source(_message.Message):
    __slots__ = ("id", "name", "table_op_graph", "room_id", "org_id", "pipeline_id", "created_at", "prop_table_op_graph")
    ID_FIELD_NUMBER: _ClassVar[int]
    NAME_FIELD_NUMBER: _ClassVar[int]
    TABLE_OP_GRAPH_FIELD_NUMBER: _ClassVar[int]
    ROOM_ID_FIELD_NUMBER: _ClassVar[int]
    ORG_ID_FIELD_NUMBER: _ClassVar[int]
    PIPELINE_ID_FIELD_NUMBER: _ClassVar[int]
    CREATED_AT_FIELD_NUMBER: _ClassVar[int]
    PROP_TABLE_OP_GRAPH_FIELD_NUMBER: _ClassVar[int]
    id: str
    name: str
    table_op_graph: _table_pb2.TableComputeOp
    room_id: str
    org_id: str
    pipeline_id: str
    created_at: _timestamp_pb2.Timestamp
    prop_table_op_graph: _table_pb2.TableComputeOp
    def __init__(self, id: _Optional[str] = ..., name: _Optional[str] = ..., table_op_graph: _Optional[_Union[_table_pb2.TableComputeOp, _Mapping]] = ..., room_id: _Optional[str] = ..., org_id: _Optional[str] = ..., pipeline_id: _Optional[str] = ..., created_at: _Optional[_Union[_timestamp_pb2.Timestamp, _Mapping]] = ..., prop_table_op_graph: _Optional[_Union[_table_pb2.TableComputeOp, _Mapping]] = ...) -> None: ...

class Pipeline(_message.Message):
    __slots__ = ("id", "name", "description", "room_id", "source_outputs", "pipeline_transformation", "org_id", "created_at")
    class SourceOutputsEntry(_message.Message):
        __slots__ = ("key", "value")
        KEY_FIELD_NUMBER: _ClassVar[int]
        VALUE_FIELD_NUMBER: _ClassVar[int]
        key: str
        value: Source
        def __init__(self, key: _Optional[str] = ..., value: _Optional[_Union[Source, _Mapping]] = ...) -> None: ...
    ID_FIELD_NUMBER: _ClassVar[int]
    NAME_FIELD_NUMBER: _ClassVar[int]
    DESCRIPTION_FIELD_NUMBER: _ClassVar[int]
    ROOM_ID_FIELD_NUMBER: _ClassVar[int]
    SOURCE_OUTPUTS_FIELD_NUMBER: _ClassVar[int]
    PIPELINE_TRANSFORMATION_FIELD_NUMBER: _ClassVar[int]
    ORG_ID_FIELD_NUMBER: _ClassVar[int]
    CREATED_AT_FIELD_NUMBER: _ClassVar[int]
    id: str
    name: str
    description: str
    room_id: str
    source_outputs: _containers.MessageMap[str, Source]
    pipeline_transformation: _pipeline_pb2.PipelineTransformation
    org_id: str
    created_at: _timestamp_pb2.Timestamp
    def __init__(self, id: _Optional[str] = ..., name: _Optional[str] = ..., description: _Optional[str] = ..., room_id: _Optional[str] = ..., source_outputs: _Optional[_Mapping[str, Source]] = ..., pipeline_transformation: _Optional[_Union[_pipeline_pb2.PipelineTransformation, _Mapping]] = ..., org_id: _Optional[str] = ..., created_at: _Optional[_Union[_timestamp_pb2.Timestamp, _Mapping]] = ...) -> None: ...

class FeatureViewSource(_message.Message):
    __slots__ = ("id", "source", "table_op_graph", "drop_disconnected", "org_id", "created_at", "room_id")
    ID_FIELD_NUMBER: _ClassVar[int]
    SOURCE_FIELD_NUMBER: _ClassVar[int]
    TABLE_OP_GRAPH_FIELD_NUMBER: _ClassVar[int]
    DROP_DISCONNECTED_FIELD_NUMBER: _ClassVar[int]
    ORG_ID_FIELD_NUMBER: _ClassVar[int]
    CREATED_AT_FIELD_NUMBER: _ClassVar[int]
    ROOM_ID_FIELD_NUMBER: _ClassVar[int]
    id: str
    source: Source
    table_op_graph: _table_pb2.TableComputeOp
    drop_disconnected: bool
    org_id: str
    created_at: _timestamp_pb2.Timestamp
    room_id: str
    def __init__(self, id: _Optional[str] = ..., source: _Optional[_Union[Source, _Mapping]] = ..., table_op_graph: _Optional[_Union[_table_pb2.TableComputeOp, _Mapping]] = ..., drop_disconnected: bool = ..., org_id: _Optional[str] = ..., created_at: _Optional[_Union[_timestamp_pb2.Timestamp, _Mapping]] = ..., room_id: _Optional[str] = ...) -> None: ...

class FeatureView(_message.Message):
    __slots__ = ("id", "name", "description", "room_id", "feature_view_output", "feature_view_sources", "space_ids", "org_id", "created_at")
    ID_FIELD_NUMBER: _ClassVar[int]
    NAME_FIELD_NUMBER: _ClassVar[int]
    DESCRIPTION_FIELD_NUMBER: _ClassVar[int]
    ROOM_ID_FIELD_NUMBER: _ClassVar[int]
    FEATURE_VIEW_OUTPUT_FIELD_NUMBER: _ClassVar[int]
    FEATURE_VIEW_SOURCES_FIELD_NUMBER: _ClassVar[int]
    SPACE_IDS_FIELD_NUMBER: _ClassVar[int]
    ORG_ID_FIELD_NUMBER: _ClassVar[int]
    CREATED_AT_FIELD_NUMBER: _ClassVar[int]
    id: str
    name: str
    description: str
    room_id: str
    feature_view_output: _feature_view_pb2.FeatureViewOutput
    feature_view_sources: _containers.RepeatedCompositeFieldContainer[FeatureViewSource]
    space_ids: _containers.RepeatedScalarFieldContainer[str]
    org_id: str
    created_at: _timestamp_pb2.Timestamp
    def __init__(self, id: _Optional[str] = ..., name: _Optional[str] = ..., description: _Optional[str] = ..., room_id: _Optional[str] = ..., feature_view_output: _Optional[_Union[_feature_view_pb2.FeatureViewOutput, _Mapping]] = ..., feature_view_sources: _Optional[_Iterable[_Union[FeatureViewSource, _Mapping]]] = ..., space_ids: _Optional[_Iterable[str]] = ..., org_id: _Optional[str] = ..., created_at: _Optional[_Union[_timestamp_pb2.Timestamp, _Mapping]] = ...) -> None: ...

class Space(_message.Message):
    __slots__ = ("id", "name", "description", "room_id", "space_parameters", "feature_view", "auto_sync", "org_id", "created_at")
    ID_FIELD_NUMBER: _ClassVar[int]
    NAME_FIELD_NUMBER: _ClassVar[int]
    DESCRIPTION_FIELD_NUMBER: _ClassVar[int]
    ROOM_ID_FIELD_NUMBER: _ClassVar[int]
    SPACE_PARAMETERS_FIELD_NUMBER: _ClassVar[int]
    FEATURE_VIEW_FIELD_NUMBER: _ClassVar[int]
    AUTO_SYNC_FIELD_NUMBER: _ClassVar[int]
    ORG_ID_FIELD_NUMBER: _ClassVar[int]
    CREATED_AT_FIELD_NUMBER: _ClassVar[int]
    id: str
    name: str
    description: str
    room_id: str
    space_parameters: _space_pb2.SpaceParameters
    feature_view: FeatureView
    auto_sync: bool
    org_id: str
    created_at: _timestamp_pb2.Timestamp
    def __init__(self, id: _Optional[str] = ..., name: _Optional[str] = ..., description: _Optional[str] = ..., room_id: _Optional[str] = ..., space_parameters: _Optional[_Union[_space_pb2.SpaceParameters, _Mapping]] = ..., feature_view: _Optional[_Union[FeatureView, _Mapping]] = ..., auto_sync: bool = ..., org_id: _Optional[str] = ..., created_at: _Optional[_Union[_timestamp_pb2.Timestamp, _Mapping]] = ...) -> None: ...

class DataConnector(_message.Message):
    __slots__ = ("id", "name", "org_id", "parameters", "base_path", "secret_key", "last_validation_time", "last_successful_validation", "created_at")
    ID_FIELD_NUMBER: _ClassVar[int]
    NAME_FIELD_NUMBER: _ClassVar[int]
    ORG_ID_FIELD_NUMBER: _ClassVar[int]
    PARAMETERS_FIELD_NUMBER: _ClassVar[int]
    BASE_PATH_FIELD_NUMBER: _ClassVar[int]
    SECRET_KEY_FIELD_NUMBER: _ClassVar[int]
    LAST_VALIDATION_TIME_FIELD_NUMBER: _ClassVar[int]
    LAST_SUCCESSFUL_VALIDATION_FIELD_NUMBER: _ClassVar[int]
    CREATED_AT_FIELD_NUMBER: _ClassVar[int]
    id: str
    name: str
    org_id: str
    parameters: _data_connector_pb2.DataConnectorParameters
    base_path: str
    secret_key: str
    last_validation_time: _timestamp_pb2.Timestamp
    last_successful_validation: _timestamp_pb2.Timestamp
    created_at: _timestamp_pb2.Timestamp
    def __init__(self, id: _Optional[str] = ..., name: _Optional[str] = ..., org_id: _Optional[str] = ..., parameters: _Optional[_Union[_data_connector_pb2.DataConnectorParameters, _Mapping]] = ..., base_path: _Optional[str] = ..., secret_key: _Optional[str] = ..., last_validation_time: _Optional[_Union[_timestamp_pb2.Timestamp, _Mapping]] = ..., last_successful_validation: _Optional[_Union[_timestamp_pb2.Timestamp, _Mapping]] = ..., created_at: _Optional[_Union[_timestamp_pb2.Timestamp, _Mapping]] = ...) -> None: ...

class PipelineDataConnection(_message.Message):
    __slots__ = ("pipeline_id", "data_connector", "room_id", "org_id", "prefix", "glob", "last_ingestion_time", "last_successful_ingestion_time", "created_at", "interval_seconds", "watermark_time")
    PIPELINE_ID_FIELD_NUMBER: _ClassVar[int]
    DATA_CONNECTOR_FIELD_NUMBER: _ClassVar[int]
    ROOM_ID_FIELD_NUMBER: _ClassVar[int]
    ORG_ID_FIELD_NUMBER: _ClassVar[int]
    PREFIX_FIELD_NUMBER: _ClassVar[int]
    GLOB_FIELD_NUMBER: _ClassVar[int]
    LAST_INGESTION_TIME_FIELD_NUMBER: _ClassVar[int]
    LAST_SUCCESSFUL_INGESTION_TIME_FIELD_NUMBER: _ClassVar[int]
    CREATED_AT_FIELD_NUMBER: _ClassVar[int]
    INTERVAL_SECONDS_FIELD_NUMBER: _ClassVar[int]
    WATERMARK_TIME_FIELD_NUMBER: _ClassVar[int]
    pipeline_id: str
    data_connector: DataConnector
    room_id: str
    org_id: str
    prefix: str
    glob: str
    last_ingestion_time: _timestamp_pb2.Timestamp
    last_successful_ingestion_time: _timestamp_pb2.Timestamp
    created_at: _timestamp_pb2.Timestamp
    interval_seconds: int
    watermark_time: _timestamp_pb2.Timestamp
    def __init__(self, pipeline_id: _Optional[str] = ..., data_connector: _Optional[_Union[DataConnector, _Mapping]] = ..., room_id: _Optional[str] = ..., org_id: _Optional[str] = ..., prefix: _Optional[str] = ..., glob: _Optional[str] = ..., last_ingestion_time: _Optional[_Union[_timestamp_pb2.Timestamp, _Mapping]] = ..., last_successful_ingestion_time: _Optional[_Union[_timestamp_pb2.Timestamp, _Mapping]] = ..., created_at: _Optional[_Union[_timestamp_pb2.Timestamp, _Mapping]] = ..., interval_seconds: _Optional[int] = ..., watermark_time: _Optional[_Union[_timestamp_pb2.Timestamp, _Mapping]] = ...) -> None: ...

class DataConnection(_message.Message):
    __slots__ = ("id", "pipeline_id", "data_connector", "room_id", "org_id", "prefix", "glob", "last_ingestion_time", "last_successful_ingestion_time", "created_at", "interval_seconds", "watermark_time")
    ID_FIELD_NUMBER: _ClassVar[int]
    PIPELINE_ID_FIELD_NUMBER: _ClassVar[int]
    DATA_CONNECTOR_FIELD_NUMBER: _ClassVar[int]
    ROOM_ID_FIELD_NUMBER: _ClassVar[int]
    ORG_ID_FIELD_NUMBER: _ClassVar[int]
    PREFIX_FIELD_NUMBER: _ClassVar[int]
    GLOB_FIELD_NUMBER: _ClassVar[int]
    LAST_INGESTION_TIME_FIELD_NUMBER: _ClassVar[int]
    LAST_SUCCESSFUL_INGESTION_TIME_FIELD_NUMBER: _ClassVar[int]
    CREATED_AT_FIELD_NUMBER: _ClassVar[int]
    INTERVAL_SECONDS_FIELD_NUMBER: _ClassVar[int]
    WATERMARK_TIME_FIELD_NUMBER: _ClassVar[int]
    id: str
    pipeline_id: str
    data_connector: DataConnector
    room_id: str
    org_id: str
    prefix: str
    glob: str
    last_ingestion_time: _timestamp_pb2.Timestamp
    last_successful_ingestion_time: _timestamp_pb2.Timestamp
    created_at: _timestamp_pb2.Timestamp
    interval_seconds: int
    watermark_time: _timestamp_pb2.Timestamp
    def __init__(self, id: _Optional[str] = ..., pipeline_id: _Optional[str] = ..., data_connector: _Optional[_Union[DataConnector, _Mapping]] = ..., room_id: _Optional[str] = ..., org_id: _Optional[str] = ..., prefix: _Optional[str] = ..., glob: _Optional[str] = ..., last_ingestion_time: _Optional[_Union[_timestamp_pb2.Timestamp, _Mapping]] = ..., last_successful_ingestion_time: _Optional[_Union[_timestamp_pb2.Timestamp, _Mapping]] = ..., created_at: _Optional[_Union[_timestamp_pb2.Timestamp, _Mapping]] = ..., interval_seconds: _Optional[int] = ..., watermark_time: _Optional[_Union[_timestamp_pb2.Timestamp, _Mapping]] = ...) -> None: ...
