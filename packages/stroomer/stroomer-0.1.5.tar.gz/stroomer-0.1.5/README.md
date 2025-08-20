# stroomer

<p align="center">
  <img src="https://stroomer.co.id/images/logo/logo-stroom.png" alt="Stroomer" width="240"/>
</p>

<p align="center">
  <a href="https://pypi.org/project/stroomer/">
    <img src="https://img.shields.io/pypi/v/stroomer.svg" alt="PyPI">
  </a>
  <a href="https://pepy.tech/project/stroomer">
    <img src="https://static.pepy.tech/badge/stroomer" alt="Downloads">
  </a>
  <a href="https://pypi.org/project/stroomer/">
    <img src="https://img.shields.io/pypi/pyversions/stroomer.svg" alt="Python versions">
  </a>
  <a href="https://github.com/foldadjo/stroomer/blob/main/LICENSE">
    <img src="https://img.shields.io/badge/license-MIT-blue.svg" alt="License">
  </a>
  <a href="https://github.com/foldadjo/stroomer">
    <img src="https://img.shields.io/badge/types-typed-brightgreen.svg" alt="types: typed">
  </a>
  <a href="https://github.com/foldadjo/stroomer/issues/new?labels=question">
    <img src="https://img.shields.io/badge/stackoverflow-Ask%20questions-ef8236.svg" alt="Ask questions">
  </a>
</p>

NumPy-style quick links:

- **Website:** <https://stroomer.co.id>
- **Documentation:** <https://github.com/foldadjo/stroomer#readme>
- **PyPI:** <https://pypi.org/project/stroomer/>
- **Source code:** <https://github.com/foldadjo/stroomer>
- **Contributing:** <https://github.com/foldadjo/stroomer#kontribusi>
- **Bug reports:** <https://github.com/foldadjo/stroomer/issues>
- **Report a security vulnerability:** <https://github.com/foldadjo/stroomer/security/advisories/new>

---

Utilities untuk **appliance inference** (menebak perangkat yang menyala dari V, I, PF, P) dan **EV charging ETA** (berbasis SoC).

- **Catalog built-in**: tiap perangkat punya `watt`, `pf`, `type`, `phase`, `standby_w`, `surge_mult`.
- **Prediksi multi-fitur**: cocokkan **P**, **I**, **PF** (bukan power saja).
- **Standby-aware**: total daya = *standby* seluruh unit + kontribusi aktif unit ON.
- **SoC ETA**: prediksi durasi & waktu selesai charging berbasis kapasitas, target SoC, efisiensi.

Repo: **<https://github.com/foldadjo/stroomer>**

---

## Tabel Isi

