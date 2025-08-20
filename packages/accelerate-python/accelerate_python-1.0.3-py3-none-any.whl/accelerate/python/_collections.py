"""This module provides wrapper/utility classes for basic collection types like dict, list, etc."""

## external Imports
import copy
import itertools
import json
import re
import xml.etree.ElementTree as xml_package
from dataclasses import asdict, is_dataclass
from io import BytesIO
from operator import itemgetter
from pathlib import Path
from typing import Any, Callable, cast

import jmespath
import yaml
from jproperties import Properties as JProperties

## internal imports
from ._exceptions import AppException
from ._logging import AccelerateLogger
from ._tracker import PerformanceTracker
from ._utils import AppUtil, PathUtil

## performance tracking
PerformanceTracker.register_module_start(__name__)


## global variables
_LOGGER = AccelerateLogger.get_logger(__name__)
_TOKEN_SPLITTER = re.compile(r"(?<!\\)\.")


## class definitions
@_LOGGER.audit_class(exclude=["__check_type", "__get_key_tokens"])
class DICT:
    @staticmethod
    def get_key_list(dict_obj: dict, level=1):
        DICT.__check_type(dict_obj)

        if not dict_obj:
            return []

        if level == 1:
            return list(dict_obj.keys())

        key_list = []
        key_stack = []
        current_depth = [0]

        def traverse_dict(dict_obj: dict):
            current_depth[0] = current_depth[0] + 1

            # print("1.0 | ", current_depth[0], " | ", dict.keys())

            for _k, _v in dict_obj.items():
                key_stack.append(_k)
                # print("2.0 | ", current_depth[0], " | ", _k, " | ", key_stack)

                if current_depth[0] < level and isinstance(_v, dict):
                    # print("3.1 | ", current_depth[0], " | ", _k, " | ", _v.keys())
                    traverse_dict(_v)
                    # print("3.2 | ", current_depth[0], " | ", _k, " | ", key_stack)
                else:
                    # print("4.0 | ", current_depth[0], " | ", _k, " | ", key_stack)
                    key_list.append(AppUtil.join_string(".", key_stack))
                    key_stack.pop()

                # print("5.0 | ", current_depth[0], " | ", _k, " | ", key_stack)

            current_depth[0] = current_depth[0] - 1
            if key_stack:
                key_stack.pop()
            # print("6.0 | ", current_depth[0], " | ", _k, " | ", dict.keys())

        traverse_dict(dict_obj)
        return key_list

    @staticmethod
    def get_value(dict_obj: dict, *keys, default_value=None):
        """
        This method gets the key value from given dictionary.
        It supports dot delimited as well as multiple keys to traverse inside the dictionary.
        """
        DICT.__check_type(dict_obj)

        key_path = AppUtil.join_string(".", *keys)
        if not dict_obj or not key_path.strip():
            _LOGGER.trace("NO_TARGET_OR_KEY: {} == {}", len(dict_obj), len(key_path))
            return default_value

        key_tokens = DICT.__get_key_tokens(key_path)
        key_value = dict_obj
        for key_part in key_tokens:
            if key_value is None:
                _LOGGER.trace("NO_KEY_VALUE: {} | {}", key_part, key_value)
                return default_value

            if isinstance(key_value, dict):
                if key_part not in key_value:
                    _LOGGER.trace(
                        "MISSING_KEY_PART: {} | {}", key_part, key_value.keys()
                    )
                    return default_value
                key_value = key_value[key_part]
            elif isinstance(key_value, list):
                if not key_part.isnumeric():
                    _LOGGER.error("NON_NUMERIC_LIST_INDEX: {} | {}", key_part, key_path)
                    raise KeyError(f"NON_NUMERIC_LIST_INDEX: {key_part} | {key_path}")

                idx = int(key_part)
                if idx >= len(key_value):
                    _LOGGER.trace("INDEX_OUT_OF_BOUNDS: {} | {}", idx, key_value)
                    return default_value

                key_value = key_value[idx]
            else:
                _LOGGER.trace(
                    "UNKNOWN_CONDITION: {} | {} | {}",
                    key_part,
                    type(key_value),
                    key_value,
                )
                return default_value

        return key_value

    @staticmethod
    def search(dict_obj: dict, jmes_path: str) -> Any:
        """
        Method run a JMES path search on dict
        """
        DICT.__check_type(dict_obj)

        return jmespath.search(jmes_path, dict_obj)

    @staticmethod
    def set_value(dict_obj: dict, key: str | list[str], value):
        """
        This method set the key value into given dictionary.
        It supports dot delimited as well as multiple keys to traverse inside the dictionary.
        """
        DICT.__check_type(dict_obj)

        key_path = key if isinstance(key, str) else AppUtil.join_string(".", *key)

        if not key_path.strip():
            _LOGGER.trace("NO_KEY: {} | {}", len(dict_obj), len(key_path))
            return

        key_tokens = DICT.__get_key_tokens(key_path)
        last_key = key_tokens.pop()
        key_value = dict_obj
        for key_idx, key_part in enumerate(key_tokens):
            _LOGGER.trace("KEY_PART: {} | {} | {}", key_idx, key_part, key_tokens)

            next_val: str = ""
            if key_idx == len(key_tokens) - 1:
                next_val = last_key
            else:
                next_val = key_tokens[key_idx + 1]
            _LOGGER.trace("NEXT_VAL: {} | {}", key_idx, next_val)

            if key_value is None:
                _LOGGER.error("NO_KEY_VALUE: {} | {}", key_part, key_path)
                raise KeyError(f"NO_KEY_VALUE: {key_part} | {key_path}")

            elif isinstance(key_value, list):
                if not key_part.isnumeric():
                    _LOGGER.error("NON_NUMERIC_LIST_INDEX: {} | {}", key_part, key_path)
                    raise KeyError(f"NON_NUMERIC_LIST_INDEX: {key_part} | {key_path}")

                list_len = len(key_value)
                key_part = int(key_part)

                if list_len != 0 and key_part != 0 and key_part >= list_len:
                    raise IndexError(
                        f"Index out of bounds for list value: {key_part} | {key_path}"
                    )

                if list_len > 0:
                    _temp_value = key_value[key_part]
                    key_value[key_part] = _temp_value
                else:
                    _temp_value = [] if next_val.isnumeric() else {}
                    key_value.append(_temp_value)

                key_value = _temp_value
            else:
                ## dicts can have numeric keys
                # if key_part.isnumeric():
                #     raise KeyError(
                #         f"Numeric key for non-list value: {key_part} | {type(key_value)} | {key_path}"
                #     )

                key_value = key_value.setdefault(key_part, {})

        if key_value is None:
            _LOGGER.error("NO_KEY_VALUE: {} | {}", last_key, key_path)
            raise KeyError(f"NO_KEY_VALUE: {last_key} | {key_path}")

        if isinstance(key_value, list):
            if not last_key.isnumeric():
                _LOGGER.error("NON_NUMERIC_LIST_INDEX: {} | {}", last_key, key_path)
                raise KeyError(f"NON_NUMERIC_LIST_INDEX: {last_key} | {key_path}")
            key_value.insert(int(last_key), value)
        else:
            key_value[last_key] = value

        return value

    @staticmethod
    def merge(dict_obj: dict, *overrides: dict, key_stack: list[str] = []):
        DICT.__check_type(dict_obj)

        if not overrides or len(overrides) == 0:
            _LOGGER.debug("No overrides provided")
            return dict_obj

        if len(overrides) > 1:
            for override_dict in overrides:
                if not override_dict:
                    continue

                AppException.check(
                    isinstance(override_dict, dict),
                    "Only Objects {{}} are supported: {} | {}",
                    type(override_dict),
                    override_dict,
                )

                DICT.merge(dict_obj, override_dict)

            return dict_obj

        override_dict = overrides[0]
        _LOGGER.trace("Merging Override ...")
        for key, value in override_dict.items():
            new_value = copy.deepcopy(value)
            if key not in dict_obj:
                dict_obj[key] = new_value
            else:
                current_value = dict_obj[key]
                key_stack = [*key_stack.copy(), key]
                if not current_value:
                    dict_obj[key] = new_value
                elif isinstance(current_value, dict) and isinstance(new_value, dict):
                    DICT.merge(current_value, new_value, key_stack=key_stack)
                else:
                    _LOGGER.trace("OVERRIDE: {}", key_stack)
                    dict_obj[key] = new_value

        return dict_obj

    @staticmethod
    def compare(dict_1: dict, dict_2: dict):
        result = {}

        if not dict_1 and not dict_2:
            return result

        if not dict_2:
            result["extra_in_1"] = dict_1
            return result

        if not dict_1:
            result["extra_in_2"] = dict_2
            return result

        for key, value in dict_1.items():
            if key not in dict_2:
                result.setdefault("extra_in_1", {})[key] = value
                continue

            if isinstance(value, dict):
                cmp_val = DICT.compare(value, dict_2[key])
                if cmp_val:
                    result.setdefault("conflicts", {})[key] = cmp_val
            elif value != dict_2[key]:
                result.setdefault("conflicts", {})[key] = [value, dict_2[key]]

        for key, value in dict_2.items():
            if key not in dict_1:
                result.setdefault("extra_in_2", {})[key] = value

        return result

    @staticmethod
    def __get_key_tokens(key_path: str) -> list[str]:
        return [part.replace("\\", "") for part in _TOKEN_SPLITTER.split(key_path)]

    @staticmethod
    def __check_type(value: dict):
        AppException.check(
            isinstance(value, dict),
            "Value shoud be of type dict: got -> {}",
            type(value),
        )


