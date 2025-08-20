"""This module provides wrapper classes for executing system processes/commands"""

## external imports
import os
import shutil
import subprocess
from dataclasses import dataclass, field
from pathlib import Path
from typing import Self

## internal imports
from ._dataclasses import DataClass
from ._exceptions import AppException
from ._inspect import InspectUtil
from ._logging import AccelerateLogger
from ._tracker import PerformanceTracker
from ._utils import Environment

## performance tracking
PerformanceTracker.register_module_start(__name__)


## global variables
_LOGGER = AccelerateLogger.get_logger(__name__)


## class definitions
@dataclass(frozen=True)
@_LOGGER.audit_class()
class Process(DataClass):
    """
    Wrapper class to manage process executions
    """

    name: str
    args: list
    kwargs: dict
    returnCode: int
    stdout: str
    stderr: str
    error: Exception | None
    completedProcess: subprocess.CompletedProcess | None = field(
        default=None, repr=False, compare=False, init=True
    )

    def __repr__(self):
        return f"{self.name}[{self.returnCode}]"

    def log(self, level: int | None = None):
        if self.returnCode != 0:
            _LOGGER.log(
                level or AccelerateLogger.ERROR, "Process errored out: {}", self
            )
        elif self.completedProcess is None:
            _LOGGER.log(
                level or AccelerateLogger.WARNING, "Process not executed: {}", self
            )
        else:
            _LOGGER.log(
                level or AccelerateLogger.VERBOSE,
                "Process completed successfully: {}",
                self,
            )

    @classmethod
    def execute(cls, name, *args, **kwargs) -> Self:
        AppException.check(args, "No Arguments: {}", args)
        AppException.check(
            not any([arg for arg in args if not arg]),
            "Empty process arguments: {}",
            args,
        )

        if kwargs.get("simulation", Environment.is_simulation_enabled()):
            _stdout = "Simulation enabled. Retuning without executing"
            _LOGGER.warning("{}: {} | {}", _stdout, name, args)
            return cls(name, list(args), kwargs, 0, _stdout, "", None, None)

        if "dir" in kwargs:
            _LOGGER.verbose("Switching current directory: {}", kwargs["dir"])
            os.chdir(kwargs["dir"])

        try:
            completed_process = subprocess.run(args, capture_output=True)
            return_code = completed_process.returncode
            stdout = completed_process.stdout.decode("utf-8", "ignore")
            stderr = completed_process.stderr.decode("utf-8", "ignore")
            error = None
        except Exception as exc:
            completed_process = None
            return_code = -1
            stdout = ""
            stderr = InspectUtil.get_error_message(exc)
            error = exc

        process = cls(
            name,
            list(args),
            kwargs,
            return_code,
            stdout,
            stderr,
            error,
            completed_process,
        )

        if return_code != 0 and kwargs.get("fail_on_error", True):
            process.log()
            raise AppException(
                "Process failed: {}",
                name,
                error_code=return_code,
                process=process,
            )

        return process

    ## shortcuts for common process executions
    @classmethod
    def python(cls, file: str | Path, *args, **kwargs) -> Self:
        """Execute python script with arguments"""
        file = Path(file)
        AppException.check(file.is_file(), "Python file not found: {}", file)

        return cls.execute(
            kwargs.pop("name", f"python[{file.stem}]"),
            shutil.which("python3"),
            file.as_posix(),
            *args,
            **kwargs,
        )

    @classmethod
    def mvn(cls, pom: str | Path, *args, **kwargs) -> Self:
        """Execute maven command with arguments"""
        pom = Path(pom)
        AppException.check(pom.is_file(), "POM file not found: {}", pom)

        return cls.execute(
            kwargs.pop("name", f"mvn[{pom.parent.stem}][{args[-1]}]"),
            shutil.which("mvn"),
            "-f",
            pom.as_posix(),
            *args,
            **kwargs,
        )

    @classmethod
    def npm(cls, project: str | Path, *args, **kwargs) -> Self:
        """Execute npm command with arguments"""
        project = Path(project)
        package_json = project.joinpath("package.json")
        AppException.check(
            package_json.is_file(), "package.json not found: {}", package_json
        )

        return cls.execute(
            kwargs.pop("name", f"npm[{project.stem}]"),
            shutil.which("npm"),
            "--prefix",
            project.as_posix(),
            *args,
            **kwargs,
        )

    @classmethod
    def az(cls, cmd: str, *args, **kwargs) -> Self:
        """Execute az command with arguments"""
        AppException.check(cmd, "az command is mandatory")

        return cls.execute(
            kwargs.pop("name", f"az[{cmd}]"), shutil.which("az"), cmd, *args, **kwargs
        )

    @classmethod
    def pwsh(cls, cmd_or_script: str | Path, *args, **kwargs) -> Self:
        """Execute pwsh command with arguments"""
        AppException.check(cmd_or_script, "pwsh command or script is mandatory")
        cmd_or_script = Path(cmd_or_script)

        _flag = kwargs.pop("type", "command")  # "file"
        if _flag == "file":
            AppException.check(
                cmd_or_script.is_file(),
                "PowerShell script not found: {}",
                cmd_or_script,
            )

        return cls.execute(
            kwargs.pop("name", f"pwsh[{cmd_or_script.stem}]"),
            shutil.which("pwsh"),
            f"-{_flag.capitalize()}",
            cmd_or_script.as_posix(),
            *args,
            **kwargs,
        )


## export symbols
__all__ = ["Process"]


## log performance tracker
PerformanceTracker.log_module_load(__name__)


## disable standalone execution for library
if __name__ == "__main__":
    raise Exception(
        "This is not a standalone module, and should be imported as a library"
    )
