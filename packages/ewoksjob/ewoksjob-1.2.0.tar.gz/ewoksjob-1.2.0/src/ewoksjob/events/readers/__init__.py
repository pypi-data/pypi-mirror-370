from typing import Iterator
from contextlib import contextmanager

from .base import EventType  # noqa F401
from .base import EwoksEventReader
from .sqlite3 import Sqlite3EwoksEventReader  # noqa F401

try:
    from .redis import RedisEwoksEventReader  # noqa F401
except ImportError:
    pass


def instantiate_reader(url: str, **kw) -> EwoksEventReader:
    s = url.lower()
    if any(s.startswith(scheme) for scheme in ("redis:", "rediss:", "unix:")):
        return RedisEwoksEventReader(url, **kw)
    elif s.startswith("file:"):
        return Sqlite3EwoksEventReader(url, **kw)
    else:
        raise ValueError(f"unknown scheme for '{url}'")


@contextmanager
def read_ewoks_events(url: str, **kw) -> Iterator[EwoksEventReader]:
    with instantiate_reader(url, **kw) as reader:
        yield reader
