import warnings
import logging
from typing import Dict, List, Optional, Set, Any
from celery import current_app

from .futures import CeleryFuture

__all__ = [
    "get_future",
    "cancel",
    "get_result",
    "get_unfinished_uuids",
    "get_not_finished_task_ids",
    "get_not_finished_futures",
    "get_queues",
    "get_workers",
]


logger = logging.getLogger(__name__)


def get_future(uuid: str) -> CeleryFuture:
    return CeleryFuture(uuid)


def cancel(uuid: str) -> None:
    future = get_future(uuid)
    future.abort()


def get_result(uuid: str, timeout: Optional[float] = None, **kwargs) -> Any:
    future = CeleryFuture(uuid)
    return future.result(timeout=timeout, **kwargs)


def get_unfinished_uuids() -> List[str]:
    inspect = current_app.control.inspect()
    uuids = list()

    worker_task_info: Optional[Dict[str, List[dict]]] = inspect.active()  # running
    if worker_task_info is None:
        logger.warning("No Celery workers were detected")
        worker_task_info = dict()
    for task_infos in worker_task_info.values():
        for task_info in task_infos:
            uuids.append(task_info["id"])

    worker_task_info: Optional[Dict[str, List[dict]]] = inspect.scheduled()  # pending
    if worker_task_info is None:
        worker_task_info = dict()
    for task_infos in worker_task_info.values():
        for task_info in task_infos:
            uuids.append(task_info["id"])

    return uuids


def get_not_finished_task_ids() -> List[str]:
    warnings.warn(
        "get_not_finished_task_ids() is deprecated and will be removed in a future release. Use `get_unfinished_uuids()` instead.",
        DeprecationWarning,
        stacklevel=2,
    )
    return get_unfinished_uuids()


def get_not_finished_futures() -> List[CeleryFuture]:
    lst = [get_future(uuid) for uuid in get_unfinished_uuids()]
    return [future for future in lst if future is not None]


def get_workers() -> List[str]:
    warnings.warn(
        "'get_workers' is deprecated and will be removed in a future release. Use 'get_queues' instead.",
        DeprecationWarning,
        stacklevel=2,
    )
    return get_queues()


def get_queues() -> List[str]:
    worker_queue_info: Optional[Dict[str, List[dict]]] = (
        current_app.control.inspect().active_queues()
    )
    if worker_queue_info is None:
        return list()

    queues: Set[str] = set()
    for queue_infos in worker_queue_info.values():
        for queue_info in queue_infos:
            queues.add(queue_info["name"])

    return list(queues)
