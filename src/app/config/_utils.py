from __future__ import annotations

import json
import os
from pathlib import Path
from typing import TYPE_CHECKING, cast, overload

if TYPE_CHECKING:
    from collections.abc import Callable

BASE_DIR = Path(__file__).parent.parent
TRUE_VALUES = frozenset({"True", "true", "1", "yes", "YES", "Y", "y", "T", "t"})

type ParseTypes = bool | int | str | list[str] | Path | list[Path]


class MissingType:
    """Placeholder for a Missing type.

    This helps differentiate None from the default
    """


_MISSING = MissingType()


@overload
def get_env(
    key: str,
    default: bool,  # noqa: FBT001
    type_hint: MissingType = _MISSING,
) -> Callable[[], bool]: ...


@overload
def get_env(
    key: str, default: int, type_hint: MissingType = _MISSING
) -> Callable[[], int]: ...


@overload
def get_env(
    key: str, default: str, type_hint: MissingType = _MISSING
) -> Callable[[], str]: ...


@overload
def get_env(
    key: str, default: Path, type_hint: MissingType = _MISSING
) -> Callable[[], Path]: ...


@overload
def get_env(
    key: str, default: list[Path], type_hint: MissingType = _MISSING
) -> Callable[[], list[Path]]: ...


@overload
def get_env(
    key: str, default: list[str], type_hint: MissingType = _MISSING
) -> Callable[[], list[str]]: ...


@overload
def get_env(
    key: str, default: None, type_hint: MissingType = _MISSING
) -> Callable[[], None]: ...


@overload
def get_env[T](
    key: str, default: ParseTypes | None, type_hint: type[T]
) -> Callable[[], T]: ...


def get_env[T](
    key: str, default: ParseTypes | None, type_hint: type[T] | MissingType = _MISSING
) -> Callable[[], ParseTypes | T | None]:
    return lambda: get_config_val(key=key, default=default, type_hint=type_hint)


@overload
def get_config_val(
    key: str,
    default: bool,  # noqa: FBT001
    type_hint: MissingType = _MISSING,
) -> bool: ...


@overload
def get_config_val(key: str, default: int, type_hint: MissingType = _MISSING) -> int: ...


@overload
def get_config_val(key: str, default: str, type_hint: MissingType = _MISSING) -> str: ...


@overload
def get_config_val(
    key: str, default: Path, type_hint: MissingType = _MISSING
) -> Path: ...


@overload
def get_config_val(
    key: str, default: list[Path], type_hint: MissingType = _MISSING
) -> list[Path]: ...


@overload
def get_config_val(
    key: str, default: list[str], type_hint: MissingType = _MISSING
) -> list[str]: ...


@overload
def get_config_val(
    key: str, default: None, type_hint: MissingType = _MISSING
) -> None: ...


@overload
def get_config_val[T](key: str, default: ParseTypes | None, type_hint: type[T]) -> T: ...


def get_config_val[T](  # noqa: PLR0911
    key: str, default: ParseTypes | None, type_hint: type[T] | MissingType = _MISSING
) -> ParseTypes | T | None:
    """Parse environment variables."""
    value = os.getenv(key)
    if value is None:
        if type_hint is _MISSING:
            return cast("T", default)
        return default

    typ = type(default)

    if typ is bool:
        bool_value = value in TRUE_VALUES
        if type_hint is _MISSING:
            return cast("T", bool_value)
        return bool_value
    if typ is int:
        int_value = int(value)
        if type_hint is _MISSING:
            return cast("T", int_value)
        return int_value
    if typ is Path:
        path_value = Path(value)
        if type_hint is _MISSING:
            return cast("T", path_value)
        return path_value
    if typ is list[Path]:
        if value.startswith("[") and value.endswith("]"):
            try:
                path_list = [Path(s) for s in json.loads(value)]
                if type_hint is _MISSING:
                    return cast("T", path_list)
            except (SyntaxError, ValueError) as e:
                msg = f"{key} is not a valid list representation."
                raise ValueError(msg) from e
            else:
                return value
        path_list = [Path(host.strip()) for host in value.split(",")]
        if type_hint is _MISSING:
            return cast("T", path_list)
        return path_list
    if typ is list[str]:
        if value.startswith("[") and value.endswith("]"):
            try:
                str_list = cast("list[str]", json.loads(value))
                if type_hint is _MISSING:
                    return cast("T", str_list)
            except (SyntaxError, ValueError) as e:
                msg = f"{key} is not a valid list representation."
                raise ValueError(msg) from e
            else:
                return value
        str_list = [host.strip() for host in value.split(",")]
        if type_hint is _MISSING:
            return cast("T", str_list)
        return str_list
    if type_hint is _MISSING:
        return cast("T", value)
    return value
