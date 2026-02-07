from dataclasses import dataclass
from datetime import datetime


@dataclass
class WeightEntry:
    log_id: str
    timestamp: datetime
    weight_kg: float
    body_fat_pct: float | None = None
    bmi: float | None = None
