import json
from pathlib import Path

import joblib
import pandas as pd
import math

MODELS_DIR = Path(__file__).parent / "models"

model = joblib.load(MODELS_DIR / "late_orders.joblib")
INFO = json.loads((MODELS_DIR / "model_info.json").read_text())

THRESHOLD = INFO["threshold"]
NUMERIC_FEATURES = INFO["numeric_features"]
CATEGORICAL_FEATURES = INFO["categorical_features"]

LIMITS = {
    "distance_km": (0.1, 30),
    "items": (1, 20),
    "hour": (10, 22),
    "prep_minutes": (1, 60),
    "courier_months": (0, 120),
}
CHOICES = {
    "weather": ["clear", "rain", "snow"],
    "day_type": ["weekday", "weekend"],
    "vehicle": ["bike", "scooter", "car"],
}
WHOLE_NUMBER_FIELDS = {"items", "hour"}

def check_order(order):
    """Raise ValueError naming the field and the rule if the order is not valid."""
    for field, (low, high) in LIMITS.items():
        value = order.get(field)
        if value is None:
            if field == "prep_minutes":
                continue
            raise ValueError(f"{field} is required.")
        if isinstance(value, bool) or not isinstance(value, (int, float)):
            raise ValueError(f"{field} must be a number.")
        if not math.isfinite(value):
            raise ValueError(f"{field} must be a finite number.")
        if field in WHOLE_NUMBER_FIELDS and value != int(value):
            raise ValueError(f"{field} must be a whole number.")
        if not low <= value <= high:
            raise ValueError(f"{field} must be between {low} and {high}.")
    for field, allowed in CHOICES.items():
        if order.get(field) not in allowed:
            raise ValueError(f"{field} must be one of: {', '.join(allowed)}.")