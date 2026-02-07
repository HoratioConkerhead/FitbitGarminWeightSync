from __future__ import annotations

import json
from datetime import date
from pathlib import Path

from .config import DATA_DIR


STATE_FILE = DATA_DIR / "state.json"


def load_state() -> dict:
    if STATE_FILE.exists():
        return json.loads(STATE_FILE.read_text())
    return {"last_sync_date": None, "synced_log_ids": []}


def save_state(last_sync_date: date, synced_log_ids: list[str]) -> None:
    STATE_FILE.parent.mkdir(parents=True, exist_ok=True)
    state = {
        "last_sync_date": last_sync_date.isoformat(),
        "synced_log_ids": synced_log_ids,
    }
    STATE_FILE.write_text(json.dumps(state, indent=2))


def reset_state() -> None:
    if STATE_FILE.exists():
        STATE_FILE.unlink()
    print("Sync state cleared.")
