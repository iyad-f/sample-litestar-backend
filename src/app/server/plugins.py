from dataclasses import dataclass, field
from functools import lru_cache

from litestar.plugins.problem_details import ProblemDetailsPlugin
from litestar.plugins.structlog import StructlogPlugin
from litestar_asyncpg import AsyncpgPlugin
from litestar_granian import GranianPlugin

from app.config.app import get_config

__all__ = ("get_plugins",)

config = get_config().plugins


@dataclass
class Plugins:
    """A collection of plugins."""

    structlog: StructlogPlugin = field(default_factory=lambda: StructlogPlugin(config=config.LOG))
    granian: GranianPlugin = field(default_factory=GranianPlugin)
    problem_details: ProblemDetailsPlugin = field(default_factory=lambda: ProblemDetailsPlugin(config=config.PROBLEM_DETAILS))
    asyncpg: AsyncpgPlugin = field(default_factory=lambda: AsyncpgPlugin(config=config.ASYNCPG))


@lru_cache(maxsize=1, typed=True)
def get_plugins() -> Plugins:
    """Return the plugins for the applcation."""
    return Plugins()
