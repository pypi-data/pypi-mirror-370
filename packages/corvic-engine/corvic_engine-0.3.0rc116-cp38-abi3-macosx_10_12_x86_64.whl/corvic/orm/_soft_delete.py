"""Mixin models for corvic orm tables."""

from datetime import UTC, datetime
from types import TracebackType
from typing import Any, LiteralString

import sqlalchemy as sa
from sqlalchemy import event, exc
from sqlalchemy import orm as sa_orm
from sqlalchemy.exc import (
    DBAPIError,
)
from sqlalchemy.ext import hybrid
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.ext.hybrid import hybrid_property

from corvic.orm.errors import DeletedObjectError, dbapi_error_to_result


class BadDeleteError(DeletedObjectError):
    """Raised when deleting deleted objects."""

    def __init__(self):
        super().__init__(message="deleting an object that is already deleted")


def _filter_deleted_objects_when_orm_loading(
    execute_state: sa_orm.session.ORMExecuteState,
):
    # check if the orm operation was submitted with an option to force load despite
    # soft-load status and if so just skip this event
    if any(
        isinstance(opt, SoftDeleteMixin.ForceLoadOption)
        for opt in execute_state.user_defined_options
    ) or any(
        isinstance(opt, SoftDeleteMixin.ForceLoadOption)
        for opt in execute_state.local_execution_options.values()
    ):
        return

    def where_criteria(cls: type[SoftDeleteMixin]) -> sa.ColumnElement[bool]:
        return ~cls.is_deleted

    execute_state.statement = execute_state.statement.options(
        sa_orm.with_loader_criteria(
            entity_or_base=SoftDeleteMixin,
            # suppressing pyright is unfortunately required as there seems to be a
            # problem with sqlalchemy.orm.util::LoaderCriteriaOption which will
            # construct a 'DeferredLambdaElement' when `where_criteria` is callable.
            # However, the type annotations are not consistent with the implementation.
            # The implementation, on callables criteria, passes to the lambda the
            # mapping class for using in constructing the `ColumnElement[bool]` result
            # needed. For this reason we ignore the argument type.
            where_criteria=where_criteria,
            include_aliases=True,
        )
    )


class SoftDeleteMixin(sa_orm.MappedAsDataclass):
    """Mixin to make corvic orm models use soft-delete.

    Modifications to objects which are marked as deleted will result in
    an error.
    """

    class ForceLoadOption(sa_orm.UserDefinedOption):
        """Option for ignoring soft delete status when loading."""

    _deleted_at: sa_orm.Mapped[datetime | None] = sa_orm.mapped_column(
        "deleted_at",
        sa.DateTime(timezone=True),
        server_default=None,
        default=None,
    )
    is_live: sa_orm.Mapped[bool | None] = sa_orm.mapped_column(
        init=False,
        default=True,
    )

    @hybrid.hybrid_property
    def deleted_at(self) -> datetime | None:
        if not self._deleted_at:
            return None
        return self._deleted_at.replace(tzinfo=UTC)

    @deleted_at.inplace.expression
    @classmethod
    def _deleted_at_at_expression(cls):
        return cls._deleted_at

    def reset_delete(self):
        self._deleted_at = None

    @classmethod
    def _force_load_option(cls):
        return cls.ForceLoadOption()

    @classmethod
    def force_load_options(cls):
        """Options to force load soft-deleted objects when using session.get."""
        return [cls._force_load_option()]

    @classmethod
    def force_load_execution_options(cls):
        """Options to force load soft-deleted objects when using session.execute.

        Also works with session.scalars.
        """
        return {"ignored_option_name": cls._force_load_option()}

    def mark_deleted(self):
        """Updates soft-delete object.

        Note: users should not use this directly and instead should use
        `session.delete(obj)`.
        """
        if self.is_deleted:
            raise BadDeleteError()
        # set is_live to None instead of False so that orm objects can use it to
        # build uniqueness constraints that are only enforced on non-deleted objects
        self.is_live = None
        self._deleted_at = datetime.now(tz=UTC)

    @hybrid_property
    def is_deleted(self) -> bool:
        """Useful when constructing queries for direct use (e.g via `session.execute`).

        ORM users can rely on the typical session interfaces for checking object
        persistence.
        """
        return not self.is_live

    @is_deleted.inplace.expression
    @classmethod
    def _is_deleted_expression(cls):
        return cls.is_live.is_not(True)

    @staticmethod
    def register_session_event_listeners(session: type[sa_orm.Session]):
        event.listen(
            session, "do_orm_execute", _filter_deleted_objects_when_orm_loading
        )


