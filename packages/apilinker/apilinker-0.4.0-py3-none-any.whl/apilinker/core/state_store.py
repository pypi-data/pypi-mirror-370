"""
State store for resumability.

Provides a pluggable interface and a default file-backed implementation
to persist last sync cursors, checkpoints, and DLQ pointers.
"""

from __future__ import annotations

import json
import threading
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, Optional, cast


def now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


class StateStore:
    def get_last_sync(
        self, endpoint_name: str
    ) -> Optional[str]:  # pragma: no cover - interface
        raise NotImplementedError

    def set_last_sync(
        self, endpoint_name: str, iso_timestamp: str
    ) -> None:  # pragma: no cover - interface
        raise NotImplementedError

    def get_checkpoint(
        self, name: str
    ) -> Optional[Dict[str, Any]]:  # pragma: no cover - interface
        raise NotImplementedError

    def set_checkpoint(
        self, name: str, data: Dict[str, Any]
    ) -> None:  # pragma: no cover - interface
        raise NotImplementedError

    def get_dlq_pointer(self) -> Optional[str]:  # pragma: no cover - interface
        raise NotImplementedError

    def set_dlq_pointer(self, pointer: str) -> None:  # pragma: no cover - interface
        raise NotImplementedError

    # Convenience APIs for introspection and maintenance
    def list_last_sync(self) -> Dict[str, str]:  # pragma: no cover - interface
        raise NotImplementedError

    def list_checkpoints(self) -> Dict[str, Any]:  # pragma: no cover - interface
        raise NotImplementedError

    def reset(self) -> None:  # pragma: no cover - interface
        raise NotImplementedError


class FileStateStore(StateStore):
    def __init__(
        self, file_path: str, *, default_last_sync: Optional[str] = None
    ) -> None:
        self.file = Path(file_path)
        self.default_last_sync = default_last_sync
        self._lock = threading.Lock()
        self._data: Dict[str, Any] = {"last_sync": {}, "checkpoints": {}, "dlq": {}}
        self._load()

    def _load(self) -> None:
        if self.file.exists():
            try:
                self._data = json.loads(self.file.read_text(encoding="utf-8"))
            except Exception:
                # Keep empty data on failure
                self._data = {"last_sync": {}, "checkpoints": {}, "dlq": {}}

    def _save(self) -> None:
        self.file.parent.mkdir(parents=True, exist_ok=True)
        with self._lock:
            self.file.write_text(json.dumps(self._data, indent=2), encoding="utf-8")

    def get_last_sync(self, endpoint_name: str) -> Optional[str]:
        return (
            self._data.get("last_sync", {}).get(endpoint_name) or self.default_last_sync
        )

    def set_last_sync(self, endpoint_name: str, iso_timestamp: str) -> None:
        self._data.setdefault("last_sync", {})[endpoint_name] = iso_timestamp
        self._save()

    def get_checkpoint(self, name: str) -> Optional[Dict[str, Any]]:
        value: Any = self._data.get("checkpoints", {}).get(name)
        return cast(Optional[Dict[str, Any]], value)

    def set_checkpoint(self, name: str, data: Dict[str, Any]) -> None:
        self._data.setdefault("checkpoints", {})[name] = data
        self._save()

    def get_dlq_pointer(self) -> Optional[str]:
        value: Any = self._data.get("dlq", {}).get("pointer")
        return cast(Optional[str], value)

    def set_dlq_pointer(self, pointer: str) -> None:
        self._data.setdefault("dlq", {})["pointer"] = pointer
        self._save()

    def list_last_sync(self) -> Dict[str, str]:
        return dict(self._data.get("last_sync", {}))

    def list_checkpoints(self) -> Dict[str, Any]:
        return dict(self._data.get("checkpoints", {}))

    def reset(self) -> None:
        self._data = {"last_sync": {}, "checkpoints": {}, "dlq": {}}
        self._save()


