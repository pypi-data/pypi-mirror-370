"""This module provides wrapper classes for pandas library"""

## external imports
from decimal import Decimal
from io import BytesIO
from pathlib import Path

import pandas
from openpyxl.workbook.workbook import Workbook

from ._exceptions import AppException
from ._logging import AccelerateLogger

## internal imports
from ._microsoft import ExcelUtil
from ._tracker import PerformanceTracker

## start performance tracker
PerformanceTracker.register_module_start(__name__)


## global variables
_LOGGER = AccelerateLogger.get_logger(__name__)


## class definitions
@_LOGGER.audit_class()
class PandasUtil:
    @staticmethod
    def get_field(row: pandas.Series, field_name: str, required: bool = True):
        field_value = row[field_name]
        is_valid = pandas.isna(field_value) is False

        AppException.check(
            required is False or is_valid, "Field is required: {}", field_name
        )

        return field_value if is_valid else None

    @staticmethod
    def get_string_field(row: pandas.Series, field_name: str, required: bool = True):
        field_value = PandasUtil.get_field(row, field_name, required)
        return str(field_value or "")

    @staticmethod
    def get_decimal_field(
        row: pandas.Series,
        field_name: str,
        precision: int = 2,
        required: bool = True,
    ) -> Decimal:
        field_value = PandasUtil.get_string_field(row, field_name, required)
        return Decimal(str(round(Decimal(field_value or 0), precision)))

    @staticmethod
    def to_excel(data: pandas.DataFrame, path: str | Path) -> Path:
        output = Path(path)
        with pandas.ExcelWriter(output.as_posix(), engine="openpyxl") as writer:
            data.to_excel(writer, index=False)
        return output

    @staticmethod
    def to_workbook(data: pandas.DataFrame) -> Workbook:
        output = BytesIO()
        with pandas.ExcelWriter(output, engine="openpyxl") as writer:  # type: ignore[reportArgumentType]
            data.to_excel(writer, index=False)
        return ExcelUtil.load_workbook(output)


## export symbols
__all__ = ["PandasUtil"]


## log performance tracker
PerformanceTracker.log_module_load(__name__)


## disable standalone execution for library
if __name__ == "__main__":
    raise Exception(
        "This is not a standalone module, and should be imported as a library"
    )
