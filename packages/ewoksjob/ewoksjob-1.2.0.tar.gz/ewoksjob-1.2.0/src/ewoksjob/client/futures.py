import warnings
from typing import Any, Optional
from abc import abstractmethod

from concurrent.futures import TimeoutError  # noqa F401
from concurrent.futures import CancelledError  # noqa F401


class FutureInterface:
    # Same API has `concurrent.futures.Future`

    @abstractmethod
    def cancel(self) -> bool:
        """Cancel the future if possible.

        Returns `True` if the future was cancelled, False otherwise. A future
        cannot be cancelled if it is running or has already completed.
        """
        pass

    @abstractmethod
    def cancelled(self) -> bool:
        """Return `True` if the future was cancelled."""
        pass

    @abstractmethod
    def running(self) -> bool:
        """Return `True` if the future is currently executing."""
        pass

    @abstractmethod
    def done(self) -> bool:
        """Return `True` of the future was cancelled, aborted or finished executing."""
        pass

    @abstractmethod
    def result(self, timeout: Optional[float] = None) -> Any:
        """Return the result of the call that the future represents.

        :param timeout: The number of seconds to wait for the result if the future isn't done.
                        If `None`, then there is no limit on the wait time.
        :returns: The result of the call that the future represents.
        :raises CancelledError: If the future was cancelled.
        :raises TimeoutError: If the future didn't finish executing before the given timeout.
        :raises Exception: If the call raised then that exception will be raised.
        """
        pass

    def exception(self, timeout: Optional[float] = None) -> Optional[Exception]:
        """Return the exception raised by the call that the future represents.

        :param timeout: The number of seconds to wait for the result if the future isn't done.
                        If `None`, then there is no limit on the wait time.
        :returns: The exception raised by the call that the future represents or `None`
                  if the call completed without raising.
        :raises CancelledError: If the future was cancelled.
        :raises TimeoutError: If the future didn't finish executing before the given timeout.
        """
        pass

    # API in addition to `concurrent.futures.Future`

    @property
    def uuid(self) -> str:
        """Identifier of the call that the future represents."""
        pass

    @abstractmethod
    def aborted(self) -> bool:
        """Return `True` if the task is (being) aborted."""
        pass

    @abstractmethod
    def abort(self) -> bool:
        """Abort the execution of the call that the future represents if possible.

        Returns `True` if the future was aborted, False otherwise.
        """
        pass

    # Deprecated API

    @property
    def task_id(self) -> str:
        warnings.warn(
            "task_id is deprecated and will be removed in a future release. Use `uuid` instead.",
            DeprecationWarning,
            stacklevel=2,
        )
        return self.uuid

    @property
    def job_id(self) -> str:
        warnings.warn(
            "job_id is deprecated and will be removed in a future release. Use `uuid` instead.",
            DeprecationWarning,
            stacklevel=2,
        )
        return self.uuid

    @property
    def queue(self) -> str:
        warnings.warn(
            "queue is deprecated and will be removed in a future release.",
            DeprecationWarning,
            stacklevel=2,
        )
        return self._get_queue()

    @abstractmethod
    def _get_queue(self) -> str:
        pass

    def get(self, timeout: Optional[float] = None, **kwargs) -> Any:
        warnings.warn(
            "get() is deprecated and will be removed in a future release. Use `result()` instead.",
            DeprecationWarning,
            stacklevel=2,
        )
        return self.result(timeout=timeout)

    def ready(self) -> bool:
        warnings.warn(
            "ready() is deprecated and will be removed in a future release. Use `done()` instead.",
            DeprecationWarning,
            stacklevel=2,
        )
        return self.done()

    def failed(self) -> bool:
        warnings.warn(
            "failed() is deprecated and will be removed in a future release. Use `exception()` instead.",
            DeprecationWarning,
            stacklevel=2,
        )
        return self.exception() is not None

    def revoke(self, terminate: bool = False) -> bool:
        warnings.warn(
            "revoke() is deprecated and will be removed in a future release. Use `cancel()` or `abort()` instead.",
            DeprecationWarning,
            stacklevel=2,
        )
        if terminate:
            return self.abort()
        else:
            return self.cancel()
