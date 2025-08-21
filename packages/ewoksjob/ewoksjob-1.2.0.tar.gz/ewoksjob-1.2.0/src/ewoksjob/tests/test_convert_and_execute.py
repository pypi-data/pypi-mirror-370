from ewokscore.tests.examples.graphs import get_graph
from ..client import celery
from ..client import local


def test_submit(ewoks_worker, slurm_tmp_path):
    assert_submit(celery, slurm_tmp_path)
    assert_submit_test(celery, slurm_tmp_path)


def test_submit_local(local_ewoks_worker, slurm_tmp_path):
    assert_submit(local, slurm_tmp_path)
    assert_submit_test(local, slurm_tmp_path)


def assert_submit(mod, slurm_tmp_path):
    graph, expected = get_graph("acyclic1")
    expected = expected["task6"]
    filename = slurm_tmp_path / "test.json"
    args = (graph,)
    kwargs = {"save_options": {"indent": 2}, "convert_destination": str(filename)}
    future1 = mod.submit(args=args, kwargs=kwargs)
    future2 = mod.get_future(future1.uuid)
    results = future1.result(timeout=60)
    assert results == expected
    results = future2.result(timeout=0)
    assert results == expected
    assert filename.exists()


def assert_submit_test(mod, slurm_tmp_path):
    filename = slurm_tmp_path / "test.json"
    kwargs = {"save_options": {"indent": 2}, "convert_destination": str(filename)}
    future1 = mod.submit_test(kwargs=kwargs)
    future2 = mod.get_future(future1.uuid)
    results = future1.result(timeout=60)
    assert results == {"return_value": True}
    results = future2.result(timeout=0)
    assert results == {"return_value": True}
    assert filename.exists()
