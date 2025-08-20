"""This module provides wrapper class to manage configuration"""

## external imports
import re
import threading
from pathlib import Path
from typing import Any, Literal, Self

## internal imports
from ._collections import DICT, JSON, YAML
from ._exceptions import AppException
from ._logging import AccelerateLogger
from ._tracker import PerformanceTracker
from ._utils import AppUtil

## performance tracking
PerformanceTracker.register_module_start(__name__)


## global variables
_LOGGER = AccelerateLogger.get_logger(__name__)
_REF_OBJ_PATTERN = re.compile(r"^(\@){(.+)}$")
_REF_LIST_PATTERN = re.compile(r"^(\#){(.+)}$")
_REF_VALUE_PATTERN = re.compile(r"\$\{([^\{\}]+)\}")
_NESTED_PATTERN = re.compile(r"^([\@\#\$]){(.*?(([\@\#\$]){(.+)}).*?)}$")
_THREAD_LOCAL = threading.local()


## class definitions
@_LOGGER.audit_class()
class Config(dict):
    """
    Special dictionary class extending JSON with support for internal references with placeholders like '@{}', '#{}', '${}'.
    It supports nested references and expressions for dictionary normalization.
    It can be used to load and merge multiple configuration files in JSON or YAML formats.
    """

    def __init__(
        self,
        *paths: str | Path,
        config_type: Literal["json", "yaml"] = "yaml",
        normalize=False,
    ) -> None:
        config_path = Path(*paths)
        AppException.check(
            config_path.exists(), "Config Path not found: {}", config_path
        )

        config_files = (
            [config_path]
            if config_path.is_file()
            else list(config_path.rglob(f"*.{config_type}"))
        )
        _LOGGER.verbose("config_files: {}", config_files)

        config_list = [
            JSON.read_file(f) if config_type == "json" else YAML.read_file(f)
            for f in config_files.sort() or config_files
        ]
        _LOGGER.trace("config_list: {}", config_list)

        DICT.merge(self, *config_list)  # type: ignore[reportArgumentType]

        if normalize:
            self.normalize()

        _LOGGER.success("Config Loaded: {}", config_path)

    def get_value(self, *keys, default_value=None) -> Any:
        return DICT.get_value(self, *keys, default_value=default_value)

    def set_value(self, key: str | list[str], value) -> Any:
        return DICT.set_value(self, key, value)

    def normalize(self, **kwargs) -> Self:
        _LOGGER.verbose("Config.normalize: keys={} | kwargs={}", self.keys(), kwargs)

        _LOGGER.trace("pre-normalize: {}", self)

        _THREAD_LOCAL.traceKeys = kwargs.get("trace_keys", [])

        ## config is always of type dict, a root list is not supported
        self.__normalize_dict([], self)

        return self

    def __normalize_dict(self, key_stack: list, dict_value: dict):
        AppException.check(
            isinstance(dict_value, dict),
            "__normalize_dict: Expected dict at '{}', but got {}",
            key_stack,
            dict_value,
        )

        try:
            if "__extends__" in dict_value:
                ## the key extends another key in the same dictionary, so get the value and merge
                _parent_value = self.__normalize_value(
                    [*key_stack, "__extends__"],
                    dict_value.pop("__extends__"),
                )
                assert isinstance(_parent_value, dict), (
                    f"__extends__ must resolve to a dict at '{key_stack}', but got {type(_parent_value).__name__}"
                )
                new_value = DICT.merge({}, _parent_value, dict_value)
                dict_value.clear()
                dict_value.update(new_value)

            for key, value in dict_value.items():
                ## starting a new key stack to debug the current key
                _key_stack = key_stack.copy()
                _key_stack.append(key)
                current_key = AppUtil.join_string(".", _key_stack)

                # enable tracing if required
                if current_key in _THREAD_LOCAL.traceKeys:
                    _LOGGER.update_level(AccelerateLogger.TRACE)

                if isinstance(value, dict):
                    # recursively normalize the dictionary
                    self.__normalize_dict(_key_stack, value)
                elif isinstance(value, list):
                    # traverse the list and normalize the elements
                    self.__normalize_list(_key_stack, value)
                elif isinstance(value, str):
                    # normalize the value and update the dictionary
                    dict_value[key] = self.__normalize_value(_key_stack, value)

                # other value types are carried over as-is

                # disable tracing again
                _LOGGER.restore_level()
        except RecursionError:
            _LOGGER.exception("Recursion Error: {}", key_stack)
            pass

    def __normalize_list(self, key_stack: list, list_value: list):
        AppException.check(
            isinstance(list_value, list),
            "__normalize_list: Expected dict at '{}', but got {}",
            key_stack,
            list_value,
        )

        list_type = None
        new_list = []
        for idx, value in enumerate(list_value):
            _key_stack = key_stack.copy()
            _key_stack.append(idx)

            if value is None:
                new_list.append(value)
                continue

            ## if the list item is not a reference, check if the type is consistent
            if not self.__is_reference(value, _key_stack):
                value_type = type(value)
                if not list_type:
                    # determine list type from the first non-expression value
                    list_type = value_type

                AppException.check(
                    value_type == list_type,
                    f"List Value Type [{_key_stack}]",
                    list_value,
                )

            if isinstance(value, dict):
                self.__normalize_dict(_key_stack, value)
                new_list.append(value)
            elif isinstance(value, list):
                self.__normalize_list(_key_stack, value)
                new_list.extend(value)
            elif isinstance(value, str):
                item_value = self.__normalize_value(_key_stack, value)
                # if item is a reference to another list, extend the list
                if _REF_LIST_PATTERN.match(value) and isinstance(item_value, list):
                    new_list.extend(item_value)
                else:
                    new_list.append(item_value)
            else:
                new_list.append(value)

        list_value.clear()
        list_value.extend(new_list)

    def __normalize_value(self, key_stack: list, value):
        AppException.check(
            isinstance(value, str),
            "__normalize_value: Expected string value for {}, but got {}",
            key_stack,
            value,
        )

        if not self.__is_reference(value, key_stack):
            ## simple value, return as-is
            return value

        return_value = self.__evaluate_reference(value)

        # if the referenced value is a dictionary or list, normalize it recursively
        if isinstance(return_value, dict):
            self.__normalize_dict(key_stack, return_value)
        elif isinstance(return_value, list):
            self.__normalize_list(key_stack, return_value)

        return return_value

    def __evaluate_reference(self, value: str):
        _value = value

        # iteratively find and replace all ${} references
        # if the replaced value is not a string, stop the loop
        while isinstance(_value, str) and re.search(_REF_VALUE_PATTERN, _value):
            matches = _REF_VALUE_PATTERN.findall(_value)
            _LOGGER.trace("Value References: {} | {}", _value, matches)
            for match in matches:
                _referenced_value = self.get_value(match, default_value="__NONE__")
                _LOGGER.trace("Referenced Value: {} | {}", match, _referenced_value)
                _placeholder = f"${{{match}}}"
                if _placeholder == _value:
                    _replaced_value = _referenced_value
                else:
                    _replaced_value = _value.replace(
                        _placeholder, str(_referenced_value)
                    )
                _LOGGER.trace("Post Substitution: {} | {}", _value, _replaced_value)
                _value = _replaced_value

        if isinstance(_value, str):
            # if the evaluated value is a string, check if it is a reference to another object or list
            expr = _REF_OBJ_PATTERN.match(_value) or _REF_LIST_PATTERN.match(_value)
            if expr:
                # 0: full match, 1: expr prefix, 2: reference key
                return self.get_value(expr.group(2), default_value="__NONE__")

        return _value if _value != "__NONE__" else value

    def __is_reference(self, value, key_stack):
        """
        This method checks if the value is a placeholder for dictionary normalization
        """
        if isinstance(value, str):
            if _REF_OBJ_PATTERN.match(value) or _REF_LIST_PATTERN.match(value):
                if _REF_VALUE_PATTERN.search(value):
                    _LOGGER.warning(
                        "Nested references are discouraged due to complexity: {} | {} | {}",
                        key_stack,
                        value,
                        _REF_VALUE_PATTERN.findall(value),
                    )
                return True
            elif _REF_VALUE_PATTERN.search(value):
                return True

        return False

    def test(self):
        print(self.__normalize_value([], "${root.config-2.key-2-1}"))
        print(
            self.__normalize_value(
                [], "${root.${root.config-3.key-3-0}.${root.config-3.key-3-1}}"
            )
        )


## export symbols
__all__ = ["Config"]


## log performance tracker
PerformanceTracker.log_module_load(__name__)


## disable standalone execution for library
if __name__ == "__main__":
    raise Exception(
        "This is not a standalone module, and should be imported as a library"
    )
