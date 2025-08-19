"""Tests for ZecMF task monitoring API endpoints."""

from datetime import UTC, datetime, timedelta
from http import HTTPStatus

from flask import Flask
from flask.testing import FlaskClient

from zecmf.extensions.database import db
from zecmf.models.task_monitoring import (
    TaskExecution,
    TaskExecutionLog,
    TaskExecutionLogLevel,
    TaskExecutionStatus,
)

# Test constants
EXPECTED_TASK_COUNT = 3
EXPECTED_LOG_COUNT = 2
EXPECTED_SUCCESS_COUNT = 3
ITEMS_PER_PAGE = 5
SUCCESS_STATUS_CODE = 200
EXPECTED_FAILURE_COUNT = 1
EXPECTED_RUNNING_COUNT = 1
EXPECTED_TASK_TYPE_A_COUNT = 2
EXPECTED_TASK_TYPE_B_COUNT = 2
EXPECTED_TASK_TYPE_C_COUNT = 1
EXPECTED_RECENT_ACTIVITY_COUNT = 4
EXPECTED_TOTAL_EXECUTIONS = 5
DURATION_TOLERANCE = 0.01


class TestTaskMonitoringAPI:
    """Test task monitoring REST API endpoints."""

    def setup_method(self) -> None:
        """Set up test data before each test method."""
        # This will be called before each test method

    def test_list_task_executions(self, app: Flask, client: FlaskClient) -> None:
        """Test GET /task-monitoring/executions endpoint."""
        with app.app_context():
            # Create test task executions
            task1 = TaskExecution(
                task_id="test-task-1",
                task_name="test_task_1",
                status=TaskExecutionStatus.SUCCESS.value,
                created_at=datetime.now(UTC) - timedelta(hours=1),
            )
            task2 = TaskExecution(
                task_id="test-task-2",
                task_name="test_task_2",
                status=TaskExecutionStatus.FAILURE.value,
                created_at=datetime.now(UTC) - timedelta(minutes=30),
            )
            task3 = TaskExecution(
                task_id="test-task-3",
                task_name="another_task",
                status=TaskExecutionStatus.RUNNING.value,
                created_at=datetime.now(UTC) - timedelta(minutes=15),
            )
            db.session.add_all([task1, task2, task3])
            db.session.commit()

            # Test getting all executions
            response = client.get("/api/task-monitoring/executions")
            assert response.status_code == HTTPStatus.OK

            data = response.get_json()
            assert len(data) == EXPECTED_TASK_COUNT

            # Should be ordered by most recent first
            assert data[0]["task_id"] == "test-task-3"
            assert data[1]["task_id"] == "test-task-2"
            assert data[2]["task_id"] == "test-task-1"

    def test_list_task_executions_with_filters(
        self, app: Flask, client: FlaskClient
    ) -> None:
        """Test GET /task-monitoring/executions with filters."""
        with app.app_context():
            # Create test task executions
            task1 = TaskExecution(
                task_id="test-task-1",
                task_name="test_task_1",
                status=TaskExecutionStatus.SUCCESS.value,
            )
            task2 = TaskExecution(
                task_id="test-task-2",
                task_name="test_task_2",
                status=TaskExecutionStatus.FAILURE.value,
            )
            task3 = TaskExecution(
                task_id="test-task-3",
                task_name="another_task",
                status=TaskExecutionStatus.SUCCESS.value,
            )
            db.session.add_all([task1, task2, task3])
            db.session.commit()

            # Test status filter
            response = client.get("/api/task-monitoring/executions?status=success")
            assert response.status_code == HTTPStatus.OK

            data = response.get_json()
            assert len(data) == EXPECTED_LOG_COUNT
            for execution in data:
                assert execution["status"] == TaskExecutionStatus.SUCCESS.value

            # Test task_name filter
            response = client.get("/api/task-monitoring/executions?task_name=test_task")
            assert response.status_code == HTTPStatus.OK

            data = response.get_json()
            assert len(data) == EXPECTED_LOG_COUNT
            for execution in data:
                assert "test_task" in execution["task_name"]

    def test_list_task_executions_pagination(
        self, app: Flask, client: FlaskClient
    ) -> None:
        """Test GET /task-monitoring/executions pagination."""
        with app.app_context():
            # Create multiple task executions
            tasks = []
            for i in range(15):
                task = TaskExecution(
                    task_id=f"test-task-{i}",
                    task_name=f"test_task_{i}",
                    status=TaskExecutionStatus.SUCCESS.value,
                )
                tasks.append(task)
            db.session.add_all(tasks)
            db.session.commit()

            # Test first page
            response = client.get("/api/task-monitoring/executions?page=1&per_page=5")
            assert response.status_code == HTTPStatus.OK

            data = response.get_json()
            assert len(data) == ITEMS_PER_PAGE

            # Test second page
            response = client.get("/api/task-monitoring/executions?page=2&per_page=5")
            assert response.status_code == HTTPStatus.OK

            data = response.get_json()
            assert len(data) == ITEMS_PER_PAGE

    def test_get_task_execution_detail(self, app: Flask, client: FlaskClient) -> None:
        """Test GET /task-monitoring/executions/<id> endpoint."""
        with app.app_context():
            # Create test task execution
            task = TaskExecution(
                task_id="test-task-detail",
                task_name="test_task_detail",
                status=TaskExecutionStatus.SUCCESS.value,
                args="[1, 2, 3]",
                kwargs='{"key": "value"}',
                result='{"output": "success"}',
            )
            db.session.add(task)
            db.session.commit()

            # Test getting task detail
            response = client.get(f"/api/task-monitoring/executions/{task.id}")
            assert response.status_code == HTTPStatus.OK

            data = response.get_json()
            assert data["task_id"] == "test-task-detail"
            assert data["task_name"] == "test_task_detail"
            assert data["status"] == TaskExecutionStatus.SUCCESS.value
            assert data["args"] == "[1, 2, 3]"
            assert data["kwargs"] == '{"key": "value"}'
            assert data["result"] == '{"output": "success"}'

    def test_get_task_execution_detail_not_found(
        self, app: Flask, client: FlaskClient
    ) -> None:
        """Test GET /task-monitoring/executions/<id> with non-existent ID."""
        response = client.get("/api/task-monitoring/executions/999999")
        assert response.status_code == HTTPStatus.NOT_FOUND

    def test_get_task_execution_logs(self, app: Flask, client: FlaskClient) -> None:
        """Test GET /task-monitoring/executions/<id>/logs endpoint."""
        with app.app_context():
            # Create test task execution
            task = TaskExecution(
                task_id="test-task-logs",
                task_name="test_task_logs",
                status=TaskExecutionStatus.SUCCESS.value,
            )
            db.session.add(task)
            db.session.commit()

            # Create test logs
            log1 = TaskExecutionLog(
                task_execution_id=task.id,
                level=TaskExecutionLogLevel.INFO.value,
                message="Task started",
                timestamp=datetime.now(UTC) - timedelta(minutes=5),
            )
            log2 = TaskExecutionLog(
                task_execution_id=task.id,
                level=TaskExecutionLogLevel.ERROR.value,
                message="Error occurred",
                timestamp=datetime.now(UTC) - timedelta(minutes=3),
                context='{"error_code": 500}',
            )
            log3 = TaskExecutionLog(
                task_execution_id=task.id,
                level=TaskExecutionLogLevel.INFO.value,
                message="Task completed",
                timestamp=datetime.now(UTC) - timedelta(minutes=1),
            )
            db.session.add_all([log1, log2, log3])
            db.session.commit()

            # Test getting all logs
            response = client.get(f"/api/task-monitoring/executions/{task.id}/logs")
            assert response.status_code == HTTPStatus.OK

            data = response.get_json()
            assert len(data) == EXPECTED_TASK_COUNT

            # Should be ordered by timestamp
            assert data[0]["message"] == "Task started"
            assert data[1]["message"] == "Error occurred"
            assert data[2]["message"] == "Task completed"

    def test_get_task_execution_logs_with_level_filter(
        self, app: Flask, client: FlaskClient
    ) -> None:
        """Test GET /task-monitoring/executions/<id>/logs with level filter."""
        with app.app_context():
            # Create test task execution
            task = TaskExecution(
                task_id="test-task-logs-filter",
                task_name="test_task_logs_filter",
                status=TaskExecutionStatus.SUCCESS.value,
            )
            db.session.add(task)
            db.session.commit()

            # Create test logs with different levels
            log1 = TaskExecutionLog(
                task_execution_id=task.id,
                level=TaskExecutionLogLevel.INFO.value,
                message="Info message",
            )
            log2 = TaskExecutionLog(
                task_execution_id=task.id,
                level=TaskExecutionLogLevel.ERROR.value,
                message="Error message",
            )
            log3 = TaskExecutionLog(
                task_execution_id=task.id,
                level=TaskExecutionLogLevel.INFO.value,
                message="Another info message",
            )
            db.session.add_all([log1, log2, log3])
            db.session.commit()

            # Test level filter
            response = client.get(
                f"/api/task-monitoring/executions/{task.id}/logs?level=info"
            )
            assert response.status_code == HTTPStatus.OK

            data = response.get_json()
            assert len(data) == EXPECTED_LOG_COUNT
            for log in data:
                assert log["level"] == TaskExecutionLogLevel.INFO.value

    def test_get_task_execution_logs_not_found(
        self, app: Flask, client: FlaskClient
    ) -> None:
        """Test GET /task-monitoring/executions/<id>/logs with non-existent task."""
        response = client.get("/api/task-monitoring/executions/999999/logs")
        assert response.status_code == HTTPStatus.NOT_FOUND

    def test_get_task_execution_stats(self, app: Flask, client: FlaskClient) -> None:
        """Test GET /task-monitoring/stats endpoint."""
        with app.app_context():
            # Create test task executions with various statuses
            tasks = [
                TaskExecution(
                    task_id="task-1",
                    task_name="task_type_a",
                    status=TaskExecutionStatus.SUCCESS.value,
                    duration_seconds=10.5,
                    created_at=datetime.now(UTC) - timedelta(hours=2),
                ),
                TaskExecution(
                    task_id="task-2",
                    task_name="task_type_a",
                    status=TaskExecutionStatus.SUCCESS.value,
                    duration_seconds=15.2,
                    created_at=datetime.now(UTC) - timedelta(hours=1),
                ),
                TaskExecution(
                    task_id="task-3",
                    task_name="task_type_b",
                    status=TaskExecutionStatus.FAILURE.value,
                    created_at=datetime.now(UTC) - timedelta(minutes=30),
                ),
                TaskExecution(
                    task_id="task-4",
                    task_name="task_type_b",
                    status=TaskExecutionStatus.RUNNING.value,
                    created_at=datetime.now(UTC) - timedelta(minutes=15),
                ),
                TaskExecution(
                    task_id="task-5",
                    task_name="task_type_c",
                    status=TaskExecutionStatus.SUCCESS.value,
                    duration_seconds=8.1,
                    created_at=datetime.now(UTC)
                    - timedelta(hours=25),  # Outside 24h window
                ),
            ]
            db.session.add_all(tasks)
            db.session.commit()

            # Test getting stats
            response = client.get("/api/task-monitoring/stats")
            assert response.status_code == HTTPStatus.OK

            data = response.get_json()

            # Check status counts
            assert "status_counts" in data
            status_counts = data["status_counts"]
            assert (
                status_counts.get(TaskExecutionStatus.SUCCESS.value)
                == EXPECTED_SUCCESS_COUNT
            )
            assert (
                status_counts.get(TaskExecutionStatus.FAILURE.value)
                == EXPECTED_FAILURE_COUNT
            )
            assert (
                status_counts.get(TaskExecutionStatus.RUNNING.value)
                == EXPECTED_RUNNING_COUNT
            )

            # Check task counts
            assert "task_counts" in data
            task_counts = data["task_counts"]
            assert task_counts.get("task_type_a") == EXPECTED_TASK_TYPE_A_COUNT
            assert task_counts.get("task_type_b") == EXPECTED_TASK_TYPE_B_COUNT
            assert task_counts.get("task_type_c") == EXPECTED_TASK_TYPE_C_COUNT

            # Check recent activity (last 24 hours)
            assert "recent_activity_24h" in data
            assert (
                data["recent_activity_24h"] == EXPECTED_RECENT_ACTIVITY_COUNT
            )  # Excludes the 25-hour-old task

            # Check average duration
            assert "average_duration_seconds" in data
            expected_avg = (
                10.5 + 15.2 + 8.1
            ) / EXPECTED_SUCCESS_COUNT  # Only tasks with duration_seconds
            assert (
                abs(data["average_duration_seconds"] - expected_avg)
                < DURATION_TOLERANCE
            )

            # Check total executions
            assert "total_executions" in data
            assert data["total_executions"] == EXPECTED_TOTAL_EXECUTIONS

    def test_get_task_execution_stats_empty(
        self, app: Flask, client: FlaskClient
    ) -> None:
        """Test GET /task-monitoring/stats with no task executions."""
        response = client.get("/api/task-monitoring/stats")
        assert response.status_code == SUCCESS_STATUS_CODE

        data = response.get_json()
        assert data["status_counts"] == {}
        assert data["task_counts"] == {}
        assert data["recent_activity_24h"] == 0
        assert data["average_duration_seconds"] is None
        assert data["total_executions"] == 0
