from __future__ import annotations

from datetime import datetime

from garminconnect import Garmin

from .models import WeightEntry


def get_garmin_client(email: str, password: str) -> Garmin:
    client = Garmin(email, password)
    client.login()
    return client


def upload_weight_entry(client: Garmin, entry: WeightEntry) -> None:
    ts = entry.timestamp.isoformat()
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
