"""Tests for ZecMF task monitoring system."""

import json
from typing import Never
from unittest.mock import patch

import pytest
from flask import Flask

from zecmf.extensions.database import db
from zecmf.extensions.task_monitor import (
    TaskLogger,
    create_task_execution,
    ensure_task_execution_exists,
    get_task_execution,
    log_task_message,
    monitored_task,
    update_task_status_by_id,
    with_app_context,
)
from zecmf.models.task_monitoring import (
    TaskExecution,
    TaskExecutionLog,
    TaskExecutionLogLevel,
    TaskExecutionStatus,
)

# Test constants
EXPECTED_LOG_COUNT = 2
EXPECTED_LOG_COUNT_MULTIPLE = 5


class TestTaskMonitoringModels:
    """Test task monitoring database models."""

    def test_task_execution_creation(self, app: Flask) -> None:
        """Test creating a TaskExecution instance."""
        with app.app_context():
            task_execution = TaskExecution(
                task_id="test-task-123",
                task_name="test_task",
                status=TaskExecutionStatus.PENDING.value,
            )
            db.session.add(task_execution)
            db.session.commit()

            assert task_execution.id is not None
            assert task_execution.task_id == "test-task-123"
            assert task_execution.task_name == "test_task"
            assert task_execution.status == TaskExecutionStatus.PENDING.value
            assert task_execution.retry_count == 0

    def test_task_execution_to_dict(self, app: Flask) -> None:
        """Test TaskExecution to_dict method."""
        with app.app_context():
            task_execution = TaskExecution(
                task_id="test-task-123",
                task_name="test_task",
                status=TaskExecutionStatus.SUCCESS.value,
                args="[1, 2, 3]",
                kwargs='{"key": "value"}',
                result='{"status": "ok"}',
            )
            db.session.add(task_execution)
            db.session.commit()

            task_dict = task_execution.to_dict()
            assert task_dict["task_id"] == "test-task-123"
            assert task_dict["task_name"] == "test_task"
            assert task_dict["status"] == TaskExecutionStatus.SUCCESS.value
            assert task_dict["args"] == "[1, 2, 3]"
            assert task_dict["kwargs"] == '{"key": "value"}'
            assert task_dict["result"] == '{"status": "ok"}'

    def test_task_execution_log_creation(self, app: Flask) -> None:
        """Test creating a TaskExecutionLog instance."""
        with app.app_context():
            # Create parent task execution
            task_execution = TaskExecution(
                task_id="test-task-123",
                task_name="test_task",
                status=TaskExecutionStatus.RUNNING.value,
            )
            db.session.add(task_execution)
            db.session.commit()

            # Create log entry
            log_entry = TaskExecutionLog(
                task_execution_id=task_execution.id,
                level=TaskExecutionLogLevel.INFO.value,
                message="Task started",
                context='{"step": 1}',
            )
            db.session.add(log_entry)
            db.session.commit()

            assert log_entry.id is not None
            assert log_entry.task_execution_id == task_execution.id
            assert log_entry.level == TaskExecutionLogLevel.INFO.value
            assert log_entry.message == "Task started"
            assert log_entry.context == '{"step": 1}'

    def test_task_execution_log_relationship(self, app: Flask) -> None:
        """Test TaskExecution and TaskExecutionLog relationship."""
        with app.app_context():
            # Create parent task execution
            task_execution = TaskExecution(
                task_id="test-task-123",
                task_name="test_task",
                status=TaskExecutionStatus.RUNNING.value,
            )
            db.session.add(task_execution)
            db.session.commit()

            # Create multiple log entries
            log1 = TaskExecutionLog(
                task_execution_id=task_execution.id,
                level=TaskExecutionLogLevel.INFO.value,
                message="Task started",
            )
            log2 = TaskExecutionLog(
                task_execution_id=task_execution.id,
                level=TaskExecutionLogLevel.INFO.value,
                message="Task progress",
            )
            db.session.add_all([log1, log2])
            db.session.commit()

            # Test relationship
            assert len(task_execution.logs) == EXPECTED_LOG_COUNT
            assert log1.task_execution == task_execution
            assert log2.task_execution == task_execution


