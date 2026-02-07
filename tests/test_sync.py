import json
from datetime import date, datetime
from unittest.mock import MagicMock, patch

from fitbit_garmin_sync.models import WeightEntry
from fitbit_garmin_sync.sync import run_sync


def _make_entry(log_id: str, weight: float, day: int = 15) -> WeightEntry:
    return WeightEntry(
        log_id=log_id,
        timestamp=datetime(2026, 1, day, 8, 0),
        weight_kg=weight,
    )


@patch("fitbit_garmin_sync.sync.save_state")
@patch("fitbit_garmin_sync.sync.load_state")
@patch("fitbit_garmin_sync.sync.fetch_weight_entries")
@patch("fitbit_garmin_sync.sync.upload_weight_entry")
def test_sync_uploads_new_entries(mock_upload, mock_fetch, mock_load_state, mock_save):
    mock_load_state.return_value = {"last_sync_date": None, "synced_log_ids": []}
    mock_fetch.return_value = [
        _make_entry("100", 75.0),
        _make_entry("101", 75.5, day=16),
    ]

    fitbit_client = MagicMock()
    garmin_client = MagicMock()

    run_sync(fitbit_client, garmin_client)

    assert mock_upload.call_count == 2


@patch("fitbit_garmin_sync.sync.save_state")
@patch("fitbit_garmin_sync.sync.load_state")
@patch("fitbit_garmin_sync.sync.fetch_weight_entries")
@patch("fitbit_garmin_sync.sync.upload_weight_entry")
def test_sync_skips_already_synced(mock_upload, mock_fetch, mock_load_state, mock_save):
    mock_load_state.return_value = {
        "last_sync_date": "2026-01-15",
        "synced_log_ids": ["100"],
    }
    mock_fetch.return_value = [
        _make_entry("100", 75.0),
        _make_entry("101", 75.5, day=16),
    ]

    fitbit_client = MagicMock()
    garmin_client = MagicMock()

    run_sync(fitbit_client, garmin_client)

    assert mock_upload.call_count == 1


@patch("fitbit_garmin_sync.sync.save_state")
@patch("fitbit_garmin_sync.sync.load_state")
@patch("fitbit_garmin_sync.sync.fetch_weight_entries")
@patch("fitbit_garmin_sync.sync.upload_weight_entry")
def test_dry_run_does_not_upload(mock_upload, mock_fetch, mock_load_state, mock_save):
    mock_load_state.return_value = {"last_sync_date": None, "synced_log_ids": []}
    mock_fetch.return_value = [_make_entry("100", 75.0)]

    fitbit_client = MagicMock()
    garmin_client = MagicMock()

    run_sync(fitbit_client, garmin_client, dry_run=True)

    mock_upload.assert_not_called()
    mock_save.assert_not_called()
