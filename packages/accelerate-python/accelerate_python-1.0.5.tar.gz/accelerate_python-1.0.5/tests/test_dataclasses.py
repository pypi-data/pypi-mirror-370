## external imports
from dataclasses import dataclass
from pathlib import Path

import pytest
from assertpy import assert_that

## internal imports
from accelerate.python import DataClass, WrapperTest

## global variables
DATA_PATH = Path(__file__).parent.joinpath("input/data")


## test cases
@dataclass
class SampleDataClass(DataClass):
    field1: int
    field2: str


class TestDataClass(WrapperTest):
    def test_dataclass_str(self):
        obj = SampleDataClass(field1=1, field2="test")
        assert_that(str(obj)).is_equal_to(obj.to_json())

    def test_dataclass_repr(self):
        obj = SampleDataClass(field1=1, field2="test")
        assert_that(repr(obj)).is_equal_to(obj.to_json())

    def test_dataclass_fields(self):
        fields = SampleDataClass.fields()
        assert_that(fields).extracting("name").contains("field1", "field2")

    def test_dataclass_classname(self):
        obj = SampleDataClass(field1=1, field2="test")
        assert_that(obj.classname).is_equal_to("tests.test_dataclasses.SampleDataClass")

    def test_dataclass_objectId(self):
        obj = SampleDataClass(field1=1, field2="test")
        assert_that(obj.objectId).is_equal_to(id(obj))

    def test_dataclass_as_dict(self):
        obj = SampleDataClass(field1=1, field2="test")
        expected_dict = {"field1": 1, "field2": "test"}
        assert_that(obj.as_dict()).is_equal_to(expected_dict)

    def test_dataclass_to_json(self):
        obj = SampleDataClass(field1=1, field2="test")
        expected_json = '{"field1": 1, "field2": "test"}'
        assert_that(obj.to_json()).is_equal_to(expected_json)

    def test_dataclass_to_yaml(self):
        obj = SampleDataClass(field1=1, field2="test")
        expected_yaml = "field1: 1\nfield2: test\n"
        assert_that(obj.to_yaml()).is_equal_to(expected_yaml)

    def test_dataclass_overwrite_field(self):
        obj = SampleDataClass(field1=1, field2="test")
        obj.overwrite_field("field1", 2)
        assert_that(obj.field1).is_equal_to(2)


if __name__ == "__main__":
    pytest.main([__file__])
