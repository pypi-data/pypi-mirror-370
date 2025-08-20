"""This module provides different utility classes for app development"""

## external Imports
import base64
import copy
import importlib
import numbers
import os
import os.path
import sys
import tempfile
import time
from operator import attrgetter
from pathlib import Path
from typing import Any, Callable, Mapping, Sequence, TypeVar, get_args

## internal imports
from ._logging import AccelerateLogger
from ._tracker import PerformanceTracker

## performance tracking
PerformanceTracker.register_module_start(__name__)


## global variables
_LOGGER = AccelerateLogger.get_logger(__name__)
_ANY = TypeVar("_ANY")


## class definitions
@_LOGGER.audit_class()
class Environment:
    @staticmethod
    def get_all() -> dict[str, str]:
        return dict(os.environ)

    @staticmethod
    def get(name: str, default_value: str | None = None) -> str | None:
        return os.environ.get(name, default_value)

    @staticmethod
    def set(name: str, value: str) -> str:
        print(
            "Environment.set()",
            name,
            value,
            sep=" | ",
        )
        os.environ[name] = value
        return value

    @staticmethod
    def is_enabled(name: str, default_value: bool = False) -> bool:
        return (
            AppUtil.bool_value(os.environ.get(name, default_value), fail_on_error=False)
            or False
        )

    @staticmethod
    def is_simulation_enabled() -> bool:
        # print(
        #     "Environment.is_simulation_enabled()",
        #     Environment.get("SIMULATION"),
        #     Environment.is_enabled("SIMULATION"),
        #     sep=" | ",
        # )
        return Environment.is_enabled("SIMULATION")


@_LOGGER.audit_class()
class Base64:
    """
    Utility class for base64 encoding/decoding
    """

    @staticmethod
    def encode(value: Any) -> str:
        _b = value if isinstance(value, bytes) else str(value).encode()
        return base64.b64encode(_b).decode()

    @staticmethod
    def decode(value: Any) -> bytes:
        _b = value if isinstance(value, bytes) else str(value).encode()
        return base64.b64decode(_b)

    @staticmethod
    def decode_to_string(value: Any) -> str:
        return Base64.decode(value).decode()


@_LOGGER.audit_class()
class AppUtil:
    @staticmethod
    def import_string(cls_qualname: str, package: str | None = None) -> Any:
        try:
            assert not cls_qualname.startswith(".") or package is not None, (
                f"Package name is required for relative import: {cls_qualname}"
            )

            module_path, class_name = cls_qualname.rsplit(".", 1)
            module = importlib.import_module(module_path, package)
            cls = getattr(module, class_name)
            globals()[class_name] = cls  # cache for future access
            return cls
        except ValueError as err:
            raise ImportError(f"Invalid classpath: {cls_qualname}") from err

    @staticmethod
    def get_generic_type(instance) -> Any:
        return get_args(instance.__orig_bases__[0])[0]

    @staticmethod
    def exit(message, *args, exit_code=1):
        """Method to log and exit program"""
        if exit_code == 0:
            _LOGGER.success(message, *args)
        else:
            _LOGGER.fatal(message, *args, exc_info=(sys.exc_info()[0] is not None))

        sys.exit(exit_code)

    @staticmethod
    def wait(wait_seconds, message, *args, log_level=AccelerateLogger.INFO):
        """Method to wait for a process to complete"""
        _LOGGER.log(log_level, message, *args)
        time.sleep(wait_seconds)

    @staticmethod
    def copy_object(object, **kwargs):
        return copy.deepcopy(object, **kwargs)

    @staticmethod
    def bool_value(value, fail_on_error: bool = True) -> bool | None:
        if isinstance(value, bool):
            return value

        if str(value).lower() in ["true", "yes", "enabled"]:
            return True
        elif str(value).lower() in ["false", "no", "disabled", "none"]:
            return False

        if fail_on_error:
            raise ValueError(value)

        ## To handle configFlag processing
        return None

    @staticmethod
    def is_empty(value: Any):
        if value is None:
            return True

        if isinstance(value, numbers.Number) or isinstance(value, bool):
            return False

        if isinstance(value, str):
            return len(value.strip()) == 0

        if isinstance(value, Sequence) or isinstance(value, Mapping):
            return len(value) == 0

        return False if value else True

    @staticmethod
    def get_length(value):
        return -1 if value is None else len(value)

    @staticmethod
    def get_or_default(value, default_value=None):
        return default_value if AppUtil.is_empty(value) else value

    @staticmethod
    def null_safe_attrgetter(*paths, default=None) -> Callable:
        """
        Returns a null-safe attrgetter function.

        Args:
            path (str): The attribute path to get, e.g., 'a.b.c'.
            default: The default value to return if any attribute in the path is None.

        Returns:
            A function that takes an object and returns the attribute value or the default.
        """
        _attrgetter = attrgetter(*paths)

        def getter(obj):
            try:
                result = _attrgetter(obj)
                return [result] if not isinstance(result, tuple) else list(result)
            except AttributeError:
                return default

        return getter

    @staticmethod
    def join_string(separator: str, *values: Any) -> str:
        if not values:
            return ""

        if (
            len(values) == 1
            and isinstance(values[0], Sequence)
            and not isinstance(values[0], str)
        ):
            ## if an array, list, or tuple is passed without expansion
            values = tuple(values[0])

        return separator.join([str(v) for v in values])


@_LOGGER.audit_class()
class PathUtil:
    @staticmethod
    def temp_dir() -> Path:
        return Path(tempfile.gettempdir())

    @staticmethod
    def append_sys_path(path: str):
        _LOGGER.warning("Adding to system path: {}", path)
        sys.path.append(path)

    @staticmethod
    def write_file(content: str | bytes, *paths: str | Path, **kwargs) -> Path:
        output_file = Path(*paths)
        output_file.parent.mkdir(parents=True, exist_ok=True)
        if isinstance(content, str):
            output_file.write_text(content, encoding=kwargs.get("encoding"))
        else:
            output_file.write_bytes(content)

        return output_file


## export symbols
__all__ = ["Environment", "Base64", "AppUtil", "PathUtil"]


## log performance tracker
PerformanceTracker.log_module_load(__name__)


## disable standalone execution for library
if __name__ == "__main__":
    raise Exception(
        "This is not a standalone module, and should be imported as a library"
    )
