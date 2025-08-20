from ._argparse import ProgramArgs
from ._collections import DICT, JSON, LIST, XML, YAML, Properties
from ._config import Config
from ._console import Console
from ._dataclasses import DataClass
from ._exceptions import AbstractMethodError, AppException
from ._inspect import InspectUtil
from ._logging import AccelerateLogger, FormatLogRecord
from ._subprocess import Process
from ._threading import Task, TaskPool
from ._tracker import PerformanceTracker
from ._unittest import WrapperTest
from ._utils import (
    AppUtil,
    Base64,
    Environment,
    PathUtil,
)

__all__ = [
    "ProgramArgs",
    "DICT",
    "LIST",
    "JSON",
    "YAML",
    "Properties",
    "XML",
    "Config",
    "Console",
    "DataClass",
    "AppException",
    "AbstractMethodError",
    "InspectUtil",
    "AccelerateLogger",
    "FormatLogRecord",
    "Process",
    "Task",
    "TaskPool",
    "PerformanceTracker",
    "WrapperTest",
    "Environment",
    "Base64",
    "AppUtil",
    "PathUtil",
]


## optional dependencies
# ruff: noqa: F401
try:
    from ._microsoft import CellFormat, ExcelUtil, WorkbookTemplate

    __all__.extend(["CellFormat", "ExcelUtil", "WorkbookTemplate"])
except ImportError:
    print(
        "accelerate-python: optional dependency 'openpyxl' missing, skipping '_microsoft' exports."
    )
    pass


try:
    from ._pandas import PandasUtil

    __all__.extend(["PandasUtil"])
except ImportError:
    print(
        "accelerate-python: optional dependency 'pandas' missing, skipping '_pandas' exports."
    )
    pass
