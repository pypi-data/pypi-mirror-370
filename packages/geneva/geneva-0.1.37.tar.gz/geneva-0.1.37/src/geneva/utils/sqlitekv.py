# SPDX-License-Identifier: Apache-2.0
# SPDX-FileCopyrightText: Copyright The Geneva Authors

# An dict backed by sqlite3

import functools
import logging
import sqlite3
from collections.abc import Callable, Iterator, MutableMapping
from pathlib import Path
from typing import TypeVar

import attrs

_LOG = logging.getLogger(__name__)


T = TypeVar("T")


@attrs.define
class SQLiteKV(MutableMapping[str, str]):
    """An dict backed by sqlite3"""

    # Path to the sqlite3 database
    db_path: Path = attrs.field(converter=lambda x: Path(x).expanduser().resolve())

    _conn: sqlite3.Connection = attrs.field(init=False)

    def __attrs_post_init__(self) -> None:
        if not self.db_path.exists():
            _LOG.info("Creating sqlite3 database at %s", self.db_path)
            self.db_path.parent.mkdir(parents=True, exist_ok=True)

        self._conn = sqlite3.connect(
            self.db_path,
        )
        self._conn.execute(
            """
            CREATE TABLE IF NOT EXISTS kv (
                key TEXT PRIMARY KEY,
                value TEXT
            )
            """,
        )
        self._conn.commit()

    @staticmethod
    def _tx_safe(func: Callable[..., T]) -> Callable[..., T]:
        @functools.wraps(func)
        def wrapper(self: "SQLiteKV", *args, **kwargs) -> T:
            self._conn.execute("BEGIN")
            try:
                result = func(self, *args, **kwargs)
                self._conn.commit()
                return result
            except Exception:
                self._conn.rollback()
                raise

        return wrapper

    def close(self) -> None:
        self._conn.close()

    def __getitem__(self, key: str) -> str:
        cursor = self._conn.cursor()
        cursor.execute("SELECT value FROM kv WHERE key=?", (key,))
        result = cursor.fetchone()
        if result is None:
            raise KeyError(key)
        return result[0]

    @_tx_safe
    def __setitem__(self, key: str, value: str) -> None:
        self._conn.execute(
            "INSERT OR REPLACE INTO kv (key, value) VALUES (?, ?)",
            (key, value),
        )

    @_tx_safe
    def __delitem__(self, key: str) -> None:
        self._conn.execute("DELETE FROM kv WHERE key=?", (key,))

    def __iter__(self) -> Iterator[str]:
        cursor = self._conn.cursor()
        cursor.execute("SELECT key FROM kv")
        for row in cursor:
            yield row[0]

    def __len__(self) -> int:
        cursor = self._conn.cursor()
        cursor.execute("SELECT COUNT(*) FROM kv")
        return cursor.fetchone()[0]

    def __contains__(self, key: object) -> bool:
        if not isinstance(key, str):
            return False
        cursor = self._conn.cursor()
        cursor.execute("SELECT 1 FROM kv WHERE key=?", (key,))
        return cursor.fetchone() is not None
