from typing import Dict, List, Tuple
import itertools

class StroomerPredictor:
    def __init__(self):
        self.appliances: Dict[str, float] = {}

    def set_appliances(self, mapping: Dict[str, float]):
        self.appliances = dict(mapping)

    @staticmethod
    def _real_power(voltage: float, current: float, power_factor: float, power: float = None) -> float:
        if power is not None:
            return float(power)
        return float(voltage) * float(current) * float(power_factor)

    def predict(self, voltage: float = None, current: float = None, power_factor: float = 1.0, power: float = None, max_combo: int = 3) -> Dict[str, float]:
        """
        Return probability per appliance that is ON (simple rule-based via subset-sum fit).
        """
        if not self.appliances:
            return {}

        target = self._real_power(voltage or 0.0, current or 0.0, power_factor or 1.0, power)
        if target <= 0:
            return {}

        items: List[Tuple[str, float]] = list(self.appliances.items())
        best_combo, best_error = [], float("inf")

        # Try combinations up to size max_combo
        for r in range(1, min(max_combo, len(items)) + 1):
            for combo in itertools.combinations(items, r):
                s = sum(p for _, p in combo)
                error = abs(s - target) / max(1.0, target)
                if error < best_error:
                    best_error = error
                    best_combo = combo

        result: Dict[str, float] = {k: 0.0 for k in self.appliances.keys()}
        if not best_combo:
            return result

        total_in_combo = sum(p for _, p in best_combo)
        for name, p in best_combo:
            contrib = p / max(1.0, total_in_combo)
            score = max(0.0, 1.0 - best_error) * contrib
            result[name] = score

        s = sum(result.values())
        if s > 0:
            for k in result:
                result[k] /= s
        return result
