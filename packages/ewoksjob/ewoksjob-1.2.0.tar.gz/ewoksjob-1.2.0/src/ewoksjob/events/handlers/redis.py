import os
import json
import socket
import logging
import redis
from typing import Dict, Optional, Tuple

from ewoksutils.logging_utils.connection import ConnectionHandler
from ewokscore.events.handlers import EwoksEventHandlerMixIn


RedisRecordType = Tuple[str, Dict[str, str]]


class RedisEwoksEventHandler(EwoksEventHandlerMixIn, ConnectionHandler):
    # TODO: https://redisql.redbeardlab.com/blog/python/using-redisql-with-python/

    def __init__(self, url: str, ttl=None):
        """An example url is "redis://localhost:10003?db=2"."""
        self._redis_url = url
        self._ttl = ttl
        super().__init__()

    def _connect(self, timeout=1) -> None:
        """This is called when no connection exists."""
        client_name = f"ewoks:writer:{socket.gethostname()}:{os.getpid()}"
        self._connection = redis.Redis.from_url(
            self._redis_url, client_name=client_name
        )

    def _disconnect(self) -> None:
        """This is called when a connection exists and is connected."""
        self._connection.close()

    def _serialize_record(self, record: logging.LogRecord) -> Optional[RedisRecordType]:
        """Convert a record to something that can be given to the connection."""
        job_id = getattr(record, "job_id", None)
        adict = dict()
        for field in self.FIELD_TYPES:
            value = getattr(record, field, None)
            adict[field] = json.dumps(value)
        return job_id, adict

    def _send_serialized_record(self, srecord: Optional[RedisRecordType]):
        """Send the output from `_serialize_record` to the connection."""
        if not srecord:
            return
        job_id, value = srecord
        n = self._connection.incrby("ewoks_events_count")
        key = f"ewoks:{job_id}:{n}"
        self._connection.hset(key, mapping=value)
        if self._ttl:
            self._connection.expire(key, self._ttl)
