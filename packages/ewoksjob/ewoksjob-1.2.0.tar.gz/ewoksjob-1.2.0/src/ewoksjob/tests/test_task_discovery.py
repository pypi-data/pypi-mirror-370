from ..client import celery
from ..client import local


def test_submit(ewoks_worker):
    assert_submit(celery)
    assert_submit(celery, "ewokscore")
    assert_submit(celery)


def test_submit_local(local_ewoks_worker):
    assert_submit(local)
    assert_submit(local, "ewokscore")
    assert_submit(local)


def assert_submit(mod, *modules):
    if modules:
        future1 = mod.discover_tasks_from_modules(args=modules)
    else:
        future1 = mod.discover_all_tasks()
    future2 = mod.get_future(future1.uuid)
    results = future1.result(timeout=60)
    assert results
    results = future2.result(timeout=0)
    assert results
