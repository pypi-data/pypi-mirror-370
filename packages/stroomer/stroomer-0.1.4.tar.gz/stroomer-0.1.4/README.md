# stroomer

Utilities for **appliance inference** (menebak perangkat yang menyala dari V, I, PF, P) dan **EV charging ETA** (SoC-based).

- **Catalog built-in**: tiap perangkat punya `watt`, `pf`, `type`, `phase`, `standby_w`, `surge_mult`.
- **Prediksi multi-fitur**: cocokkan **P**, **I**, dan **PF** (bukan power saja).
- **Standby-aware**: total daya = standby seluruh unit + kontribusi aktif unit yang ON.
- **SoC ETA**: hitung durasi & waktu selesai charging berbasis SoC, kapasitas, efisiensi.

---

## Install

Dari PyPI:
```bash
pip install stroomer
```

(Opsional) Dari TestPyPI:
```bash
pip install -i https://test.pypi.org/simple --extra-index-url https://pypi.org/simple stroomer
```

---

## Usage

### 1) Appliance inference (catalog-based)

```python
from stroomer import StroomerPredictor

p = StroomerPredictor()

# Lihat daftar elektronik yang tersedia di catalog (nama → spec)
catalog = p.electronic_list()
# print(catalog)  # optional

# Beri JUMLAH MAKSIMAL unit yang mungkin ADA di lokasi (bukan watt per unit)
# Nama boleh alias/varian: "lampu_18W", "TV", "chrger_motor", dsb (akan dinormalkan)
p.set_appliances({
    "kipas": 5,
    "lampu_18W": 5,
    "lampu_32W": 5,
    "lampu": 3,
    "TV": 2,
    "Kulkas": 2,
    "AC": 1,
    "ev_charger": 1,
    "mesin_cuci": 1,
    "chrger_motor": 3,  # alias typo → otomatis dipetakan
})

# (Opsional) Override spesifikasi catalog untuk site tertentu
p.configure_catalog({
    "ev_charger": {"watt": 3200, "pf": 0.99},   # contoh: wallbox lebih besar
})

# Pembacaan meter saat ini
V  = 220
I  = 6
PF = 0.95
P  = 2301  # jika P real dari meter tersedia, berikan ini (diprioritaskan)

out = p.predict(voltage=V, current=I, power_factor=PF, power=P)

print("Perangkat ON :", out["on"])   # contoh: {"lampu_18w": 3, "kipas": 1, ...}
print("Target       :", out["target"])  # {"P":..., "I":..., "PF":..., "V":...}
print("Prediksi     :", out["pred"])    # {"P":..., "I":..., "PF":...}
print("Loss         :", out["loss"])
print("RelErr P     :", out["rel_error_P"])
```

> Catatan: Bila `V*I*PF` dan `P` tidak konsisten (sering terjadi pada meter berbeda), model **memprioritaskan P** sambil tetap menilai I & PF agar kombinasi lebih masuk akal.

---

### 2) EV Charging ETA (SoC-based)

```python
from stroomer import ChargingTimePredictor

eta = ChargingTimePredictor(capacity_kwh=50, target_soc=90, efficiency=0.92)
print(eta.predict(power=8000, SoC=30))
# -> {"FinishDuration":"03:14","FinishTime":"2025-08-18T13:25:00+00:00"}
```

---

## API Ringkas

### `StroomerPredictor`
- `electronic_list() -> dict`
  Katalog efektif (watt, pf, type, phase, standby_w, surge_mult).
- `configure_catalog(overrides: dict)`
  Override sebagian atribut katalog, mis. `{"ev_charger": {"watt": 3500, "pf": 0.99}}`.
- `set_appliances(counts: dict[str,int])`
  Daftarkan jumlah **maksimal** unit per perangkat di lokasi (nama fleksibel/alias).
- `predict(voltage=None, current=None, power_factor=None, power=None) -> dict`
  Mengembalikan:
  ```python
  {
    "on": {"nama": jumlah_on, ...},
    "target": {"P":..., "I":..., "PF":..., "V":...},
    "pred":   {"P":..., "I":..., "PF":...},
    "loss": float,              # skor gabungan (semakin kecil semakin baik)
    "rel_error_P": float        # |P_pred - P_meas| / P_meas
  }
  ```
- Atribut yang bisa dituning:
  - `weights = {"P": 0.6, "I": 0.3, "PF": 0.1}`
  - `tolerance = 0.08`  (pruning relatif di domain P)
  - `global_count_cap = 30` (batas hard per perangkat)

### `ChargingTimePredictor`
- `__init__(capacity_kwh, target_soc=90.0, efficiency=0.92)`
- `predict(power: W, SoC: %) -> {"FinishDuration": "HH:MM", "FinishTime": ISO8601_UTC}`

---

## Dev

```bash
pip install -U build twine pytest
pip install -e .
pytest -q
python -m build
```

---

## Deploy

1) **Bump versi** di `pyproject.toml`, mis. `version = "0.1.2"`  
## Deploy

```bash
rm -rf dist/ build/
```

```bash
rm -rf src/stroomer.egg-info
```

```bash
python3.11 -m build
```

```bash
python3.11 -m twine upload -r testpypi dist/*
```

or

```bash
python3.11 -m twine upload dist/*
```

> Pastikan `~/.pypirc` sudah diset (`username=__token__`, `password=pypi-...`).

---

## Catatan Akurasi

- **PF tipikal** di katalog adalah nilai rata-rata umum; silakan sesuaikan per lokasi melalui `configure_catalog`.
- **Standby** dihitung otomatis sebagai baseline; kontribusi aktif = `watt - standby_w`.
- Sensor/metode pengukuran berbeda bisa membuat **P** dan **V·I·PF** tidak identik—model tetap memadukan ketiganya (dengan bobot).

---

## License

MIT
