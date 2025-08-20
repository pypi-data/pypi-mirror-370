"""Object-Relational Mappings."""

from __future__ import annotations

from collections.abc import Callable
from datetime import UTC, datetime
from typing import Any, ClassVar, cast

import sqlalchemy as sa
from sqlalchemy import event as sa_event
from sqlalchemy import orm as sa_orm
from sqlalchemy.ext.asyncio import AsyncAttrs
from sqlalchemy.ext.hybrid import hybrid_property

import corvic.context
from corvic.orm._proto_columns import ProtoMessageDecorator
from corvic.orm._soft_delete import (
    BadDeleteError,
    Session,
    SoftDeleteMixin,
    live_unique_constraint,
)
from corvic.orm.errors import (
    DeletedObjectError,
    InvalidORMIdentifierError,
    RequestedObjectsForNobodyError,
    dbapi_error_to_result,
)
from corvic.orm.func import time_offset, utc_now
from corvic.orm.ids import (
    BaseID,
    BaseIDFromInt,
    BaseIDFromStr,
    IntIDDecorator,
    StrIDDecorator,
)
from corvic.orm.keys import (
    INT_PK_TYPE,
    ForeignKey,
    primary_key_foreign_column,
    primary_key_identity_column,
    primary_key_uuid_column,
)
from corvic.result import InvalidArgumentError


class OrgID(BaseIDFromStr):
    """A unique identifier for an organization."""

    @property
    def is_super_user(self):
        return self._value == corvic.context.SUPERUSER_ORG_ID

    @property
    def is_nobody(self):
        return self._value == corvic.context.NOBODY_ORG_ID


# A quick primer on SQLAlchemy (sa) hybrid methods:
#
# Hybrid just means functionality that is different at the class-level versus
# the instance-level, and in the sa documentation, the authors really
# want to stress that class-versus-instance (decorators) is orthgonal to an
# ORM.
#
# However, this distinction is not particularly helpful for users of sa.
# It is best to have a working model of instance-level means Python-world and
# class-level means SQL-world. So, a hybrid method is something that has
# a different Python representation from its SQL representation.
#
# Since sa already handles conversions like "Python str" to "SQL text",
# certain representation differences between Python and SQL are already handled
# (not considered differences at all).
#
# Hybrid methods are for cases where we want to do non-trivial transformations
# between SQL and Python representations.
#
# The recipe is:
#
# 1. Define a hybrid_method / hybrid_property (wlog property) that produces the Python
#    object you want.
# 2. If the property doesn't need to be used in any sa query again, you are done.
# 3. If the property is simple enough for sa to also use it to produce the SQL
#    representation, you are also done. E.g., comparisons and bitwise operations
#    on columns.
# 4. Otherwise, you need to define a class-level function, hybrid_property.expression,
#    which gives the SQL representation of your property when it is passed to
#    a sa query.
# 5. Because of how redefining decorators is supposed to work in Python [1], you
#    should use @<property_method_name>.inplace.expression to define your
#    class-level function that describes how the property should be represented
#    in SQL.
#
# [1] https://docs.sqlalchemy.org/en/20/orm/extensions/hybrid.html#using-inplace-to-create-pep-484-compliant-hybrid-properties


class Base(sa_orm.MappedAsDataclass, sa_orm.DeclarativeBase, AsyncAttrs):
    """Base class for all DB mapped classes."""

    type_annotation_map: ClassVar = {
        OrgID: StrIDDecorator(OrgID()),
    }

    _created_at: sa_orm.Mapped[datetime] = sa_orm.mapped_column(
        "created_at",
        sa.DateTime(timezone=True),
        server_default=utc_now(),
        init=False,
        index=True,
    )

    _updated_at: sa_orm.Mapped[datetime] = sa_orm.mapped_column(
        "updated_at",
        sa.DateTime(timezone=True),
        onupdate=utc_now(),
        server_default=utc_now(),
        init=False,
        nullable=True,
    )

    @hybrid_property
    def created_at(self) -> datetime | None:
        if not self._created_at:
            return None
        return self._created_at.replace(tzinfo=UTC)

    @created_at.inplace.expression
    @classmethod
    def _created_at_expression(cls):
        return cls._created_at

    @hybrid_property
    def updated_at(self) -> datetime | None:
        if not self._updated_at:
            return None
        return self._updated_at.replace(tzinfo=UTC)

    @updated_at.inplace.expression
    @classmethod
    def _updated_at_expression(cls):
        return cls._updated_at


