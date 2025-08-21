import sys
import pathlib

import pytest

from ..client import celery
from ..client import local
from ..client import TimeoutError
from ..client import CancelledError

from .utils import wait_not_finished


def test_normal(ewoks_worker, slurm_tmp_path):
    _assert_normal(celery, slurm_tmp_path)


def test_normal_local(local_ewoks_worker, slurm_tmp_path):
    _assert_normal(local, slurm_tmp_path)


def _assert_normal(mod, slurm_tmp_path):
    filename = slurm_tmp_path / "finished.smf"
    future = mod.submit_test(seconds=5, filename=str(filename))
    wait_not_finished(mod, {future.uuid}, timeout=3)

    # Do not use future.result() so we test geting the result from the uuid.
    results = mod.get_result(future.uuid, timeout=30)

    assert results == {"return_value": True}
    _nfs_cache_refresh(filename)
    assert filename.exists()
    wait_not_finished(mod, set(), timeout=3)


def test_cancel(ewoks_worker, slurm_tmp_path):
    on_windows = sys.platform == "win32"
    if on_windows:
        # Cancelling a Celery job on Windows does not work.
        # https://docs.celeryq.dev/en/stable/faq.html#does-celery-support-windows
        _assert_cannot_be_cancelled(celery, slurm_tmp_path)
    else:
        _assert_cancel(celery, slurm_tmp_path)


def test_cancel_local(local_ewoks_worker, slurm_tmp_path):
    is_slurm_pool = local.get_active_pool().pool_type == "slurm"
    if is_slurm_pool:
        _assert_cancel(local, slurm_tmp_path)
    else:
        _assert_cannot_be_cancelled(local, slurm_tmp_path)


def _assert_cancel(mod, slurm_tmp_path):
    filename = slurm_tmp_path / "finished.smf"
    future = mod.submit_test(seconds=12, filename=str(filename))
    wait_not_finished(mod, {future.uuid}, timeout=3)

    _ = mod.cancel(future.uuid)

    # Check whether the job is cancelled.
    with pytest.raises(CancelledError):
        # Do not use future.result() so we test geting the result from the uuid.
        _ = mod.get_result(future.uuid, timeout=30)

    _nfs_cache_refresh(filename)
    assert not filename.exists()


def _assert_cannot_be_cancelled(mod, slurm_tmp_path):
    filename = slurm_tmp_path / "finished.smf"
    future = mod.submit_test(seconds=12, filename=str(filename))
    wait_not_finished(mod, {future.uuid}, timeout=3)

    _ = mod.cancel(future.uuid)

    # Check that the job cannot be cancelled.
    with pytest.raises(TimeoutError):
        # Do not use future.result() so we test geting the result from the uuid.
        _ = mod.get_result(future.uuid, timeout=3)

    _ = future.result(timeout=30)
    _nfs_cache_refresh(filename)
    assert filename.exists()


def _nfs_cache_refresh(filename: pathlib.Path):
    dirname = filename.parent
    for entry in dirname.iterdir():
        _ = entry.stat()  # Triggers a fresh stat call
