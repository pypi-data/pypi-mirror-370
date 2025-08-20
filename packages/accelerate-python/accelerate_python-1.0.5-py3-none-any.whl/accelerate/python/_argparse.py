"""This module provides wrapper class to handle command line arguments"""

## external imports
import argparse
from typing import Any, Self

## internal imports
from ._logging import AccelerateLogger
from ._tracker import PerformanceTracker
from ._utils import AppUtil, Environment

## performance tracking
PerformanceTracker.register_module_start(__name__)


## global variables
_LOGGER = AccelerateLogger.get_logger(__name__)
_LOG_LEVELS = {
    "FATAL": AccelerateLogger.FATAL,
    "CRITICAL": AccelerateLogger.CRITICAL,
    "ERROR": AccelerateLogger.ERROR,
    "SUCCESS": AccelerateLogger.SUCCESS,
    "WARNING": AccelerateLogger.WARNING,
    "NOTICE": AccelerateLogger.NOTICE,
    "INFO": AccelerateLogger.INFO,
    "VERBOSE": AccelerateLogger.VERBOSE,
    "DEBUG": AccelerateLogger.DEBUG,
    "SPAM": AccelerateLogger.SPAM,
    "TRACE": AccelerateLogger.TRACE,
    "F": AccelerateLogger.FATAL,
    "C": AccelerateLogger.CRITICAL,
    "E": AccelerateLogger.ERROR,
    "S": AccelerateLogger.SUCCESS,
    "W": AccelerateLogger.WARNING,
    "N": AccelerateLogger.NOTICE,
    "I": AccelerateLogger.INFO,
    "V": AccelerateLogger.VERBOSE,
    "D": AccelerateLogger.DEBUG,
    "P": AccelerateLogger.SPAM,
    "T": AccelerateLogger.TRACE,
}


## class definitions
@_LOGGER.audit_class(exclude=["__getattr__"])
class ProgramArgs(argparse.ArgumentParser):
    """
    ArgumentParser extension to provide shortcut methods
    """

    __slots__ = (
        "__knownArgs",
        "__unknownArgs",
        "__configFlags",
    )

    def __init__(self, prog: str, *args, **kwargs):
        super().__init__(prog=prog, *args, **kwargs)

    @property
    def knownArgs(self) -> argparse.Namespace:
        return self.__knownArgs

    @property
    def unknownArgs(self) -> list[str]:
        return self.__unknownArgs

    @property
    def configFlags(self) -> dict[str, Any]:
        return self.__configFlags

    @property
    def simulation(self) -> bool:
        return getattr(self.__knownArgs, "simulation", False)

    @property
    def logLevel(self) -> str | None:
        return getattr(self.__knownArgs, "logLevel", None)

    @property
    def logFile(self) -> str | None:
        return getattr(self.__knownArgs, "logFile", None)

    @property
    def runMode(self) -> str | None:
        return getattr(self.__knownArgs, "runMode", None)

    def __getattr__(self, item):
        # print(f"--> ProgramArgs.__getattr__: {item}")
        if item in self.__knownArgs:
            return getattr(self.__knownArgs, item)

        raise AttributeError

    def add_boolean_argument(self, *args, **kwargs) -> Self:
        kwargs.setdefault("type", AppUtil.bool_value)
        kwargs.setdefault("default", False)
        self.add_argument(*args, **kwargs)

        return self

    def add_run_mode_argument(self, required: bool, *choices, **kwargs) -> Self:
        kwargs["choices"] = list(choices)
        self.add_argument(
            "-m",
            "--run-mode",
            required=required,
            dest="runMode",
            help="Run Mode for the script",
            **kwargs,
        )

        return self

    def read(
        self,
        add_default_arguments: bool = True,
        simulation: bool = False,
        log_level: str | None = None,
        log_file: str | None = None,
        allow_extra_args: bool = False,
        args: list[str] | None = None,
    ) -> Self:
        if add_default_arguments:
            self.__add_default_arguments(simulation, log_level, log_file)

        if allow_extra_args:
            self.__knownArgs, self.__unknownArgs = self.parse_known_args(args)
        else:
            self.__knownArgs, self.__unknownArgs = self.parse_args(args), []

        # set config flags
        self.__configFlags = {
            c[0]: AppUtil.bool_value(True if len(c) == 1 else c[1], fail_on_error=False)
            or c[1]
            for c in [f.split("=") for f in getattr(self.__knownArgs, "kwargs", [])]
        }

        # set environment variables
        for v in [e.split("=") for e in getattr(self.__knownArgs, "envVars", [])]:
            Environment.set(v[0], v[1])

        # set simulation mode
        _simulation = getattr(self.__knownArgs, "simulation", "False")
        Environment.set("SIMULATION", str(_simulation).lower())

        _LOGGER.warning(
            "Program Arguments: {}",
            " | ".join([f"{k}={v}" for k, v in vars(self.knownArgs).items()]),
        )
        return self

    def __add_default_arguments(
        self, simulation: bool, log_level: str | None, log_file: str | None
    ):
        self.add_argument(
            "--simulation",
            required=False,
            dest="simulation",
            type=AppUtil.bool_value,
            default=simulation,
            help="Flag to toggle simulation mode",
        )
        self.add_argument(
            "--NS",
            required=False,
            action="store_false",
            dest="simulation",
            help="Flag to disable simulation mode",
        )
        self.add_argument(
            "--ll",
            "--log-level",
            required=False,
            dest="logLevel",
            type=str.upper,
            choices=_LOG_LEVELS.keys(),
            default=log_level,
            help="Log level",
        )
        self.add_argument(
            "--lf",
            "--log-file",
            required=False,
            dest="logFile",
            default=log_file,
            help="Log file",
        )

        self.add_argument(
            "--kwargs", nargs="*", dest="kwargs", default=[], help="General Args"
        )

        ## Arguments for testing
        self.add_argument(
            "--env",
            nargs="*",
            dest="envVars",
            default=[],
            help="Env vars for testing",
        )

    def get_config_flag(self, config_key: str, default_value: Any = None) -> Any:
        return self.__configFlags.get(config_key, default_value)

    def initialize_logging(self) -> AccelerateLogger:
        return AccelerateLogger.initialize(
            self.prog.replace(" ", "_").lower(),
            _LOG_LEVELS.get(getattr(self, "logLevel", "VERBOSE")),
            getattr(self, "logFile", None),
        )


## export symbols
__all__ = ["ProgramArgs"]


## log performance tracker
PerformanceTracker.log_module_load(__name__)


## disable standalone execution for library
if __name__ == "__main__":
    raise Exception(
        "This is not a standalone module, and should be imported as a library"
    )
