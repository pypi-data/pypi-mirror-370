"""This module provide wrapper classes for custom exceptions"""

# external imports
import sys
from typing import Any

## internal imports
from ._logging import AccelerateLogger
from ._tracker import PerformanceTracker

## performance tracking
PerformanceTracker.register_module_start(__name__)

## global variables
_LOGGER = AccelerateLogger.get_logger(__name__)


## class definitions
@_LOGGER.audit_class()
class AppException(Exception):
    """
    Base exception
    """

    message: str
    errorCode: int
    errorData: dict[str, Any]

    def __init__(self, message: str, *message_args, error_code: int = -1, **error_data):
        self.message = message.format(*message_args)
        self.errorCode = error_code
        self.errorData = error_data
        super().__init__(self.message)

    def __str__(self):
        return f"{self.errorCode} | {self.message} | {self.errorData}"

    @classmethod
    def check(cls, input: Any, message: str, *message_args, **kwargs):
        if not input:
            raise AppException(message, *message_args, **kwargs)


@_LOGGER.audit_class()
class AbstractMethodError(AppException, NotImplementedError):
    """
    Method not implemented exception
    """

    def __init__(self):
        ## going back two frames to skip the audit_class() wrapper
        audit_frame = sys._getframe().f_back
        last_frame = audit_frame.f_back if audit_frame else None
        assert last_frame is not None, (
            "Could not determine source frame, check code and annotations"
        )

        super().__init__(
            "Class [{}] does not implement abstract method: `{}`",
            (
                last_frame.f_locals["self"].__class__
                if "self" in last_frame.f_locals
                else last_frame.f_locals["cls"]
            ).__qualname__,
            last_frame.f_code.co_qualname,
        )


## export symbols
__all__ = ["AppException", "AbstractMethodError"]


## log performance tracker
PerformanceTracker.log_module_load(__name__)


## disable standalone execution for library
if __name__ == "__main__":
    raise Exception(
        "This is not a standalone module, and should be imported as a library"
    )
