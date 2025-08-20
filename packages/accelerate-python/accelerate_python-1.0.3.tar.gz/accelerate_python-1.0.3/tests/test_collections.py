## external imports
import xml.etree.ElementTree as xml_package
from pathlib import Path

import pytest
from assertpy import assert_that

## internal imports
from accelerate.python import (
    DICT,
    JSON,
    LIST,
    XML,
    YAML,
    AppException,
    Properties,
    WrapperTest,
)

## global variables
DATA_PATH = Path(__file__).parent.joinpath("input/data")


## test cases
class TestDICT(WrapperTest):
    @pytest.fixture
    def json(self) -> dict:
        return JSON.read_file(DATA_PATH.joinpath("test.json"))

    def test_get_key_list(self, json: dict):
        assert_that(DICT.get_key_list({}), "get_key_list").is_iterable().is_empty()

        assert_that(DICT.get_key_list(json), "get_key_list").is_equal_to(
            ["a", "b", "c", "f", "g"]
        )
        assert_that(DICT.get_key_list(json, level=2), "get_key_list.2").is_equal_to(
            ["a", "b", "c.d", "c.e", "f", "g"]
        )

    def test_get_value(self, json: dict):
        assert_that(DICT.get_value({}, "any_key"), "NO_TARGET_OR_KEY").is_none()
        assert_that(DICT.get_value(json, ""), "NO_TARGET_OR_KEY").is_none()

        assert_that(DICT.get_value(json, "no_key.child_key"), "NO_KEY_VALUE").is_none()

        assert_that(DICT.get_value, "NON_NUMERIC_LIST_INDEX").raises(
            KeyError
        ).when_called_with(json, "f.a")

        assert_that(
            DICT.get_value(json, "b.not_dict"), "KEY_VALUE_NOT_A_DICT"
        ).is_none()
        assert_that(DICT.get_value(json, "c.missing"), "MISSING_KEY_PART").is_none()

        assert_that(
            DICT.get_value(json, "h", default_value="default"),
            "default_value",
        ).is_equal_to("default")

    def test_set_value(self, json: dict):
        assert_that(DICT.set_value({}, "", "value"), "NO_KEY")

        DICT.set_value(json, "f.3", 8)
        assert_that(DICT.get_value(json, "f.3"), "Set List Value").is_equal_to(8)

        dict_obj = {}
        DICT.set_value(dict_obj, "key.innerkey", "value")
        assert_that(dict_obj, "inner_set_value").is_equal_to(
            {"key": {"innerkey": "value"}}
        )

    def test_set_value_errors(self):
        assert_that(DICT.set_value, "NO_KEY_VALUE").raises(KeyError).when_called_with(
            {"a": None}, "a.b", None
        )

        assert_that(DICT.set_value, "NON_NUMERIC_LIST_INDEX").raises(
            KeyError
        ).when_called_with({"a": []}, "a.b", "value")

    def test_search(self):
        assert_that(
            DICT.search({"key": {"innerkey": "value"}}, "key.innerkey"), "search"
        ).is_equal_to("value")

    def test_merge(self):
        main_dict = {"key1": "value1"}
        assert_that(DICT.merge(main_dict), "No overrides").is_equal_to(main_dict)

        override_dict = {"key2": "value2"}
        DICT.merge(main_dict, override_dict, {})
        assert_that(main_dict, "merge").contains_entry({"key2": "value2"})

        main_dict = {"key": {"innerkey1": "value1"}, "key2": None}
        override_dict = {"key": {"innerkey2": "value2"}, "key2": "value2"}
        DICT.merge(main_dict, override_dict)
        assert_that(main_dict["key"], "nested_merge").contains_entry(
            {"innerkey2": "value2"}
        )
        assert_that(main_dict["key2"], "replace None").is_equal_to("value2")

    def test_compare(self):
        dict_1 = {
            "key0": "value0",
            "key1": "value1",
            "key2": "value2",
            "key3": {"key3.1": "value3.1"},
        }
        dict_2 = {
            "key1": "value1",
            "key2": "value2.2",
            "key3": {"key3.1": "value3.2"},
            "key4": "value4",
        }

        assert DICT.compare(None, {}) == {}

        assert_that(DICT.compare(dict_1, None), "empty dict_2").is_instance_of(
            dict
        ).contains_key("extra_in_1").does_not_contain_key("extra_in_2")
        assert_that(DICT.compare(None, dict_2), "empty dict_1").is_instance_of(
            dict
        ).contains_key("extra_in_2").does_not_contain_key("extra_in_1")

        result = DICT.compare(dict_1, dict_2)
        assert_that(result, "instance check").is_instance_of(dict)
        # assert_that(result, "extra_in_1").does_not_contain("extra_in_1")
        assert_that(result["extra_in_1"], "extra_in_1").contains_entry(
            {"key0": "value0"}
        )
        assert_that(result["extra_in_2"], "extra_in_2").contains_entry(
            {"key4": "value4"}
        )
        assert_that(result["conflicts"], "conflicts").contains_entry(
            {"key2": ["value2", "value2.2"]}
        ).contains_entry({"key3": {"conflicts": {"key3.1": ["value3.1", "value3.2"]}}})


