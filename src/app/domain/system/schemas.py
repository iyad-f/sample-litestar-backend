from __future__ import annotations

from dataclasses import dataclass
from typing import TYPE_CHECKING

from app.__about__ import __version__ as current_version
from app.config.settings import get_settings

if TYPE_CHECKING:
    from typing import Literal


settings = get_settings()


@dataclass
class SystemHealth:
    """Represents the system health."""

    database_status: Literal["online", "offline"]
    app: str = settings.app.NAME
    version: str = current_version
