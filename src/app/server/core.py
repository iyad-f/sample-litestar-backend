from __future__ import annotations

from typing import TYPE_CHECKING

from litestar.plugins import InitPluginProtocol

if TYPE_CHECKING:
    from litestar.config.app import AppConfig


class ApplicationCore(InitPluginProtocol):
    """Application core configuration plugin."""

    __slots__ = ()

    def on_app_init(self, app_config: AppConfig) -> AppConfig:
        """Configure the application.

        Parameters.
        """
        from app.config.app import get_config
        from app.config.settings import get_settings
        from app.domain.accounts.controllers.auth import AuthController
        from app.domain.system.controllers import SystemController
        from app.server.plugins import get_plugins

        settings = get_settings()
        config = get_config()
        plugins = get_plugins()

        app_config.debug = settings.app.DEBUG
        # openapi
        app_config.openapi_config = config.openapi
        # cors
        app_config.cors_config = config.security.CORS
        # csrf
        # app_config.csrf_config = config.security.CSRF
        # plugins
        app_config.plugins.extend([
            plugins.structlog,
            plugins.granian,
            plugins.asyncpg,
            plugins.problem_details,
        ])

        app_config.route_handlers.extend([
            SystemController,
            AuthController
        ])

        from typing import Literal
        app_config.signature_namespace.update(
            {"Literal": Literal}
        )

        return app_config