@_LOGGER.audit_class(exclude=["__check_type"])
class LIST:
    @staticmethod
    def get(value: list, index: int = 0) -> Any:
        if not value:
            return None

        LIST.__check_type(value)

        if AppUtil.get_length(value) > index:
            return value[index]

        return None

    @staticmethod
    def sort(value: list, key=None, reverse=False) -> list:
        LIST.__check_type(value)
        value.sort(key=key, reverse=reverse)
        return value

    @staticmethod
    def filter(value: list, filter):
        LIST.__check_type(value)

        from inspect import isfunction

        return [x for x in value if (filter(x) if isfunction(filter) else x == filter)]

    @staticmethod
    def group_by(
        value: list,
        key_fn: Callable[[Any], str],
        value_fn: Callable[[Any], Any] | None = None,
        group_fn: Callable[[Any], Any] | None = None,
    ) -> dict[str, Any]:
        if not value:
            return {}

        LIST.__check_type(value)
        value.sort(key=key_fn)  # as group_by expects sorted input

        grouped_dict = {
            key: [value_fn(v) if value_fn else v for v in value]
            for key, value in itertools.groupby(value, key_fn)
        }

        if group_fn:
            grouped_dict = {key: group_fn(value) for key, value in grouped_dict.items()}

        return grouped_dict

    @staticmethod
    def __check_type(value: list):
        AppException.check(
            isinstance(value, list),
            "Value shoud be of type list: got -> {}",
            type(value),
        )


