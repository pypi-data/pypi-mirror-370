import os
import sys
import functools
import celery


def _patch_eventlet():
    import eventlet.debug

    eventlet.monkey_patch()
    blockdetect = float(os.environ.get("EVENTLET_NOBLOCK", 0))
    if blockdetect:
        eventlet.debug.hub_blocking_detection(blockdetect, blockdetect)


def _patch_gevent():
    import gevent.monkey
    import gevent.signal

    gevent.monkey.patch_all()


_PATCHES = {
    "eventlet": _patch_eventlet,
    "gevent": _patch_gevent,
    "slurm": _patch_gevent,
}

celery.maybe_patch_concurrency = functools.partial(
    celery.maybe_patch_concurrency, patches=_PATCHES
)


def main(argv=None) -> None:
    if argv is None:
        argv = sys.argv
    if "worker" in argv:
        if "-A" not in argv:
            argv = argv[:1] + ["-A", "ewoksjob.apps.ewoks"] + argv[1:]
        if "--loglevel" not in argv and "-l" not in argv:
            argv += ["--loglevel", "INFO"]
    elif "monitor" in argv:
        argv[argv.index("monitor")] = "flower"
    sys.argv = argv
    os.environ.setdefault("CELERY_LOADER", "ewoksjob.config.EwoksLoader")

    from celery.__main__ import main as _main

    sys.exit(_main())


if __name__ == "__main__":
    main()
