import pytest
from app.intent import rule_based_fallback

def test_fallback_select_option():
    res = rule_based_fallback("book the first one")
    assert res.intent == "select_option"
    assert res.option_index == 1

    res2 = rule_based_fallback("option 3 please")
    assert res2.intent == "select_option"
    assert res2.option_index == 3

def test_fallback_confirm():
    res = rule_based_fallback("yes, proceed with booking and pay now")
    assert res.intent == "confirm"

def test_fallback_cancel():
    res = rule_based_fallback("cancel my booking please")
    assert res.intent == "cancel_booking"

def test_fallback_search():
    res = rule_based_fallback("find parking near Hitech City for 2 hours with EV charging")
    assert res.intent == "search"
    assert "ev_charging" in res.facilities
    assert res.duration_minutes == 120
    assert "Hitech City" in (res.location_text or "")
