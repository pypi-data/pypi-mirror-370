"""Base configuration classes for the application."""

import logging
import os
from pathlib import Path
from typing import Any, ClassVar

from dotenv import load_dotenv

load_dotenv(dotenv_path=Path.cwd() / ".env")

logger = logging.getLogger(__name__)


class BaseConfig:
    """Base configuration class with shared settings for all applications.

    This contains all common settings that are shared across all applications.
    Applications should only need to define app-specific settings or override
    settings that differ from these defaults.
    """

    # Flask settings
    SECRET_KEY: str | None = os.getenv(
        "SECRET_KEY"
    )  # Required in production, default in dev/test
    DEBUG: bool = False
    TESTING: bool = False

    # Database settings
    SQLALCHEMY_DATABASE_URI: str | None = os.getenv("DATABASE_URI")
    SQLALCHEMY_TRACK_MODIFICATIONS: bool = False
    SQLALCHEMY_ENGINE_OPTIONS: ClassVar[dict[str, Any]] = {
        "pool_recycle": 3600,
        "pool_pre_ping": True,
    }

    # API settings
    API_TITLE: str = "API"
    API_VERSION: str = "1.0"
    API_DESCRIPTION: str = "REST API Service"
    API_PREFIX: str = "/api/v1"
    API_VERSION_HEADER: bool = True

    # File upload settings
    MAX_CONTENT_LENGTH: int = 1024 * 1024  # 1MB

    # JWT settings - supporting both public key (RS256) and secret key (HS256) methods
    JWT_PUBLIC_KEY: str | None = os.getenv("JWT_PUBLIC_KEY")
    JWT_PUBLIC_KEY_PATH: str | None = os.getenv("JWT_PUBLIC_KEY_PATH")
    JWT_SECRET_KEY: str | None = os.getenv("JWT_SECRET_KEY")
    JWT_ALGORITHM: str = "RS256"
    JWT_TOKEN_LOCATION: ClassVar[list[str]] = ["headers"]
    JWT_HEADER_NAME: str = "Authorization"
    JWT_HEADER_TYPE: str = "Bearer"
    JWT_ACCESS_TOKEN_EXPIRES: int = 30 * 60  # seconds
    JWT_REFRESH_TOKEN_EXPIRES: int = 30 * 24 * 60 * 60  # seconds

    # LLM client settings
    CLIENT_LLM_URL: str | None = os.getenv("CLIENT_LLM_URL")
    CLIENT_LLM_KEY: str | None = os.getenv("CLIENT_LLM_KEY")
    CLIENT_LLM_TIMEOUT: int = int(os.getenv("CLIENT_LLM_TIMEOUT", "100"))

    # Answering Machine client settings
    CLIENT_ANSWERING_MACHINE_URL: str | None = os.getenv("CLIENT_ANSWERING_MACHINE_URL")
    CLIENT_ANSWERING_MACHINE_KEY: str | None = os.getenv("CLIENT_ANSWERING_MACHINE_KEY")
    CLIENT_ANSWERING_MACHINE_TIMEOUT: int = int(
        os.getenv("CLIENT_ANSWERING_MACHINE_TIMEOUT", "100")
    )

    # CORS settings - disabled by default for security
    CORS_ORIGINS: str | None = os.getenv("CORS_ORIGINS")  # None = CORS disabled
    CORS_METHODS: str = os.getenv(
        "CORS_METHODS", "GET,HEAD,PUT,PATCH,POST,DELETE,OPTIONS"
    )
    CORS_ALLOW_HEADERS: str = os.getenv("CORS_ALLOW_HEADERS", "*")
    CORS_EXPOSE_HEADERS: str | None = os.getenv("CORS_EXPOSE_HEADERS")
    CORS_SUPPORTS_CREDENTIALS: bool = (
        os.getenv("CORS_SUPPORTS_CREDENTIALS", "false").lower() == "true"
    )
    CORS_MAX_AGE: int | None = None

    def __init__(self) -> None:
        """Initialize configuration with validation.

        This validates the configuration based on the selected algorithm:
        - For RS256: requires either JWT_PUBLIC_KEY or JWT_PUBLIC_KEY_PATH
        - For HS256: requires JWT_SECRET_KEY
        """
        # Parse CORS_MAX_AGE from environment if set
        cors_max_age_str = os.getenv("CORS_MAX_AGE")
        if cors_max_age_str:
            try:
                self.CORS_MAX_AGE = int(cors_max_age_str)
            except ValueError:
                logger.warning(
                    f"Invalid CORS_MAX_AGE value: {cors_max_age_str}. Using None."
                )
                self.CORS_MAX_AGE = None

        # Skip validation for testing
        if getattr(self, "SKIP_VALIDATION", False):
            return

        # Secret key must be set in production
        if not self.DEBUG and not self.SECRET_KEY:
            raise ValueError("SECRET_KEY must be set in production environments.")

        # For RS256 (asymmetric) authentication
        if self.JWT_ALGORITHM == "RS256":
            self._validate_rs256_config()
        # For HS256 (symmetric) authentication
        elif self.JWT_ALGORITHM == "HS256":
            self._validate_hs256_config()
        else:
            raise ValueError(
                f"Unsupported JWT algorithm: {self.JWT_ALGORITHM}. "
                "Supported algorithms are 'RS256' and 'HS256'."
            )

    def _validate_rs256_config(self) -> None:
        """Validate RS256 configuration settings."""
        if self.JWT_PUBLIC_KEY and self.JWT_PUBLIC_KEY_PATH:
            raise ValueError(
                "Both JWT_PUBLIC_KEY and JWT_PUBLIC_KEY_PATH are set. "
                "Please provide only one of them."
            )
        elif not self.JWT_PUBLIC_KEY and not self.JWT_PUBLIC_KEY_PATH:
            raise ValueError(
                "Either JWT_PUBLIC_KEY or JWT_PUBLIC_KEY_PATH must be set "
                "when using RS256."
            )
        elif self.JWT_PUBLIC_KEY_PATH and not self.JWT_PUBLIC_KEY:
            path = Path(self.JWT_PUBLIC_KEY_PATH)
            if path.exists():
                with open(path, encoding="utf-8") as f:
                    self.JWT_PUBLIC_KEY = f.read()
            else:
                raise ValueError(f"JWT_PUBLIC_KEY_PATH '{path}' does not exist.")

    def _validate_hs256_config(self) -> None:
        """Validate HS256 configuration settings."""
        if not self.JWT_SECRET_KEY:
            raise ValueError(
                "JWT_SECRET_KEY must be set in production when using HS256 algorithm."
            )


