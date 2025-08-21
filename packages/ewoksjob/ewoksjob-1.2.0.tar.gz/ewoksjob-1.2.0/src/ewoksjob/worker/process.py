import os
import sys
import time
import signal
import logging
from queue import Queue
from threading import Thread, Timer
from multiprocessing import Manager
from multiprocessing import get_context
from contextlib import contextmanager
from concurrent.futures import ProcessPoolExecutor
from concurrent.futures import wait
from concurrent.futures import Future
from concurrent.futures.process import BrokenProcessPool
from typing import Optional, Callable, Any

from celery.concurrency import base
from celery.concurrency import prefork
from celery.exceptions import SoftTimeLimitExceeded
from celery.exceptions import Terminated
from billiard.einfo import ExceptionInfo
from billiard.common import reset_signals


logger = logging.getLogger(__name__)


class TaskPool(base.BasePool):
    """Multiprocessing Pool of non-daemonic processes which
    can create child processes without the need for billiard.
    """

    EXECUTOR_OPTIONS = dict()

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._executor = None
        self._manager = Manager()

    def _ensure_executor(self):
        if self._executor is None:
            logger.info("Start executor ...")
            mp_context = get_context(self.EXECUTOR_OPTIONS.get("context"))
            initargs = self.options["initargs"]
            maxtasksperchild = self.options["maxtasksperchild"]

            kwargs = {
                "max_workers": self.limit,
                "initializer": process_initializer,
                "initargs": initargs,
                "mp_context": mp_context,
            }

            if sys.version_info >= (3, 11):
                kwargs["max_tasks_per_child"] = maxtasksperchild
            elif maxtasksperchild:
                logger.warning(
                    "'max_tasks_per_child' requires Python 3.11 or newer and will be ignored"
                )

            self._executor = ProcessPoolExecutor(**kwargs)

            if self.EXECUTOR_OPTIONS.get("precreate"):
                if maxtasksperchild:
                    logger.warning(
                        "Pre-creating processes is ignored because 'max_tasks_per_child' is used. Use '--process-no-precreate' to remove this warning."
                    )
                else:
                    timeout = self.EXECUTOR_OPTIONS.get("timeout", 10)
                    logger.info("Pre-create workers ...")
                    try:
                        self._executor.submit(os.getpid).result(timeout=timeout)
                    except TimeoutError:
                        logger.error(
                            f"Cannot pre-create workers within {timeout} seconds"
                        )
                        raise
            logger.info("Executor started")
        return self._executor

    def _ensure_no_executor(self):
        """Running jobs are not interrupted"""
        if self._executor is None:
            return
        logger.info("Stop executor (wait indefinitely for jobs to finish)...")
        try:
            self._executor.shutdown(wait=True)
        except BaseException:
            logger.error("Stop executor cancelled")
            raise
        logger.info("Executor stopped")
        self._executor = None

    def on_start(self):
        self._ensure_executor()

    def did_start_ok(self):
        return self._executor is not None

    def on_stop(self):
        """Called on the first CTRL-C of the worker process (warm shutdown)"""
        self._ensure_no_executor()

    def on_terminate(self):
        """Called when?"""
        self._ensure_no_executor()

    def on_close(self):
        """Called when?"""

    def terminate_job(self, pid, sig=None):
        """Called when revoking a job"""
        if sig is None:
            sig = signal.SIGTERM
        try:
            os.kill(pid, sig)
        except ProcessLookupError:
            pass

    def restart(self):
        self._ensure_no_executor()
        self._ensure_executor()

    def shrink(self, n=1):
        self._ensure_no_executor()
        self.limit = max(self.limit - n, 0)
        self._ensure_executor()

    def grow(self, n=1):
        self._ensure_no_executor()
        self.limit = max(self.limit + n, 0)
        self._ensure_executor()

    def on_apply(
        self,
        target,
        args=None,
        kwargs=None,
        accept_callback=None,
        callback=None,
        error_callback=None,
        **_,
    ):
        f = self._safe_submit(target, args, kwargs, accept_callback)

        if callback is not None or error_callback is not None:

            def done_callback(f):
                try:
                    result = f.result()
                except BrokenProcessPool:
                    # Child process was killed
                    # TODO: prefork.process_destructor(pid, exitcode)
                    if error_callback is None:
                        return
                    error_callback(parse_exception(Terminated(signal.SIGKILL)))
                except BaseException as e:
                    # Terminated: Job was cancelled
                    if error_callback is None:
                        return
                    error_callback(parse_exception(e))
                else:
                    # Job succeeded or failed: somehow the result is already
                    # converted to a tuple (failed, stringified result, time)
                    if callback is not None:
                        callback(result)

        f.add_done_callback(done_callback)
        return ApplyResult(f)

    def _safe_submit(self, target, args, kwargs, accept_callback) -> Future:
        while True:
            try:
                return self._submit(target, args, kwargs, accept_callback)
            except BrokenProcessPool:
                logger.warning("Restart executor because a child received SIGKILL")
                self.restart()

    def _submit(self, target, args, kwargs, accept_callback) -> Future:
        if args is None:
            args = tuple()
        if kwargs is None:
            kwargs = dict()

        executor = self._ensure_executor()
        if accept_callback is None:
            queue = None
        else:
            queue = self._manager.Queue()
            thread = Thread(target=accept_callback_main, args=(queue, accept_callback))
            thread.daemon = True
            thread.start()

        timeout = self.options["timeout"]
        soft_timeout = self.options["soft_timeout"]

        return executor.submit(
            subprocess_main, queue, target, args, kwargs, timeout, soft_timeout
        )

    def _get_info(self):
        if self._executor is None:
            return {
                "max-concurrency": self.limit,
                "processes": [],
                "max-tasks-per-child": "N/A",
            }
        max_tasks_per_child = getattr(self._executor, "_max_tasks_per_child", None)
        return {
            "max-concurrency": self.limit,
            "processes": list(self._executor._processes),
            "max-tasks-per-child": max_tasks_per_child or "N/A",
        }

    @property
    def num_processes(self):
        if self._executor is None:
            return 0
        return len(self._executor._processes)


