## external imports
import pytest
from assertpy import assert_that

## internal imports
from accelerate.python import AbstractMethodError, AppException


## test cases
class TestAppException:
    def test_app_exception(self):
        error_message = "An error occurred"
        error_code = 500
        error_data = {"key": "value"}

        exception = AppException(error_message, error_code=error_code, **error_data)
        assert_that(str(exception), "__str__").is_equal_to(
            f"{error_code} | {error_message} | {error_data}"
        )

    def test_check(self):
        with pytest.raises(AppException) as exc_info:
            AppException.check(False, "An error occurred")

        assert_that(str(exc_info.value), "check").is_equal_to(
            "-1 | An error occurred | {}"
        )


class TestClass:
    def method(self):
        raise AbstractMethodError()


class TestAbstractMethodError:
    def test_abstract_method_error(self):
        with pytest.raises(AbstractMethodError) as exc_info:
            TestClass().method()

        assert_that(str(exc_info.value), "AbstractMethodError").contains(
            "Class [TestClass] does not implement abstract method: `TestClass.method`"
        )


if __name__ == "__main__":
    pytest.main([__file__])
