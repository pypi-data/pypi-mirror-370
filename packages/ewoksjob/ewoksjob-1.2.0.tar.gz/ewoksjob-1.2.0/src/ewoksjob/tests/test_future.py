import pytest

from ..client import celery
from ..client import local
from ..client.futures import TimeoutError


def test_future(ewoks_worker):
    future = celery.get_future("abc")
    assert not future.running()
    with pytest.raises(TimeoutError):
        _ = future.result(timeout=0)
    async_result = future._async_result
    async_result.on_ready(async_result)


def test_future_local(local_ewoks_worker):
    future = local.get_future("abc")
    assert not future.running()
    with pytest.raises(TimeoutError):
        _ = future.result(timeout=0)
