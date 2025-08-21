import time
import logging
import subprocess
from types import ModuleType

logger = logging.getLogger(__name__)


def has_redis() -> bool:
    try:
        import redis  # noqa F401
    except ImportError:
        return False
    return _check_redis_server()


def _check_redis_server() -> bool:
    try:
        result = subprocess.run(
            ["redis-server", "--version"], capture_output=True, text=True, check=True
        )
        return bool(result.stdout.strip())
    except Exception:
        return False


def wait_not_finished(mod: ModuleType, expected_uuids: set, timeout=3):
    """Wait until all running job ID's are `expected_uuids`"""
    if mod.__name__.endswith("celery") and not has_redis():
        logger.warning(
            "memory and sqlite do not support task monitoring, sleep %f sec instead",
            timeout,
        )
        time.sleep(timeout)
        return
    t0 = time.time()
    while True:
        uuids = set(mod.get_unfinished_uuids())
        if uuids == expected_uuids:
            return
        dt = time.time() - t0
        if dt > timeout:
            assert uuids == expected_uuids, f"{uuids} != {expected_uuids}"
        time.sleep(0.2)
