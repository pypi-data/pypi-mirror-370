## external imports
import pytest
from assertpy import assert_that

## internal imports
from accelerate.python import AccelerateLogger, WrapperTest
from accelerate.python._logging import FormatLogRecord

## global variables
_LOGGER = AccelerateLogger.get_logger(__name__)


## test cases
class TestAccelerateLogger(WrapperTest):
    def test_initialize_logger(self, caplog):
        log_file = self.get_output_path("TestAccelerateLogger.log")
        _logger = AccelerateLogger.initialize(
            "accelerate.python", level=AccelerateLogger.INFO, file=log_file
        )
        assert_that(_logger, "initialize").is_instance_of(AccelerateLogger)
        assert_that(_logger.root.level, "root level").is_equal_to(AccelerateLogger.INFO)

        _logger.verbose("This is a verbose message")
        assert_that(caplog.text, "log at lower level").does_not_contain(
            "This is a verbose message"
        )

        _logger.warning("This is a warning message")
        assert_that(caplog.text, "log at higher level").contains(
            "This is a warning message"
        )

        _logger = AccelerateLogger.initialize(
            "accelerate.python",
            level=AccelerateLogger.VERBOSE,
            file=None,
            update_loggers={"accelerate.python": AccelerateLogger.INFO},
        )
        assert_that(_logger, "initialize").is_instance_of(AccelerateLogger)
        assert_that(_logger.root.level, "root level").is_equal_to(
            AccelerateLogger.VERBOSE
        )
        assert_that(caplog.text, "update_loggers").contains(
            "Updating Logger Level: accelerate.python -> INFO"
        )

        _logger.info("This is a %s with %%", "message")
        assert_that(caplog.text, "update_loggers").contains("This is a message with %")

    def test_get_logger(self):
        assert_that(_LOGGER, "logger").is_instance_of(AccelerateLogger)

    @_LOGGER.audit_method()
    def test_update_restore_level_and_trace(self, caplog):
        _LOGGER.update_level(AccelerateLogger.TRACE)
        _LOGGER.trace("This is a trace message")
        assert_that(caplog.text, "update_level_and_trace").contains(
            "This is a trace message"
        )
        _LOGGER.restore_level()
        _LOGGER.trace("This is another trace message")
        assert_that(caplog.text, "restore_level").does_not_contain(
            "This is another trace message"
        )

    def test_log_variables(self, caplog):
        var1, var2, var3, var4 = 1, "var2", ["var3"], {"var4": 4}
        _LOGGER.debug_variables("var1, var2", "debug_variables")
        assert_that(caplog.text, "log_variables").does_not_contain(
            f"debug_variables -> var1={var1} | var2={var2}"
        )

        _LOGGER.log_variables(
            "var3, var4", "log_variables", level=AccelerateLogger.WARNING
        )
        assert_that(caplog.text, "log_variables").contains(
            f"log_variables -> var3={var3} | var4={var4}"
        )

    # def test_log_args(self, logger: AccelerateLogger, caplog):
    #     logger.log_args(
    #         1, "var2", ["var3"], {"var4": 4}, log_level=AccelerateLogger.WARNING
    #     )
    #     assert_that(caplog.text, "log_args").contains(
    #         "TestAccelerateLogger.test_logger_log_args: 1 | var2 | ['var3'] | {'var4': 4}"
    #     )

    # def test_log_args_verbose(self, logger: AccelerateLogger, caplog):
    #     logger.log_args_verbose(1, "var2", ["var3"], {"var4": 4})
    #     assert_that(caplog.text, "log_args").contains(
    #         "TestAccelerateLogger.test_log_args_verbose: 1 | var2 | ['var3'] | {'var4': 4}"
    #     )

    # def test_log_args_trace(self, logger: AccelerateLogger, caplog):
    #     logger.log_args_trace(1, "var2", ["var3"], {"var4": 4})
    #     assert_that(caplog.text, "log_args").does_not_contain(
    #         "TestAccelerateLogger.test_log_args_trace: 1 | var2 | ['var3'] | {'var4': 4}"
    #     )


class TestFormatLogRecord(WrapperTest):
    def test_format_log_record(self):
        record = FormatLogRecord(
            "test_logger",
            AccelerateLogger.INFO,
            __file__,
            1,
            "This is a {} message",
            ("formatted",),
            None,
            "test_format_log_record",
            None,
        )
        assert record.getMessage() == "This is a formatted message"


if __name__ == "__main__":
    pytest.main([__file__])
