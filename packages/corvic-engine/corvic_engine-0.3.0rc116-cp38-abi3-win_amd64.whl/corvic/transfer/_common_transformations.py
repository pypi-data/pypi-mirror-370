import datetime
import uuid
from typing import Any, TypeVar

from google.protobuf import timestamp_pb2

from corvic import orm
from corvic.result import Ok

OrmIdT = TypeVar("OrmIdT", bound=orm.BaseID[Any])

UNCOMMITTED_ID_PREFIX = "__uncommitted_object-"


def generate_uncommitted_id_str():
    return f"{UNCOMMITTED_ID_PREFIX}{uuid.uuid4()}"


def translate_orm_id(
    obj_id: str, id_class: type[OrmIdT]
) -> Ok[OrmIdT | None] | orm.InvalidORMIdentifierError:
    if obj_id.startswith(UNCOMMITTED_ID_PREFIX):
        return Ok(None)
    parsed_obj_id = id_class(obj_id)
    match parsed_obj_id.to_db():
        case orm.InvalidORMIdentifierError() as err:
            return err
        case Ok():
            return Ok(parsed_obj_id)


def translate_nongenerated_orm_id(
    proto_id: str, obj_id_class: type[OrmIdT]
) -> Ok[OrmIdT] | orm.InvalidORMIdentifierError:
    if proto_id.startswith(UNCOMMITTED_ID_PREFIX):
        return orm.InvalidORMIdentifierError(
            "non generated orm id starts with uncommitted prefix"
        )
    obj_id = obj_id_class.from_str(proto_id)
    match obj_id.to_db():
        case orm.InvalidORMIdentifierError() as err:
            return err
        case Ok():
            return Ok(obj_id)


def non_empty_timestamp_to_datetime(
    timestamp: timestamp_pb2.Timestamp,
) -> datetime.datetime | None:
    if timestamp != timestamp_pb2.Timestamp():
        return timestamp.ToDatetime(tzinfo=datetime.UTC)
    return None