class TestTaskMonitorUtilities:
    """Test task monitoring utility functions."""

    def test_with_app_context_decorator(self, app: Flask) -> None:
        """Test with_app_context decorator."""

        @with_app_context
        def test_function() -> str:
            return "success"

        # Test with app context
        with app.app_context():
            result = test_function()
            assert result == "success"

        # We need to be outside app context to properly test other scenarios
        # The test fixture has an app context, so the rest of the scenarios
        # will be tested in a separate function outside app context

        # For coverage, test the flask_app path by temporarily clearing app context
        from zecmf.extensions import task_monitor  # noqa: PLC0415

        original_flask_app = task_monitor.flask_app

        # The with_app_context decorator prioritizes existing app context,
        # so this tests the normal case where app context is available
        task_monitor.flask_app = app
        with app.app_context():
            result = test_function()
            assert result == "success"

        # Restore original flask_app
        task_monitor.flask_app = original_flask_app

    def test_create_task_execution(self, app: Flask) -> None:
        """Test create_task_execution function."""
        with app.app_context():
            task_execution = create_task_execution(
                task_id="test-task-456",
                task_name="test_create_task",
                args=[1, 2, 3],
                kwargs={"key": "value"},
            )

            assert task_execution.task_id == "test-task-456"
            assert task_execution.task_name == "test_create_task"
            assert task_execution.status == TaskExecutionStatus.PENDING.value
            assert json.loads(task_execution.args) == [1, 2, 3]
            assert json.loads(task_execution.kwargs) == {"key": "value"}

    def test_get_task_execution(self, app: Flask) -> None:
        """Test get_task_execution function."""
        with app.app_context():
            # Create a task execution
            original = create_task_execution(
                task_id="test-task-789", task_name="test_get_task"
            )

            # Get it back
            retrieved = get_task_execution("test-task-789")
            assert retrieved is not None
            assert retrieved.task_id == original.task_id
            assert retrieved.task_name == original.task_name

            # Test non-existent task
            non_existent = get_task_execution("non-existent")
            assert non_existent is None

    def test_ensure_task_execution_exists(self, app: Flask) -> None:
        """Test ensure_task_execution_exists function."""
        with app.app_context():
            # First call should create the task
            ensure_task_execution_exists(
                task_id="test-ensure-123",
                task_name="test_ensure_task",
                args=[1, 2],
                kwargs={"test": True},
            )

            task = get_task_execution("test-ensure-123")
            assert task is not None
            assert task.task_name == "test_ensure_task"

            # Second call should not create duplicate
            ensure_task_execution_exists(
                task_id="test-ensure-123",
                task_name="test_ensure_task_updated",
            )

            # Should still be the original task
            task = get_task_execution("test-ensure-123")
            assert task.task_name == "test_ensure_task"  # Original name preserved

    def test_update_task_status_by_id(self, app: Flask) -> None:
        """Test update_task_status_by_id function."""
        with app.app_context():
            # Create a task execution
            create_task_execution(
                task_id="test-update-456", task_name="test_update_task"
            )

            # Update to running
            update_task_status_by_id(
                task_id="test-update-456",
                status=TaskExecutionStatus.RUNNING,
            )

            updated_task = get_task_execution("test-update-456")
            assert updated_task.status == TaskExecutionStatus.RUNNING.value
            assert updated_task.started_at is not None

            # Update to success with result
            update_task_status_by_id(
                task_id="test-update-456",
                status=TaskExecutionStatus.SUCCESS,
                result={"output": "success"},
            )

            updated_task = get_task_execution("test-update-456")
            assert updated_task.status == TaskExecutionStatus.SUCCESS.value
            assert updated_task.completed_at is not None
            assert updated_task.duration_seconds is not None
            assert json.loads(updated_task.result) == {"output": "success"}

    def test_log_task_message(self, app: Flask) -> None:
        """Test log_task_message function."""
        with app.app_context():
            # Create a task execution
            task = create_task_execution(
                task_id="test-log-789", task_name="test_log_task"
            )

            # Log a message
            log_task_message(
                task_id="test-log-789",
                level=TaskExecutionLogLevel.INFO,
                message="Test log message",
                context={"step": 1, "action": "test"},
            )

            # Verify the log was created
            log_entry = (
                db.session.query(TaskExecutionLog)
                .filter_by(task_execution_id=task.id)
                .first()
            )
            assert log_entry is not None
            assert log_entry.level == TaskExecutionLogLevel.INFO.value
            assert log_entry.message == "Test log message"
            assert json.loads(log_entry.context) == {"step": 1, "action": "test"}

    def test_task_logger_class(self, app: Flask) -> None:
        """Test TaskLogger class."""
        with app.app_context():
            # Create a task execution
            task = create_task_execution(
                task_id="test-logger-123", task_name="test_logger_task"
            )

            # Create logger and test different log levels
            logger = TaskLogger(task.id)
            logger.debug("Debug message")
            logger.info("Info message")
            logger.warning("Warning message")
            logger.error("Error message")
            logger.critical("Critical message")

            # Verify all logs were created
            logs = (
                db.session.query(TaskExecutionLog)
                .filter_by(task_execution_id=task.id)
                .order_by(TaskExecutionLog.timestamp.asc())  # type: ignore[attr-defined]
                .all()
            )
            assert len(logs) == EXPECTED_LOG_COUNT_MULTIPLE
            assert logs[0].level == TaskExecutionLogLevel.DEBUG.value
            assert logs[1].level == TaskExecutionLogLevel.INFO.value
            assert logs[2].level == TaskExecutionLogLevel.WARNING.value
            assert logs[3].level == TaskExecutionLogLevel.ERROR.value
            assert logs[4].level == TaskExecutionLogLevel.CRITICAL.value

    def test_task_logger_exception_method(self, app: Flask) -> None:
        """Test TaskLogger exception method."""
        with app.app_context():
            # Create a task execution
            task = create_task_execution(
                task_id="test-exception-123", task_name="test_exception_task"
            )

            logger = TaskLogger(task.id)

            # Test with current exception context
            try:
                raise ValueError("Test exception")  # noqa: TRY301
            except ValueError:
                logger.exception("An error occurred")

            # Test with custom context
            try:
                raise RuntimeError("Another test exception")  # noqa: TRY301
            except RuntimeError as e:
                logger.exception("Custom error", exc_info=e, context={"custom": "data"})

            # Test with exc_info=False (no exception info)
            logger.exception("No exception info", exc_info=False)

            # Verify logs were created
            logs = (
                db.session.query(TaskExecutionLog)
                .filter_by(task_execution_id=task.id)
                .order_by(TaskExecutionLog.timestamp.asc())  # type: ignore[attr-defined]
                .all()
            )

            assert len(logs) == 3  # noqa: PLR2004

            # Check first log (with automatic exception info)
            assert logs[0].level == TaskExecutionLogLevel.ERROR.value
            assert logs[0].message == "An error occurred"
            context1 = json.loads(logs[0].context)
            assert context1["exception_type"] == "ValueError"
            assert context1["exception_message"] == "Test exception"
            assert "traceback" in context1

            # Check second log (with explicit exception and custom context)
            assert logs[1].level == TaskExecutionLogLevel.ERROR.value
            assert logs[1].message == "Custom error"
            context2 = json.loads(logs[1].context)
            assert context2["exception_type"] == "RuntimeError"
            assert context2["exception_message"] == "Another test exception"
            assert "traceback" in context2
            assert context2["custom"] == "data"

            # Check third log (no exception info)
            assert logs[2].level == TaskExecutionLogLevel.ERROR.value
            assert logs[2].message == "No exception info"
            # Context should be empty or minimal when exc_info=False
            if logs[2].context:
                context3 = json.loads(logs[2].context)
                assert "exception_type" not in context3
                assert "traceback" not in context3


