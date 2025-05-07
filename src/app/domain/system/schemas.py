from __future__ import annotations

from dataclasses import dataclass
from typing import Literal

from app.__about__ import __version__ as current_version
from app.config.settings import get_settings

settings = get_settings()


@dataclass
class SystemHealth:
    """Represents the system health."""

    database_status: Literal["online", "offline"]
    app: str = settings.app.NAME
    version: str = current_version