@_LOGGER.audit_class()
class JSON:
    @staticmethod
    def load(input_string: str, **kwargs) -> dict | list:
        root_key = kwargs.pop("root_key", None)

        json_obj = json.loads(input_string, **kwargs)

        if root_key is not None:
            json_obj = itemgetter(root_key)(json_obj)

        return json_obj

    @staticmethod
    def load_dict(input_string: str, **kwargs) -> dict:
        return cast(dict, JSON.load(input_string, **kwargs))

    @staticmethod
    def load_list(input_string: str, **kwargs) -> list:
        return cast(list, JSON.load(input_string, **kwargs))

    @staticmethod
    def serialize(json_obj, **kwargs) -> str:
        kwargs.setdefault(
            "default",
            lambda o: asdict(o)
            if is_dataclass(o) and not isinstance(o, type)
            else repr(o),
        )  # default to dict for dataclasses and repr for others

        return json.dumps(json_obj, **kwargs)

    @staticmethod
    def read_file(*paths: str | Path, **kwargs) -> dict | list:
        return JSON.load(Path(*paths).read_text(encoding=kwargs.get("encoding")))

    @staticmethod
    def read_dict(*paths: str | Path, **kwargs) -> dict:
        return cast(dict, JSON.read_file(*paths, **kwargs))

    @staticmethod
    def read_list(*paths: str | Path, **kwargs) -> list:
        return cast(list, JSON.read_file(*paths, **kwargs))

    @staticmethod
    def write_file(json_obj, *paths: str | Path, **kwargs) -> Path:
        kwargs.setdefault("indent", "\t")  # default to tab indentation for file writing
        return PathUtil.write_file(JSON.serialize(json_obj, **kwargs), *paths, **kwargs)


