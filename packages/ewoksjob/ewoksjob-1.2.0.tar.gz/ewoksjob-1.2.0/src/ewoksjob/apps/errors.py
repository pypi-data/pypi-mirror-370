import traceback
from contextlib import contextmanager

_CLIENT_EXCEPTION_MODULES = (
    "builtins",
    "concurrent",
    "celery",
    "billiard",
    "multiprocessing",
    "kombu",
    "ewoksjob",
    "gevent",
    "greenlet",
)


class EwoksJobException(Exception):
    pass


class EwoksJobExceptionCause(Exception):
    pass


class EwoksJobBaseException(BaseException):
    pass


class EwoksJobBaseExceptionCause(BaseException):
    pass


@contextmanager
def replace_exception_for_client():
    try:
        yield
    except Exception as e:
        if _client_can_deserialize(e):
            raise
        tb = traceback.format_exc().rstrip()
        cause = EwoksJobExceptionCause(f"\n\n{tb}")
        raise EwoksJobException(str(e)) from cause
    except BaseException as e:
        if _client_can_deserialize(e):
            raise
        tb = traceback.format_exc().rstrip()
        cause = EwoksJobBaseExceptionCause(f"\n\n{tb}")
        raise EwoksJobBaseException(str(e)) from cause


def _client_can_deserialize(exception: BaseException) -> bool:
    """Returns `True` when the client-side will be able to deserialize the Exception object."""
    queue = [exception]
    while queue:
        e = queue.pop()
        emodule = e.__class__.__module__
        client_can_deserialize = any(
            emodule.startswith(mod) for mod in _CLIENT_EXCEPTION_MODULES
        )
        if not client_can_deserialize:
            return False
        if isinstance(e.__cause__, BaseException):
            queue.append(e.__cause__)
        if isinstance(e.__context__, BaseException):
            queue.append(e.__context__)
    return True
