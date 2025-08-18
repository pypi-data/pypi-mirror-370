# stroomer

Utilities for appliance inference and EV charging ETA (SoC-based).

## Usage

### Appliance inference
```python
from stroomer import StroomerPredictor

p = StroomerPredictor()
# daya per unit (W)
p.set_appliances({
    "Lampu": 10,
    "Kipas": 50,
    "TV": 100,
    "Kulkas": 150,
    "AC": 1000
})

# Opsional: batasi jumlah masuk akal (mis. lampu maksimal 20 unit)
p.set_max_counts({
    "Lampu": 20,
    "Kipas": 2,
    "TV": 2,
    "Kulkas": 2,
    "AC": 1
})

out = p.predict(power=180)  # misal terbaca 180 W total
print(out)
# Kemungkinan output:
# {
#   "on": {"Lampu": 3, "Kipas": 1},  # 3*10 + 1*50 = 80 W (contoh) -> akan dicari kombinasi terdekat ke 180
#   "target_power": 180.0,
#   "predicted_total": 180.0,
#   "relative_error": 0.0
# }
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

## Deploy
rm -rf dist/ build/
rm -rf src/stroomer.egg-info
python3.11 -m build
python3.11 -m twine upload dist/*
