from __future__ import annotations
from datetime import datetime, timedelta, timezone
from typing import Dict, Optional

def _fmt_duration(td: timedelta) -> str:
    total_minutes = int(td.total_seconds() // 60)
    hours, minutes = divmod(total_minutes, 60)
    return f"{hours:02d}:{minutes:02d}"

class ChargingTimePredictor:
    def __init__(self, capacity_kwh: float, target_soc: float = 90.0, efficiency: float = 0.92):
        self.capacity_kwh = float(capacity_kwh)
        self.target_soc = float(target_soc)
        self.efficiency = float(efficiency)

    def predict(self, power: float, SoC: float, now_utc: Optional[datetime] = None) -> Dict[str, str]:
        if now_utc is None:
            now_utc = datetime.utcnow().replace(tzinfo=timezone.utc)

        SoC = max(0.0, min(100.0, float(SoC)))
        tgt = max(SoC, min(100.0, float(self.target_soc)))

        if power <= 0 or tgt <= SoC or self.capacity_kwh <= 0:
            return {"FinishDuration": "00:00", "FinishTime": now_utc.isoformat()}

        energy_needed_kwh = self.capacity_kwh * (tgt - SoC) / 100.0
        grid_energy_kwh = energy_needed_kwh / max(1e-6, self.efficiency)
        duration_hours = grid_energy_kwh / (power / 1000.0)

        if SoC >= 80.0:
            duration_hours *= 1.10  # simple taper correction

        duration = timedelta(hours=duration_hours)
        finish_time = now_utc + duration

        return {
            "FinishDuration": _fmt_duration(duration),
            "FinishTime": finish_time.isoformat(),
        }
