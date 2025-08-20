## external imports
from unittest.mock import patch

import pytest
from assertpy import assert_that

## internal imports
from accelerate.python import AbstractMethodError, AppException, Task, TaskPool


## test cases
class TestTask:
    def test_task_initialization(self):
        task = Task("test_task")
        assert_that(task, "__init__").is_instance_of(Task).has_name(
            "test_task"
        ).has_props({}).has_future(None).has_error(None)

    def test_task_get_prop(self):
        task = Task("test_task", key1="value1")
        assert_that(task.get_prop("key1")).is_equal_to("value1")
        assert_that(task.get_prop("key2", "default")).is_equal_to("default")

    def test_task_set_future(self):
        task = Task("test_task")
        future = object()  # Mock future object
        task.set_future(future)
        assert_that(task.future).is_equal_to(future)

    def test_task_run_abstract_method(self):
        task = Task("test_task")
        with pytest.raises(AbstractMethodError):
            task.run()

    def test_task_start(self):
        class MyTask(Task):
            def run(self):
                self.props["key1"] = "value1"

        task = MyTask("my_task")
        task.start()
        assert_that(task).has_error(None).has_props({"key1": "value1"})

    def test_task_start_with_exception(self):
        class MyTask(Task):
            def run(self):
                raise ValueError("Test error")

        task = MyTask("my_task")
        with pytest.raises(ValueError):
            task.start()
        assert_that(task.error).is_instance_of(ValueError)


class TestTaskPool:
    @pytest.fixture
    def task_pool(self):
        return TaskPool(20)

    def test_task_pool_init(self, task_pool: TaskPool):
        assert_that(task_pool.maxWorkers).is_equal_to(20)
        assert_that(task_pool.tasks).is_empty()

    def test_task_pool_submit(self, task_pool: TaskPool):
        class MyTask(Task):
            def run(self):
                pass

        task = MyTask("test_task_pool_submit")
        task_pool.submit(task)
        assert_that(task.future, "submitted task").is_not_none()
        assert_that(task_pool.tasks).is_not_empty().contains(task.name)

    def test_task_pool_shutdown(self, task_pool: TaskPool, caplog):
        class MyTask(Task):
            def run(self):
                pass

        task = MyTask("test_task_pool_shutdown")
        task_pool.submit(task)
        task_pool.shutdown()
        assert_that(task_pool.executor._shutdown).is_true()
        assert_that(caplog.text).contains("shutdown.complete: tasks=1 | time=")

    def test_task_pool_shutdown_with_exception(self):
        task_pool = TaskPool()

        class MyTask(Task):
            def run(self):
                raise ValueError("Test error")

        task = MyTask("test_task_pool_shutdown_with_exception")
        task_pool.submit(task)
        with pytest.raises(AppException):
            task_pool.shutdown(fail_on_error=True)

    @patch("concurrent.futures.Future.exception")
    @patch("concurrent.futures.ThreadPoolExecutor.shutdown")
    def test_shutdown_default_options(
        self, mock_shutdown, mock_exception, task_pool: TaskPool
    ):
        task_pool.submit(Task("test_shutdown_default_options")).shutdown(
            fail_on_error=False
        )
        mock_shutdown.assert_called_once_with(wait=True, cancel_futures=False)
        mock_exception.assert_called_once_with(timeout=None)

    @patch("concurrent.futures.Future.exception")
    @patch("concurrent.futures.ThreadPoolExecutor.shutdown")
    def test_shutdown_change_options(
        self, mock_shutdown, mock_exception, task_pool: TaskPool
    ):
        task_pool.submit(Task("test_shutdown_change_options")).shutdown(
            False, True, 5, False
        )
        mock_shutdown.assert_called_once_with(wait=False, cancel_futures=True)
        mock_exception.assert_called_once_with(timeout=5)

    def test_shutdown_fail_on_error_true(self, task_pool: TaskPool):
        task = Task("test_shutdown_fail_on_error_true")
        task_pool.submit(task)
        with pytest.raises(AppException):
            task_pool.shutdown(fail_on_error=True)

    def test_shutdown_fail_on_error_false(self, task_pool: TaskPool):
        task = Task("test_shutdown_fail_on_error_false")
        task_pool.submit(task)

        try:
            task_pool.shutdown(fail_on_error=False)
        except AppException:
            pytest.fail("AppException was raised with fail_on_error=False")


if __name__ == "__main__":
    pytest.main([__file__])
