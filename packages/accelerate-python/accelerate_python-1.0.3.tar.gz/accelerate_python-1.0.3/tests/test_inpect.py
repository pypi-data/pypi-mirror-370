## external imports
import inspect

import pytest
from assertpy import assert_that

## internal imports
from accelerate.python import AppException, InspectUtil, WrapperTest


## test cases
class InspectedClass(dict):
    def __init__(self):
        self["val"] = 99

    def main(self):
        var1 = 1
        var2 = "var2"
        var3 = ["var3"]
        var4 = {"var4": 4}

        self.normal(var1, var2, var3, var4=var4)
        self.error()

    def normal(self, name: str, age: str, *args, **kwargs):
        self.set_value("val", 100)
        return {"val": self.get_value("val")}

    def error(self):
        raise AppException("This is a test exception")


class TestInspectUtil(WrapperTest):
    @pytest.fixture
    def target(self) -> InspectedClass:
        return InspectedClass()

    def test_get_fully_qualified_name_with_frame(self):
        frame = inspect.currentframe()
        result = InspectUtil.get_fully_qualified_name(frame)
        assert_that(result).is_equal_to(f"{__name__}.{frame.f_code.co_qualname}")

    def test_get_fully_qualified_name_with_obj(self):
        result = InspectUtil.get_fully_qualified_name(self)
        assert_that(result).is_equal_to("tests.test_inpect.TestInspectUtil")

    def test_get_fully_qualified_name_with_class(self):
        result = InspectUtil.get_fully_qualified_name(InspectUtil)
        assert_that(result).is_equal_to("accelerate.python._inspect.InspectUtil")

    def test_get_error_message(self):
        try:
            raise ValueError("Test error")
        except ValueError as e:
            result = InspectUtil.get_error_message(e)
            assert_that(result).is_equal_to("builtins.ValueError -> Test error")

    def test_inspect_values(self, target: InspectedClass):
        values = [1, "test", target]
        result = InspectUtil.inspect_values(*values)
        expected = [
            "builtins.int:1",
            "builtins.str:test",
            "tests.test_inpect.InspectedClass:{'val': 99}",
        ]
        assert_that(result).is_equal_to(expected)

    def test_inspect_method_arguments(self):
        def sample_method(a, b, c=3):
            pass

        result = InspectUtil.inspect_method_arguments(sample_method, (1, 2), {"c": 4})
        expected = ["a=1", "b=2", "c=4"]
        assert_that(result).is_equal_to(expected)

    # def test_inspect_frame_arguments(self):
    #     def sample_method(a, b, c=3):
    #         return InspectUtil.inspect_frame_arguments()

    #     result = sample_method(1, 2, c=4)
    #     expected = ["a=1", "b=2", "c=4"]
    #     assert_that(result).is_equal_to(expected)

    def test_inspect_variables(self):
        a = 1
        b = "test"
        result = InspectUtil.inspect_variables("a, b")
        expected = [f"a={a}", f"b={b}"]
        assert_that(result).is_equal_to(expected)


if __name__ == "__main__":
    pytest.main([__file__])
