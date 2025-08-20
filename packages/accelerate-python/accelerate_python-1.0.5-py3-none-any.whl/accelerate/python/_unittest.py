## external imports
import functools
from pathlib import Path

## internal imports
from ._logging import AccelerateLogger

## global variables
_LOGGER = AccelerateLogger.get_logger(__name__)
OUTPUT_PATH = Path(__file__).parent.parent.parent.parent.joinpath("tests/output")
_TEST_FILES: dict[str, list[Path]] = {}


## parent test class
@_LOGGER.audit_class()
class WrapperTest:
    def get_output_path(self, *paths: str | Path) -> Path:
        path = OUTPUT_PATH.joinpath(*paths)
        _TEST_FILES.setdefault(self.__class__.__name__, []).append(path)
        return path

    def assert_path_exists(self, path: Path, message: str = ""):
        assert_that(path.as_posix(), message).exists()

    def assert_path_is_dir(self, path: Path, message: str = ""):
        assert_that(path.as_posix(), message).is_directory()

    @staticmethod
    def cleanup_files(func):
        """
        A decorator to clean up files created inside the wrapped function.
        It tracks files created during the execution and ensures they are deleted after the function completes.
        """

        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            path = None
            try:
                return func(*args, **kwargs)
            finally:
                try:
                    class_name = func.__qualname__.split(".")[0]
                    for path in _TEST_FILES.pop(class_name, []):
                        # path.unlink()
                        _LOGGER.warning(f"Cleaned Up File: {path}")
                except Exception:
                    _LOGGER.exception("Error cleaning up files: {}", path)

        return wrapper


## adding extensions to assertpy
try:
    from assertpy import assert_that
    # add_extension(WrapperTest.assert_path_exists)
    # add_extension(WrapperTest.assert_path_is_dir)
except ImportError:
    ## ignoring assertpy import error as it is only used in unittests
    pass
