from buf.validate import validate_pb2 as _validate_pb2
from google.protobuf.internal import containers as _containers
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from typing import ClassVar as _ClassVar, Iterable as _Iterable, Mapping as _Mapping, Optional as _Optional, Union as _Union

DESCRIPTOR: _descriptor.FileDescriptor

class OutputSource(_message.Message):
    __slots__ = ("source_id",)
    SOURCE_ID_FIELD_NUMBER: _ClassVar[int]
    source_id: str
    def __init__(self, source_id: _Optional[str] = ...) -> None: ...

class ForeignKeyRelationship(_message.Message):
    __slots__ = ("foreign_key_having_source_id", "foreign_key_column_name", "referenced_source_id", "primary_key_column_name")
    FOREIGN_KEY_HAVING_SOURCE_ID_FIELD_NUMBER: _ClassVar[int]
    FOREIGN_KEY_COLUMN_NAME_FIELD_NUMBER: _ClassVar[int]
    REFERENCED_SOURCE_ID_FIELD_NUMBER: _ClassVar[int]
    PRIMARY_KEY_COLUMN_NAME_FIELD_NUMBER: _ClassVar[int]
    foreign_key_having_source_id: str
    foreign_key_column_name: str
    referenced_source_id: str
    primary_key_column_name: str
    def __init__(self, foreign_key_having_source_id: _Optional[str] = ..., foreign_key_column_name: _Optional[str] = ..., referenced_source_id: _Optional[str] = ..., primary_key_column_name: _Optional[str] = ...) -> None: ...

class FeatureViewRelationship(_message.Message):
    __slots__ = ("start_source_id", "end_source_id", "foreign_key_relationship", "join_column_name")
    START_SOURCE_ID_FIELD_NUMBER: _ClassVar[int]
    END_SOURCE_ID_FIELD_NUMBER: _ClassVar[int]
    FOREIGN_KEY_RELATIONSHIP_FIELD_NUMBER: _ClassVar[int]
    JOIN_COLUMN_NAME_FIELD_NUMBER: _ClassVar[int]
    start_source_id: str
    end_source_id: str
    foreign_key_relationship: ForeignKeyRelationship
    join_column_name: str
    def __init__(self, start_source_id: _Optional[str] = ..., end_source_id: _Optional[str] = ..., foreign_key_relationship: _Optional[_Union[ForeignKeyRelationship, _Mapping]] = ..., join_column_name: _Optional[str] = ...) -> None: ...

class FeatureViewOutput(_message.Message):
    __slots__ = ("relationships", "output_sources")
    RELATIONSHIPS_FIELD_NUMBER: _ClassVar[int]
    OUTPUT_SOURCES_FIELD_NUMBER: _ClassVar[int]
    relationships: _containers.RepeatedCompositeFieldContainer[FeatureViewRelationship]
    output_sources: _containers.RepeatedCompositeFieldContainer[OutputSource]
    def __init__(self, relationships: _Optional[_Iterable[_Union[FeatureViewRelationship, _Mapping]]] = ..., output_sources: _Optional[_Iterable[_Union[OutputSource, _Mapping]]] = ...) -> None: ...
