import pytest
from datetime import datetime, timezone
from app.forecast import ForecastModelManager

@pytest.mark.asyncio
async def test_forecast_training_and_predict(tmp_path):
    mgr = ForecastModelManager(model_dir=str(tmp_path))
    
    # Generate 60 synthetic records for location 1
    sample_records = []
    base_ts = datetime(2026, 10, 1, 8, 0, tzinfo=timezone.utc)
    for i in range(80):
        sample_records.append({
            "location_id": 1,
            "ts": datetime.fromtimestamp(base_ts.timestamp() + i * 300, tz=timezone.utc).isoformat(),
            "total_slots": 50,
            "occupied": 20 + (i % 15),
            "available": 30 - (i % 15),
            "synthetic": 1,
        })

    train_res = await mgr.train_on_data(sample_records)
    assert "version" in train_res
    assert "1" in train_res["metrics"]
    assert train_res["metrics"]["1"]["train_samples"] > 0

    pred = mgr.predict(
        location_id=1,
        target_time_str="2026-10-15T10:00:00Z",
        current_occ_pct=0.45,
        total_slots=50,
    )
    assert pred["location_id"] == 1
    assert 0 <= pred["predicted_available"] <= 50
    assert 0.0 <= pred["occupancy_pct"] <= 1.0
    assert pred["is_estimate"] is True
