"""Celery ewoks application executed on the worker side."""

from functools import wraps
from typing import Dict, List, Union, Callable, Any

import celery
import ewoks
from ewokscore import task_discovery

from ..worker.options import add_options
from ..worker.executor import get_execute_method
from .errors import replace_exception_for_client
from .arguments import merge_execute_arguments

app = celery.Celery("ewoks")
add_options(app)


def _ensure_ewoks_job_id(celery_task: Callable) -> Callable:
    """Use celery task ID as ewoks job ID when ewoks job ID is not provided"""

    @wraps(celery_task)
    def new_celery_task(self, *args, **kwargs):
        execinfo = kwargs.setdefault("execinfo", dict())
        if not execinfo.get("job_id"):
            execinfo["job_id"] = self.request.id
        return celery_task(self, *args, **kwargs)

    return new_celery_task


def _task_wrapper(celery_task: Callable) -> Callable:
    """Wraps all celery tasks in order to

    * convert exceptions that the client is not expected to have
    * execute with a worker specific executor (e.g. redirect the
      ewoks task to another job scheduler)
    """

    @wraps(celery_task)
    def new_celery_task(*args, **kwargs) -> Any:
        with replace_exception_for_client():
            execute = get_execute_method()

            if execute is None:
                return celery_task(*args, **kwargs)

            # Remove all references to ewoksjob
            ewoks_task = _get_ewoks_task_from_celery_task(celery_task)
            if _celery_task_is_bound(celery_task):
                args = args[1:]  # remove `self`

            return execute(ewoks_task, *args, **kwargs)

    return new_celery_task


def _merge_execute_arguments(celery_task: Callable) -> Callable:
    """Inject ewoks execution parameters from the worker configuration."""

    @wraps(celery_task)
    def new_celery_task(self, *args, **client_execute_arguments) -> Any:
        worker_execute_arguments = self.app.conf.get("ewoks_execution")
        kwargs = merge_execute_arguments(
            client_execute_arguments, worker_execute_arguments
        )
        return celery_task(self, *args, **kwargs)

    return new_celery_task


@app.task(bind=True)
@_ensure_ewoks_job_id
@_merge_execute_arguments
@_task_wrapper
def execute_graph(self, *args, **kwargs) -> Dict:
    return ewoks.execute_graph(*args, **kwargs)


@app.task()
@_task_wrapper
def convert_graph(*args, **kwargs) -> Union[str, dict]:
    return ewoks.convert_graph(*args, **kwargs)


@app.task()
@_task_wrapper
def discover_tasks_from_modules(*args, **kwargs) -> List[dict]:
    return task_discovery.discover_tasks_from_modules(*args, **kwargs)


@app.task()
@_task_wrapper
def discover_all_tasks(*args, **kwargs) -> List[dict]:
    return task_discovery.discover_all_tasks(*args, **kwargs)


_TASK_MAPPING: Dict[Callable, Callable] = {
    "execute_graph": ewoks.execute_graph,
    "convert_graph": ewoks.convert_graph,
    "discover_tasks_from_modules": task_discovery.discover_tasks_from_modules,
    "discover_all_tasks": task_discovery.discover_all_tasks,
}

_BOUND_TASKS = {"execute_graph"}


def _get_ewoks_task_from_celery_task(celery_task: Callable) -> Callable:
    return _TASK_MAPPING[celery_task.__name__]


def _celery_task_is_bound(celery_task: Callable) -> Callable:
    return celery_task.__name__ in _BOUND_TASKS
