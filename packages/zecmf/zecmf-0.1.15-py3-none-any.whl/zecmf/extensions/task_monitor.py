"""Task monitoring utilities for ZecMF queue system.

Provides decorators and functions for tracking Celery task executions with
comprehensive monitoring, logging, and retry capabilities.
"""

import functools
import json
import sys
import traceback
from collections.abc import Callable
from datetime import UTC, datetime
from typing import TYPE_CHECKING, Any

from celery import current_task
from flask import Flask, has_app_context

if TYPE_CHECKING:
    from celery import Task

from zecmf.extensions.database import db
from zecmf.models.task_monitoring import (
    TaskExecution,
    TaskExecutionLog,
    TaskExecutionLogLevel,
    TaskExecutionStatus,
)

# Global app instance set by application workers
flask_app: Flask | None = None


def with_app_context(func: Callable) -> Callable:
    """Ensure Flask app context is available for task functions."""

    @functools.wraps(func)
    def wrapper(*args: Any, **kwargs: Any) -> Any:  # noqa: ANN401
        if has_app_context():
            return func(*args, **kwargs)
        elif flask_app:
            with flask_app.app_context():
                return func(*args, **kwargs)
        else:
            # No app context available, skip monitoring
            return None

    return wrapper


class TaskLogger:
    """Logger for task execution events."""

    def __init__(self, task_execution_id: int) -> None:
        """Initialize the task logger with a task execution ID."""
        self.task_execution_id = task_execution_id

    @with_app_context
    def log(
        self,
        level: TaskExecutionLogLevel,
        message: str,
        context: dict[str, Any] | None = None,
    ) -> None:
        """Add a log entry for the task execution."""
        log_entry = TaskExecutionLog(
            task_execution_id=self.task_execution_id,
            level=level.value,
            message=message,
            context=json.dumps(context) if context else None,
        )
        db.session.add(log_entry)
        db.session.commit()

    def debug(self, message: str, context: dict[str, Any] | None = None) -> None:
        """Log a debug message."""
        self.log(TaskExecutionLogLevel.DEBUG, message, context)

    def info(self, message: str, context: dict[str, Any] | None = None) -> None:
        """Log an info message."""
        self.log(TaskExecutionLogLevel.INFO, message, context)

    def warning(self, message: str, context: dict[str, Any] | None = None) -> None:
        """Log a warning message."""
        self.log(TaskExecutionLogLevel.WARNING, message, context)

    def error(self, message: str, context: dict[str, Any] | None = None) -> None:
        """Log an error message."""
        self.log(TaskExecutionLogLevel.ERROR, message, context)

    def critical(self, message: str, context: dict[str, Any] | None = None) -> None:
        """Log a critical message."""
        self.log(TaskExecutionLogLevel.CRITICAL, message, context)

    def exception(
        self,
        message: str,
        exc_info: bool | tuple | BaseException = True,
        context: dict[str, Any] | None = None,
    ) -> None:
        """Log an error message with exception information.

        Args:
            message: The error message to log.
            exc_info: If True, exception info is added to the logging message.
                     Can also be an exception tuple or an exception instance.
            context: Additional context data to include with the log entry.

        """
        # Build context with exception information
        exception_context = context.copy() if context else {}

        # Handle different exc_info types
        if exc_info:
            if exc_info is True:
                # Get current exception info from sys
                exc_type, exc_value, exc_traceback = sys.exc_info()
                if exc_type:
                    exception_context["exception_type"] = exc_type.__name__
                    exception_context["exception_message"] = str(exc_value)
                    exception_context["traceback"] = traceback.format_exc()
            elif isinstance(exc_info, tuple) and len(exc_info) == 3:  # noqa: PLR2004
                # exc_info is a tuple (type, value, traceback)
                exc_type, exc_value, exc_traceback = exc_info
                if exc_type:
                    exception_context["exception_type"] = (
                        exc_type.__name__ if exc_type else None
                    )
                    exception_context["exception_message"] = (
                        str(exc_value) if exc_value else None
                    )
                    exception_context["traceback"] = "".join(
                        traceback.format_exception(exc_type, exc_value, exc_traceback)
                    )
            elif isinstance(exc_info, BaseException):
                # exc_info is an exception instance
                exception_context["exception_type"] = type(exc_info).__name__
                exception_context["exception_message"] = str(exc_info)
                exception_context["traceback"] = "".join(
                    traceback.format_exception(
                        type(exc_info), exc_info, exc_info.__traceback__
                    )
                )

        # Log as error level with exception context
        self.log(TaskExecutionLogLevel.ERROR, message, exception_context)


