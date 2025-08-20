"""Errors specific to communicating with the database."""

from sqlalchemy.exc import (
    DBAPIError,
    IntegrityError,
    InterfaceError,
    InternalError,
    NotSupportedError,
    OperationalError,
    ProgrammingError,
)

from corvic import result


class InvalidORMIdentifierError(result.InvalidArgumentError):
    """Raised when an identifier can't be translated to its orm equivalent."""


class RequestedObjectsForNobodyError(result.Error):
    """Raised when attempts are made to access database objects as the nobody org."""


class DeletedObjectError(result.Error):
    """DeletedObjectError result Error.

    Raised on invalid operations to objects which are soft deleted.
    """


def dbapi_error_to_result(err: DBAPIError):
    # based on https://docs.sqlalchemy.org/en/20/errors.html
    match err:
        case NotSupportedError():
            # raised in the unexpected case that we're doing something that the
            # database just doesn't support
            raise result.InternalError.from_(err) from err
        case OperationalError() | InterfaceError() | InternalError():
            # These are commonly things that are outside of our control that might
            # succeed on retry, e.g., connections being dropped
            return result.UnavailableError.from_(err)
        case IntegrityError():
            return result.InvalidArgumentError.from_(err)
        case ProgrammingError():
            if "could not serialize" in str(err):
                return result.UnavailableError.from_(err)
        case _:
            pass

    try:
        import psycopg.errors

        if isinstance(err.orig, psycopg.errors.SerializationFailure):
            return result.UnavailableError.from_(err)
    except ModuleNotFoundError:
        pass

    return result.InvalidArgumentError.from_(err)
