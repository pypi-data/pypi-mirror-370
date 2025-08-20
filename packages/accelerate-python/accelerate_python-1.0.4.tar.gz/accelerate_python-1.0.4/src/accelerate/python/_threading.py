"""This module wrapper classes to execute tasks in parallel"""

## external imports
import concurrent.futures
import threading
import time
from abc import abstractmethod
from typing import Any, Generic, Self, TypeVar

## internal imports
from ._exceptions import AbstractMethodError, AppException
from ._logging import AccelerateLogger
from ._tracker import PerformanceTracker

## performance tracking
PerformanceTracker.register_module_start(__name__)


## global variables
_LOGGER = AccelerateLogger.get_logger(__name__)
_TaskType = TypeVar("_TaskType", bound="Task")


## class definitions
@_LOGGER.audit_class()
class Task:
    """
    Custom class to execute operations as a Thread
    """

    __slots__ = ("__name", "__props", "__future", "__error")

    def __init__(self, name: str, **props: dict[str, Any]) -> None:
        self.__name = name
        self.__props = props
        self.__future = None
        self.__error = None

    @property
    def name(self) -> str:
        return self.__name

    @property
    def props(self) -> dict[str, Any]:
        return self.__props

    @property
    def future(self) -> concurrent.futures.Future | None:
        return self.__future

    @property
    def error(self) -> Exception | None:
        return self.__error

    def get_prop(self, key, default_value=None):
        return self.props.get(key, default_value)

    def set_future(self, future: concurrent.futures.Future):
        self.__future = future

    def start(self):
        _LOGGER.info(
            "{}.start: {} | {}", self.__class__.__qualname__, self.name, self.props
        )

        try:
            threading.current_thread().name = self.__name
            self.run()
        except Exception as error:
            self.__error = error
            _LOGGER.exception("Error in Task: {}", self.name)
            raise error

        _LOGGER.info(
            "{}.end: {} | {}", self.__class__.__qualname__, self.name, self.props
        )

    @abstractmethod
    def run(self):
        raise AbstractMethodError()


@_LOGGER.audit_class()
class TaskPool(Generic[_TaskType]):
    __slots__ = ("__maxWorkers", "__executor", "__tasks")

    def __init__(self, max_workers=10):
        self.__maxWorkers = max_workers
        self.__executor = concurrent.futures.ThreadPoolExecutor(max_workers)
        self.__tasks = {}

    @property
    def maxWorkers(self) -> int:
        return self.__maxWorkers

    @property
    def executor(self) -> concurrent.futures.ThreadPoolExecutor:
        return self.__executor

    @property
    def tasks(self) -> dict[str, _TaskType]:
        return self.__tasks

    def submit(self, *tasks: _TaskType) -> Self:
        for task in tasks:
            task.set_future(self.executor.submit(task.start))
            self.tasks[task.name] = task

        return self  # for chaining

    def shutdown(
        self,
        wait: bool = True,
        cancel_futures: bool = False,
        timeout: float | None = None,
        fail_on_error: bool = True,
    ):
        _LOGGER.log_variables(
            "self.tasks,wait,cancel_futures,timeout,fail_on_error",
            "shutdown.initiated",
            level=AccelerateLogger.NOTICE,
        )

        start = time.perf_counter()
        self.executor.shutdown(wait=wait, cancel_futures=cancel_futures)
        # task_pool_result = concurrent.futures.wait([t.future for t in self.tasks.values()])
        end = time.perf_counter()

        _LOGGER.success(
            "shutdown.complete: tasks={} | time={:.6f} seconds",
            len(self.tasks),
            (end - start),
        )

        failed_tasks = [
            task
            for task in self.tasks.values()
            if task.future is not None and task.future.exception(timeout=timeout)
        ]
        if failed_tasks and fail_on_error:
            raise AppException(
                "TaskPool Error", error_data={t.name: t.error for t in failed_tasks}
            )


## export symbols
__all__ = ["Task", "TaskPool"]


## log performance tracker
PerformanceTracker.log_module_load(__name__)


## disable standalone execution for library
if __name__ == "__main__":
    raise Exception(
        "This is not a standalone module, and should be imported as a library"
    )
