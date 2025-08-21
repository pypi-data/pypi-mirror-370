from ..client import celery
from ..client import local


def test_convert(ewoks_worker, slurm_tmp_path):
    assert_convert(celery, slurm_tmp_path)


def test_convert_local(local_ewoks_worker, slurm_tmp_path):
    assert_convert(local, slurm_tmp_path)


def assert_convert(mod, slurm_tmp_path):
    filename = slurm_tmp_path / "test.json"
    args = {"graph": {"id": "testgraph", "schema_version": "1.0"}}, str(filename)
    kwargs = {"save_options": {"indent": 2}}
    future = mod.convert_graph(args=args, kwargs=kwargs)
    results = future.result(timeout=60)
    assert results == str(filename) or results is None  # TODO: None is deprecated
    assert filename.exists()
