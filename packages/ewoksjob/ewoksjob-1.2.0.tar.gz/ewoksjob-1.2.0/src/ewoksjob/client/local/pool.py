import sys
from contextlib import contextmanager
from typing import Mapping, Optional, Tuple
from uuid import uuid4
import multiprocessing
import weakref
from concurrent.futures import ProcessPoolExecutor
from concurrent.futures import ThreadPoolExecutor
from concurrent.futures import Future as NativeFuture

try:
    from pyslurmutils.client.errors import RemoteExit
    from pyslurmutils.concurrent.futures import SlurmRestFuture
    from pyslurmutils.concurrent.futures import SlurmRestExecutor
except ImportError:
    SlurmRestExecutor = None
    SlurmRestFuture = None
    RemoteExit = None

from .futures import LocalFuture


__all__ = ["get_active_pool", "pool_context"]


_EWOKS_WORKER_POOL = None


def get_active_pool(raise_on_missing: Optional[bool] = True):
    if raise_on_missing and _EWOKS_WORKER_POOL is None:
        raise RuntimeError("No worker pool is available")
    return _EWOKS_WORKER_POOL


@contextmanager
def pool_context(*args, **kwargs):
    global _EWOKS_WORKER_POOL
    if _EWOKS_WORKER_POOL is None:
        with _LocalPool(*args, **kwargs) as pool_obj:
            _EWOKS_WORKER_POOL = pool_obj
            try:
                yield pool_obj
            finally:
                _EWOKS_WORKER_POOL = None
    else:
        yield _EWOKS_WORKER_POOL


class _LocalPool:
    def __init__(
        self,
        *args,
        pool_type: Optional[str] = None,
        context: Optional[str] = None,
        **kwargs,
    ) -> None:
        if pool_type is None:
            pool_type = "process"
        if context is None:
            context = "spawn"
        if pool_type == "process":
            if context:
                if sys.version_info >= (3, 7):
                    kwargs["mp_context"] = multiprocessing.get_context(context)
                else:
                    multiprocessing.set_start_method(context, force=True)
            self._executor = ProcessPoolExecutor(*args, **kwargs)
        elif pool_type == "thread":
            self._executor = ThreadPoolExecutor(*args, **kwargs)
        elif pool_type == "slurm":
            if SlurmRestExecutor is None:
                raise RuntimeError("requires pyslurmutils")
            self._executor = SlurmRestExecutor(*args, **kwargs)
        else:
            raise ValueError(f"Unknown pool type '{pool_type}'")
        self._pool_type = pool_type
        self._tasks = weakref.WeakValueDictionary()

    def __enter__(self):
        self._executor.__enter__()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        return self._executor.__exit__(exc_type, exc_val, exc_tb)

    def shutdown(self, **kw):
        return self._executor.shutdown(**kw)

    @property
    def pool_type(self):
        return self._pool_type

    def submit(
        self,
        func,
        uuid: Optional[str] = None,
        args: Optional[Tuple] = tuple(),
        kwargs: Optional[Mapping] = None,
    ) -> LocalFuture:
        """Like celery.send_task"""
        if kwargs is None:
            kwargs = dict()
        if uuid is None:
            uuid = str(uuid4())
        native_future = self._executor.submit(func, *args, **kwargs)
        future = LocalFuture(uuid, native_future)
        self._tasks[uuid] = future
        return future

    def get_future(self, uuid: str) -> LocalFuture:
        future = self._tasks.get(uuid)
        if future is not None:
            return future
        if self.pool_type == "slurm":
            future = SlurmRestFuture()
        else:
            future = NativeFuture()
        return LocalFuture(uuid, future)

    def get_unfinished_uuids(self) -> list:
        return [uuid for uuid, future in self._tasks.items() if not future.done()]