def process_initializer(*args):
    os.environ["FORKED_BY_MULTIPROCESSING"] = "1"
    prefork.process_initializer(*args)
    reset_signals(full=True)
    try:
        signal.signal(signal.SIGUSR1, soft_timeout_sighandler)
    except AttributeError:
        pass
    try:
        signal.signal(signal.SIGINT, signal.SIG_IGN)
    except AttributeError:
        pass


def subprocess_main(
    queue: Optional[Queue],
    target: Callable,
    args: tuple,
    kwargs: dict,
    timeout: Optional[float],
    soft_timeout: Optional[float],
) -> Any:
    """Main function called in a child process"""
    try:
        if queue is not None:
            queue.put(os.getpid())
        with apply_time_limit(signal.SIGKILL, timeout):
            with apply_time_limit(signal.SIGUSR1, soft_timeout):
                return target(*args, **kwargs)
    except SystemExit as e:
        raise Terminated(e)


def accept_callback_main(queue: Queue, accept_callback: Callable) -> None:
    """Background task that wait for the start of job execution in a child process"""
    try:
        pid = queue.get()
    except EOFError:
        return
    accept_callback(pid, time.monotonic())


def parse_exception(e: BaseException) -> ExceptionInfo:
    """Prepare an exception for the error callback"""
    try:
        raise e from None
    except type(e):
        return ExceptionInfo()


class ApplyResult:
    def __init__(self, future):
        self._future = future

    def get(self):
        return self._future.result()

    def wait(self, timeout=None):
        wait([self._future], timeout)

    def terminate(self, signum):
        raise NotImplementedError


def soft_timeout_sighandler(signum, frame):
    raise SoftTimeLimitExceeded()


@contextmanager
def apply_time_limit(sig: int, timeout: Optional[float] = None):
    timer = None
    if timeout is not None:
        pid = os.getpid()
        timer = Timer(timeout, lambda: os.kill(pid, sig))
        timer.start()
    try:
        yield
    finally:
        if timer:
            timer.cancel()
