"""Corvic sqlalchemy functions."""

import datetime

from sqlalchemy import orm as sa_orm
from sqlalchemy import sql

from corvic.orm.func.time_offset_func import TimeOffset as _TimeOffset
from corvic.orm.func.utc_func import UTCNow as _UTCNow
from corvic.orm.func.uuid_func import UUIDFunction as _UUIDFunction


def utc_now(offset: datetime.timedelta | None = None):
    """Sqlalchemy function returning utc now."""
    return _UTCNow(offset=offset)


def time_offset(
    datetime_column: sa_orm.InstrumentedAttribute[datetime.datetime | None]
    | sql.expression.ColumnElement[datetime.datetime | None],
    offset_seconds_column: sa_orm.InstrumentedAttribute[int | None]
    | sql.expression.ColumnElement[int | None],
):
    """Sqlalchemy function returning a time offset."""
    return _TimeOffset(
        datetime_column=datetime_column.expression,
        offset_seconds_column=offset_seconds_column.expression,
    )


def gen_uuid():
    """Sqlalchemy function returning a random uuid."""
    return _UUIDFunction()


__all__ = ["utc_now", "gen_uuid", "time_offset"]
