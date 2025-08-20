## external imports
from decimal import Decimal
from pathlib import Path

import pytest
from assertpy import assert_that
from openpyxl import Workbook
from pandas import DataFrame

## internal imports
from accelerate.python import AppException, PandasUtil, WrapperTest

## global variables
INPUT_PATH = Path(__file__).parent.joinpath("input")


## test cases
class TestPandasUtil(WrapperTest):
    @pytest.fixture
    def data_frame(self):
        return DataFrame(
            {
                "field1": ["value1", "value2", "3.5"],
                "field2": [None, 2, 3],
                "field3": [None, None, 22 / 7],
            }
        )

    def test_get_field(self, data_frame: DataFrame):
        row = data_frame.iloc[0]
        assert_that(PandasUtil.get_field(row, "field1"), "get_field").is_equal_to(
            "value1"
        )
        assert_that(
            PandasUtil.get_field(row, "field2", required=False), "get_field - optional"
        ).is_none()
        assert_that(PandasUtil.get_field, "get_field - required").raises(
            AppException
        ).when_called_with(row, "field3")

    def test_get_string_field(self, data_frame: DataFrame):
        row = data_frame.iloc[1]
        assert_that(
            PandasUtil.get_string_field(row, "field1"), "get_string_field"
        ).is_equal_to("value2")
        assert_that(
            PandasUtil.get_string_field(row, "field2"), "get_string_field - numeric"
        ).is_equal_to("2.0")
        assert_that(
            PandasUtil.get_string_field(row, "field3", required=False),
            "get_string_field - optional",
        ).is_empty()

    def test_get_decimal_field(self, data_frame: DataFrame):
        row = data_frame.iloc[2]
        assert_that(
            PandasUtil.get_decimal_field(row, "field1"), "get_decimal_field - string"
        ).is_equal_to(3.50)
        assert_that(
            PandasUtil.get_decimal_field(row, "field2"), "get_decimal_field"
        ).is_equal_to(3.00)
        assert_that(
            PandasUtil.get_decimal_field(row, "field3", precision=3),
            "get_decimal_field - precision",
        ).is_equal_to(Decimal("3.143"))
        assert_that(
            PandasUtil.get_decimal_field(
                data_frame.iloc[1], "field3", precision=2, required=False
            ),
            "get_decimal_field - None",
        ).is_equal_to(Decimal("0.00"))

    def test_to_excel(self, data_frame: DataFrame):
        path = self.get_output_path("test_to_excel.xlsx")
        assert_that(PandasUtil.to_excel(data_frame, path), "to_excel").is_equal_to(path)
        self.assert_path_exists(path)

    def test_to_workbook(self, data_frame: DataFrame):
        assert_that(PandasUtil.to_workbook(data_frame), "to_workbook").is_instance_of(
            Workbook
        )


if __name__ == "__main__":
    pytest.main([__file__])
