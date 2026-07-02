from .framework_exception import FrameworkException


class NetworkInterceptorException(FrameworkException):
    """Raised when a Playwright route intercept setup fails."""
    pass