@with_app_context
def get_task_execution(task_id: str) -> TaskExecution | None:
    """Get a task execution record by task ID."""
    task_execution = db.session.query(TaskExecution).filter_by(task_id=task_id).first()
    if task_execution:
        # Ensure it's merged into the current session to avoid DetachedInstanceError
        task_execution = db.session.merge(task_execution)
    return task_execution


@with_app_context
def create_task_execution(
    task_id: str,
    task_name: str,
    args: list[Any] | None = None,
    kwargs: dict[str, Any] | None = None,
    context_id: int | None = None,
    context_type: str | None = None,
    context_step: int | None = None,
) -> TaskExecution:
    """Create a new task execution record."""
    task_execution = TaskExecution(
        task_id=task_id,
        task_name=task_name,
        status=TaskExecutionStatus.PENDING.value,
        args=json.dumps(args) if args else None,
        kwargs=json.dumps(kwargs) if kwargs else None,
        context_id=context_id,
        context_type=context_type,
        context_step=context_step,
    )
    db.session.add(task_execution)
    db.session.commit()
    return task_execution


@with_app_context
def update_task_status(
    task_execution: TaskExecution,
    status: TaskExecutionStatus,
    result: str | dict | None = None,
    error_message: str | None = None,
    traceback_str: str | None = None,
) -> None:
    """Update task execution status and related fields."""
    # Merge the object to the current session to avoid DetachedInstanceError
    task_execution = db.session.merge(task_execution)

    task_execution.status = status.value
    task_execution.updated_at = datetime.now(UTC)

    if status == TaskExecutionStatus.RUNNING and not task_execution.started_at:
        task_execution.started_at = datetime.now(UTC)

    if status in {TaskExecutionStatus.SUCCESS, TaskExecutionStatus.FAILURE}:
        task_execution.completed_at = datetime.now(UTC)
        if task_execution.started_at:
            # Ensure both datetimes have the same timezone handling
            started_at = task_execution.started_at
            completed_at = task_execution.completed_at

            # If started_at is naive, make it UTC-aware
            if started_at.tzinfo is None:
                started_at = started_at.replace(tzinfo=UTC)

            # If completed_at is naive, make it UTC-aware
            if completed_at.tzinfo is None:
                completed_at = completed_at.replace(tzinfo=UTC)

            duration = completed_at - started_at
            task_execution.duration_seconds = duration.total_seconds()

    if result is not None:
        task_execution.result = (
            json.dumps(result) if not isinstance(result, str) else result
        )

    if error_message:
        task_execution.error_message = error_message

    if traceback_str:
        task_execution.traceback = traceback_str

    db.session.commit()


def _handle_task_retry(
    task_id: str,
    task_name: str,
    task_instance: "Task | None",
    error_message: str,
    result: dict,
) -> bool:
    """Handle retry logic for failed tasks. Returns True if retry was attempted."""
    if not (task_instance and hasattr(task_instance, "request")):
        return False

    current_retries = getattr(task_instance.request, "retries", 0)
    max_retries = getattr(task_instance, "max_retries", 3)

    if current_retries >= max_retries:
        return False

    # Log the retry attempt
    log_task_message(
        task_id,
        TaskExecutionLogLevel.WARNING,
        f"Task {task_name} failed, attempting retry {current_retries + 1}/{max_retries + 1}: {error_message}",
        {"result": result, "retry_count": current_retries + 1},
    )

    # Update status to retry
    update_task_status_by_id(
        task_id,
        TaskExecutionStatus.RETRY,
        result=result,
        error_message=error_message,
        retry_count=current_retries + 1,
    )

    # Trigger retry (this will raise Retry exception)
    # Use exponential backoff: 60s, 120s, 240s
    countdown = 60 * (2**current_retries)
    task_instance.retry(countdown=countdown, exc=Exception(error_message))
    # This line should never be reached as retry() raises an exception
    return True  # pragma: no cover