class TestLIST(WrapperTest):
    input_list = [1, 2, 3, 4, 5]

    def test_sort_list(self):
        # Test case 1: Sorting an empty list
        assert LIST.sort([]) == []

        # Test case 2: Sorting a list with one element
        assert LIST.sort([5]) == [5]

        # Test case 3: Sorting a list with multiple elements
        input_list = [3, 1, 4, 1, 5, 9, 2, 6, 5]
        expected_output = [1, 1, 2, 3, 4, 5, 5, 6, 9]
        assert LIST.sort(input_list) == expected_output

        # Test case 4: Sorting a list with duplicate elements
        input_list = [2, 1, 3, 2, 1]
        expected_output = [1, 1, 2, 2, 3]
        assert LIST.sort(input_list) == expected_output

    def test_get_list_item_with_valid_index(self):
        result = LIST.get(self.input_list, 2)
        assert result == 3

    def test_get_list_item_with_invalid_index(self):
        result = LIST.get(self.input_list, 10)
        assert result is None

    def test_get_list_item_with_empty_list(self):
        result = LIST.get([], 0)
        assert result is None

    def test_get_list_item_with_non_list_input(self):
        with pytest.raises(AppException):
            LIST.get("not a list", 0)

    def test_filter_list_with_function_filter(self):
        result = LIST.filter(self.input_list, lambda x: x % 2 == 0)
        assert result == [2, 4]

    def test_filter_list_with_value_filter(self):
        result = LIST.filter(self.input_list, 3)
        assert result == [3]

    def test_filter_list_with_invalid_input(self):
        with pytest.raises(AppException):
            LIST.filter("not a list", lambda x: x % 2 == 0)

    def test_group_by_empty(self):
        assert LIST.group_by(None, None) == {}

    def test_group_by_non_list(self):
        with pytest.raises(AppException):
            LIST.group_by("not a list", None)

    def test_group_by_valid(self):
        input = [
            {"key": "value1", "group": "A"},
            {"key": "value2", "group": "B"},
            {"key": "value3", "group": "A"},
        ]
        output = LIST.group_by(input, lambda o: o["group"])
        assert len(output) == 2
        assert len(output["A"]) == 2
        assert len(output["B"]) == 1
        assert output["A"][0]["key"] == "value1"

        output = LIST.group_by(input, lambda o: o["group"], lambda v: v["key"])
        assert output["A"][0] == "value1"

        output = LIST.group_by(
            input, lambda o: o["group"], lambda v: v["key"], lambda v: len(v)
        )
        assert output["A"] == 2


class TestJSON(WrapperTest):
    def test_load_json(self):
        json_obj = JSON.load('{"key": "value"}')
        assert_that(json_obj, "load").is_equal_to({"key": "value"})
        json_obj = JSON.load('{"root": {"key": "value"}}', root_key="root")
        assert_that(json_obj, "load - root_key").is_equal_to({"key": "value"})

    def test_serialize(self):
        assert_that(JSON.serialize({"key": "value"}), "serialize").is_equal_to(
            '{"key": "value"}'
        )
        assert_that(
            JSON.serialize({"key": "value"}, indent=2), "serialize"
        ).is_equal_to('{\n  "key": "value"\n}')

    def test_read_file(self):
        assert_that(
            JSON.read_file(DATA_PATH.joinpath("test.json"))["a"],
            "read_file",
        ).is_equal_to(1)

    def test_write_json(self):
        file_path = self.get_output_path("test_write_json.json")
        json_obj = {"key": "value"}
        JSON.write_file(json_obj, file_path)
        self.assert_path_exists(file_path, "write_json")
        read = JSON.read_file(file_path)
        assert_that(read, "write_json").is_equal_to(json_obj)


