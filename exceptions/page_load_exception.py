from .framework_exception import FrameworkException


class PageLoadException(FrameworkException):
    """Raised when a page does not reach the expected URL or state within timeout."""
    pass
