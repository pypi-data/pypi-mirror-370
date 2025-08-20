"""This module provides wrapper classes for logging"""

## external imports
import functools
import inspect
import logging
import os
import sys
import time
from datetime import datetime
from pathlib import Path
from typing import Self

import verboselogs

try:
    import coloredlogs
except ImportError:
    coloredlogs = None

## internal imports
from ._inspect import InspectUtil
from ._tracker import PerformanceTracker

## performance tracking
PerformanceTracker.register_module_start(__name__)


## global variables
# _DEFAULT_LEVEL = getattr(AccelerateLogger, )
# _DEFAULT_SEPARATOR = os.environ.get("AUDIT_LOG_SEPARATOR", " | ")


## Class definitions
class AccelerateLogger(verboselogs.VerboseLogger):
    """
    Custom logger class to support more granluar logging levels

    This subclass of :class:`verboselogs.VerboseLogger` adds support for the additional
    logging methods :func:`trace()`.

    It also provides method to change logging level at runtime via
    :func:`update_level(self, level)` and :func:`trace(self, msg, *args, **kwargs)`.
    """

    NOTSET = logging.NOTSET
    CRITICAL = logging.CRITICAL
    FATAL = logging.FATAL
    ERROR = logging.ERROR
    SUCCESS = verboselogs.SUCCESS
    WARNING = logging.WARNING
    NOTICE = verboselogs.NOTICE
    INFO = logging.INFO
    VERBOSE = verboselogs.VERBOSE
    DEBUG = logging.DEBUG
    SPAM = verboselogs.SPAM
    TRACE = 1
    LOG_FILE = None

    DEFAULT_FORMAT: str = "%(asctime)s,%(msecs)03d %(threadName)s[%(process)d] %(caller)s %(levelname)s %(message)s"

    __slots__ = ("__init_level", "__audit_level", "__audit_separator")

    def __init__(self, *args, **kw):
        super().__init__(*args, **kw)
        self.__init_level = self.level
        self.__audit_level = getattr(
            self, os.environ.get("AUDIT_LOG_LEVEL", "SPAM").upper()
        )
        self.__audit_separator = os.environ.get("AUDIT_FIELD_SEPARATOR", " | ")

    ## class methods
    @classmethod
    def initialize(
        cls,
        root_logger_name: str = "accelerate",
        level: int | None = None,
        file: str | None = None,
        **kwargs,
    ) -> Self:
        print(
            "AccelerateLogger.initialize.args:",
            InspectUtil.inspect_variables("root_logger_name, level, file, kwargs"),
        )

        ## determine log level
        level = level or getattr(
            cls, os.environ.get("DEFAULT_LOG_LEVEL", "VERBOSE").upper()
        )
        assert level is not None, "Unable to determine log level"

        # determine log file
        if file:
            _path = Path(file)  # log file path
            if not _path.suffix:
                _path = _path.parent.joinpath(
                    f"{_path.stem}_{datetime.now().strftime('%Y%m%d%H%M%S')}.log"
                )

            os.makedirs(_path.parent, exist_ok=True)
            file = str(_path)
            cls.LOG_FILE = _path

        ## set default values
        kwargs.setdefault(
            "fmt", os.environ.get("DEFAULT_LOG_FORMAT", cls.DEFAULT_FORMAT)
        )
        kwargs.setdefault("isatty", True)
        kwargs.setdefault(
            "field_styles",
            {
                **(coloredlogs.DEFAULT_FIELD_STYLES if coloredlogs else {}),
                "caller": {"bold": True, "bright": True},
            },
        )
        kwargs.setdefault(
            "level_styles",
            {
                **(coloredlogs.DEFAULT_LEVEL_STYLES if coloredlogs else {}),
                "critical": {"background": "red", "bold": True},
            },
        )

        print(
            "AccelerateLogger.initialize.config:",
            InspectUtil.inspect_variables("level,file,kwargs"),
        )

        ## initialize logging [at lowest level - TRACE]
        logging.basicConfig(filename=file, format=kwargs["fmt"], level=cls.TRACE)
        if coloredlogs and kwargs["isatty"]:
            coloredlogs.install(level=cls.TRACE, **kwargs)

        ##
        # set root logger level to given level to control logging level for all loggers
        # This allows update_level()/restore_level() methods to work
        ##
        logging.root.setLevel(level)

        _logger = cls.get_logger(root_logger_name)

        ## suppress loggers
        for logger_name, logger_level in kwargs.get("update_loggers", {}).items():
            _logger.notice(
                "Updating Logger Level: {} -> {}",
                logger_name,
                logging.getLevelName(int(logger_level)),
            )
            logging.getLogger(logger_name).setLevel(logger_level)

        _logger.notice(
            "Accelerate Logger Initialized -> {} | {}",
            logging.getLevelName(level),
            file,
        )
        return _logger

    @classmethod
    def get_logger(cls, logger_name: str | None) -> Self:
        """
        Method to get logger instance
        """
        _logger = logging.getLogger(logger_name)
        # assert isinstance(_logger, cls), "Logger is not of type AccelerateLogger"
        return _logger  # type: ignore[reportReturnType]

        # if logger_name:
        #     _logger.propagate = False
        #     _logger.handlers = logging.root.handlers

        # return _logger

    ## override methods
    def makeRecord(
        self,
        name,
        level,
        fn,
        lno,
        msg,
        args,
        exc_info,
        func=None,
        extra=None,
        sinfo=None,
    ) -> logging.LogRecord:
        record = super().makeRecord(
            name, level, fn, lno, msg, args, exc_info, func, extra, sinfo
        )
        if hasattr(record, "caller"):
            return record

        last_frame = sys._getframe()
        while last_frame and last_frame.f_globals.get("__name__") in [
            "accelerate.python._logging",
            "verboselogs",
            "logging",
        ]:
            #     outer_frames = inspect.getouterframes(inspect.currentframe())
            last_frame = last_frame.f_back

        record.caller = InspectUtil.get_fully_qualified_name(last_frame)
        return record

    ## additional methods
    def update_level(self, level: int) -> Self:
        """Update logger to given level"""

        if level == self.__init_level:
            return self

        self.info("Updating Log Level -> {} -> {}", self.__init_level, level)
        self.setLevel(level)
        for handler in self.handlers:
            handler.setLevel(level)

        return self

    def restore_level(self) -> Self:
        """Revert logger to original level"""

        if self.level == self.__init_level:
            return self

        self.info("Restoring Log Level -> {} -> {}", self.level, self.__init_level)
        self.setLevel(self.__init_level)
        for handler in self.handlers:
            handler.setLevel(self.__init_level)

        return self

    def trace(self, msg, *args, **kwargs):
        """Log a message with level TRACE"""
        self.log(self.TRACE, msg, *args, **kwargs)

    ## audit decorators
    def __inspect_method(
        self,
        func,
        exclude: list[str] = [],
        include: list[str] = [],
        level: int | None = None,
        log_return_value: bool = False,
    ):
        _logger = AccelerateLogger.get_logger(func.__module__)
        _level = level or self.__audit_level

        @functools.wraps(func)
        def _wrapper(*args, **kwargs):
            _func_name = InspectUtil.get_fully_qualified_name(func)
            try:
                if _logger.isEnabledFor(_level):
                    _args = InspectUtil.inspect_method_arguments(
                        func, args, kwargs, exclude, include
                    )
                    _logger.log(
                        _level,
                        "Enter -> {}",
                        self.__audit_separator.join(_args) if _args else "<empty>",
                        extra={"caller": _func_name},
                    )
            except Exception as error:
                _logger.warning(
                    "inspect_error: {}{}{}",
                    _func_name,
                    self.__audit_separator,
                    InspectUtil.get_error_message(error),
                )
                pass

            try:
                start_time = time.perf_counter()
                return_value = func(*args, **kwargs)
                end_time = time.perf_counter()
                try:
                    value_length = len(return_value)
                except Exception:
                    value_length = len(str(return_value))

                if log_return_value:
                    _logger.log(
                        _level,
                        "ReturnValue -> {}",
                        return_value,
                        extra={"caller": _func_name},
                    )

                _logger.log(
                    _level,
                    "Exit -> {}",
                    self.__audit_separator.join(
                        [
                            f"Time={end_time - start_time:.6f}",
                            f"type={InspectUtil.get_fully_qualified_name(return_value)}",
                            f"length={value_length}",
                        ]
                    ),
                    extra={"caller": _func_name},
                )

                return return_value
            except Exception as error:
                if not getattr(error, "__method_auditor_handled", False):
                    error_message = (
                        f"{InspectUtil.get_fully_qualified_name(error)} -> {str(error)}"
                    )
                    setattr(error, "__method_auditor_handled", True)
                else:
                    error_message = (
                        f"Raised {InspectUtil.get_fully_qualified_name(error)}"
                    )

                _logger.log(
                    _level,
                    "Error -> {}",
                    _func_name,
                    error_message,
                    extra={"caller": _func_name},
                )
                raise

        return _wrapper

    def audit_method(
        self,
        exclude: list[str] = [],
        include: list[str] = [],
        level=None,
        log_return_value: bool = False,
    ):
        return lambda func: self.__inspect_method(
            func, exclude, include, level, log_return_value=log_return_value
        )

    def audit_class(
        self,
        exclude: list[str] = [],
        include: list[str] = [],
        level=None,
        log_return_value: bool = False,
    ):
        def class_decorator(target_class):
            # Retrieve all members that are functions (methods)
            _all_methods = inspect.getmembers(
                target_class, predicate=inspect.isfunction
            )
            _all_methods = _all_methods
            for name, func in _all_methods:
                # Check if the attribute is a method
                if (
                    func.__qualname__.startswith(target_class.__name__ + ".")
                    and (not include or func.__name__ in include)
                    and (func.__name__ not in exclude)
                ):
                    # Replace the method with the decorated version
                    setattr(
                        target_class,
                        name,
                        self.__inspect_method(
                            func, level=level, log_return_value=log_return_value
                        ),
                    )
            return target_class

        return class_decorator

    ## helper methods
    def debug_variables(self, var_names: str, message: str | None = None):
        self.log_variables(
            var_names,
            message,
            level=AccelerateLogger.DEBUG,
            caller=sys._getframe().f_back,
        )

    def trace_variables(self, var_names: str, message: str | None = None):
        self.log_variables(
            var_names,
            message,
            level=AccelerateLogger.TRACE,
            caller=sys._getframe().f_back,
        )

    def log_variables(
        self,
        var_names: str,
        message: str | None = None,
        level=None,
        caller=None,
    ):
        level = level or self.VERBOSE
        if self.isEnabledFor(level):
            self.log(
                level,
                "{} -> {}",
                message or "Variables",
                self.__audit_separator.join(
                    InspectUtil.inspect_variables(
                        var_names, caller or sys._getframe().f_back
                    )
                ),
            )


STACK = [
    "logging.Logger.makeRecord",
    "logging.Logger._log",
    "logging.Logger.log",
    "accelerate.python._logging.AccelerateLogger.__inspect_method.<locals>.wrapper",
]


class FormatLogRecord(logging.LogRecord):
    """
    Custom Log Record class to handle '{}' placeholders for variables in log statements
    """

    def getMessage(self):
        _msg = str(self.msg)
        if not self.args:
            return _msg

        if _msg.find("%") > -1:
            return _msg % self.args

        # if multiple arguments
        if isinstance(self.args, tuple):
            return _msg.format(*self.args)

        return _msg.format(self.args)


## Add custom logging levels
logging.addLevelName(AccelerateLogger.TRACE, "TRACE")
setattr(logging, "TRACE", AccelerateLogger.TRACE)


## Set custom logger class and log record factory
print("registering AccelerateLogger ...")
logging.setLoggerClass(AccelerateLogger)
logging.setLogRecordFactory(FormatLogRecord)


## export symbols
__all__ = ["AccelerateLogger"]


## log performance tracker
PerformanceTracker.log_module_load(__name__)


## disable standalone execution for library
if __name__ == "__main__":
    raise Exception(
        "This is not a standalone module, and should be imported as a library"
    )