class TestYAML(WrapperTest):
    def test_load(self):
        yaml_obj = YAML.load("key:\n  innerkey: value")
        assert_that(yaml_obj, "load").is_equal_to({"key": {"innerkey": "value"}})
        yaml_obj = YAML.load("key:\n  innerkey: value", root_key="key")
        assert_that(yaml_obj, "load - root_key").is_equal_to({"innerkey": "value"})

    def test_serialize(self):
        assert_that(
            YAML.serialize({"key": {"innerkey": "value"}}), "serialize"
        ).is_equal_to("key:\n  innerkey: value\n")

    def test_read_file(self):
        assert_that(
            YAML.read_file(DATA_PATH.joinpath("test.yaml"))["a"], "read_yaml"
        ).is_equal_to(1)

    def test_write_yaml(self):
        file_path = self.get_output_path("test_write_yaml.yaml")
        yaml_obj = {"key": {"innerkey": "value"}}
        YAML.write_file(yaml_obj, file_path)
        self.assert_path_exists(file_path, "write_file")
        read = YAML.read_file(file_path)
        assert_that(read, "write_file").is_equal_to(yaml_obj)

    def test_load_all(self):
        yaml_objs = YAML.load_all(
            "key:\n  innerkey: value\n---\nkey2:\n  innerkey2: value2"
        )
        assert_that(yaml_objs, "load_all").is_iterable().is_length(2)
        assert_that(yaml_objs[1], "load_all.1").is_equal_to(
            {"key2": {"innerkey2": "value2"}}
        )

    def test_read_mult_file(self):
        yaml_objs = YAML.read_multi_file(DATA_PATH.joinpath("test_multi.yaml"))
        assert_that(yaml_objs, "read_multi_file").is_iterable().is_length(2)
        assert_that(yaml_objs[1]["f"][0], "read_mult_yaml").is_equal_to(5)


class TestProperties(WrapperTest):
    def test_load(self):
        assert_that(Properties.load("key.innerkey=value"), "load").is_equal_to(
            {"key": {"innerkey": "value"}}
        )

    def test_serialize(self):
        assert_that(
            Properties.serialize({"key": {"innerkey": "value"}}), "serialize"
        ).is_equal_to("key.innerkey=value")

    def test_read_file(self):
        assert_that(
            Properties.read_file(DATA_PATH.joinpath("test.properties"))["a"],
            "read_file",
        ).is_equal_to("1")

    def test_write_file(self):
        file_path = self.get_output_path("test_write_properties.properties")
        props_obj = {"key": {"innerkey": "value"}}
        Properties.write_file(props_obj, file_path)
        self.assert_path_exists(file_path, "write_file")
        read = Properties.read_file(file_path)
        assert_that(read, "write_file").is_equal_to(props_obj)


class TestWrapperXML(WrapperTest):
    def test_load(self):
        content = "<root><element>value1</element></root>"
        assert_that(XML.load(content), "load").is_instance_of(xml_package.ElementTree)

    def test_serialize(self):
        assert_that(
            XML.serialize(XML.load("<root><element>value1</element></root>")),
            "serialize",
        ).contains("<element>value1</element>")

    def test_read_file(self):
        xml = XML.read_file(DATA_PATH.joinpath("test.xml"))
        assert_that(xml, "read_file").is_instance_of(xml_package.ElementTree)

    def test_write_file(self):
        file_path = self.get_output_path("test_write_xml.xml")
        content = "<root><element>value1</element></root>"
        xml = XML.load(content)
        XML.write_file(xml, file_path)
        self.assert_path_exists(file_path, "write_file")
        read = XML.read_file(file_path)
        assert_that(read, "write_file").is_instance_of(xml_package.ElementTree)

    # def test_find(self):
    #     xml = XML.read_file(DATA_PATH.joinpath("test.xml"))
    #     assert_that(XML.find("element"), "find").is_not_none().has_text("value1")

    # def test_find_all(self):
    #     xml = XML.read_file(DATA_PATH.joinpath("test.xml"))
    #     assert_that(wrapper.find_all("element"), "find_all").is_length(2).extracting(
    #         "text"
    #     ).is_equal_to(["value1", "value2"])

    # def test_find_text(self):
    #     xml = XML.read_file(DATA_PATH.joinpath("test.xml"))
    #     assert_that(XML.find_text("element"), "find_text").is_equal_to("value1")


if __name__ == "__main__":
    pytest.main([__file__])
