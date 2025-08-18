from stroomer import ChargingTimePredictor

def test_simple_eta():
    p = ChargingTimePredictor(capacity_kwh=50, target_soc=90, efficiency=0.92)
    out = p.predict(power=8000, SoC=30)
    assert "FinishDuration" in out and "FinishTime" in out