def _handle_error_result(
    task_id: str, task_name: str, result: dict, args: tuple
) -> None:
    """Handle task results that indicate an error."""
    error_message = result.get("message", "Task returned error status")

    # Check if this is a bound task (has self parameter for retry)
    task_instance = args[0] if args and hasattr(args[0], "retry") else None

    # Try to retry if applicable
    if _handle_task_retry(task_id, task_name, task_instance, error_message, result):
        return  # Retry was triggered, function will exit via exception

    # Mark as failure (either no retries left or retry not applicable)
    update_task_status_by_id(
        task_id,
        TaskExecutionStatus.FAILURE,
        result=result,
        error_message=error_message,
    )
    log_task_message(
        task_id,
        TaskExecutionLogLevel.ERROR,
        f"Task {task_name} failed: {error_message}",
        {"result": result},
    )


def _extract_context_info(
    args: tuple, kwargs: dict
) -> tuple[int | None, str | None, int | None]:
    """Extract context information from task arguments."""
    context_id = None
    context_type = None
    context_step = None

    # Look for common context patterns in kwargs
    if "project_id" in kwargs:
        context_id = kwargs["project_id"]
        context_type = "project"
    elif "user_id" in kwargs:
        context_id = kwargs["user_id"]
        context_type = "user"

    # Look for step information
    if "step" in kwargs:
        context_step = kwargs["step"]

    # Also check in args (common pattern: project_id as first arg, step as second)
    min_args_for_step = 3

    if not context_id and len(args) > 1 and isinstance(args[1], int):
        context_id = args[1]
        context_type = "project"  # Assume project for backward compatibility

    if (
        not context_step
        and len(args) > min_args_for_step - 1
        and isinstance(args[min_args_for_step - 1], int)
    ):
        context_step = args[min_args_for_step - 1]

    return context_id, context_type, context_step


def _initialize_task_monitoring(
    task_id: str | None, task_name: str, args: tuple, kwargs: dict
) -> None:
    """Initialize task monitoring."""
    if not task_id:
        return

    # Filter out non-serializable task instance from args
    # For bound tasks, args[0] is always the task instance
    serializable_args = []
    for i, arg in enumerate(args):
        # Skip the first argument if it looks like a task instance
        if i == 0 and (
            hasattr(arg, "retry")
            or hasattr(arg, "request")
            or "task" in str(type(arg)).lower()
            or hasattr(arg, "__name__")
        ):
            continue
        serializable_args.append(arg)

    # Extract context information
    context_id, context_type, context_step = _extract_context_info(args, kwargs)

    # Ensure task execution record exists
    ensure_task_execution_exists(
        task_id=task_id,
        task_name=task_name,
        args=serializable_args,
        kwargs=kwargs,
        context_id=context_id,
        context_type=context_type,
        context_step=context_step,
    )


def monitored_task(func: Callable) -> Callable:
    """Monitor Celery task execution with comprehensive tracking."""

    @functools.wraps(func)
    def wrapper(*args: Any, **kwargs: Any) -> Any:  # noqa: ANN401
        # Get task info
        task_id = getattr(current_task.request, "id", None) if current_task else None
        task_name = func.__name__

        # Initialize monitoring
        _initialize_task_monitoring(task_id, task_name, args, kwargs)

        try:
            # Update status to running
            if task_id:
                # Get current retry count from Celery
                current_retries = (
                    getattr(current_task.request, "retries", 0) if current_task else 0
                )
                update_task_status_by_id(
                    task_id, TaskExecutionStatus.RUNNING, retry_count=current_retries
                )
                # Filter out task instance for logging (skip first arg if it's a task)
                serializable_args = []
                for i, arg in enumerate(args):
                    if i == 0 and (
                        hasattr(arg, "retry")
                        or hasattr(arg, "request")
                        or "task" in str(type(arg)).lower()
                        or hasattr(arg, "__name__")
                    ):
                        continue
                    serializable_args.append(arg)
                log_task_message(
                    task_id,
                    TaskExecutionLogLevel.INFO,
                    f"Started task {task_name}",
                    {"args": serializable_args, "kwargs": kwargs},
                )

            # Execute the actual task
            result = func(*args, **kwargs)

            # Handle result
            if task_id:
                if isinstance(result, dict) and result.get("status") == "error":
                    _handle_error_result(task_id, task_name, result, args)
                else:
                    # Task completed successfully
                    update_task_status_by_id(
                        task_id, TaskExecutionStatus.SUCCESS, result=result
                    )
                    log_task_message(
                        task_id,
                        TaskExecutionLogLevel.INFO,
                        f"Completed task {task_name} successfully",
                        {"result": result},
                    )

            return result  # noqa: TRY300

        except Exception as e:
            error_message = str(e)
            traceback_str = traceback.format_exc()

            # Update status to failure
            if task_id:
                update_task_status_by_id(
                    task_id,
                    TaskExecutionStatus.FAILURE,
                    error_message=error_message,
                    traceback_str=traceback_str,
                )
                log_task_message(
                    task_id,
                    TaskExecutionLogLevel.CRITICAL,
                    f"Task {task_name} failed: {error_message}",
                    {"traceback": traceback_str},
                )

            # Re-raise the exception
            raise

    return wrapper