# Optional SQLite-backed state store
class SQLiteStateStore(StateStore):
    def __init__(
        self, db_path: str, *, default_last_sync: Optional[str] = None
    ) -> None:
        import sqlite3  # lazy import

        self._sqlite3 = sqlite3
        self.db_path = db_path
        self.default_last_sync = default_last_sync
        self._init_db()

    def _conn(self):
        return self._sqlite3.connect(self.db_path)

    def _init_db(self) -> None:
        with self._conn() as conn:
            cur = conn.cursor()
            cur.execute(
                "CREATE TABLE IF NOT EXISTS last_sync (endpoint TEXT PRIMARY KEY, iso TEXT)"
            )
            cur.execute(
                "CREATE TABLE IF NOT EXISTS checkpoints (name TEXT PRIMARY KEY, data TEXT)"
            )
            cur.execute(
                "CREATE TABLE IF NOT EXISTS dlq (id INTEGER PRIMARY KEY CHECK(id=1), pointer TEXT)"
            )
            conn.commit()

    def get_last_sync(self, endpoint_name: str) -> Optional[str]:
        with self._conn() as conn:
            cur = conn.cursor()
            cur.execute("SELECT iso FROM last_sync WHERE endpoint=?", (endpoint_name,))
            row = cur.fetchone()
            return row[0] if row else self.default_last_sync

    def set_last_sync(self, endpoint_name: str, iso_timestamp: str) -> None:
        with self._conn() as conn:
            cur = conn.cursor()
            cur.execute(
                "INSERT INTO last_sync(endpoint, iso) VALUES(?, ?) ON CONFLICT(endpoint) DO UPDATE SET iso=excluded.iso",
                (endpoint_name, iso_timestamp),
            )
            conn.commit()

    def get_checkpoint(self, name: str) -> Optional[Dict[str, Any]]:
        with self._conn() as conn:
            cur = conn.cursor()
            cur.execute("SELECT data FROM checkpoints WHERE name=?", (name,))
            row = cur.fetchone()
            if not row:
                return None
            try:
                data = json.loads(row[0])
                return cast(Optional[Dict[str, Any]], data)
            except Exception:
                return None

    def set_checkpoint(self, name: str, data: Dict[str, Any]) -> None:
        with self._conn() as conn:
            cur = conn.cursor()
            cur.execute(
                "INSERT INTO checkpoints(name, data) VALUES(?, ?) ON CONFLICT(name) DO UPDATE SET data=excluded.data",
                (name, json.dumps(data)),
            )
            conn.commit()

    def get_dlq_pointer(self) -> Optional[str]:
        with self._conn() as conn:
            cur = conn.cursor()
            cur.execute("SELECT pointer FROM dlq WHERE id=1")
            row = cur.fetchone()
            return cast(Optional[str], row[0] if row else None)

    def set_dlq_pointer(self, pointer: str) -> None:
        with self._conn() as conn:
            cur = conn.cursor()
            cur.execute(
                "INSERT INTO dlq(id, pointer) VALUES(1, ?) ON CONFLICT(id) DO UPDATE SET pointer=excluded.pointer",
                (pointer,),
            )
            conn.commit()

    def list_last_sync(self) -> Dict[str, str]:
        with self._conn() as conn:
            cur = conn.cursor()
            cur.execute("SELECT endpoint, iso FROM last_sync")
            return {row[0]: row[1] for row in cur.fetchall()}

    def list_checkpoints(self) -> Dict[str, Any]:
        with self._conn() as conn:
            cur = conn.cursor()
            cur.execute("SELECT name, data FROM checkpoints")
            out: Dict[str, Any] = {}
            for name, data in cur.fetchall():
                try:
                    out[name] = json.loads(data)
                except Exception:
                    out[name] = None
            return out

    def reset(self) -> None:
        with self._conn() as conn:
            cur = conn.cursor()
            cur.execute("DELETE FROM last_sync")
            cur.execute("DELETE FROM checkpoints")
            cur.execute("DELETE FROM dlq")
            conn.commit()
