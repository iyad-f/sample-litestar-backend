from __future__ import annotations

import binascii
import json
import os
from dataclasses import dataclass, field
from functools import lru_cache
from pathlib import Path
from typing import TYPE_CHECKING

from litestar.data_extractors import RequestExtractorField, ResponseExtractorField
from litestar.utils.module_loader import module_to_os_path

from ._utils import get_env

if TYPE_CHECKING:
    from typing import Self


__all__ = ("get_settings",)


DEFAULT_MODULE_NAME = "app"
BASE_DIR: Path = module_to_os_path(DEFAULT_MODULE_NAME)


@dataclass
class DatabaseSettings:
    """Database configuration."""

    DSN: str = field(default_factory=get_env("DATABASE_DSN", ""))
    POOL_COMMAND_TIMEOUT: int = field(
        default_factory=get_env("DATABASE_POOL_COMMAND_TIMEOUT", 30)
    )
    POOL_APP_STATE_KEY: str = field(
        default_factory=get_env("DATABASE_POOL_APP_STATE_KEY", "db_pool")
    )
    POOL_DEPENDENCY_KEY: str = field(
        default_factory=get_env("DATABASE_DEPENDENCY_KEY", "db_pool")
    )
    CONNECTION_DEPENDENCY_KEY: str = field(
        default_factory=get_env("DATABASE_CONNECTION_DEPENDENCY_KEY", "db_connection")
    )


@dataclass
class ServerSettings:
    """Server configuration."""

    HOST: str = field(default_factory=get_env("LITESTAR_HOST", "127.0.0.1"))
    PORT: int = field(default_factory=get_env("LITESTAR_PORT", 8000))


@dataclass
class LoggingSettings:
    """Logging configuration."""

    # https://stackoverflow.com/a/1845097/6560549
    EXCLUDE_PATHS: str = r"\A(?!x)x"
    HTTP_EVENT: str = "HTTP"
    INCLUDE_COMPRESSED_BODY: bool = False
    LEVEL: int = field(default_factory=get_env("LOG_LEVEL", 30))
    OBFUSCATE_COOKIES: set[str] = field(default_factory=lambda: {"session", "XSRF-TOKEN"})
    OBFUSCATE_HEADERS: set[str] = field(
        default_factory=lambda: {"Authorization", "X-API-KEY", "X-XSRF-TOKEN"}
    )
    REQUEST_FIELDS: list[RequestExtractorField] = field(
        default_factory=get_env(
            "LOG_REQUEST_FIELDS",
            [
                "path",
                "method",
                "query",
                "path_params",
            ],
            list[RequestExtractorField],
        ),
    )
    RESPONSE_FIELDS: list[ResponseExtractorField] = field(
        default_factory=get_env(
            "LOG_RESPONSE_FIELDS", ["status_code"], list[ResponseExtractorField]
        )
    )
    ASGI_ACCESS_LEVEL: int = field(default_factory=get_env("ASGI_ACCESS_LOG_LEVEL", 30))
    ASGI_ERROR_LEVEL: int = field(default_factory=get_env("ASGI_ERROR_LOG_LEVEL", 30))


@dataclass
class AppSettings:
    """Application configuration."""

    APP_LOC: str = "app.asgi:create_app"
    URL: str = field(default_factory=get_env("APP_URL", "http://localhost:8000"))
    DEBUG: bool = field(default_factory=get_env("LITESTAR_DEBUG", False))
    SECRET_KEY: str = field(
        default_factory=get_env(
            "SECRET_KEY", binascii.hexlify(os.urandom(32)).decode(encoding="utf-8")
        ),
    )
    NAME: str = field(default_factory=lambda: "device-hub-api")
    ALLOWED_CORS_ORIGINS: list[str] = field(
        default_factory=get_env("ALLOWED_CORS_ORIGINS", ["*"])
    )
    CSRF_COOKIE_NAME: str = field(
        default_factory=get_env("CSRF_COOKIE_NAME", "XSRF-TOKEN")
    )
    CSRF_COOKIE_SECURE: bool = field(default_factory=get_env("CSRF_COOKIE_SECURE", False))
    JWT_ENCRYPTION_ALGORITHM: str = field(default_factory=lambda: "HS256")

    def __post_init__(self) -> None:
        # while ALLOWED_CROS_ORIGINS is typed as list[str], the input inside
        # the .env will be a string and we need to validate it.
        origins = self.ALLOWED_CORS_ORIGINS
        if isinstance(origins, str):
            if origins.startswith("[") and origins.endswith("]"):
                try:
                    origins = json.loads(origins)
                except (SyntaxError, ValueError):
                    msg = "ALLOWED_CORS_ORIGINS is not a valid list representation."
                    raise ValueError(msg) from None
            else:
                origins = [host.strip() for host in origins.split(",")]

        self.ALLOWED_CORS_ORIGINS = origins  # pyright: ignore[reportConstantRedefinition]


@dataclass
class Settings:
    """Configuration."""

    app: AppSettings = field(default_factory=AppSettings)
    db: DatabaseSettings = field(default_factory=DatabaseSettings)
    server: ServerSettings = field(default_factory=ServerSettings)
    log: LoggingSettings = field(default_factory=LoggingSettings)

    @classmethod
    def from_env(cls, env_filename: str = ".env") -> Self:
        """Build settings from .env file."""
        env_file = Path(f"{os.curdir}/{env_filename}")
        if env_file.is_file():
            from dotenv import load_dotenv

            load_dotenv(env_file, override=True)

        return cls()


@lru_cache(maxsize=1, typed=True)
def get_settings() -> Settings:
    """Return the settings for the application."""
    return Settings.from_env()
