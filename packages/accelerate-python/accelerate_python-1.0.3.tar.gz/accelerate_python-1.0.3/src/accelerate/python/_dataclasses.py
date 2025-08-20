"""This module provides wrapper class and utility functions for dataclasses"""

## external imports
from dataclasses import Field, asdict, dataclass, fields, is_dataclass

## internal imports
from ._collections import JSON, YAML
from ._logging import AccelerateLogger
from ._tracker import PerformanceTracker

## performance tracking
PerformanceTracker.register_module_start(__name__)


## global variables
_LOGGER = AccelerateLogger.get_logger(__name__)


## Wrapper for dataclass
@_LOGGER.audit_class()
class DataClass:
    """Wrapper class for dataclass"""

    def __str__(self):
        return self.to_json()

    def __repr__(self):
        return self.__str__()

    @classmethod
    def fields(cls) -> tuple[Field, ...]:
        assert is_dataclass(cls), "Class is not a dataclass"
        return fields(cls)

    @property
    def classname(self) -> str:
        return str(type(self)).split()[-1][1:-2]

    @property
    def objectId(self) -> int:
        return id(self)

    def as_dict(self) -> dict:
        assert is_dataclass(self), "Object is not a dataclass"
        return {
            k: v for k, v in asdict(self).items() if self.__dataclass_fields__[k].repr
        }

    def to_json(self) -> str:
        return JSON.serialize(self.as_dict())

    def to_yaml(self) -> str:
        return YAML.serialize(self.as_dict())

    def overwrite_field(self, key, value):
        object.__setattr__(self, key, value)


## setting the default for 'repr' injection to false to let 'DataClass.__repr__' take effect
dataclass.__kwdefaults__["repr"] = False  # type: ignore[reportOptionalSubscript]


## export symbols
__all__ = [
    "DataClass",
]


## log performance tracker
PerformanceTracker.log_module_load(__name__)


## disable standalone execution for library
if __name__ == "__main__":
    raise Exception(
        "This is not a standalone module, and should be imported as a library"
    )
