from datetime import datetime

from fitbit_garmin_sync.models import WeightEntry


def test_weight_entry_defaults():
    entry = WeightEntry(
        log_id="123",
        timestamp=datetime(2026, 1, 15, 8, 30),
        weight_kg=75.5,
    )
    assert entry.body_fat_pct is None
    assert entry.bmi is None
    assert entry.weight_kg == 75.5


def test_weight_entry_with_body_fat():
    entry = WeightEntry(
        log_id="456",
        timestamp=datetime(2026, 1, 15, 8, 30),
        weight_kg=75.5,
        body_fat_pct=18.2,
        bmi=24.1,
    )
    assert entry.body_fat_pct == 18.2
    assert entry.bmi == 24.1
