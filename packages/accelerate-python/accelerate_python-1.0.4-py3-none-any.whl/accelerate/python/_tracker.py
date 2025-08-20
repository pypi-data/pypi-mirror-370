"""This module provides utility class to track performance of modules"""

## external imports
from datetime import datetime


## class definitions
class PerformanceTracker:
    __MODULE_MAP = {}

    @classmethod
    def register_module_start(cls, module_name):
        cls.__MODULE_MAP[module_name] = datetime.now()

    @classmethod
    def log_module_load(cls, module_name):
        load_time = int(
            (datetime.now() - cls.__MODULE_MAP[module_name]).total_seconds()
        )
        if load_time > 0:
            print(
                "\033[31m\033[1mSlow Module Load:\033[0m{} | {}", module_name, load_time
            )


## export symbols
__all__ = [
    "PerformanceTracker",
]

## disable standalone execution for library
if __name__ == "__main__":
    raise Exception(
        "This is not a standalone module, and should be imported as a library"
    )