class Org(SoftDeleteMixin, Base, kw_only=True):
    """An organization is a top-level grouping of resources."""

    __tablename__ = "org"

    id: sa_orm.Mapped[OrgID | None] = primary_key_uuid_column()

    @property
    def name(self) -> str:
        return str(self.id)


def _filter_org_objects(orm_execute_state: sa_orm.ORMExecuteState):
    if all(
        not issubclass(mapper.class_, BelongsToOrgMixin | Org)
        for mapper in orm_execute_state.all_mappers
    ):
        # operation has nothing to do with models owned by org
        return
    if orm_execute_state.is_select:
        requester = corvic.context.get_requester()
        org_id = OrgID(requester.org_id)
        if org_id.is_super_user:
            return

        if org_id.is_nobody:
            raise RequestedObjectsForNobodyError(
                "requester org from context was nobody"
            )
        # we need the real value in in expression world and
        # because of sqlalchemys weird runtime parsing of this it
        # needs to be a real local with a name
        db_id = org_id.to_db().unwrap_or_raise()

        # this goofy syntax doesn't typecheck well, but is the documented way to apply
        # these operations to all subclasses (recursive). Sqlalchemy is inspecting the
        # lambda rather than just executing it so a function won't work.
        # https://docs.sqlalchemy.org/en/20/orm/queryguide/api.html#sqlalchemy.orm.with_loader_criteria
        check_org_id_lambda: Callable[  # noqa: E731
            [type[BelongsToOrgMixin]], sa.ColumnElement[bool]
        ] = lambda cls: cls.org_id == db_id
        orm_execute_state.statement = orm_execute_state.statement.options(
            sa_orm.with_loader_criteria(
                BelongsToOrgMixin,
                cast(Any, check_org_id_lambda),
                include_aliases=True,
                track_closure_variables=False,
            ),
            sa_orm.with_loader_criteria(
                Org,
                Org.id == org_id,
                include_aliases=True,
                track_closure_variables=False,
            ),
        )


class BelongsToOrgMixin(sa_orm.MappedAsDataclass):
    """Mark models that should be subject to org level access control."""

    @staticmethod
    def _current_org_id_from_context():
        requester = corvic.context.get_requester()
        return OrgID(requester.org_id)

    @staticmethod
    def _make_org_id_default() -> OrgID | None:
        org_id = BelongsToOrgMixin._current_org_id_from_context()

        if org_id.is_nobody:
            raise RequestedObjectsForNobodyError(
                "the nobody org cannot change orm objects"
            )

        if org_id.is_super_user:
            return None

        return org_id

    org_id: sa_orm.Mapped[OrgID | None] = sa_orm.mapped_column(
        ForeignKey(Org).make(ondelete="CASCADE"),
        nullable=False,
        default_factory=_make_org_id_default,
        init=False,
    )

    @sa_orm.validates("org_id")
    def validate_org_id(self, _key: str, orm_id: OrgID | None):
        expected_org_id = self._current_org_id_from_context()
        if expected_org_id.is_nobody:
            raise RequestedObjectsForNobodyError(
                "the nobody org cannot change orm objects"
            )

        if expected_org_id.is_super_user:
            return orm_id

        if orm_id != expected_org_id:
            raise InvalidArgumentError(
                "provided org_id must match the current org",
                provided=orm_id,
                expected=expected_org_id,
            )

        return orm_id

    @staticmethod
    def register_session_event_listeners(session: type[sa_orm.Session]):
        sa_event.listen(session, "do_orm_execute", _filter_org_objects)


BelongsToOrgMixin.register_session_event_listeners(Session.sync_session_class)


ID = OrgID


__all__ = [
    "BadDeleteError",
    "Base",
    "BaseID",
    "BaseIDFromInt",
    "BelongsToOrgMixin",
    "DeletedObjectError",
    "ForeignKey",
    "ID",
    "INT_PK_TYPE",
    "IntIDDecorator",
    "InvalidORMIdentifierError",
    "Org",
    "OrgID",
    "ProtoMessageDecorator",
    "RequestedObjectsForNobodyError",
    "Session",
    "SoftDeleteMixin",
    "live_unique_constraint",
    "primary_key_foreign_column",
    "primary_key_identity_column",
    "primary_key_uuid_column",
    "dbapi_error_to_result",
    "time_offset",
]
