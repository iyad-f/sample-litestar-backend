from __future__ import annotations

from typing import TYPE_CHECKING

from asyncpg import ConnectionRejectionError
from litestar import Controller, MediaType, get
from litestar.response import Response
from litestar.status_codes import HTTP_200_OK, HTTP_500_INTERNAL_SERVER_ERROR
from structlog.stdlib import get_logger

from .schemas import SystemHealth
from .urls import SYSTEM_HEALTH

if TYPE_CHECKING:
    from asyncpg import Connection


logger = get_logger()


class SystemController(Controller):
    """SystemController."""

    tags = ["system"]

    @get(path=SYSTEM_HEALTH, media_type=MediaType.JSON)
    async def check_health(self, db_connection: Connection) -> Response[SystemHealth]:
        """Check database availibility and return app info."""
        try:
            await db_connection.execute("SELECT 1")
        except ConnectionRejectionError:
            db_ping = False
        else:
            db_ping = True

        if db_ping:
            db_status = "online"
            status_code = HTTP_200_OK
            await logger.adebug("System Health", database_status=db_status)
        else:
            db_status = "offline"
            status_code = HTTP_500_INTERNAL_SERVER_ERROR
            await logger.awarning("System Health", database_status=db_status)

        return Response(
            content=SystemHealth(database_status=db_status),
            status_code=status_code,
            media_type=MediaType.JSON,
        )
