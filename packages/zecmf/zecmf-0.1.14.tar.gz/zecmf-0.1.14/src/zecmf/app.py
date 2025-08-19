"""Application factory for creating Flask microservice applications with standardized configuration."""

import logging
import os
from typing import TYPE_CHECKING

from flask import Flask

from zecmf.api import init_api
from zecmf.auth import init_jwt
from zecmf.cli import register_commands
from zecmf.config import BaseConfig, get_config
from zecmf.constants import Config as ConfigConstants
from zecmf.extensions import cors, database

if TYPE_CHECKING:
    from flask_restx import Namespace

logger = logging.getLogger(__name__)


def create_app(
    config_name: str | None = None,
    api_namespaces: list[tuple["Namespace", str]] | None = None,
    app_config_module: str = ConfigConstants.APP_CONFIG_MODULE,
) -> Flask:
    """Create and configure a Flask microservice application.

    Args:
        config_name: The name of the configuration to use (development, production, etc).
        api_namespaces: List of namespaces to register with the API.
        app_config_module: The module path for the app-specific configuration.

    Returns:
        A configured Flask application.

    """
    logger.debug(f"Creating app with config_name: {config_name}")

    if not config_name:
        logger.info("No config_name provided, using environment variable FLASK_ENV")
        config_name = os.getenv("FLASK_ENV", "production")
        logger.debug(f"Using config_name from environment: {config_name}")

    app_config = _resolve_and_validate_config(config_name, app_config_module)
    app = _initialize_flask_app(app_config)
    _setup_database(app)
    _setup_cors(app)
    _setup_auth(app)
    _setup_api(app, api_namespaces)
    register_commands(app)
    return app


def _resolve_and_validate_config(
    config_name: str, app_config_module: str
) -> BaseConfig:
    """Resolve and instantiate the configuration class."""
    config_class = get_config(config_name, app_config_module)
    logger.debug(f"Resolved config class: {config_class.__name__}")
    config_instance = config_class()  # Validation on instantiation
    return config_instance


def _initialize_flask_app(app_config: BaseConfig) -> Flask:
    """Create and configure the Flask app instance."""
    app = Flask("app")
    app.config.from_object(app_config)
    return app


def _setup_database(app: Flask) -> None:
    """Initialize database extension."""
    database.init_app(app)


def _setup_cors(app: Flask) -> None:
    """Initialize CORS if enabled via environment variables."""
    cors.init_app(app)


def _setup_auth(app: Flask) -> None:
    """Initialize JWT authentication."""
    init_jwt(app)


def _setup_api(
    app: Flask,
    api_namespaces: list[tuple["Namespace", str]] | None = None,
) -> None:
    """Configure API and register namespaces."""
    api = init_api(app)

    if api_namespaces:
        for namespace, path in api_namespaces:
            api.add_namespace(namespace, path=path)
