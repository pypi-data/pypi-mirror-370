"""Pool that redirects tasks to a Slurm cluster."""

import atexit
import weakref
import logging
import datetime
from functools import wraps
from typing import Callable, Any, Optional

try:
    import gevent
    from gevent import GreenletExit
except ImportError:
    # Avoid error one import. Do cause error when actually trying to use this pool.
    gevent = NotImplemented
    GreenletExit = NotImplemented

from celery import signals
from celery.concurrency.gevent import TaskPool as _TaskPool

try:
    from pyslurmutils.concurrent.futures import SlurmRestExecutor
    from pyslurmutils.concurrent.futures import SlurmRestFuture
except ImportError:
    SlurmRestExecutor = None
    SlurmRestFuture = Any

from .executor import set_execute_getter, ExecuteType


__all__ = ("TaskPool",)

logger = logging.getLogger(__name__)


class TaskPool(_TaskPool):
    """SLURM Task Pool."""

    EXECUTOR_OPTIONS = dict()

    SLURM_SHUTDOWN_TIMEOUT = 60.0  # seconds

    def __init__(self, *args, **kwargs):
        if SlurmRestExecutor is None:
            raise RuntimeError("requires pyslurmutils")
        super().__init__(*args, **kwargs)

        self._slurm_executor = None
        self._slurm_cleanup_task = None

        signals.worker_shutdown.connect(
            self._blocking_wait_for_slurm_cleanup, weak=False
        )
        atexit.register(self._blocking_wait_for_slurm_cleanup)

        self._create_slurm_executor()

    def restart(self):
        self._safe_remove_slurm_executor()
        self._create_slurm_executor()

    def on_stop(self):
        self._safe_remove_slurm_executor()
        super().on_stop()

    def _safe_remove_slurm_executor(self):
        """
        Initiate cleanup. If we're NOT in a gevent hub callback, block until
        the executor is fully cleaned up. If we ARE in a hub callback, only
        kick off cleanup and return immediately; final waiting happens in
        worker_shutdown/atexit.
        """
        self._start_slurm_cleanup()
        self._wait_for_slurm_cleanup(timeout=self.SLURM_SHUTDOWN_TIMEOUT)

    def _wait_for_slurm_cleanup(self, timeout=None):
        """
        Wait until the cleanup thread signals completion. Safe to call outside
        gevent hub callbacks. If called inside a hub callback, it just returns.
        """
        if self._is_in_gevent_callback():
            return

        task = self._slurm_cleanup_task
        if task:
            task.join(timeout=timeout)
            if task:
                logger.warning(
                    "Timed out waiting for SLURM executor cleanup (%.1fs).",
                    timeout or -1,
                )

    def _blocking_wait_for_slurm_cleanup(self, **_):
        """
        Runs on Celery's worker_shutdown signal and at process exit.
        Not a gevent hub callback → can block safely.
        """
        self._wait_for_slurm_cleanup(timeout=self.SLURM_SHUTDOWN_TIMEOUT)

    def _is_in_gevent_callback(self):
        if gevent is None:
            return False
        hub = gevent.get_hub()
        return gevent.getcurrent() is hub

    def _create_slurm_executor(self):
        maxtasksperchild = self.options["maxtasksperchild"]
        if maxtasksperchild is None:
            logger.warning(
                "The 'slurm' pool does not support Slurm jobs which execute an unlimited number of celery jobs. "
                "Use '--max-tasks-per-child=1' to remove this warning."
            )
            maxtasksperchild = 1
        kwargs = {
            "max_workers": self.limit,
            "max_tasks_per_worker": maxtasksperchild,
            **self.EXECUTOR_OPTIONS,
        }
        self._slurm_executor = SlurmRestExecutor(**kwargs)
        self._slurm_executor._celery_options = dict(self.options)
        _set_slurm_executor(self._slurm_executor)

    def _start_slurm_cleanup(self):
        """
        Start cleanup if not already running. Never blocks.
        """
        # If nothing to clean or already cleaning, just ensure the event reflects state
        if self._slurm_executor is None:
            self._slurm_cleanup_task = None
            return

        # If a previous cleanup greenlet is still around, don't start another
        if self._slurm_cleanup_task:
            return

        # Request non-blocking shutdown
        self._slurm_executor.shutdown(wait=False)

        # Do the blocking part in a greenlet
        self._slurm_cleanup_task = gevent.spawn(self._blocking_cleanup_main)

    def _blocking_cleanup_main(self):
        """
        Runs in a greenlet; allowed to block (e.g., Thread.join inside executor).
        """
        if self._slurm_executor is not None:
            try:
                # __exit__ may perform blocking joins internally; that's fine here.
                self._slurm_executor.__exit__(None, None, None)
            except Exception:
                logger.exception("Error while cleaning up SLURM executor")
            finally:
                self._slurm_executor = None

        logger.debug("SLURM executor cleanup complete")


_SLURM_EXECUTOR = None


def _set_slurm_executor(slurm_executor):
    global _SLURM_EXECUTOR
    _SLURM_EXECUTOR = weakref.proxy(slurm_executor)
    set_execute_getter(_get_execute_method)


def _get_execute_method() -> ExecuteType:
    try:
        submit = _SLURM_EXECUTOR.submit
    except (AttributeError, ReferenceError):
        # TaskPool is not instantiated
        return
    timeout = _SLURM_EXECUTOR._celery_options["timeout"]
    soft_timeout = _SLURM_EXECUTOR._celery_options["soft_timeout"]
    return _slurm_execute_method(submit, timeout, soft_timeout)


_SubmitType = Callable[[Callable, Any, Any], SlurmRestFuture]


def _slurm_execute_method(
    submit: _SubmitType, timeout: Optional[float], soft_timeout: Optional[float]
) -> Callable[[_SubmitType], ExecuteType]:
    """Instead of executing the celery task, forward the ewoks task to Slurm."""

    if timeout is None and soft_timeout is None:
        time_limit_sec = None
    elif soft_timeout is None:
        time_limit_sec = timeout
    elif timeout is None:
        time_limit_sec = soft_timeout + 10
    else:
        time_limit_sec = timeout

    @wraps(submit)
    def execute(ewoks_task: Callable, *args, **kwargs):
        if time_limit_sec is not None:
            slurm_arguments = kwargs.setdefault("slurm_arguments", {})
            parameters = slurm_arguments.setdefault("parameters", {})
            time_limit = str(datetime.timedelta(seconds=round(time_limit_sec)))
            _ = parameters.setdefault("time_limit", time_limit)

        future = submit(ewoks_task, *args, **kwargs)
        try:
            return future.result()
        except GreenletExit:
            _ensure_cancel_job(future)
            raise

    return execute


def _ensure_cancel_job(future: SlurmRestFuture) -> None:
    not_cancelled = True
    while not_cancelled:
        try:
            logger.info("Cancel Slurm job %s", future.job_id)
            future.abort()
        except GreenletExit:
            continue
        not_cancelled = False
