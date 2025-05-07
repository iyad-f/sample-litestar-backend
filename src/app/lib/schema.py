from __future__ import annotations

from typing import TYPE_CHECKING

from msgspec import UNSET, Struct

if TYPE_CHECKING:
    from typing import Any


class BaseStruct(Struct):
    """Base Struct."""

    def to_dict(self) -> dict[str, Any]:
        """Return dict form of the struct."""
        return {f: getattr(self, f) for f in self.__struct_fields__ if getattr(self, f, None) != UNSET}