def live_unique_constraint(
    column_name: LiteralString, *other_column_names: LiteralString
) -> sa.UniqueConstraint:
    """Construct a unique constraint that only applies to live objects.

    Live objects are those that support soft deletion and have not been soft deleted.
    """
    return sa.UniqueConstraint(column_name, *other_column_names, "is_live")


class Session(AsyncSession):
    """Wrapper around sqlalchemy.orm.Session."""

    _soft_deleted: dict[sa_orm.InstanceState[Any], Any] | None = None

    async def __aexit__(
        self,
        type_: type[BaseException] | None,
        value: BaseException | None,
        traceback: TracebackType | None,
    ):
        await super().__aexit__(type_, value, traceback)
        if isinstance(value, DBAPIError):
            raise dbapi_error_to_result(value) from value

    def _track_soft_deleted(self, instance: object):
        if self._soft_deleted is None:
            self._soft_deleted = {}
        self._soft_deleted[sa_orm.attributes.instance_state(instance)] = instance

    def _reset_soft_deleted(self):
        self._soft_deleted = {}

    def _ensure_persistence(self, instance: object):
        instance_state = sa_orm.attributes.instance_state(instance)
        if instance_state.key is None:
            raise exc.InvalidRequestError("Instance is not persisted")

    async def _delete_soft_deleted(self, instance: SoftDeleteMixin):
        self._ensure_persistence(instance)

        instance.mark_deleted()

        # Soft deleted should be tracked so that way a deleted soft-delete instance is
        # correctly identified as being "deleted"
        self._track_soft_deleted(instance)

        # Flushing the objects being deleted is needed to ensure the 'soft-delete'
        # impact is spread. This is because sqlalchemy flush implementation is doing
        # the heavy lifting of updating deleted/modified state across dependencies
        # after flushing. Ensuring this is done necessary to ensure relationships with
        # cascades have valid state after a soft-delete. Otherwise divergence between
        # hard-delete and soft-delete will be seen here (and surprise the user).
        # Note: the cost is reduced by limiting the flush to the soft-delete instance.
        await self.flush([instance])

        # Invalidate existing session references for expected get-after-delete behavior.
        if (
            sa_orm.attributes.instance_state(instance).session_id
            is self.sync_session.hash_key
        ):
            self.expunge(instance)

    async def commit(self):
        await super().commit()
        if self._soft_deleted:
            self._reset_soft_deleted()

    async def rollback(self):
        await super().rollback()
        if self._soft_deleted:
            for obj in self._soft_deleted.values():
                if isinstance(obj, SoftDeleteMixin):
                    obj.reset_delete()
                    obj.is_live = True
                    continue
                raise RuntimeError("non-soft delete object in soft deleted set")
            self._reset_soft_deleted()

    @property
    def deleted(self):
        deleted = super().deleted
        if self._soft_deleted:
            deleted.update(self._soft_deleted.values())
        return deleted

    async def delete(self, instance: object, *, force_hard_delete=False):
        if isinstance(instance, SoftDeleteMixin) and not force_hard_delete:
            await self._delete_soft_deleted(instance)
            return
        await super().delete(instance)


SoftDeleteMixin.register_session_event_listeners(Session.sync_session_class)
