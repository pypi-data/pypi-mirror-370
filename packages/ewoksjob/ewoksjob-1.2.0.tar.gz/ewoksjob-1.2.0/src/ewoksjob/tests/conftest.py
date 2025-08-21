import gc
import os

import pytest
from ewokscore import events
from ewoksjob.events.readers import read_ewoks_events
from ewoksjob.worker import options as worker_options

from .utils import has_redis
from ..client import local


if has_redis():
    import redis

    @pytest.fixture(scope="session")
    def celery_config(redis_proc):
        url = f"redis://{redis_proc.host}:{redis_proc.port}"
        # celery -A ewoksjob.apps.ewoks --broker={url}/0 --result-backend={url}/1 inspect stats -t 5
        return {
            "broker_url": f"{url}/0",
            "result_backend": f"{url}/1",
            "result_serializer": "pickle",
            "accept_content": ["application/json", "application/x-python-serialize"],
            "task_remote_tracebacks": True,
            "enable_utc": False,
        }

else:

    @pytest.fixture(scope="session")
    def celery_config(tmpdir_factory):
        tmpdir = tmpdir_factory.mktemp("celery")
        return {
            "broker_url": "memory://",
            # "broker_url": f"sqla+sqlite:///{tmpdir / 'celery.db'}",
            "result_backend": f"db+sqlite:///{tmpdir / 'celery_results.db'}",
            "result_serializer": "pickle",
            "accept_content": ["application/json", "application/x-python-serialize"],
            "task_remote_tracebacks": True,
            "enable_utc": False,
        }


@pytest.fixture(scope="session")
def celery_includes():
    return ("ewoksjob.apps.ewoks",)


@pytest.fixture(scope="session")
def celery_worker_parameters(slurm_client_kwargs):
    if _use_slurm_pool():
        rmap = {v: k for k, v in worker_options.SLURM_NAME_MAP.items()}
        options = {rmap[k]: v for k, v in slurm_client_kwargs.items() if k in rmap}
        worker_options.apply_worker_options(options)
    return {"loglevel": "debug"}


@pytest.fixture(scope="session")
def celery_worker_pool():
    if os.name == "nt":
        # "prefork" nor "process" works on windows
        return "solo"
    elif _use_slurm_pool():
        return "slurm"
    else:
        return "process"


def _use_slurm_pool() -> bool:
    return gevent_patched()


def gevent_patched() -> bool:
    try:
        from gevent.monkey import is_anything_patched
    except ImportError:
        return False

    return is_anything_patched()


@pytest.fixture()
def skip_if_gevent():
    if gevent_patched():
        pytest.skip("not supported with gevent yet")


@pytest.fixture()
def ewoks_worker(celery_session_worker, celery_worker_pool):
    yield celery_session_worker
    if celery_worker_pool == "solo":
        events.cleanup()


@pytest.fixture(scope="session")
def local_ewoks_worker(slurm_client_kwargs):
    kw = {"max_workers": 8}
    if _use_slurm_pool():
        pool_type = "slurm"
        kw.update(slurm_client_kwargs)
    else:
        pool_type = None
    with local.pool_context(pool_type=pool_type, **kw) as pool:
        yield

        if pool_type != "slurm":
            # TODO: Fails with Slurm for one test specifically:
            #       test_task_discovery.py::test_submit_local with slurm

            while gc.collect():
                pass

            assert len(pool._tasks) == 0, str(list(pool._tasks.values()))


@pytest.fixture()
def sqlite3_ewoks_events(tmp_path):
    uri = f"file:{tmp_path / 'ewoks_events.db'}"
    handlers = [
        {
            "class": "ewokscore.events.handlers.Sqlite3EwoksEventHandler",
            "arguments": [{"name": "uri", "value": uri}],
        }
    ]
    with read_ewoks_events(uri) as reader:
        yield handlers, reader
        events.cleanup()


@pytest.fixture()
def redis_ewoks_events(redisdb):
    url = f"unix://{redisdb.connection_pool.connection_kwargs['path']}"
    handlers = [
        {
            "class": "ewoksjob.events.handlers.RedisEwoksEventHandler",
            "arguments": [
                {"name": "url", "value": url},
                {"name": "ttl", "value": 3600},
            ],
        }
    ]
    with read_ewoks_events(url) as reader:
        yield handlers, reader

        connection = redis.Redis.from_url(url)
        for key in connection.keys("ewoks:*"):
            assert connection.ttl(key) >= 0, key

        events.cleanup()