- [Install](#install)
- [Quickstart](#quickstart)
  - [Appliance inference](#appliance-inference)
  - [EV charging ETA](#ev-charging-eta)
- [API Ringkas](#api-ringkas)
- [Konfigurasi & Tuning](#konfigurasi--tuning)
- [Catatan Akurasi](#catatan-akurasi)
- [Kontribusi](#kontribusi)
- [Lisensi](#lisensi)

---

## Install

Dari **PyPI**:

```bash
pip install stroomer
```

(Opsional) Dari **TestPyPI**:

```bash
pip install -i https://test.pypi.org/simple --extra-index-url https://pypi.org/simple stroomer
```

> Disarankan Python 3.9+.

---

## Quickstart

### Appliance inference

```python
from stroomer import StroomerPredictor

p = StroomerPredictor()

# Lihat daftar elektronik di katalog (nama → spesifikasi)
catalog = p.electronic_list()
# print(catalog)

# Daftarkan JUMLAH MAKSIMAL unit yang mungkin ADA (nama fleksibel/alias)
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

# (Opsional) Sesuaikan katalog untuk site tertentu
p.configure_catalog({
    "ev_charger": {"watt": 3200, "pf": 0.99},
})

# Snapshot meter
V, I, PF, P = 220, 6, 0.95, 2301  # jika P real tersedia, berikan (diprioritaskan)

out = p.predict(voltage=V, current=I, power_factor=PF, power=P)

print("Perangkat ON :", out["on"])        # contoh: {"lampu_18w": 3, "kipas_berdiri": 1}
print("Target       :", out["target"])     # {"P":..., "I":..., "PF":..., "V":...}
print("Prediksi     :", out["pred"])       # {"P":..., "I":..., "PF":...}
print("Loss         :", out["loss"])       # skor gabungan (semakin kecil semakin baik)
print("RelErr P     :", out["rel_error_P"])
```

> Jika `V*I*PF` dan `P` tidak konsisten (lumrah antar meter), model **memprioritaskan P** sambil tetap menilai I & PF untuk kombinasi yang masuk akal.

---

### EV charging ETA

```python
from stroomer import ChargingTimePredictor

eta = ChargingTimePredictor(
    capacity_kwh=50,  # kapasitas baterai
    target_soc=90,    # target SoC (%)
    efficiency=0.92   # efisiensi pengisian
)

result = eta.predict(power=8000, SoC=30)
print(result)
# -> {"FinishDuration":"03:14","FinishTime":"2025-08-18T13:25:00+00:00"}
```

---

## API Ringkas

### `StroomerPredictor`

- `electronic_list() -> dict`  
  Katalog efektif (watt, pf, type, phase, standby_w, surge_mult).

- `configure_catalog(overrides: dict)`  
  Override sebagian atribut, mis. `{"ev_charger": {"watt": 3500, "pf": 0.99}}`.

- `set_appliances(counts: dict[str,int])`  
  Daftarkan jumlah **maksimal** unit per perangkat di lokasi (nama fleksibel/alias).

- `predict(voltage=None, current=None, power_factor=None, power=None, ...) -> dict`  
  Mengembalikan:

  ```python
  {
    "on": {"nama": jumlah_on, ...},
    "target": {"P":..., "I":..., "PF":..., "V":...},
    "pred":   {"P":..., "I":..., "PF":...},
    "loss": float,              # skor gabungan
    "rel_error_P": float        # |P_pred - P_meas| / P_meas
  }
  ```

### `ChargingTimePredictor`

- `__init__(capacity_kwh, target_soc=90.0, efficiency=0.92)`
- `predict(power: W, SoC: %) -> {"FinishDuration": "HH:MM", "FinishTime": ISO8601_UTC}`

---

## Konfigurasi & Tuning

- **Bobot loss**: menyeimbangkan pentingnya P, I, PF  

  ```python
  p.weights = {"P": 0.6, "I": 0.3, "PF": 0.1}
  ```

- **Tolerance pruning** (relatif di domain P)  

  ```python
  p.tolerance = 0.08  # 8% → pruning lebih agresif
  ```

- **Batas hard per perangkat**  

  ```python
  p.global_count_cap = 30
  ```

**Tips akurasi**

- Sesuaikan `pf` dan `watt` di katalog agar mendekati kondisi lapangan via `configure_catalog`.
- Berikan **P** dari meter jika tersedia; jika tidak, berikan kombinasi **V, I, PF** yang reliabel.
- `set_appliances` sebaiknya **upper bound** realistis, bukan jumlah pasti.

---

## Catatan Akurasi

- **PF tipikal** pada katalog adalah nilai rata-rata umum; silakan sesuaikan.
- **Standby-aware**: algoritma menghitung baseline *standby* + kontribusi aktif unit ON.
- Perbedaan instrumen/pipeline dapat membuat **P** dan **V·I·PF** tidak identik—model memadukan semuanya (dengan bobot).

---

## Kontribusi

Kontribusi sangat diterima 🙌  
Buka **issue** atau **pull request** di:

**<https://github.com/foldadjo/stroomer>**

Untuk pengembangan lokal:

```bash
git clone https://github.com/foldadjo/stroomer.git
cd stroomer
pip install -U build twine pytest
pip install -e .
pytest -q
```

> Ikuti PEP8 dan tambahkan test untuk setiap fitur/perbaikan.

---

## Lisensi

MIT © Stroomer Team — lihat berkas `LICENSE`.
