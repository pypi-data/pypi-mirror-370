try:
    from gevent.monkey import is_module_patched
    from gevent.monkey import is_anything_patched
except ImportError:
    GEVENT = False
    GEVENT_WITHOUT_THREAD_PATCHING = False
else:
    GEVENT = is_anything_patched()
    GEVENT_WITHOUT_THREAD_PATCHING = GEVENT and not is_module_patched("threading")

try:
    import asyncio

    asyncio.get_running_loop()
    ASYNCIO = True
except RuntimeError:
    ASYNCIO = False
