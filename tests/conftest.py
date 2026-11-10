import json
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parent.parent

VALID_ORDER = {
    "distance_km": 3.5,
    "items": 3,
    "hour": 13,
    "prep_minutes": 14.0,
    "courier_months": 12,
    "weather": "clear",
    "day_type": "weekday",
    "vehicle": "scooter",
}


@pytest.fixture
def valid_order():
    """A valid order. Each test gets its own copy, so none can change another's."""
    return dict(VALID_ORDER)


@pytest.fixture
def light_order(valid_order):
    """A clearly easy order: short, small, clear weather, experienced courier."""
    return {
        **valid_order,
        "distance_km": 1,
        "items": 1,
        "hour": 15,
        "courier_months": 59,
        "weather": "clear",
        "day_type": "weekday",
        "vehicle": "car",
    }


@pytest.fixture
def heavy_order(valid_order):
    """A clearly hard order: far, big, rush hour, snow, weekend, new courier."""
    return {
        **valid_order,
        "distance_km": 15,
        "items": 8,
        "hour": 19,
        "prep_minutes": 30,
        "courier_months": 0,
        "weather": "snow",
        "day_type": "weekend",
        "vehicle": "bike",
    }


@pytest.fixture
def required_fields():
    """Every field that must be present. prep_minutes is the only optional one."""
    return [
        "distance_km",
        "items",
        "hour",
        "courier_months",
        "weather",
        "day_type",
        "vehicle",
    ]


@pytest.fixture
def model_info():
    """What models/model_info.json says (the saved threshold, for one)."""
    return json.loads((ROOT / "models" / "model_info.json").read_text())
