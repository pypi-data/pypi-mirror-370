import warnings
from typing import List, Optional

from .futures import LocalFuture
from .pool import get_active_pool


__all__ = [
    "get_future",
    "cancel",
    "get_result",
    "get_unfinished_uuids",
    "get_not_finished_task_ids",
    "get_not_finished_futures",
]


def get_future(uuid: str) -> LocalFuture:
    pool = get_active_pool()
    return pool.get_future(uuid)


def cancel(uuid: str):
    """The current implementation does not allow cancelling running tasks"""
    future = get_future(uuid)
    future.abort()


def get_result(uuid: str, timeout: Optional[float] = None):
    future = get_future(uuid)
    return future.result(timeout=timeout)


def get_unfinished_uuids() -> list:
    """Get all task ID's that are not finished"""
    pool = get_active_pool()
    return pool.get_unfinished_uuids()


def get_not_finished_task_ids() -> List[str]:
    warnings.warn(
        "get_not_finished_task_ids() is deprecated and will be removed in a future release. Use `get_unfinished_uuids()` instead.",
        DeprecationWarning,
        stacklevel=2,
    )
    return get_unfinished_uuids()


def get_not_finished_futures() -> List[LocalFuture]:
    """Get all futures that are not finished"""
    return [get_future(uuid) for uuid in get_unfinished_uuids()]
