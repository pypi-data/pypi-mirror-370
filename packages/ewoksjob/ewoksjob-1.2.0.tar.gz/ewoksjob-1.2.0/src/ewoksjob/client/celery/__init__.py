"""Remote worker pool managed by Celery"""

import os

from .. import async_state

if async_state.GEVENT_WITHOUT_THREAD_PATCHING:
    # Make Celery use `celery.backends.asynchronous.Drainer`
    # instead of `celery.backends.asynchronous.geventDrainer`.
    # The later causes CTRL-C to not be raised and other things
    # like Bliss scans to hang when calling `AsyncResult.get`.
    from kombu.utils import compat

    compat._environment = "default"

    # The real solution is to patch threads.

from .tasks import *  # noqa F403
from .utils import *  # noqa F403
from .futures import CeleryFuture as Future  # noqa F403
from .futures import TimeoutError  # noqa F401
from .futures import CancelledError  # noqa F401
from .tasks import execute_graph as submit  # noqa F401
from .tasks import execute_test_graph as submit_test  # noqa F401

# For clients (workers need it in the environment before starting the python process)
os.environ.setdefault("CELERY_LOADER", "ewoksjob.config.EwoksLoader")
