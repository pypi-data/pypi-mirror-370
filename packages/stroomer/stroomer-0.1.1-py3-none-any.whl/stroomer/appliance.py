from typing import Dict, List, Tuple, Optional
import math

class StroomerPredictor:
    """
    Mencari kombinasi JUMLAH unit per perangkat sehingga
    sum(count_i * unit_watt_i) ≈ target_power (dari power atau V*I*PF).

    - set_appliances: mapping nama -> daya per unit (W)
    - set_max_counts (opsional): batasi jumlah unit per perangkat
    - predict_counts: kembalikan dict {nama: jumlah_on}, plus meta
    """

    def __init__(self):
        self.unit_watts: Dict[str, float] = {}
        self.max_counts: Dict[str, int] = {}   # opsional batas per perangkat
        self.global_count_cap: int = 20        # batas aman default per perangkat

    # --- Konfigurasi ---
    def set_appliances(self, mapping: Dict[str, float]):
        # mapping: nama -> daya PER UNIT (W)
        self.unit_watts = {k: float(v) for k, v in mapping.items() if v > 0}

    def set_max_counts(self, max_counts: Dict[str, int]):
        # mapping: nama -> maksimal unit ON yang masuk akal (opsional)
        self.max_counts = {k: int(max(0, v)) for k, v in max_counts.items()}

    # --- Utilitas power ---
    @staticmethod
    def _real_power(voltage: Optional[float], current: Optional[float],
                    power_factor: float, power: Optional[float]) -> float:
        if power is not None:
            return float(power)
        v = float(voltage or 0.0)
        i = float(current or 0.0)
        pf = float(power_factor or 1.0)
        return v * i * pf

    # --- Core search ---
    def predict_counts(self,
                       voltage: float = None,
                       current: float = None,
                       power_factor: float = 1.0,
                       power: float = None,
                       tolerance: float = 0.08  # 8% toleransi
                       ) -> Dict[str, object]:
        """
        Menghasilkan jumlah unit ON per perangkat.
        Return:
          {
            "on": {"Lampu": 3, "Kipas": 1, ...},
            "target_power": ...,
            "predicted_total": ...,
            "relative_error": ...,
          }
        """
        if not self.unit_watts:
            return {"on": {}, "target_power": 0.0, "predicted_total": 0.0, "relative_error": 1.0}

        target = self._real_power(voltage, current, power_factor, power)
        if target <= 0:
            return {"on": {}, "target_power": target, "predicted_total": 0.0, "relative_error": 1.0}

        # Siapkan item terurut dari unit watt terbesar → kecil (pruning lebih efektif)
        items: List[Tuple[str, float]] = sorted(self.unit_watts.items(), key=lambda x: x[1], reverse=True)

        # Batas count default per perangkat bila tidak diset:
        # min(floor(target/u) + 2, global cap)
        bounds: List[int] = []
        for name, u in items:
            auto_cap = min(int(math.floor(target / max(1.0, u))) + 2, self.global_count_cap)
            bounds.append(self.max_counts.get(name, auto_cap))

        tol_abs = max(1.0, tolerance * target)  # toleransi absolut (W)
        n = len(items)
        unit_list = [u for _, u in items]

        # Precompute upper bound kontribusi maksimum sisa (untuk pruning)
        suffix_max = [0.0]*(n+1)
        for i in range(n-1, -1, -1):
            suffix_max[i] = suffix_max[i+1] + unit_list[i] * bounds[i]

        best_err = float("inf")
        best_counts: List[int] = [0]*n
        cur_counts: List[int] = [0]*n

        def dfs(idx: int, cur_sum: float):
            nonlocal best_err, best_counts

            # Hitung error saat ini terhadap target
            cur_err = abs(cur_sum - target)
            if cur_err < best_err:
                best_err = cur_err
                best_counts = cur_counts.copy()
                # Early stop bila sudah dalam toleransi sangat kecil
                if best_err <= tol_abs * 0.2:
                    # cukup dekat; boleh berhenti lebih awal
                    pass

            if idx == n:
                return

            # Pruning 1: jika walau maksimal sisa tidak bisa mendekati target
            max_possible = cur_sum + suffix_max[idx]
            if target - max_possible > tol_abs and (target > max_possible):
                return

            name, u = items[idx]
            max_c = bounds[idx]

            # Coba dari jumlah maksimum → 0 agar cepat menyentuh target
            # (branch & bound)
            max_by_sum = int(min(max_c, math.ceil((target + tol_abs - cur_sum) / max(1.0, u))))
            for c in range(max_by_sum, -1, -1):
                new_sum = cur_sum + c * u

                # Pruning 2: terlalu overshoot melewati target + toleransi besar
                if new_sum - target > tol_abs and c > 0:
                    continue

                cur_counts[idx] = c
                dfs(idx + 1, new_sum)
                cur_counts[idx] = 0

        dfs(0, 0.0)

        # Susun hasil
        on: Dict[str, int] = {}
        pred_total = 0.0
        for (name, u), c in zip(items, best_counts):
            if c > 0:
                on[name] = int(c)
                pred_total += c * u

        rel_error = (abs(pred_total - target) / max(1.0, target)) if target > 0 else 1.0
        return {
            "on": on,
            "target_power": float(target),
            "predicted_total": float(pred_total),
            "relative_error": float(rel_error),
        }

    # Alias agar kompatibel dengan pemanggilan lama
    def predict(self, *args, **kwargs):
        return self.predict_counts(*args, **kwargs)
