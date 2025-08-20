"""Defines a sqlalchemy function for time_offset."""

import datetime
from typing import Any

from sqlalchemy import sql
from sqlalchemy.ext.compiler import compiles
from sqlalchemy.types import DateTime


class TimeOffset(sql.expression.FunctionElement[Any]):
    """Adds a time_offset() expression based on backend db used."""

    type = DateTime(timezone=True)
    inherit_cache = True

    def __init__(
        self,
        datetime_column: sql.expression.ColumnElement[datetime.datetime | None],
        offset_seconds_column: sql.expression.ColumnElement[int | None],
    ):
        self.datetime_column = datetime_column
        self.offset_seconds_column = offset_seconds_column

        super().__init__(self.datetime_column, self.offset_seconds_column)


@compiles(TimeOffset, "postgresql")
def pg_time_offset(
    element: sql.expression.FunctionElement[Any],
    compiler: sql.compiler.SQLCompiler,
    **kw: Any,
):
    """Compile time_offset for postgres."""
    match element:
        case TimeOffset() as time_offset_elem:
            datetime_col = compiler.process(time_offset_elem.datetime_column, **kw)
            offset_col = compiler.process(time_offset_elem.offset_seconds_column, **kw)
            return (
                f"TIMEZONE('utc', {datetime_col} "
                + f"+ ({offset_col} || ' seconds')::interval)"
            )

        case _:
            raise TypeError("unexpected type")


@compiles(TimeOffset)
def default_sql_time_offset(
    element: sql.expression.FunctionElement[Any],
    compiler: sql.compiler.SQLCompiler,
    **kw: Any,
):
    """Compile time_offset for other databases."""
    # this matches sqlalchemy.func.now() and is valid for postgresql
    match element:
        case TimeOffset():
            raise RuntimeError("timestamp offsets not supported for this backend")
        case _:
            raise TypeError("unexpected type")


@compiles(TimeOffset, "sqlite")
def sqlite_sql_time_offset(
    element: sql.expression.FunctionElement[Any],
    compiler: sql.compiler.SQLCompiler,
    **kw: Any,
):
    """Compile time_offset for sqlite."""
    match element:
        case TimeOffset() as time_offset_elem:
            datetime_col = compiler.process(time_offset_elem.datetime_column, **kw)
            offset_col = compiler.process(time_offset_elem.offset_seconds_column, **kw)

            # SQLite does not natively support DATE, TIME or DATETIME. Instead,
            # SQLAlchemy represents these values as "iso strings" for which
            # textual comparisons are the same as time comparisons (and vice
            # versa) [1, 2].
            #
            # [1] https://docs.sqlalchemy.org/en/20/dialects/sqlite.html#date-and-time-types
            # [2] https://github.com/sqlalchemy/sqlalchemy/blob/main/lib/sqlalchemy/dialects/sqlite/base.py#L1018
            # [3] https://www.sqlite.org/lang_datefunc.html
            return (
                f"(STRFTIME('%Y-%m-%d %H:%M:%f000', {datetime_col}, "
                + f"'+' || {offset_col} || ' seconds'))"
            )
        case _:
            raise TypeError("unexpected type")
