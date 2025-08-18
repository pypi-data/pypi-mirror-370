class DbException(Exception):
    pass


class DbApplicationError(DbException):
    pass


class DbForeignKeyMissingError(DbException):
    pass


class DbDatabaseMissingError(DbException):
    pass


class DbTableMissingError(DbException):
    pass


class DbColumnMissingError(DbException):
    pass


class DbTruncationError(DbException):
    pass


class DbConnectionError(DbException):
    pass


class DbDuplicateKeyError(DbException):
    pass


class DbObjectExistsError(DbException):
    pass


class DbLockTimeoutError(DbException):
    pass


class DbRetryTransaction(DbException):
    pass


class DbDataIntegrityError(DbException):
    pass


class DuplicateRowsFoundError(Exception):
    pass


class DbQueryError(DbException):
    """Database query error"""

    pass


class DbTransactionError(DbException):
    """Database transaction error"""

    pass


# Add aliases for backward compatibility with engine.py
class DatabaseError(DbException):
    """Generic database error - alias for DbException"""

    pass
