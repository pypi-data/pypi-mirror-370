## external imports
import subprocess
from unittest.mock import MagicMock, patch

import pytest
from assertpy import assert_that

## internal imports
from accelerate.python import (
    AccelerateLogger,
    AppException,
    Environment,
    Process,
    WrapperTest,
)

## initialize
Environment.set("SIMULATION", "false")


## test cases
class TestProcess(WrapperTest):
    @staticmethod
    def mock_completed_process():
        mock = MagicMock(subprocess.CompletedProcess)
        mock.returncode = 0
        mock.stdout = b"Mock stdout"
        mock.stderr = b"Mock stderr"

        return mock

    def test_execute_success(self, caplog):
        process = Process.execute("test_process", "echo", "hello")
        assert_that(process, "execute").is_instance_of(Process).has_name(
            "test_process"
        ).has_args(["echo", "hello"]).has_returnCode(0).has_stdout("hello\n")
        assert_that(process.completedProcess, "execute.no-simulation").is_not_none()

        assert_that(str([process]), "repr").is_equal_to("[test_process[0]]")

        process.log(AccelerateLogger.ERROR)
        assert_that(caplog.text, "log").contains(
            'Process completed successfully: {"name": "test_process", "args": ["echo", "hello"], "kwargs": {}, "returnCode": 0, '
        )

    def test_execute_failure(self):
        process = Process.execute(
            "test_process", "missing_command", fail_on_error=False
        )
        assert_that(process, "execute").is_instance_of(Process).has_name(
            "test_process"
        ).has_args(["missing_command"]).has_returnCode(-1)
        assert_that(process.stderr, "execute.stderr").contains(
            "builtins.FileNotFoundError -> [Errno 2] No such file or directory: 'missing_command'"
        )

        with pytest.raises(AppException):
            Process.execute("test_process", "missing_command")

    @patch("accelerate.python._utils.Environment")
    def test_process_execute_simulation(self, mock_environment):
        mock_environment.is_simulation_enabled.return_value = True

        process = Process.execute("test_process", "echo", "hello")
        assert_that(process, "execute.simulation").is_instance_of(Process).has_name(
            "test_process"
        ).has_args(["echo", "hello"]).has_returnCode(0).has_stdout(
            "Simulation enabled. Retuning without executing"
        )
        assert_that(process.completedProcess, "execute.simulation").is_none()

    @patch("pathlib.Path.is_file", return_value=True)
    @patch("shutil.which", return_value="/usr/bin/python")
    @patch("subprocess.run", return_value=mock_completed_process())
    def test_process_python(self, *args):
        process = Process.python(
            "test_python.py", "-arg1", "val1", name="python_test_script"
        )
        assert_that(process, "python").is_instance_of(Process).has_name(
            "python_test_script"
        ).has_args(
            ["/usr/bin/python", "test_python.py", "-arg1", "val1"]
        ).has_returnCode(0).has_stdout("Mock stdout")

    @patch("pathlib.Path.is_file", return_value=True)
    @patch("shutil.which", return_value="/usr/bin/mvn")
    @patch("subprocess.run", return_value=mock_completed_process())
    def test_process_mvn(self, *args):
        process = Process.mvn("accelerate_python/pom.xml", "clean", "install")
        assert_that(process, "mvn").is_instance_of(Process).has_name(
            "mvn[accelerate_python][install]"
        ).has_args(
            ["/usr/bin/mvn", "-f", "accelerate_python/pom.xml", "clean", "install"]
        ).has_returnCode(0).has_stdout("Mock stdout")

    @patch("pathlib.Path.is_file", return_value=True)
    @patch("shutil.which", return_value="/usr/bin/npm")
    @patch("subprocess.run", return_value=mock_completed_process())
    def test_process_npm(self, *args):
        process = Process.npm("accelerate_python", "list", "--all")
        assert_that(process, "npm").is_instance_of(Process).has_name(
            "npm[accelerate_python]"
        ).has_args(
            ["/usr/bin/npm", "--prefix", "accelerate_python", "list", "--all"]
        ).has_returnCode(0).has_stdout("Mock stdout")

    @patch("pathlib.Path.is_file", return_value=True)
    @patch("shutil.which", return_value="/usr/bin/az")
    @patch("subprocess.run", return_value=mock_completed_process())
    def test_process_az(self, *args):
        process = Process.az("account", "show")
        assert_that(process, "az").is_instance_of(Process).has_name(
            "az[account]"
        ).has_args(["/usr/bin/az", "account", "show"]).has_returnCode(0).has_stdout(
            "Mock stdout"
        )

    @patch("pathlib.Path.is_file", return_value=True)
    @patch("shutil.which", return_value="/usr/bin/pwsh")
    @patch("subprocess.run", return_value=mock_completed_process())
    def test_process_pwsh(self, *args):
        process = Process.pwsh("test_command")
        assert_that(process, "pwsh script").is_instance_of(Process).has_name(
            "pwsh[test_command]"
        ).has_args(["/usr/bin/pwsh", "-Command", "test_command"]).has_returnCode(
            0
        ).has_stdout("Mock stdout")

        process = Process.pwsh("test_script.ps1", type="file")
        assert_that(process, "pwsh script").is_instance_of(Process).has_name(
            "pwsh[test_script]"
        ).has_args(["/usr/bin/pwsh", "-File", "test_script.ps1"]).has_returnCode(0)


if __name__ == "__main__":
    pytest.main([__file__])
