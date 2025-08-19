"""Tests for authentication decorators."""

import pytest
from flask import Flask, Response, g, jsonify
from werkzeug.exceptions import Forbidden

from zecmf.auth.decorators import (
    DecoratorFactory,
    public_endpoint,
    require_admin_role,
    require_role,
    require_user_role,
)


@pytest.fixture
def decorator_app() -> Flask:
    """Create a Flask application with routes for testing decorators."""
    app = Flask("test")

    # Add test routes for role decorators
    @app.route("/admin")
    @require_admin_role
    def admin_route() -> Response:
        return jsonify({"status": "admin access"})

    @app.route("/user")
    @require_user_role
    def user_route() -> Response:
        return jsonify({"status": "user access"})

    @app.route("/agent")
    @require_role("agent")
    def agent_route() -> Response:
        return jsonify({"status": "agent access"})

    @app.route("/multi-role")
    @require_admin_role
    @require_user_role
    def multi_role_route() -> Response:
        return jsonify({"status": "multi-role access"})

    # Add test route for public endpoint decorator
    @app.route("/public")
    @public_endpoint()
    def public_route() -> Response:
        return jsonify({"status": "public access"})

    return app


def test_require_role_has_role(decorator_app: Flask) -> None:
    """Test require_role decorator when user has the required role."""
    with decorator_app.test_request_context("/admin"):
        # Set up g with user roles
        g.user_roles = ["admin", "user"]

        # Test the admin route
        response = decorator_app.view_functions["admin_route"]()
        # Ensure we have a Response object before accessing JSON
        response_obj = decorator_app.make_response(response)  # type: ignore[arg-type]
        assert response_obj.get_json()["status"] == "admin access"


def test_require_role_missing_role(decorator_app: Flask) -> None:
    """Test require_role decorator when user doesn't have the required role."""
    with decorator_app.test_request_context("/admin"):
        # Set up g with user roles that don't include admin
        g.user_roles = ["user"]

        # Test the admin route should raise Forbidden
        with pytest.raises(Forbidden, match="Requires role: admin"):
            decorator_app.view_functions["admin_route"]()


def test_require_role_missing_user_roles(decorator_app: Flask) -> None:
    """Test require_role decorator when g.user_roles doesn't exist."""
    with (
        decorator_app.test_request_context("/admin"),
        pytest.raises(Forbidden, match="Requires role: admin"),
    ):
        # Don't set up g.user_roles

        # Test the admin route should raise Forbidden
        decorator_app.view_functions["admin_route"]()


def test_public_endpoint_decorator(decorator_app: Flask) -> None:
    """Test that public_endpoint decorator marks the function as public."""
    # Check that the public route is marked as public
    assert hasattr(decorator_app.view_functions["public_route"], "is_public")
    assert decorator_app.view_functions["public_route"].is_public is True


def test_decorator_factory() -> None:
    """Test that DecoratorFactory produces proper decorators."""
    factory = DecoratorFactory()

    # Test require_role decorator
    admin_decorator = factory.require_role("admin")

    # Define a test function
    def test_func() -> str:
        return "test"

    # Apply the decorator
    decorated = admin_decorator(test_func)

    # Verify the function has the right attributes (the wrapper name might vary depending on implementation)
    assert callable(decorated)

    # Test public_endpoint decorator
    public_decorator = factory.public_endpoint()
    public_func = public_decorator(test_func)

    # Verify the function is marked as public
    assert hasattr(public_func, "is_public")
    assert public_func.is_public is True


def test_multiple_role_decorators(decorator_app: Flask) -> None:
    """Test that multiple role decorators are applied correctly."""
    with decorator_app.test_request_context("/multi-role"):
        # Test with admin role only
        g.user_roles = ["admin"]
        with pytest.raises(Forbidden, match="Requires role: user"):
            decorator_app.view_functions["multi_role_route"]()

        # Test with user role only
        g.user_roles = ["user"]
        with pytest.raises(Forbidden, match="Requires role: admin"):
            decorator_app.view_functions["multi_role_route"]()

        # Test with both roles
        g.user_roles = ["admin", "user"]
        response = decorator_app.view_functions["multi_role_route"]()
        response_obj = decorator_app.make_response(response)  # type: ignore[arg-type]
        assert response_obj.get_json()["status"] == "multi-role access"


def test_predefined_role_decorators() -> None:
    """Test that predefined role decorators use the correct roles."""
    # Create a Flask app for testing
    app = Flask("test")

    # Define test routes with predefined decorators
    @app.route("/admin")
    @require_admin_role
    def admin_route() -> str:
        return "admin"

    @app.route("/user")
    @require_user_role
    def user_route() -> str:
        return "user"

    # Check the wrapped functions have the correct roles
    with app.test_request_context("/admin"):
        g.user_roles = ["user"]
        with pytest.raises(Forbidden, match="Requires role: admin"):
            admin_route()

    with app.test_request_context("/user"):
        g.user_roles = ["admin"]
        with pytest.raises(Forbidden, match="Requires role: user"):
            user_route()
