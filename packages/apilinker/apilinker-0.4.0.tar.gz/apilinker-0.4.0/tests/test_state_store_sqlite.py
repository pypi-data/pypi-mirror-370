import json

from apilinker.core.state_store import SQLiteStateStore


def test_sqlite_state_store_roundtrip(tmp_path):
    db = tmp_path / "state.db"
    store = SQLiteStateStore(str(db), default_last_sync="1970-01-01T00:00:00+00:00")

    # defaults when empty
    assert store.get_last_sync("endpoint") == "1970-01-01T00:00:00+00:00"
    assert store.get_checkpoint("cp") is None
    assert store.get_dlq_pointer() is None

    # set last sync
    store.set_last_sync("endpoint", "2025-01-01T00:00:00+00:00")
    assert store.get_last_sync("endpoint") == "2025-01-01T00:00:00+00:00"

    # checkpoint
    store.set_checkpoint("cp", {"a": 1})
    assert store.get_checkpoint("cp") == {"a": 1}

    # dlq pointer
    store.set_dlq_pointer("ptr")
    assert store.get_dlq_pointer() == "ptr"

    # listings
    ls = store.list_last_sync()
    cps = store.list_checkpoints()
    assert ls["endpoint"].startswith("2025")
    assert cps["cp"]["a"] == 1

    # reset
    store.reset()
    assert store.list_last_sync() == {}
    assert store.list_checkpoints() == {}
    assert store.get_dlq_pointer() is None
