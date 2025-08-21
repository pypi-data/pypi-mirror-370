import os
import json
import socket
from typing import Iterator
import redis
from .base import EwoksEventReader, EventType


class RedisEwoksEventReader(EwoksEventReader):
    def __init__(self, url: str, **_):
        client_name = f"ewoks:reader:{socket.gethostname()}:{os.getpid()}"
        self._proxy = redis.Redis.from_url(url, client_name=client_name)
        super().__init__()

    def wait_events(self, **kwargs) -> Iterator[EventType]:
        yield from self.poll_events(**kwargs)

    def get_events(self, job_id=None, **filters) -> Iterator[EventType]:
        is_equal_filter, post_filter = self.split_filter(**filters)

        if job_id:
            pattern = f"ewoks:{job_id}:*"
        else:
            pattern = "ewoks:*"
        keys = sorted(
            self._proxy.scan_iter(pattern), key=lambda x: int(x.decode().split(":")[-1])
        )
        for key in keys:
            event = self._proxy.hgetall(key)
            event = {k.decode(): json.loads(v) for k, v in event.items()}
            if not self.event_passes_filter(event, **post_filter) or any(
                event[k] != v for k, v in is_equal_filter.items()
            ):
                continue
            yield event
