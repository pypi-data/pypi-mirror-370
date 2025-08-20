## external imports
import sys
from unittest.mock import patch

import pytest
from assertpy import assert_that

## internal imports
from accelerate.python import (
    AccelerateLogger,
    AppUtil,
    Base64,
    Environment,
    PathUtil,
    WrapperTest,
)

## global variables


## test cases
class TestEnvironment(WrapperTest):
    def test_get_all_env_vars(self):
        env_vars = Environment.get_all()
        assert_that(env_vars, "get_all").is_instance_of(dict).is_not_empty()

    def test_get(self):
        Environment.set("ENV_VAR", "value")
        assert_that(Environment.get("ENV_VAR"), "get").is_equal_to("value")

    def test_is_enabled(self):
        Environment.set("ENV_VAR_TRUE", "true")
        assert_that(Environment.is_enabled("ENV_VAR_TRUE"), "is_enabled").is_true()

        Environment.set("ENV_VAR_FALSE", "value")
        assert_that(Environment.is_enabled("ENV_VAR_FALSE"), "is_enabled").is_false()

    def test_is_simulation_enabled(self):
        Environment.set("SIMULATION", "true")
        assert_that(
            Environment.is_simulation_enabled(), "is_simulation_enabled"
        ).is_true()


class TestAppUtil(WrapperTest):
    def test_is_empty(self):
        assert AppUtil.is_empty(None)
        assert not AppUtil.is_empty(1)
        assert not AppUtil.is_empty(False)
        assert AppUtil.is_empty("")
        assert not AppUtil.is_empty("not empty")
        assert AppUtil.is_empty([])
        assert not AppUtil.is_empty([1, 2, 3])
        assert AppUtil.is_empty({})
        assert not AppUtil.is_empty({"key": "value"})
        assert not AppUtil.is_empty(1 == 1)

    def test_get_length(self):
        assert AppUtil.get_length([]) == 0
        assert AppUtil.get_length([1, 2, 3]) == 3
        assert AppUtil.get_length("hello") == 5
        assert AppUtil.get_length("") == 0

    def test_get_or_default(self):
        # Test case 1: When a_value is not empty
        a_value = "Hello"
        default_value = "World"
        result = AppUtil.get_or_default(a_value, default_value)
        assert result == a_value

        # Test case 2: When a_value is empty
        a_value = ""
        default_value = "World"
        result = AppUtil.get_or_default(a_value, default_value)
        assert result == default_value

        # Test case 3: When a_value is None
        a_value = None
        default_value = "World"
        result = AppUtil.get_or_default(a_value, default_value)
        assert result == default_value

    def test_join_string(self):
        # Test case 1: Empty value list
        separator = ","
        value_list = []
        assert AppUtil.join_string(separator, *value_list) == ""

        # Test case 2: Single value in the list
        separator = ","
        value_list = ["Hello"]
        assert AppUtil.join_string(separator, *value_list) == "Hello"

        # Test case 3: Multiple values in the list
        separator = ","
        value_list = ["Hello", "World"]
        assert AppUtil.join_string(separator, *value_list) == "Hello,World"

        # Test case 4: List as a single value
        separator = ","
        value_list = ["Hello", "World"]
        assert AppUtil.join_string(separator, value_list) == "Hello,World"

        # Test case 5: Integer values
        separator = "-"
        value_list = [1, 2, 3]
        assert AppUtil.join_string(separator, *value_list) == "1-2-3"

    @patch("sys.exit")
    def test_exit(self, mock_exit, caplog):
        AppUtil.exit("EXIT_FAILURE: {}", "WITH_ARGS")
        mock_exit.assert_called_once_with(1)
        assert_that(caplog.text).contains("EXIT_FAILURE: WITH_ARGS")

        AppUtil.exit("EXIT_FAILURE {}", "WITH_ARGS", exit_code=2)
        mock_exit.assert_called_with(2)

        AppUtil.exit("EXIT_SUCCESS", exit_code=0)
        mock_exit.assert_called_with(0)
        assert_that(caplog.text).contains("EXIT_SUCCESS")

    @patch("time.sleep")
    def test_wait(self, mock_sleep, caplog):
        wait_seconds = 5
        wait_seconds
        message = "Waiting for process to {}"
        args = ("complete",)
        log_level = AccelerateLogger.CRITICAL

        AppUtil.wait(wait_seconds, message, *args, log_level=log_level)
        mock_sleep.assert_called_once_with(wait_seconds)
        assert_that(caplog.text).contains(message.format(*args))

    def test_copy_object(self):
        # Test case 1: Copying a list
        original_list = [1, 2, 3]
        copied_list = AppUtil.copy_object(original_list)
        assert copied_list == original_list
        assert copied_list is not original_list

        # Test case 2: Copying a dictionary
        original_dict = {"key": "value"}
        copied_dict = AppUtil.copy_object(original_dict)
        assert copied_dict == original_dict
        assert copied_dict is not original_dict

        # Test case 3: Copying a nested object
        original_nested = {"list": [1, 2, 3], "dict": {"key": "value"}}
        copied_nested = AppUtil.copy_object(original_nested)
        assert copied_nested == original_nested
        assert copied_nested is not original_nested

        # Test case 4: Copying an object with custom attributes
        class CustomObject:
            def __init__(self, value):
                self.value = value

        original_custom = CustomObject(42)
        copied_custom = AppUtil.copy_object(original_custom)
        assert copied_custom.value == original_custom.value
        assert copied_custom is not original_custom


class TestBase64(WrapperTest):
    def test_base64_encode(self):
        value = "Hello, World!"
        encoded_value = Base64.encode(value)
        assert isinstance(encoded_value, str)
        assert encoded_value == "SGVsbG8sIFdvcmxkIQ=="

    def test_base64_decode(self):
        encoded_value = "SGVsbG8sIFdvcmxkIQ=="
        decoded_value = Base64.decode(encoded_value)
        assert isinstance(decoded_value, bytes)
        assert decoded_value == b"Hello, World!"

    def test_base64_decode_to_string(self):
        encoded_value = "SGVsbG8sIFdvcmxkIQ=="
        decoded_string = Base64.decode_to_string(encoded_value)
        assert isinstance(decoded_string, str)
        assert decoded_string == "Hello, World!"


class TestPathUtil(WrapperTest):
    def test_tmp_dir(self):
        self.assert_path_is_dir(PathUtil.temp_dir(), "temp_dir")

    def test_add_sys_path(self):
        PathUtil.append_sys_path("/path/to/directory")
        assert_that(sys.path).contains("/path/to/directory")


if __name__ == "__main__":
    pytest.main([__file__])
