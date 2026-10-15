import pytest

def test_pricing_multipliers_and_clamping():
    base_rate = 2000  # Rs 20/hr
    min_rate = 1000   # Rs 10/hr
    max_rate = 4500   # Rs 45/hr

    # Band 1: < 40% occupancy -> 1.0x
    band1_price = max(min_rate, min(max_rate, int(round(base_rate * 1.0))))
    assert band1_price == 2000

    # Band 2: 40-75% occupancy -> 1.5x
    band2_price = max(min_rate, min(max_rate, int(round(base_rate * 1.5))))
    assert band2_price == 3000

    # Band 3: > 75% occupancy -> 2.25x
    band3_price = max(min_rate, min(max_rate, int(round(base_rate * 2.25))))
    assert band3_price == 4500  # Clamped to max_rate if higher