class BaseDevelopmentConfig(BaseConfig):
    """Development configuration for local development environments.

    Provides defaults that make development easier with minimal setup.
    """

    # Enable debugging features
    DEBUG: bool = True

    # Default database is SQLite for easy development
    SQLALCHEMY_DATABASE_URI: str = os.getenv("DATABASE_URI", "sqlite:///dev.sqlite3")

    # Default secret key for development (DO NOT use in production)
    SECRET_KEY: str = os.getenv("SECRET_KEY", "dev-key-not-for-production")


class BaseProductionConfig(BaseConfig):
    """Production configuration for deployment.

    Prioritizes security and requires proper environment configuration.
    """

    # Disable debugging features in production
    DEBUG: bool = False
    TESTING: bool = False

    # These need to be explicitly set from environment in production
    # SECRET_KEY = os.getenv("SECRET_KEY")  # This is intentionally not set to force proper configuration
    # SQLALCHEMY_DATABASE_URI = os.getenv("DATABASE_URI")  # This is intentionally not set to force proper configuration


class BaseTestingConfig(BaseConfig):
    """Testing configuration for unit and integration tests.

    Provides fast, isolated test environment with in-memory database.
    """

    # Enable testing features
    TESTING: bool = True
    DEBUG: bool = False

    # Use in-memory SQLite for speed
    # Match the BaseConfig type for compatibility
    SQLALCHEMY_DATABASE_URI: str | None = "sqlite:///:memory:"

    # Fixed secret key for test reproducibility
    # Match the BaseConfig type for compatibility
    SECRET_KEY: str | None = "testing-secret-key"

    # HS256 is easier for testing
    JWT_ALGORITHM: str = "HS256"
    # Match the BaseConfig type for compatibility
    JWT_SECRET_KEY: str | None = "testing-secret-key"

    # Skip validation in tests
    SKIP_VALIDATION: bool = True

    # Shortened token expiration for faster testing
    JWT_ACCESS_TOKEN_EXPIRES: int = 60  # 1 minute
