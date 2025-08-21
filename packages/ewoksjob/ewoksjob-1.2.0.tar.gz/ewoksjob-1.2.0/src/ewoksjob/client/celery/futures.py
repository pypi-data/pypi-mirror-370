import time
import warnings
from typing import Any, Optional

from celery import states
from celery.result import AsyncResult
from billiard.exceptions import Terminated
from celery.exceptions import TaskRevokedError
from celery.exceptions import TimeoutError as CeleryTimeoutError

from ..futures import TimeoutError
from ..futures import CancelledError
from ..futures import FutureInterface
from .. import async_state

# From celery.states
#: Task state is unknown (assumed pending since you know the id).
# PENDING = 'PENDING'
#: Task was received by a worker (only used in events).
# RECEIVED = 'RECEIVED'
#: Task was started by a worker (:setting:`task_track_started`).
# STARTED = 'STARTED'
#: Task succeeded
# SUCCESS = 'SUCCESS'
#: Task failed
# FAILURE = 'FAILURE'
#: Task was revoked.
# REVOKED = 'REVOKED'
#: Task was rejected (only used in events).
# REJECTED = 'REJECTED'
#: Task is waiting for retry.
# RETRY = 'RETRY'
# IGNORED = 'IGNORED'


_RUNNING_STATES = frozenset(
    {states.RECEIVED, states.STARTED}
)  # do not include states.PENDING
_DONE_STATES = frozenset({states.SUCCESS, states.FAILURE, states.REVOKED})


class CeleryFuture(FutureInterface):
    def __init__(self, uuid: str, async_result: Optional[AsyncResult] = None):
        if async_result is None:
            async_result = AsyncResult(uuid)
        self._async_result = async_result

    # Same API as `concurrent.futures.Future`

    def cancel(self) -> bool:
        self._async_result.revoke(terminate=False)
        return self.cancelled

    def cancelled(self) -> bool:
        return self._async_result.state == states.REVOKED

    def running(self) -> bool:
        return self._async_result.state in _RUNNING_STATES

    def done(self) -> bool:
        return self._async_result.state in _DONE_STATES

    def result(
        self,
        timeout: Optional[float] = None,
        interval: Optional[float] = None,
        **kwargs,
    ) -> Any:
        if kwargs:
            warnings.warn(
                f"arguments {list(kwargs)} are deprecated and will be removed in a future release.",
                DeprecationWarning,
                stacklevel=2,
            )
        if interval is None:
            interval = 0.1
        else:
            interval = max(interval, 0.001)

        if async_state.GEVENT_WITHOUT_THREAD_PATCHING:
            t0 = time.time()
            while not self._async_result.ready():
                if timeout is not None and time.time() - t0 >= timeout:
                    raise TimeoutError(
                        f"job '{self.uuid}' is not done with {timeout} seconds"
                    )
                if interval is not None:
                    time.sleep(interval)

        if timeout == 0:
            # celery.backend.asynchronous.Drainer.drain_events_until:
            # timeout=0 is equivalent to timeout=None: wait indefinitely.
            # In addition, the timeout is checked before the first call.
            timeout = interval
        try:
            return self._async_result.get(timeout=timeout, interval=interval, **kwargs)
        except (TaskRevokedError, Terminated) as e:
            err_msg = f"job '{self.uuid}' was cancelled or terminated"
            raise CancelledError(err_msg) from e
        except CeleryTimeoutError as e:
            err_msg = f"job '{self.uuid}' is not done with {timeout} seconds"
            raise TimeoutError(err_msg) from e

    def exception(self, timeout: Optional[float] = None) -> Optional[Exception]:
        try:
            _ = self.result(timeout=timeout)
        except (TimeoutError, CancelledError):
            raise
        except Exception as exc:
            return exc

    # API in addition to `concurrent.futures.Future`

    @property
    def uuid(self) -> str:
        return self._async_result.id

    def aborted(self) -> bool:
        return self._async_result.state == states.REVOKED

    def abort(self) -> bool:
        self._async_result.revoke(terminate=True)
        return self.aborted

    def _get_queue(self) -> str:
        return self._async_result.queue
