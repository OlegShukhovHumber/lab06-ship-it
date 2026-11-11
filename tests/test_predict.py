"""Tests for predict.py: the probability, the voucher decision and the checks."""

import importlib

import joblib
import pytest

import predict


def test_probability_is_between_0_and_1(valid_order):
    result = predict.predict_order(valid_order)
    assert 0 <= result["probability"] <= 1


def test_heavy_order_scores_higher_than_light_order(light_order, heavy_order):
    light_probability = predict.predict_order(light_order)["probability"]
    heavy_probability = predict.predict_order(heavy_order)["probability"]
    assert heavy_probability > light_probability


def test_voucher_offered_exactly_at_the_threshold():
    # Worked out by hand for a threshold of 0.30: 0.30 -> voucher.
    assert predict.decide_voucher(predict.THRESHOLD, predict.THRESHOLD)


def test_voucher_not_offered_just_below_the_threshold():
    # 0.29 -> no voucher.
    assert not predict.decide_voucher(predict.THRESHOLD - 0.01, predict.THRESHOLD)


def test_voucher_offered_just_above_the_threshold():
    # 0.31 -> voucher.
    assert predict.decide_voucher(predict.THRESHOLD + 0.01, predict.THRESHOLD)


def test_decision_uses_threshold_from_model_info(valid_order, model_info, monkeypatch):
    assert predict.THRESHOLD == model_info["threshold"]
    result = predict.predict_order(valid_order)
    assert result["threshold"] == model_info["threshold"]
    monkeypatch.setattr(predict, "THRESHOLD", 0.0)
    assert predict.predict_order(valid_order)["voucher"]
    monkeypatch.setattr(predict, "THRESHOLD", 1.0)
    assert not predict.predict_order(valid_order)["voucher"]


def test_predict_order_returns_probability_voucher_and_threshold(valid_order):
    result = predict.predict_order(valid_order)
    assert {"probability", "voucher", "threshold"} <= set(result)
    expected = predict.decide_voucher(result["probability"], result["threshold"])
    assert result["voucher"] == expected


def test_empty_prep_minutes_is_accepted(valid_order):
    valid_order["prep_minutes"] = None
    result = predict.predict_order(valid_order)
    assert 0 <= result["probability"] <= 1


@pytest.mark.parametrize(
    ("field", "bad_value"),
    [
        ("distance_km", 0),
        ("distance_km", 31),
        ("items", 0),
        ("items", 21),
        ("items", 2.5),
        ("hour", 9),
        ("hour", 23),
        ("prep_minutes", 0),
        ("prep_minutes", 61),
        ("courier_months", -1),
        ("courier_months", 121),
    ],
)
def test_impossible_number_is_rejected_and_names_the_field(
    valid_order, field, bad_value
):
    valid_order[field] = bad_value
    with pytest.raises(ValueError, match=field):
        predict.check_order(valid_order)


@pytest.mark.parametrize(
    ("field", "bad_value"),
    [("weather", "Snow"), ("weather", "hail"), ("vehicle", "truck")],
)
def test_unknown_category_is_rejected_and_names_the_field(
    valid_order, field, bad_value
):
    valid_order[field] = bad_value
    # predict_order calls check_order first, so the error reaches the caller.
    with pytest.raises(ValueError, match=field):
        predict.predict_order(valid_order)


def test_missing_required_field_is_rejected(valid_order, required_fields):
    for field in required_fields:
        order = {key: value for key, value in valid_order.items() if key != field}
        with pytest.raises(ValueError, match=field):
            predict.check_order(order)


def test_the_limits_themselves_are_accepted(valid_order):
    for field, (low, high) in predict.LIMITS.items():
        for value in (low, high):
            order = {**valid_order, field: value}
            assert predict.check_order(order) is None


def test_whole_numbers_sent_as_floats_are_accepted(valid_order):
    order = {**valid_order, "items": 5.0, "hour": 13.0}
    assert predict.check_order(order) is None


def test_model_is_loaded_only_once(valid_order, monkeypatch):
    calls = []
    real_load = joblib.load

    def counting_load(*args, **kwargs):
        calls.append(args)
        return real_load(*args, **kwargs)

    monkeypatch.setattr(joblib, "load", counting_load)
    importlib.reload(predict)
    predict.predict_order(valid_order)
    predict.predict_order(valid_order)
    assert len(calls) == 1
