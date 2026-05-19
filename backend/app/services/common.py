from __future__ import annotations

import time
from collections.abc import Callable
from typing import Any, TypeVar

from sqlalchemy.exc import OperationalError
from sqlalchemy.sql import Select

T = TypeVar("T")


def apply_mode_scope(
    stmt: Select[Any],
    *,
    mode_column: Any,
    mode_id: int | None,
    include_all_modes: bool,
) -> Select[Any]:
    if include_all_modes or mode_id is None:
        return stmt
    return stmt.where(mode_column == mode_id)


def run_with_retry(
    operation: Callable[[], T],
    *,
    max_attempts: int = 3,
    backoff_seconds: float = 0.25,
) -> T:
    if max_attempts < 1:
        raise ValueError("max_attempts must be at least 1")
    if backoff_seconds < 0:
        raise ValueError("backoff_seconds must be non-negative")

    attempt = 1
    while True:
        try:
            return operation()
        except OperationalError:
            if attempt >= max_attempts:
                raise
            time.sleep(backoff_seconds * (2 ** (attempt - 1)))
            attempt += 1
