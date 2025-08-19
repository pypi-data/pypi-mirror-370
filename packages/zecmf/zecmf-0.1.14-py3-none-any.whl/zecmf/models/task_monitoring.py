"""Task monitoring models for ZecMF queue system.

Provides comprehensive tracking for asynchronous task executions including
execution status, timing, retry counts, and detailed logging.
"""

from datetime import UTC, datetime
from enum import StrEnum
from typing import Any

from zecmf.extensions.database import db


class TaskExecutionStatus(StrEnum):
    """Status values for task executions."""

    PENDING = "pending"
    RUNNING = "running"
    SUCCESS = "success"
    FAILURE = "failure"
    RETRY = "retry"
    REVOKED = "revoked"


class TaskExecutionLogLevel(StrEnum):
    """Log level values for task execution logs."""

    DEBUG = "debug"
    INFO = "info"
    WARNING = "warning"
    ERROR = "error"
    CRITICAL = "critical"


class TaskExecution(db.Model):
    """Model for tracking all async task executions."""

    __tablename__ = "task_executions"
    __allow_unmapped__ = True

    id: int = db.Column(db.Integer, primary_key=True)
    task_id: str = db.Column(db.String(255), nullable=False, unique=True)
    task_name: str = db.Column(db.String(255), nullable=False)
    status: str = db.Column(
        db.String(30), nullable=False, default=TaskExecutionStatus.PENDING.value
    )

    # Execution details
    started_at: datetime = db.Column(db.DateTime, nullable=True)
    completed_at: datetime = db.Column(db.DateTime, nullable=True)
    duration_seconds: float = db.Column(db.Float, nullable=True)
    retry_count: int = db.Column(db.Integer, default=0)

    # Task metadata
    args: str = db.Column(db.Text, nullable=True)  # JSON string
    kwargs: str = db.Column(db.Text, nullable=True)  # JSON string
    result: str = db.Column(db.Text, nullable=True)  # JSON string
    error_message: str = db.Column(db.Text, nullable=True)
    traceback: str = db.Column(db.Text, nullable=True)

    # Context information (optional - applications can add more specific context)
    worker_name: str = db.Column(db.String(255), nullable=True)

    # Optional application-specific context fields
    # These are optional foreign keys that applications can use to link tasks to their domain objects
    context_id: int = db.Column(db.Integer, nullable=True)  # Generic context ID
    context_type: str = db.Column(
        db.String(50), nullable=True
    )  # Type of context (e.g., 'project', 'user', etc.)
    context_step: int = db.Column(
        db.Integer, nullable=True
    )  # Step number for step-based tasks

    # Timestamps
    created_at: datetime = db.Column(db.DateTime, default=lambda: datetime.now(UTC))
    updated_at: datetime = db.Column(
        db.DateTime,
        default=lambda: datetime.now(UTC),
        onupdate=lambda: datetime.now(UTC),
    )

    # Relationship to logs
    logs = db.relationship(
        "TaskExecutionLog",
        back_populates="task_execution",
        cascade="all, delete-orphan",
        order_by="TaskExecutionLog.timestamp",
    )

    def __repr__(self) -> str:
        """Return string representation of the task execution."""
        return f"<TaskExecution {self.id}: {self.task_name} ({self.status})>"

    def to_dict(self) -> dict[str, Any]:
        """Convert the model instance to a dictionary."""
        return {
            "id": self.id,
            "task_id": self.task_id,
            "task_name": self.task_name,
            "status": self.status,
            "started_at": self.started_at.isoformat() if self.started_at else None,
            "completed_at": self.completed_at.isoformat()
            if self.completed_at
            else None,
            "duration_seconds": self.duration_seconds,
            "retry_count": self.retry_count,
            "args": self.args,
            "kwargs": self.kwargs,
            "result": self.result,
            "error_message": self.error_message,
            "traceback": self.traceback,
            "worker_name": self.worker_name,
            "context_id": self.context_id,
            "context_type": self.context_type,
            "context_step": self.context_step,
            "created_at": self.created_at.isoformat(),
            "updated_at": self.updated_at.isoformat(),
            "log_count": len(self.logs) if self.logs else 0,
        }


class TaskExecutionLog(db.Model):
    """Model for storing detailed logs from task executions."""

    __tablename__ = "task_execution_logs"
    __allow_unmapped__ = True

    id: int = db.Column(db.Integer, primary_key=True)
    task_execution_id: int = db.Column(
        db.Integer, db.ForeignKey("task_executions.id"), nullable=False
    )
    level: str = db.Column(
        db.String(20), nullable=False, default=TaskExecutionLogLevel.INFO.value
    )
    message: str = db.Column(db.Text, nullable=False)
    timestamp: datetime = db.Column(db.DateTime, default=lambda: datetime.now(UTC))

    # Optional metadata
    context: str = db.Column(
        db.Text, nullable=True
    )  # JSON string for additional context

    # Relationship
    task_execution = db.relationship("TaskExecution", back_populates="logs")

    def __repr__(self) -> str:
        """Return string representation of the task execution log."""
        return f"<TaskExecutionLog {self.id}: {self.level} - {self.message[:50]}>"

    def to_dict(self) -> dict[str, Any]:
        """Convert the model instance to a dictionary."""
        return {
            "id": self.id,
            "task_execution_id": self.task_execution_id,
            "level": self.level,
            "message": self.message,
            "timestamp": self.timestamp.isoformat(),
            "context": self.context,
        }