@with_app_context
def ensure_task_execution_exists(
    task_id: str,
    task_name: str,
    args: list[Any] | None = None,
    kwargs: dict[str, Any] | None = None,
    context_id: int | None = None,
    context_type: str | None = None,
    context_step: int | None = None,
) -> None:
    """Ensure a task execution record exists."""
    existing = db.session.query(TaskExecution).filter_by(task_id=task_id).first()
    if not existing:
        task_execution = TaskExecution(
            task_id=task_id,
            task_name=task_name,
            status=TaskExecutionStatus.PENDING.value,
            args=json.dumps(args) if args else None,
            kwargs=json.dumps(kwargs) if kwargs else None,
            context_id=context_id,
            context_type=context_type,
            context_step=context_step,
        )
        db.session.add(task_execution)
        db.session.commit()


@with_app_context
def update_task_status_by_id(
    task_id: str,
    status: TaskExecutionStatus,
    result: str | dict | None = None,
    error_message: str | None = None,
    traceback_str: str | None = None,
    retry_count: int | None = None,
) -> None:
    """Update task execution status by task ID."""
    task_execution = db.session.query(TaskExecution).filter_by(task_id=task_id).first()
    if not task_execution:
        return  # Task not found, skip silently

    task_execution.status = status.value
    task_execution.updated_at = datetime.now(UTC)

    if retry_count is not None:
        task_execution.retry_count = retry_count

    # Update timing based on status
    _update_task_timing(task_execution, status)

    if result is not None:
        task_execution.result = (
            json.dumps(result) if not isinstance(result, str) else result
        )

    if error_message:
        task_execution.error_message = error_message

    if traceback_str:
        task_execution.traceback = traceback_str

    db.session.commit()


def _update_task_timing(
    task_execution: TaskExecution, status: TaskExecutionStatus
) -> None:
    """Update task timing based on status."""
    if status == TaskExecutionStatus.RUNNING and not task_execution.started_at:
        task_execution.started_at = datetime.now(UTC)

    if status in {TaskExecutionStatus.SUCCESS, TaskExecutionStatus.FAILURE}:
        task_execution.completed_at = datetime.now(UTC)
        if task_execution.started_at:
            # Ensure both datetimes have the same timezone handling
            started_at = task_execution.started_at
            completed_at = task_execution.completed_at

            # If started_at is naive, make it UTC-aware
            if started_at.tzinfo is None:
                started_at = started_at.replace(tzinfo=UTC)

            # If completed_at is naive, make it UTC-aware
            if completed_at.tzinfo is None:
                completed_at = completed_at.replace(tzinfo=UTC)

            duration = completed_at - started_at
            task_execution.duration_seconds = duration.total_seconds()


@with_app_context
def log_task_message(
    task_id: str,
    level: TaskExecutionLogLevel,
    message: str,
    context: dict[str, Any] | None = None,
) -> None:
    """Log a message for a task by task ID."""
    # Get the task execution ID
    task_execution = db.session.query(TaskExecution).filter_by(task_id=task_id).first()
    if not task_execution:
        return  # Task not found, skip silently

    log_entry = TaskExecutionLog(
        task_execution_id=task_execution.id,
        level=level.value,
        message=message,
        context=json.dumps(context) if context else None,
    )
    db.session.add(log_entry)
    db.session.commit()


def log_task_event(
    task_id: str,
    level: TaskExecutionLogLevel,
    message: str,
    context: dict[str, Any] | None = None,
) -> None:
    """Log an event for a specific task."""
    log_task_message(task_id, level, message, context)