@_LOGGER.audit_class()
class YAML:
    @staticmethod
    def load(yaml_string: str, **kwargs):
        root_key = kwargs.pop("root_key", None)

        yaml_obj = yaml.load(yaml_string, Loader=yaml.FullLoader)

        if root_key is not None:
            yaml_obj = itemgetter(root_key)(yaml_obj)

        return yaml_obj

    @staticmethod
    def load_dict(input_string: str, **kwargs) -> dict:
        return cast(dict, YAML.load(input_string, **kwargs))

    @staticmethod
    def load_list(input_string: str, **kwargs) -> list:
        return cast(list, YAML.load(input_string, **kwargs))

    @staticmethod
    def serialize(*yaml_objs, **kwargs) -> str:
        kwargs.setdefault("sort_keys", False)

        ## pyyaml configuration
        ## register representer to handle YAML instances
        # yaml.add_representer(
        #     WrapperDict, yaml.representer.SafeRepresenter.represent_dict
        # )
        ## register representer to handle any dict
        # yaml.add_representer(dict, yaml.representer.SafeRepresenter.represent_dict)
        ## crude fix for removing !!python/object/apply:<classname> tag
        yaml.emitter.Emitter.prepare_tag = lambda self, tag: ""
        return yaml.dump_all(yaml_objs, **kwargs)

    @staticmethod
    def read_file(*paths: str | Path, **kwargs):
        return YAML.load(
            Path(*paths).read_text(encoding=kwargs.get("encoding")), **kwargs
        )

    @staticmethod
    def read_dict(*paths: str | Path, **kwargs) -> dict:
        return cast(dict, YAML.read_file(*paths, **kwargs))

    @staticmethod
    def read_list(*paths: str | Path, **kwargs) -> list:
        return cast(list, YAML.read_file(*paths, **kwargs))

    @staticmethod
    def write_file(yaml_obj, *paths: str | Path, **kwargs):
        return PathUtil.write_file(YAML.serialize(yaml_obj, **kwargs), *paths, **kwargs)

    @staticmethod
    def load_all(yaml_string: str) -> list:
        all_yaml = yaml.load_all(yaml_string, Loader=yaml.FullLoader)
        return [yaml_obj for yaml_obj in all_yaml if yaml_obj]

    @staticmethod
    def read_multi_file(*paths: str | Path, encoding=None) -> list:
        return YAML.load_all(Path(*paths).read_text(encoding=encoding))

    @staticmethod
    def write_multi_file(yaml_objs: list[dict | list], *paths: str | Path, **kwargs):
        return PathUtil.write_file(
            YAML.serialize(yaml_objs, **kwargs), *paths, **kwargs
        )


@_LOGGER.audit_class()
class Properties:
    @staticmethod
    def load(input_string: str, **kwargs) -> dict:
        props = JProperties()
        props.load(input_string)

        props_obj = {}
        for key, value in props.properties.items():
            if value.startswith("[") or value.startswith("{"):
                DICT.set_value(props_obj, key, json.loads(value))
            else:
                DICT.set_value(props_obj, key, value)

        return props_obj

    @staticmethod
    def serialize(props_obj: dict, key_stack: list[str] = []) -> str:
        key_stack = key_stack or []
        prop_list = []
        for key, value in props_obj.items():
            if isinstance(value, dict):
                _LOGGER.trace_variables(
                    "key,value,key_stack", message="processing dict"
                )
                prop_list.extend(
                    Properties.serialize(value, key_stack + [key]).split("\n")
                )
            elif isinstance(value, list):
                _LOGGER.trace_variables(
                    "key,value,key_stack", message="processing list"
                )
                for idx, val in enumerate(value):
                    prop_list.append(
                        f"{'.'.join(key_stack + [key, str(idx)])}={str(val)}"
                    )
            else:
                _LOGGER.trace_variables(
                    "key,value,key_stack", message="processing value"
                )
                prop_list.append(f"{'.'.join(key_stack + [key])}={str(value)}")

        return "\n".join(prop_list)

    @staticmethod
    def read_file(*paths: str | Path, **kwargs) -> dict:
        return Properties.load(
            Path(*paths).read_text(encoding=kwargs.get("encoding")), **kwargs
        )

    @staticmethod
    def write_file(props_obj, *paths: str | Path, **kwargs):
        return PathUtil.write_file(Properties.serialize(props_obj), *paths, **kwargs)


@_LOGGER.audit_class()
class XML:
    @staticmethod
    def load(xml: str) -> xml_package.ElementTree:
        return xml_package.ElementTree(xml_package.fromstring(xml))

    @staticmethod
    def serialize(xml: xml_package.ElementTree, **kwargs) -> str:
        stream = BytesIO()
        xml.write(
            stream,
            "",
            xml_declaration=True,
            default_namespace="",
            method="xml",
            short_empty_elements=True,
        )
        return stream.getvalue().decode()

    @staticmethod
    def read_file(
        *paths: str | Path, namespaces: dict = {}, encoding=None
    ) -> xml_package.ElementTree:
        return XML.load(Path(*paths).read_text(encoding=encoding))

    @staticmethod
    def write_file(xml, *paths: str | Path, **kwargs):
        return PathUtil.write_file(XML.serialize(xml, **kwargs), *paths, **kwargs)


## export symbols
__all__ = [
    "DICT",
    "LIST",
    "JSON",
    "YAML",
    "Properties",
    "XML",
]


## log performance tracker
PerformanceTracker.log_module_load(__name__)


## disable standalone execution for library
if __name__ == "__main__":
    raise Exception(
        "This is not a standalone module, and should be imported as a library"
    )
