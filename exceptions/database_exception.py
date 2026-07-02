from .framework_exception import FrameworkException


class DatabaseException(FrameworkException):
    """Raised on DB connection failure, query error, or unexpected DB state."""
    pass
