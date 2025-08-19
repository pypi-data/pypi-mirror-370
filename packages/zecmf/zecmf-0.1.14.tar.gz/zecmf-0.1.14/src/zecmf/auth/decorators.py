"""Authentication decorators for role-based access control."""

from collections.abc import Callable
from functools import wraps
from typing import Any, TypeVar, cast

from flask import g
from werkzeug.exceptions import Forbidden

# Type variable for generic functions
F = TypeVar("F", bound=Callable[..., Any])


class DecoratorFactory:
    """Factory to create decorators only when needed in a request context."""

    @staticmethod
    def require_role(role: str) -> Callable[[F], F]:
        """Create a decorator to require a specific role."""

        def decorator(f: F) -> F:
            @wraps(f)
            def wrapper(*args: object, **kwargs: object) -> object:
                # Check if user has the required role
                if not hasattr(g, "user_roles") or role not in g.user_roles:
                    raise Forbidden(f"Requires role: {role}")

                return f(*args, **kwargs)

            return cast("F", wrapper)

        return decorator

    @staticmethod
    def public_endpoint() -> Callable[[F], F]:
        """Create a decorator to mark an endpoint as public.

        This decorator can be applied to:
        - Regular Flask routes (function-based views)
        - Specific HTTP methods in Flask-RESTX Resources (apply to method)

        Note: For Flask-RESTX Resource classes, do not apply this decorator directly to
        the class. Instead, apply it to individual methods.
        """

        def decorator(f: F) -> F:
            # Mark the original function as public
            f.is_public = True  # type: ignore

            @wraps(f)
            def wrapper(*args: object, **kwargs: object) -> object:
                return f(*args, **kwargs)

            # Mark the wrapper function as public
            wrapper.is_public = True  # type: ignore

            return cast("F", wrapper)

        return decorator


# Create decorator factory instance
decorator_factory = DecoratorFactory()


def require_role(role: str) -> Callable[[F], F]:
    """Require a specific role for an endpoint."""
    return decorator_factory.require_role(role)


def public_endpoint() -> Callable[[F], F]:
    """Mark an endpoint as public, exempt from authentication requirements."""
    return decorator_factory.public_endpoint()


# Pre-defined role decorators for convenience
require_admin_role = require_role("admin")
require_user_role = require_role("user")
require_agent_role = require_role("agent")
