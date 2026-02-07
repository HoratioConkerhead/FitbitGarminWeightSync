from __future__ import annotations

import os
from pathlib import Path

from dotenv import load_dotenv


DATA_DIR = Path.home() / ".fitbit_garmin_sync"


def load_config() -> dict[str, str]:
    load_dotenv()
    config = {
        "fitbit_client_id": os.environ.get("FITBIT_CLIENT_ID", ""),
        "fitbit_client_secret": os.environ.get("FITBIT_CLIENT_SECRET", ""),
        "garmin_email": os.environ.get("GARMIN_EMAIL", ""),
        "garmin_password": os.environ.get("GARMIN_PASSWORD", ""),
    }
    missing = [k for k, v in config.items() if not v]
    if missing:
        raise SystemExit(
            f"Missing required config: {', '.join(missing)}\n"
            "Set them in .env or as environment variables."
        )
    return config


def ensure_data_dir() -> Path:
    DATA_DIR.mkdir(parents=True, exist_ok=True)
    return DATA_DIR
