import os
from typing import Optional

from .constant import (
    DEFAULT_RETRY,
    DEFAULT_TIMEOUT,
    ENVIRON_RETRY,
    ENVIRON_TIMEOUT,
)


def _parse_float(value: Optional[str], default: float) -> float:
    if not value:
        return default
    try:
        return float(value)
    except ValueError:
        return default


def _parse_int(value: Optional[str], default: int) -> int:
    if not value:
        return default
    try:
        return int(value)
    except ValueError:
        return default


def get_blob_env() -> tuple[float, int]:
    """
    Retrieve timeout and retries values. It look for environment variables
    first and return default value otherwise
    """
    timeout = _parse_float(os.environ.get(ENVIRON_TIMEOUT), DEFAULT_TIMEOUT)
    retry = _parse_int(os.environ.get(ENVIRON_RETRY), DEFAULT_RETRY)

    return timeout, retry
