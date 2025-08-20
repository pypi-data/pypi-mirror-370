"""Corvic feature schemas."""

from __future__ import annotations

from typing import Any, Final, overload

from corvic import eorm
from corvic.op_graph.errors import OpParseError
from corvic.proto_wrapper import OneofProtoWrapper
from corvic.result import InvalidArgumentError
from corvic_generated.orm.v1 import table_pb2


@overload
def from_proto(proto: table_pb2.FeatureType) -> FeatureType: ...


@overload
def from_proto(proto: table_pb2.TextFeatureType, *, is_excluded: bool) -> Text: ...


@overload
def from_proto(
    proto: table_pb2.CategoricalFeatureType, *, is_excluded: bool
) -> Categorical: ...


@overload
def from_proto(
    proto: table_pb2.PrimaryKeyFeatureType, *, is_excluded: bool
) -> PrimaryKey: ...


@overload
def from_proto(
    proto: table_pb2.ForeignKeyFeatureType, *, is_excluded: bool
) -> ForeignKey: ...


@overload
def from_proto(
    proto: table_pb2.IdentifierFeatureType, *, is_excluded: bool
) -> Identifier: ...


@overload
def from_proto(
    proto: table_pb2.NumericalFeatureType, *, is_excluded: bool
) -> Numerical: ...


@overload
def from_proto(
    proto: table_pb2.MultiCategoricalFeatureType, *, is_excluded: bool
) -> MultiCategorical: ...


@overload
def from_proto(
    proto: table_pb2.TimestampFeatureType, *, is_excluded: bool
) -> Timestamp: ...


@overload
def from_proto(
    proto: table_pb2.EmbeddingFeatureType, *, is_excluded: bool
) -> Embedding: ...


@overload
def from_proto(
    proto: table_pb2.UnknownFeatureType, *, is_excluded: bool
) -> Unknown: ...


@overload
def from_proto(proto: table_pb2.ImageFeatureType, *, is_excluded: bool) -> Unknown: ...


def from_proto(  # noqa: C901
    proto: (
        table_pb2.FeatureType
        | table_pb2.TextFeatureType
        | table_pb2.CategoricalFeatureType
        | table_pb2.PrimaryKeyFeatureType
        | table_pb2.ForeignKeyFeatureType
        | table_pb2.IdentifierFeatureType
        | table_pb2.NumericalFeatureType
        | table_pb2.MultiCategoricalFeatureType
        | table_pb2.TimestampFeatureType
        | table_pb2.EmbeddingFeatureType
        | table_pb2.UnknownFeatureType
        | table_pb2.ImageFeatureType
    ),
    *,
    is_excluded: bool = False,
) -> FeatureType:
    """Create a FeatureType wrapper around a FeatureType protobuf message."""
    match proto:
        case table_pb2.FeatureType():
            return _from_feature_type(proto)
        case table_pb2.TextFeatureType():
            return Text(table_pb2.FeatureType(text=proto))
        case table_pb2.CategoricalFeatureType():
            return Categorical(
                table_pb2.FeatureType(categorical=proto, is_excluded=is_excluded)
            )
        case table_pb2.PrimaryKeyFeatureType():
            return PrimaryKey(
                table_pb2.FeatureType(primary_key=proto, is_excluded=is_excluded)
            )
        case table_pb2.ForeignKeyFeatureType():
            return ForeignKey(
                table_pb2.FeatureType(foreign_key=proto, is_excluded=is_excluded)
            )
        case table_pb2.IdentifierFeatureType():
            return Identifier(
                table_pb2.FeatureType(identifier=proto, is_excluded=is_excluded)
            )
        case table_pb2.NumericalFeatureType():
            return Numerical(
                table_pb2.FeatureType(numerical=proto, is_excluded=is_excluded)
            )
        case table_pb2.MultiCategoricalFeatureType():
            return MultiCategorical(
                table_pb2.FeatureType(multi_categorical=proto, is_excluded=is_excluded)
            )
        case table_pb2.TimestampFeatureType():
            return Timestamp(
                table_pb2.FeatureType(timestamp=proto, is_excluded=is_excluded)
            )
        case table_pb2.EmbeddingFeatureType():
            return Embedding(
                table_pb2.FeatureType(embedding=proto, is_excluded=is_excluded)
            )
        case table_pb2.UnknownFeatureType():
            return Unknown(
                table_pb2.FeatureType(unknown=proto, is_excluded=is_excluded)
            )
        case table_pb2.ImageFeatureType():
            return Image(table_pb2.FeatureType(image=proto, is_excluded=is_excluded))


def _from_feature_type(proto: table_pb2.FeatureType):
    field_name = proto.WhichOneof(_Base.oneof_name())
    new_feature_type = _FEATURE_FIELD_NAME_TO_FEATURE_TYPE.get(field_name)
    if new_feature_type is None:
        raise InvalidArgumentError(
            "unsupported feature type", operation_type=field_name
        )
    return new_feature_type(proto)


