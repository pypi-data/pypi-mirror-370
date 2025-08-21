from typing import Callable, Optional, Any


ExecuteType = Optional[Callable[[Callable, Any, Any], Any]]
_GET_EXECUTE_METHOD: Optional[Callable[[], ExecuteType]] = None


def set_execute_getter(get_execute_method: Callable[[], ExecuteType]) -> None:
    """Worker pools that need to wrap their tasks can implement a
    `get_execute_method` function and register it here.
    """
    global _GET_EXECUTE_METHOD
    _GET_EXECUTE_METHOD = get_execute_method


def get_execute_method() -> ExecuteType:
    if _GET_EXECUTE_METHOD is None:
        return
    return _GET_EXECUTE_METHOD()
