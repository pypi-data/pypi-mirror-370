"""Task monitoring API namespace for ZecMF.

Provides REST endpoints for monitoring and viewing async task executions.
"""

from datetime import datetime, timedelta
from typing import Any

from flask import request
from flask_restx import Namespace, Resource, fields
from sqlalchemy import func

from zecmf.extensions.database import db
from zecmf.models.task_monitoring import TaskExecution, TaskExecutionLog

# Create the namespace
task_monitoring_namespace = Namespace(
    "task-monitoring",
    description="Task monitoring and logging operations",
    path="/task-monitoring",
)

# Define models for documentation
task_execution_model = task_monitoring_namespace.model(
    "TaskExecution",
    {
        "id": fields.Integer(required=True, description="Task execution ID"),
        "task_id": fields.String(required=True, description="Celery task ID"),
        "task_name": fields.String(required=True, description="Task function name"),
        "status": fields.String(required=True, description="Task execution status"),
        "started_at": fields.String(description="Task start timestamp"),
        "completed_at": fields.String(description="Task completion timestamp"),
        "duration_seconds": fields.Float(description="Task duration in seconds"),
        "retry_count": fields.Integer(description="Number of retries"),
        "args": fields.String(description="Task arguments (JSON)"),
        "kwargs": fields.String(description="Task keyword arguments (JSON)"),
        "result": fields.String(description="Task result (JSON)"),
        "error_message": fields.String(description="Error message if failed"),
        "worker_name": fields.String(description="Worker that executed the task"),
        "created_at": fields.String(
            required=True, description="Record creation timestamp"
        ),
        "updated_at": fields.String(
            required=True, description="Record update timestamp"
        ),
        "log_count": fields.Integer(description="Number of log entries"),
    },
)

task_log_model = task_monitoring_namespace.model(
    "TaskLog",
    {
        "id": fields.Integer(required=True, description="Log entry ID"),
        "task_execution_id": fields.Integer(
            required=True, description="Task execution ID"
        ),
        "level": fields.String(required=True, description="Log level"),
        "message": fields.String(required=True, description="Log message"),
        "timestamp": fields.String(required=True, description="Log timestamp"),
        "context": fields.String(description="Additional context (JSON)"),
    },
)


@task_monitoring_namespace.route("/executions")
class TaskExecutionList(Resource):
    """Task execution list endpoint."""

    @task_monitoring_namespace.marshal_list_with(task_execution_model)
    @task_monitoring_namespace.doc("list_task_executions")
    def get(self) -> list[dict[str, Any]]:
        """Get a list of task executions with optional filtering."""
        # Get query parameters
        status = request.args.get("status")
        task_name = request.args.get("task_name")
        page = request.args.get("page", 1, type=int)
        per_page = min(request.args.get("per_page", 50, type=int), 100)

        # Build query
        query = db.session.query(TaskExecution)

        if status:
            query = query.filter(TaskExecution.status == status)
        if task_name:
            query = query.filter(TaskExecution.task_name.ilike(f"%{task_name}%"))

        # Order by most recent first
        query = query.order_by(TaskExecution.created_at.desc())

        # Paginate
        offset = (page - 1) * per_page
        executions = query.offset(offset).limit(per_page).all()

        return [execution.to_dict() for execution in executions]


@task_monitoring_namespace.route("/executions/<int:execution_id>")
class TaskExecutionDetail(Resource):
    """Task execution detail endpoint."""

    @task_monitoring_namespace.marshal_with(task_execution_model)
    @task_monitoring_namespace.doc("get_task_execution")
    def get(self, execution_id: int) -> dict[str, Any]:
        """Get a specific task execution by ID."""
        execution = db.session.get(TaskExecution, execution_id)
        if execution is None:
            task_monitoring_namespace.abort(404, "Task execution not found")

        return execution.to_dict()


@task_monitoring_namespace.route("/executions/<int:execution_id>/logs")
class TaskExecutionLogs(Resource):
    """Task execution logs endpoint."""

    @task_monitoring_namespace.marshal_list_with(task_log_model)
    @task_monitoring_namespace.doc("get_task_execution_logs")
    def get(self, execution_id: int) -> list[dict[str, Any]]:
        """Get logs for a specific task execution."""
        # Verify execution exists
        execution = db.session.get(TaskExecution, execution_id)
        if not execution:
            task_monitoring_namespace.abort(404, "Task execution not found")

        # Get query parameters
        level = request.args.get("level")
        page = request.args.get("page", 1, type=int)
        per_page = min(request.args.get("per_page", 100, type=int), 500)

        # Build query
        query = db.session.query(TaskExecutionLog).filter_by(
            task_execution_id=execution_id
        )

        if level:
            query = query.filter(TaskExecutionLog.level == level)

        # Order by timestamp
        query = query.order_by(TaskExecutionLog.timestamp.asc())

        # Paginate
        offset = (page - 1) * per_page
        logs = query.offset(offset).limit(per_page).all()

        return [log.to_dict() for log in logs]


@task_monitoring_namespace.route("/stats")
class TaskExecutionStats(Resource):
    """Task execution statistics endpoint."""

    @task_monitoring_namespace.doc("get_task_execution_stats")
    def get(self) -> dict[str, Any]:
        """Get task execution statistics."""
        # Count by status
        status_counts = (
            db.session.query(TaskExecution.status, func.count(TaskExecution.id))
            .group_by(TaskExecution.status)
            .all()
        )

        # Count by task name
        task_counts = (
            db.session.query(TaskExecution.task_name, func.count(TaskExecution.id))
            .group_by(TaskExecution.task_name)
            .order_by(func.count(TaskExecution.id).desc())
            .limit(10)
            .all()
        )

        # Recent activity (last 24 hours)
        twenty_four_hours_ago = datetime.now() - timedelta(hours=24)
        recent_count = (
            db.session.query(TaskExecution)
            .filter(TaskExecution.created_at >= twenty_four_hours_ago)
            .count()
        )

        # Average duration for completed tasks
        avg_duration = (
            db.session.query(func.avg(TaskExecution.duration_seconds))
            .filter(TaskExecution.duration_seconds.isnot(None))
            .scalar()
        )

        return {
            "status_counts": dict(status_counts),
            "task_counts": dict(task_counts),
            "recent_activity_24h": recent_count,
            "average_duration_seconds": float(avg_duration) if avg_duration else None,
            "total_executions": db.session.query(TaskExecution).count(),
        }
