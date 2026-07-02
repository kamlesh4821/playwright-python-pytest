from .framework_exception import FrameworkException


class ConfigException(FrameworkException):
    """Raised when a required config key is missing or holds an invalid value."""
    pass
