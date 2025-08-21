import time

import pytest
from ewokscore.tests.examples.graphs import get_graph

try:
    import pyicat_plus  # noqa F401

    ICAT_ERROR_MSG = "The message queue URL's are missing"
except ImportError:
    ICAT_ERROR_MSG = "requires pyicat-plus"

from ..client import celery
from ..client import local


def test_submit(ewoks_worker):
    assert_submit(celery)


def test_submit_local(local_ewoks_worker):
    assert_submit(local)


def assert_submit(mod):
    graph, expected = get_graph("acyclic1")
    expected = expected["task6"]
    kwargs = {
        "upload_parameters": {
            "metadata_urls": list(),
            "beamline": "id00",
            "proposal": f"id00{time.strftime('%y%m')}",
            "dataset": "testdataset",
            "path": "/path/to/localed/dataset",
            "metadata": {"Sample_name": "test"},
            "raw": "/path/to/raw/dataset",
        }
    }
    future = mod.submit(args=(graph,), kwargs=kwargs)
    with pytest.raises(RuntimeError, match=ICAT_ERROR_MSG):
        _ = future.result(timeout=60)