def from_bytes(serialized_proto: bytes) -> FeatureType:
    """Deserialize a FeatureType protobuf message directly into a wrapper."""
    proto = table_pb2.FeatureType()
    proto.ParseFromString(serialized_proto)
    return from_proto(proto)


class _Base(OneofProtoWrapper[table_pb2.FeatureType]):
    """Base type for all feature types."""

    _is_excluded: bool

    @classmethod
    def oneof_name(cls) -> str:
        return "feature"

    @classmethod
    def expected_oneof_field(cls) -> str:
        """Returns the name of field for this type in the root proto op type."""
        if cls not in _FEATURE_TYPE_TO_FEATURE_FIELD_NAME:
            raise OpParseError(
                "operation field name must registered in "
                + "_FEATURE_TYPE_TO_FEATURE_FIELD_NAME"
            )
        return _FEATURE_TYPE_TO_FEATURE_FIELD_NAME[cls]

    @property
    def is_excluded(self) -> bool:
        return self._proto.is_excluded


class Text(_Base):
    """Column should be treated like text."""


class Categorical(_Base):
    """Column should be treated like a categorical feature."""


class PrimaryKey(_Base):
    """Column should be treated like a primary key."""


class ForeignKey(_Base):
    """Column should be treated like a foreign key."""

    __match_args__ = ("referenced_source_id",)

    @property
    def referenced_source_id(self) -> eorm.SourceID:
        return eorm.SourceID(self._proto.foreign_key.referenced_source_id)


class Identifier(_Base):
    """Column should be treated like an identifier."""


class Numerical(_Base):
    """Column should be treated like a numerical feature."""


class MultiCategorical(_Base):
    """Column should be treated like a multi categorical feature."""


class Timestamp(_Base):
    """Column should be treated like a timestamp."""


class Embedding(_Base):
    """Column should be treated like an embedding."""


class Unknown(_Base):
    """The feature type is not known."""


class Image(_Base):
    """Column should be treated like an image."""


def text(*, is_excluded: bool = False):
    """Build a Text FeatureType."""
    return from_proto(table_pb2.TextFeatureType(), is_excluded=is_excluded)


def categorical(*, is_excluded: bool = False):
    """Build a Categorical FeatureType."""
    return from_proto(table_pb2.CategoricalFeatureType(), is_excluded=is_excluded)


def primary_key(*, is_excluded: bool = False):
    """Build a PrimaryKey FeatureType."""
    return from_proto(table_pb2.PrimaryKeyFeatureType(), is_excluded=is_excluded)


def foreign_key(
    referenced_source_id: eorm.SourceID, *, is_excluded: bool = False
) -> ForeignKey:
    """Build a ForeignKey FeatureType."""
    return from_proto(
        table_pb2.ForeignKeyFeatureType(referenced_source_id=str(referenced_source_id)),
        is_excluded=is_excluded,
    )


def identifier(*, is_excluded: bool = False) -> Identifier:
    """Build an Identifier FeatureType."""
    return from_proto(table_pb2.IdentifierFeatureType(), is_excluded=is_excluded)


def numerical(*, is_excluded: bool = False):
    """Build a Numerical FeatureType."""
    return from_proto(table_pb2.NumericalFeatureType(), is_excluded=is_excluded)


def multi_categorical(*, is_excluded: bool = False):
    """Build a MultiCategorical FeatureType."""
    return from_proto(table_pb2.MultiCategoricalFeatureType(), is_excluded=is_excluded)


def timestamp(*, is_excluded: bool = False):
    """Build a Timestamp FeatureType."""
    return from_proto(table_pb2.TimestampFeatureType(), is_excluded=is_excluded)


def embedding(*, is_excluded: bool = False):
    """Build an Embedding FeatureType."""
    return from_proto(table_pb2.EmbeddingFeatureType(), is_excluded=is_excluded)


def unknown(*, is_excluded: bool = False):
    """Build an Unknown FeatureType."""
    return from_proto(table_pb2.UnknownFeatureType(), is_excluded=is_excluded)


def image(*, is_excluded: bool = False):
    """Build an Image FeatureType."""
    return from_proto(table_pb2.ImageFeatureType(), is_excluded=is_excluded)


FeatureType = (
    Text
    | Categorical
    | PrimaryKey
    | ForeignKey
    | Identifier
    | Numerical
    | MultiCategorical
    | Timestamp
    | Embedding
    | Unknown
    | Image
)

_FEATURE_FIELD_NAME_TO_FEATURE_TYPE: Final = {
    "text": Text,
    "categorical": Categorical,
    "primary_key": PrimaryKey,
    "foreign_key": ForeignKey,
    "identifier": Identifier,
    "numerical": Numerical,
    "multi_categorical": MultiCategorical,
    "timestamp": Timestamp,
    "embedding": Embedding,
    "unknown": Unknown,
    "image": Image,
}

_FEATURE_TYPE_TO_FEATURE_FIELD_NAME: Final[dict[type[Any], str]] = {
    op: name for name, op in _FEATURE_FIELD_NAME_TO_FEATURE_TYPE.items()
}
