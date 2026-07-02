from .framework_exception import FrameworkException


class ElementNotFoundException(FrameworkException):
    """Raised when a locator cannot be found within the configured timeout."""
    pass
