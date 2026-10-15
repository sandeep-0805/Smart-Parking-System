import pytest
from app.schemas.rank import CandidateSlot
from app.rank import rank_candidates, min_max_normalize, min_max_normalize_inverted

def test_min_max_normalize():
    assert min_max_normalize([10, 20, 30]) == [0.0, 0.5, 1.0]
    assert min_max_normalize([5, 5, 5]) == [1.0, 1.0, 1.0]
    assert min_max_normalize([]) == []

def test_min_max_normalize_inverted():
    assert min_max_normalize_inverted([10, 20, 30]) == [1.0, 0.5, 0.0]
    assert min_max_normalize_inverted([5, 5, 5]) == [1.0, 1.0, 1.0]

def test_rank_candidates_ordering():
    c1 = CandidateSlot(
        slot_id=1,
        location_id=10,
        location_name="Lot A",
        distance_m=100.0,
        total_price_paise=2000,
        facilities=["ev_charging", "covered"],
        availability_confidence=1.0,
    )
    c2 = CandidateSlot(
        slot_id=2,
        location_id=10,
        location_name="Lot B",
        distance_m=500.0,
        total_price_paise=5000,
        facilities=[],
        availability_confidence=0.5,
    )

    ranked = rank_candidates(
        candidates=[c1, c2],
        preferences={"preferred_facilities": ["ev_charging"]},
        weights={"distance": 0.35, "price": 0.30, "availability": 0.15, "facilities": 0.20},
    )

    assert len(ranked) == 2
    # c1 is closer, cheaper, higher availability, has preferred facility -> must score higher than c2
    assert ranked[0].slot_id == 1
    assert ranked[0].score > ranked[1].score
    assert "Closest option" in ranked[0].reason_tags
    assert "Lowest total price" in ranked[0].reason_tags
    assert "Has EV charging" in ranked[0].reason_tags

def test_rank_empty():
    assert rank_candidates([], {}, {}) == []
