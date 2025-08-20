"""This module provides wrapper classes for formatted console printing (based on coloredlogs)"""

## external imports
import os
import sys
import threading
from datetime import datetime

## internal imports
from ._inspect import InspectUtil
from ._tracker import PerformanceTracker

## performance tracking
PerformanceTracker.register_module_start(__name__)


## global variables


## class definitions
class Console:
    BLACK = "\033[30m"
    GRAY = "\033[90m"
    RED = "\033[91m"
    GREEN = "\033[92m"
    YELLOW = "\033[93m"
    VIOLET = "\033[94m"
    PURPLE = "\033[95m"
    CYAN = "\033[96m"
    WHITE = "\033[97m"

    ERROR = "\033[31m"
    SUCCESS = "\033[32m"
    WARNING = "\033[33m"
    NOTICE = "\033[35m"
    INFO = "\033[37m"
    VERBOSE = "\033[34m"
    DEBUG = GREEN
    SPAM = CYAN
    TRACE = "\033[36m"

    NONE = "\033[0m"
    BOLD = "\033[1m"
    MUTED = "\033[2m"
    ITALICS = "\x1b[3m"
    UNDERLINE = "\033[4m"
    BLINK = "\033[5m"
    TBD = "\033[6m"
    HIGHLIGHT = "\033[7m"
    HIDDEN = "\033[8m"

    @staticmethod
    def error(message: str, *args, formats: list = []):
        Console.print("ERROR", message, *args, formats=[Console.ERROR, *formats])

    @staticmethod
    def success(message: str, *args, formats: list = []):
        Console.print(
            "SUCCESS", message, *args, formats=[Console.SUCCESS, Console.BOLD, *formats]
        )

    @staticmethod
    def warning(message: str, *args, formats: list = []):
        Console.print("WARNING", message, *args, formats=[Console.WARNING, *formats])

    @staticmethod
    def notice(message: str, *args, formats: list = []):
        Console.print("NOTICE", message, *args, formats=[Console.NOTICE, *formats])

    @staticmethod
    def info(message: str, *args, formats: list = []):
        Console.print("INFO", message, *args, formats=[Console.INFO, *formats])

    @staticmethod
    def verbose(message: str, *args, formats: list = []):
        Console.print("VERBOSE", message, *args, formats=[Console.VERBOSE, *formats])

    @staticmethod
    def debug(message: str, *args, formats: list = []):
        Console.print("DEBUG", message, *args, formats=[Console.GREEN, *formats])

    @staticmethod
    def print(level: str, message: str, *args, formats: list = []):
        last_frame = sys._getframe().f_back
        assert last_frame is not None, (
            "Could not determine source frame, check code and annotations"
        )

        source = InspectUtil.get_fully_qualified_name(last_frame.f_back)
        print(
            "{}{} {}[{}] {} {} {}{}{}".format(
                Console.NONE,
                datetime.now().strftime("%Y-%m-%d %H:%M:%S,%f")[:-3],
                threading.current_thread().name,
                os.getpid(),
                source,
                level,
                "".join(formats),
                message.format(*args),
                Console.NONE,
            ),
            file=sys.stderr if level in ["ERROR"] else sys.stdout,
        )


## export symbols
__all__ = ["Console"]


## log performance tracker
PerformanceTracker.log_module_load(__name__)


## disable standalone execution for library
if __name__ == "__main__":
    raise Exception(
        "This is not a standalone module, and should be imported as a library"
    )
