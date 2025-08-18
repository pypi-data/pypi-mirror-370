# stroomer

Utilities for appliance inference and EV charging ETA (SoC-based).

## Usage

### Appliance inference
```python
from stroomer import StroomerPredictor
p = StroomerPredictor()
p.set_appliances({"Lampu":10, "Kipas":50, "TV":100, "Kulkas":150, "AC":1000})
print(p.predict(voltage=220, current=6, power_factor=0.9, power=1200))
# -> {"AC": 0.8, "Kulkas": 0.2}
```

### Charging ETA (SoC-based)
```python
from stroomer import ChargingTimePredictor
eta = ChargingTimePredictor(capacity_kwh=50, target_soc=90, efficiency=0.92)
print(eta.predict(power=8000, SoC=30))
# -> {"FinishDuration":"03:14","FinishTime":"2025-08-18T13:25:00+00:00"}
```

## Dev
```
pip install -U build twine pytest
pip install -e .
pytest -q
python -m build
```
