import warnings
from uuid import uuid4
from typing import Mapping, Optional, Tuple

import ewoks
from ewokscore import task_discovery

from .pool import get_active_pool
from .futures import LocalFuture
from ..dummy_workflow import dummy_workflow


__all__ = [
    "execute_graph",
    "execute_test_graph",
    "convert_graph",
    "convert_workflow",
    "discover_tasks_from_modules",
    "discover_all_tasks",
]


def execute_graph(
    args: Optional[Tuple] = tuple(), kwargs: Optional[Mapping] = None
) -> LocalFuture:
    pool = get_active_pool()
    if kwargs is None:
        kwargs = dict()
    execinfo = kwargs.setdefault("execinfo", dict())
    uuid = str(uuid4())
    execinfo["job_id"] = uuid
    return pool.submit(ewoks.execute_graph, uuid=uuid, args=args, kwargs=kwargs)


def execute_test_graph(
    seconds=0, filename=None, kwargs: Optional[Mapping] = None
) -> LocalFuture:
    args = (dummy_workflow(),)
    if kwargs is None:
        kwargs = dict()
    kwargs["inputs"] = [
        {"id": "sleep", "name": 0, "value": seconds},
        {"id": "result", "name": "filename", "value": filename},
    ]
    return execute_graph(args=args, kwargs=kwargs)


def convert_graph(
    args: Optional[Tuple] = tuple(), kwargs: Optional[Mapping] = None
) -> LocalFuture:
    pool = get_active_pool()
    return pool.submit(ewoks.convert_graph, args=args, kwargs=kwargs)


def convert_workflow(**kw) -> LocalFuture:
    warnings.warn(
        "convert_workflow is deprecated, use convert_graph instead", stacklevel=2
    )
    return convert_graph(**kw)


def discover_tasks_from_modules(
    args: Optional[Tuple] = tuple(), kwargs: Optional[Mapping] = None
) -> LocalFuture:
    pool = get_active_pool()
    return pool.submit(
        task_discovery.discover_tasks_from_modules, args=args, kwargs=kwargs
    )


def discover_all_tasks(
    args: Optional[Tuple] = tuple(), kwargs: Optional[Mapping] = None
) -> LocalFuture:
    pool = get_active_pool()
    return pool.submit(task_discovery.discover_all_tasks, args=args, kwargs=kwargs)
