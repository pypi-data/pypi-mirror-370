from typing import Optional, Mapping, Dict, Any


def merge_execute_arguments(
    client_execute_arguments: Optional[Dict[str, Any]],
    worker_execute_arguments: Optional[Dict[str, Any]],
) -> Dict[str, Any]:
    """Client arguments have precedence over worker arguments in case merging does not apply."""
    if client_execute_arguments is None:
        client_execute_arguments = dict()
    if worker_execute_arguments is None:
        worker_execute_arguments = dict()

    # Handler from the client
    execinfo = client_execute_arguments.get("execinfo", dict())
    handlers = execinfo.pop("handlers", list())

    # Handler from the worker
    execinfo = worker_execute_arguments.get("execinfo", dict())
    extra_handlers = execinfo.pop("handlers", list())

    for handler in extra_handlers:
        if handler not in handlers:
            handlers.append(handler)

    if handlers:
        execinfo = client_execute_arguments.setdefault("execinfo", dict())
        execinfo["handlers"] = handlers

    return _merge_mappings(worker_execute_arguments, client_execute_arguments)


def _merge_mappings(d1: Optional[Mapping], d2: Optional[Mapping]) -> dict:
    """`d2` has precedence over `d1` in case merging does not apply.
    Merging is done like `{**d1, **d2}` but then recursive.
    """
    if d1 is None:
        merged = dict()
    else:
        merged = dict(d1)
    if not d2:
        return merged
    for key, value2 in d2.items():
        value1 = merged.get(key)
        if isinstance(value1, Mapping) and isinstance(value2, Mapping):
            value2 = _merge_mappings(value1, value2)
        merged[key] = value2
    return merged
