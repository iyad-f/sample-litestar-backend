import logging
import sys
from dataclasses import dataclass, field
from functools import lru_cache

import structlog
from litestar.config.cors import CORSConfig
from litestar.config.csrf import CSRFConfig
from litestar.logging.config import (
    LoggingConfig,
    StructLoggingConfig,
    default_logger_factory,
    default_structlog_processors,
    default_structlog_standard_lib_processors,
)
from litestar.middleware.logging import LoggingMiddlewareConfig
from litestar.openapi.config import OpenAPIConfig
from litestar.openapi.plugins import ScalarRenderPlugin
from litestar.plugins.problem_details import ProblemDetailsConfig
from litestar.plugins.structlog import StructlogConfig
from litestar_asyncpg import AsyncpgConfig, PoolConfig

from app.__about__ import __version__ as current_version

from .settings import get_settings

__all__ = ("get_config",)


settings = get_settings()


@lru_cache
def _is_tty() -> bool:
    return bool(sys.stderr.isatty() or sys.stdout.isatty())


_render_as_json = not _is_tty()
_structlog_default_processors = default_structlog_processors(as_json=_render_as_json)
_structlog_default_processors.insert(1, structlog.processors.EventRenamer("message"))
_structlog_standard_lib_processors = default_structlog_standard_lib_processors(
    as_json=_render_as_json
)
_structlog_standard_lib_processors.insert(1, structlog.processors.EventRenamer("message"))


@dataclass
class PluginsConfig:
    """Plugins configuration."""

    PROBLEM_DETAILS: ProblemDetailsConfig = field(
        default_factory=lambda: ProblemDetailsConfig(enable_for_all_http_exceptions=True)
    )
    ASYNCPG: AsyncpgConfig = field(
        default_factory=lambda: AsyncpgConfig(
            pool_config=PoolConfig(
                dsn=settings.db.DSN,
                connect_kwargs={"command_timeout": settings.db.POOL_COMMAND_TIMEOUT},
            ),
            pool_app_state_key=settings.db.POOL_APP_STATE_KEY,
            pool_dependency_key=settings.db.POOL_DEPENDENCY_KEY,
            connection_dependency_key=settings.db.CONNECTION_DEPENDENCY_KEY,
        )
    )
    LOG: StructlogConfig = field(
        default_factory=lambda: StructlogConfig(
            structlog_logging_config=StructLoggingConfig(
                log_exceptions="always",
                processors=_structlog_default_processors,
                logger_factory=default_logger_factory(as_json=_render_as_json),
                standard_lib_logging_config=LoggingConfig(
                    root={
                        "level": logging.getLevelName(settings.log.LEVEL),
                        "handlers": ["queue_listener"],
                    },
                    formatters={
                        "standard": {
                            "()": structlog.stdlib.ProcessorFormatter,
                            "processors": _structlog_standard_lib_processors,
                        },
                    },
                    loggers={
                        "_granian": {
                            "propagate": False,
                            "level": settings.log.ASGI_ERROR_LEVEL,
                            "handlers": ["queue_listener"],
                        },
                        "granian.server": {
                            "propagate": False,
                            "level": settings.log.ASGI_ERROR_LEVEL,
                            "handlers": ["queue_listener"],
                        },
                        "granian.access": {
                            "propagate": False,
                            "level": settings.log.ASGI_ACCESS_LEVEL,
                            "handlers": ["queue_listener"],
                        },
                    },
                ),
            ),
            middleware_logging_config=LoggingMiddlewareConfig(
                request_log_fields=settings.log.REQUEST_FIELDS,
                response_log_fields=settings.log.RESPONSE_FIELDS,
            ),
        ),
    )


@dataclass
class SecurityConfig:
    """Security configuration."""

    CORS: CORSConfig = field(
        default_factory=lambda: CORSConfig(
            allow_origins=settings.app.ALLOWED_CORS_ORIGINS
        )
    )

    CSRF: CSRFConfig = field(
        default_factory=lambda: CSRFConfig(
            secret=settings.app.SECRET_KEY,
            cookie_secure=settings.app.CSRF_COOKIE_SECURE,
            cookie_name=settings.app.CSRF_COOKIE_NAME,
        )
    )


@dataclass
class Config:
    """Application configuration."""

    security: SecurityConfig = field(default_factory=SecurityConfig)
    plugins: PluginsConfig = field(default_factory=PluginsConfig)
    openapi: OpenAPIConfig = field(
        default_factory=lambda: OpenAPIConfig(
            title=settings.app.NAME,
            version=current_version,
            use_handler_docstrings=True,
            render_plugins=[ScalarRenderPlugin(version="latest")],
        )
    )


@lru_cache(maxsize=1, typed=True)
def get_config() -> Config:
    """Return the configuration for the application plugins."""
    return Config()
