import os
from typing import Optional, overload

from typing_extensions import Literal


@overload
def from_env(key: str, allow_missing: Literal[False]) -> str: ...


@overload
def from_env(key: str, allow_missing: bool) -> Optional[str]: ...


@overload
def from_env(
    key: str,
) -> str: ...


def from_env(key: str, allow_missing: bool = False) -> Optional[str]:
    """Return the value of the given environment variable"""
    value = os.environ.get(key)

    if value:
        return value

    if allow_missing:
        return None

    raise KeyError(f"Missing {key} in ENV variables")
