from __future__ import annotations

from datetime import date

import fitbit as fitbit_lib
from garminconnect import Garmin

from .fitbit_client import fetch_weight_entries
from .garmin_client import upload_weight_entry
from .models import WeightEntry
from .state import load_state, save_state


def run_sync(
    fitbit_client: fitbit_lib.Fitbit,
    garmin_client: Garmin,
    start_date: date | None = None,
    end_date: date | None = None,
    dry_run: bool = False,
) -> None:
    today = date.today()
    state = load_state()
    use_state = start_date is None and end_date is None

    if use_state:
        last = state.get("last_sync_date")
        start_date = date.fromisoformat(last) if last else today
        end_date = today

    synced_ids = set(state.get("synced_log_ids", []))

    print(f"Fetching Fitbit weight data from {start_date} to {end_date}...")
    entries = fetch_weight_entries(fitbit_client, start_date, end_date)

    if not entries:
        print("No weight entries found on Fitbit for this period.")
        return

    new_entries = [e for e in entries if e.log_id not in synced_ids]

    if not new_entries:
        print(f"Found {len(entries)} entries, all already synced.")
        return

    print(f"Found {len(new_entries)} new entries to sync ({len(entries) - len(new_entries)} already synced).")

    for entry in new_entries:
        label = f"  {entry.timestamp.strftime('%Y-%m-%d %H:%M')} — {entry.weight_kg} kg"
        if entry.body_fat_pct is not None:
            label += f", {entry.body_fat_pct}% fat"

        if dry_run:
            print(f"  [DRY RUN] Would sync: {label}")
        else:
            upload_weight_entry(garmin_client, entry)
            synced_ids.add(entry.log_id)
            print(f"  Synced: {label}")

    if not dry_run and use_state:
        save_state(today, list(synced_ids))

    action = "Would sync" if dry_run else "Synced"
    print(f"\n{action} {len(new_entries)} entries.")
