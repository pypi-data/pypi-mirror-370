import sqlite3
from typing import Iterator
from ewoksutils.event_utils import FIELD_TYPES
from ewoksutils import sqlite3_utils
from .base import EwoksEventReader, EventType


class Sqlite3EwoksEventReader(EwoksEventReader):
    def __init__(self, uri: str, **_) -> None:
        super().__init__()
        self._uri = uri
        self.__connection = None
        self.__sql_types = sqlite3_utils.python_to_sql_types(FIELD_TYPES)

    def close(self):
        if self.__connection is not None:
            self.__connection.close()
            self.__connection = None
        super().close()

    @property
    def _connection(self):
        if self.__connection is None:
            self.__connection = sqlite3.connect(self._uri, uri=True)
        return self.__connection

    def wait_events(self, **kwargs) -> Iterator[EventType]:
        yield from self.poll_events(**kwargs)

    def get_events(self, **filters) -> Iterator[EventType]:
        yield from sqlite3_utils.select(
            self._connection,
            "ewoks_events",
            field_types=FIELD_TYPES,
            sql_types=self.__sql_types,
            **filters,
        )
