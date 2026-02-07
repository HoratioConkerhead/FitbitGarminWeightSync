from __future__ import annotations

import time
from datetime import datetime

from garminconnect import Garmin, GarminConnectAuthenticationError
from garth.exc import GarthHTTPError
from requests.exceptions import ReadTimeout

from .config import ensure_data_dir
from .models import WeightEntry

MAX_RETRIES = 3
RETRY_DELAY = 10  # seconds, multiplied by attempt number
UPLOAD_DELAY = 1  # seconds between uploads to avoid hammering the API

TOKENSTORE_DIR = "garmin_tokens"


def _tokenstore_path() -> str:
    return str(ensure_data_dir() / TOKENSTORE_DIR)


def get_garmin_client(email: str, password: str) -> Garmin:
    tokenstore = _tokenstore_path()

    # Try loading saved tokens first
    try:
        client = Garmin(email=email, password=password)
        client.login(tokenstore)
        print("Garmin login successful (using saved tokens).")
        return client
    except (FileNotFoundError, GarthHTTPError, GarminConnectAuthenticationError):
        pass

    # Fresh login with credentials (prompt_mfa handles MFA-enabled accounts)
    def _prompt_mfa() -> str:
        return input("Enter the MFA code sent to your email: ").strip()

    client = Garmin(email=email, password=password, prompt_mfa=_prompt_mfa)
    client.login()

    # Save tokens for future runs
    client.garth.dump(tokenstore)
    print("Garmin login successful. Tokens saved.")
    return client


def upload_weight_entry(client: Garmin, entry: WeightEntry) -> None:
    ts = entry.timestamp.isoformat()
    for attempt in range(1, MAX_RETRIES + 1):
        try:
            if entry.body_fat_pct is not None:
                client.add_body_composition(
                    timestamp=ts,
                    weight=entry.weight_kg,
                    percent_fat=entry.body_fat_pct,
                    percent_hydration=None,
                    visceral_fat_mass=None,
                    bone_mass=None,
                    muscle_mass=None,
                    basal_met=None,
                    active_met=None,
                    physique_rating=None,
                    metabolic_age=None,
                    visceral_fat_rating=None,
                    bmi=entry.bmi,
                )
            else:
                client.add_weigh_in(
                    weight=entry.weight_kg,
                    unitKey="kg",
                    timestamp=ts,
                )
            time.sleep(UPLOAD_DELAY)
            return
        except (ReadTimeout, ConnectionError, OSError) as e:
            if attempt < MAX_RETRIES:
                wait = RETRY_DELAY * attempt
                print(f"    Timeout, retrying in {wait}s ({attempt}/{MAX_RETRIES})...")
                time.sleep(wait)
            else:
                raise SystemExit(
                    f"Failed to upload after {MAX_RETRIES} retries: {e}"
                )
