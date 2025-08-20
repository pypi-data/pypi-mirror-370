## external imports
import argparse
from unittest.mock import patch

import pytest
from assertpy import assert_that

## internal imports
from accelerate.python import (
    AccelerateLogger,
    Environment,
    ProgramArgs,
    WrapperTest,
)


## test cases
class TestProgramArgs(WrapperTest):
    @pytest.fixture
    def args(self) -> ProgramArgs:
        _args = ProgramArgs("Test Program")

        _args.add_argument("--attr1", default="value1")
        _args.add_argument("--attr2", default="value2")
        _args.add_argument("--flag1", action="store_true")
        _args.add_argument("--flag2", action="store_false")
        _args.add_argument(
            "-r", "--required", required=True, dest="required", help="Required"
        )
        _args.add_argument(
            "-o", "--optional", required=False, dest="optional", help="Optional"
        )
        _args.add_boolean_argument(
            "-b", "--boolean", required=False, dest="boolean", help="Boolean"
        )
        _args.add_run_mode_argument(True, "mode1", "mode2")

        input = [
            "-r",
            "requiredValue",
            "-o",
            "optionalValue",
            "-m",
            "mode1",
            "--kwargs",
            "a=b",
            "c=d",
            "--env",
            "envKeyA=envValB",
            "--attr2",
            "value222",
            "--flag1",
        ]
        _args.read(args=input)

        return _args

    def test_init(self, args: ProgramArgs):
        assert_that(args, "Instance Check").is_instance_of(argparse.ArgumentParser)
        assert_that(args.prog, "Program").is_equal_to("Test Program")

    def test_add_boolean_argument(self, args: ProgramArgs):
        assert_that(args.boolean, "Boolean Arg").is_instance_of(bool)
        action = next(filter(lambda x: x.dest == "boolean", args._actions))
        assert_that(
            action.type("yes")
            and not action.type("no")
            and action.type("enabled")
            and not action.type("disabled"),
            "Boolean Type",
        ).is_true()

    def test_add_run_mode_argument(self, args: ProgramArgs):
        assert_that(args.runMode, "runMode").is_equal_to("mode1")
        action = next(filter(lambda x: x.dest == "runMode", args._actions))
        assert_that(action.choices, "Run Modes").is_equal_to(["mode1", "mode2"])
        assert_that(action.required, "Required Argument").is_true()

    def test_read(self, args: ProgramArgs):
        # ## test default arguments
        # elif action.dest == "simulation":
        #     if action.option_strings == ["--simulation"]:
        #         assert action.default
        #     elif action.option_strings == ["--NS"]:
        #         assert type(action) is argparse._StoreFalseAction
        # elif action.dest == "logLevel":
        #     assert action.choices == list(_LOG_LEVELS.keys())
        #     assert action.default == "i"
        # elif action.dest == "logFile":
        #     assert action.default is None

        ## known arguments
        assert_that(args.attr1, "attr1").is_equal_to("value1")
        assert_that(args.attr2, "attr2").is_equal_to("value222")
        assert_that(args.flag1, "flag1").is_true()
        assert_that(args.flag2, "flag2").is_true()
        assert_that(args.required, "required arg").is_equal_to("requiredValue")
        assert_that(args.optional, "optional arg").is_equal_to("optionalValue")
        assert_that(args.runMode, "runMode").is_equal_to("mode1")

        ## default arguments
        assert_that(args.simulation, "simulation").is_false()
        assert_that(args.logLevel, "logLevel").is_none()
        assert_that(args.logFile, "logFile").is_none()

        ## config flags
        assert_that(args.configFlags, "configFlags").is_equal_to({"a": "b", "c": "d"})

        ## environment variables
        assert_that(Environment.get("envKeyA"), "Env Var").is_equal_to("envValB")

    def test_read_unknown(self):
        args = ProgramArgs("Test Program")
        args.read(allow_extra_args=True, args=["--unknown", "unknownValue"])
        assert_that(args.unknownArgs, "unknownArgs").is_not_empty().is_equal_to(
            ["--unknown", "unknownValue"]
        )

    def test_add_default_arguments(self):
        args = ProgramArgs("Test Program")

        ## no default arguments
        args.read(add_default_arguments=False, args=[])
        # assert_that(hasattr(args, "simulation"), "simulation arg").is_false()
        # assert_that(hasattr(args, "logLevel"), "logLevel arg").is_false()
        # assert_that(hasattr(args, "logFile"), "logFile arg").is_false()
        assert_that(args.simulation, "simulation").is_false()
        assert_that(args.logLevel, "logLevel").is_none()
        assert_that(args.logFile, "logFile").is_none()

        ## default arguments
        args.read(
            add_default_arguments=True,
            simulation=False,
            log_level="d",
            log_file="test.log",
            args=[],
        )
        assert_that(args.simulation, "simulation arg").is_false()
        assert_that(args.logLevel, "logLevel arg").is_equal_to("D")
        assert_that(args.logFile, "logFile arg").is_equal_to("test.log")
        assert_that(Environment.is_enabled("SIMULATION"), "SIMULATION").is_false()

    @patch("accelerate.python.AccelerateLogger.initialize")
    def test_initialize_logging(self, mock_initialize):
        ProgramArgs("Test Program").read(
            log_level="d", log_file="test.log", args=[]
        ).initialize_logging()
        mock_initialize.assert_called_once_with(
            "test_program", AccelerateLogger.DEBUG, "test.log"
        )


if __name__ == "__main__":
    pytest.main([__file__])
