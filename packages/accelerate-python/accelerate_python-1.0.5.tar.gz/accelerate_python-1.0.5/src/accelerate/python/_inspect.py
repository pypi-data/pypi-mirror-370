## external imports
import inspect
import sys
from operator import attrgetter
from types import FrameType
from typing import Callable

## internal imports
from ._tracker import PerformanceTracker

## performance tracking
PerformanceTracker.register_module_start(__name__)


## global variables


## class definitions
class InspectUtil:
    @classmethod
    def get_fully_qualified_name(cls, target):
        if isinstance(target, FrameType):
            return f"{target.f_globals.get('__name__')}.{target.f_code.co_qualname}"

        target_type = (
            target
            if (inspect.isclass(target) or inspect.isfunction(target))
            else type(target)
        )
        return f"{target_type.__module__}.{target_type.__qualname__}"

    @classmethod
    def get_error_message(cls, error: Exception):
        return f"{cls.get_fully_qualified_name(error)} -> {str(error)}"

    @classmethod
    def inspect_values(cls, *values):
        return [f"{cls.get_fully_qualified_name(v)}:{v}" for v in values]

    @staticmethod
    def inspect_method_arguments(
        method: Callable,
        method_args: tuple,
        method_kwargs: dict,
        exclude: list[str] = [],
        include: list[str] = [],
    ) -> list[str]:
        """
        Method to get a list of delimited values of the arguments passed to the calling method
        """
        _exclude = [e for e in exclude + ["self", "cls"] if e not in include]
        _args = inspect.signature(method).bind(*method_args, **method_kwargs)
        _args.apply_defaults()
        return [f"{k}={v}" for k, v in _args.arguments.items() if k not in _exclude]

    @classmethod
    def inspect_frame_arguments(
        cls,
        caller: FrameType | None = None,
        exclude: list[str] = [],
        include: list[str] = [],
    ):
        """
        Method to get a list of delimited values of the arguments passed to the calling method
        """
        frame = None
        if caller is not None:
            frame = caller
        else:
            # e.g. methodA -> methodB -> log_arguments -> inspect_arguments
            # going back twice to get arguments passed to methodB
            current_frame = sys._getframe()
            if current_frame is not None and current_frame.f_back is not None:
                frame = (
                    current_frame.f_back.f_back
                    if current_frame.f_back.f_back is not None
                    else None
                )
        exclude = [e for e in exclude + ["self"] if e not in include]

        return (
            [f"{k}={v}" for k, v in frame.f_locals.items() if k not in exclude]
            if frame
            else []
        )

    @staticmethod
    def inspect_variables(var_names: str, source_frame: FrameType | None = None):
        """
        Method to get a list of delimited values for the given variables
        """
        frame = (
            source_frame  # log_arguments sends the frame to inspect_arguments
            or sys._getframe().f_back  # caller frame
        )
        if not frame:
            return []

        values = []
        for var in var_names.replace(" ", "").split(","):
            if "." in var:  # for nested variables
                parts = var.split(".")
                val = attrgetter(*parts[1:])(frame.f_locals[parts[0]])
                values.append(f"{var}={val() if callable(val) else val}")
            else:
                values.append(f"{var}={frame.f_locals[var]}")

        return values


## export symbols
__all__ = ["InspectUtil"]


## log performance tracker
PerformanceTracker.log_module_load(__name__)


## disable standalone execution for library
if __name__ == "__main__":
    raise Exception(
        "This is not a standalone module, and should be imported as a library"
    )