class TestMonitoredTaskDecorator:
    """Test the monitored_task decorator."""

    def test_monitored_task_success(self, app: Flask) -> None:
        """Test monitored_task decorator with successful task."""
        with app.app_context():

            @monitored_task
            def test_successful_task(x: int, y: int) -> dict[str, int]:
                return {"result": x + y}

            # Mock current_task
            with patch("zecmf.extensions.task_monitor.current_task") as mock_task:
                mock_task.request.id = "test-success-123"
                mock_task.request.retries = 0

                result = test_successful_task(5, 3)

                assert result == {"result": 8}

                # Verify task execution was created and updated
                task_execution = get_task_execution("test-success-123")
                assert task_execution is not None
                assert task_execution.status == TaskExecutionStatus.SUCCESS.value
                assert json.loads(task_execution.result) == {"result": 8}

    def test_monitored_task_failure(self, app: Flask) -> None:
        """Test monitored_task decorator with failing task."""
        with app.app_context():

            @monitored_task
            def test_failing_task() -> Never:
                raise ValueError("Test error")

            # Mock current_task
            with patch("zecmf.extensions.task_monitor.current_task") as mock_task:
                mock_task.request.id = "test-failure-456"
                mock_task.request.retries = 0

                with pytest.raises(ValueError, match="Test error"):
                    test_failing_task()

                # Verify task execution was marked as failed
                task_execution = get_task_execution("test-failure-456")
                assert task_execution is not None
                assert task_execution.status == TaskExecutionStatus.FAILURE.value
                assert "Test error" in task_execution.error_message

    def test_monitored_task_error_result(self, app: Flask) -> None:
        """Test monitored_task decorator with task returning error status."""
        with app.app_context():

            @monitored_task
            def test_error_result_task() -> dict[str, str]:
                return {"status": "error", "message": "Task failed internally"}

            # Mock current_task
            with patch("zecmf.extensions.task_monitor.current_task") as mock_task:
                mock_task.request.id = "test-error-result-789"
                mock_task.request.retries = 0

                result = test_error_result_task()

                assert result == {
                    "status": "error",
                    "message": "Task failed internally",
                }

                # Verify task execution was marked as failed
                task_execution = get_task_execution("test-error-result-789")
                assert task_execution is not None
                assert task_execution.status == TaskExecutionStatus.FAILURE.value
                assert "Task failed internally" in task_execution.error_message

    def test_monitored_task_without_celery_context(self, app: Flask) -> None:
        """Test monitored_task decorator without Celery task context."""
        with app.app_context():

            @monitored_task
            def test_no_context_task() -> str:
                return "success"

            # Test without mocking current_task (simulates no Celery context)
            result = test_no_context_task()
            assert result == "success"

            # No task execution should be created since there's no task_id
            tasks = db.session.query(TaskExecution).all()
            assert len(tasks) == 0
