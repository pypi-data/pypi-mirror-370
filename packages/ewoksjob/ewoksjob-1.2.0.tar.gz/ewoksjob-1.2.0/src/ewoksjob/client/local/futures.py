from contextlib import contextmanager
from typing import Any, Optional, Union

from concurrent.futures import Future as NativeFuture
from concurrent.futures import TimeoutError as NativeTimeoutError
from concurrent.futures import CancelledError as NativeCancelledError

try:
    from pyslurmutils.client.errors import RemoteExit
    from pyslurmutils.concurrent.futures import SlurmRestFuture

    NATIVE_FUTURE_TYPES = Union[NativeFuture, SlurmRestFuture]
except ImportError:

    class RemoteExit(Exception):
        pass

    SlurmRestFuture = None
    NATIVE_FUTURE_TYPES = Union[NativeFuture]

from ..futures import TimeoutError
from ..futures import CancelledError
from ..futures import FutureInterface


class LocalFuture(FutureInterface):

    def __init__(self, uuid: str, future: Optional[NATIVE_FUTURE_TYPES] = None) -> None:
        if future is None:
            from .pool import get_active_pool

            pool = get_active_pool()
            future = pool.get_future(uuid)
        self._native_future = future
        if SlurmRestFuture is None:
            self._is_slurm = False
        else:
            self._is_slurm = isinstance(future, SlurmRestFuture)
        self._uuid = uuid

    # Same API has `concurrent.futures.LocalFuture`

    def cancel(self) -> bool:
        return self._native_future.cancel()

    def cancelled(self) -> bool:
        return self._native_future.cancelled()

    def running(self) -> bool:
        return self._native_future.running()

    def done(self) -> bool:
        return self._native_future.done()

    def result(self, timeout: Optional[float] = None) -> Any:
        with self._convert_exceptions(timeout):
            return self._native_future.result(timeout=timeout)

    def exception(self, timeout: Optional[float] = None) -> Optional[Exception]:
        with self._convert_exceptions(timeout):
            return self._native_future.exception(timeout=timeout)

    @contextmanager
    def _convert_exceptions(self, timeout):
        try:
            yield
        except (NativeCancelledError, RemoteExit) as e:
            err_msg = f"future of job '{self.uuid}' was cancelled"
            raise CancelledError(err_msg) from e
        except NativeTimeoutError as e:
            err_msg = f"job '{self.uuid}' is not done with {timeout} seconds"
            raise TimeoutError(err_msg) from e

    # API in addition to `concurrent.futures.LocalFuture`

    @property
    def uuid(self) -> str:
        return self._uuid

    def aborted(self) -> bool:
        if self._is_slurm:
            slurm_client = self._native_future.slurm_client
            if slurm_client is None:
                return False
            status = slurm_client.get_status(self._native_future.job_id)
            return status == "CANCELLED"
        else:
            return False

    def abort(self) -> bool:
        if self._is_slurm:
            self._native_future.abort()
        return self.aborted()

    def _get_queue(self) -> str:
        return "local"
