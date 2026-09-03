from __future__ import annotations

import importlib.util
import json
from pathlib import Path
import tempfile
import unittest


SCRIPT = Path(__file__).parents[1] / "scripts" / "audit_model_specification_neighborhood.py"
SPEC = importlib.util.spec_from_file_location("spec_neighborhood", SCRIPT)
MODULE = importlib.util.module_from_spec(SPEC)
assert SPEC.loader is not None
SPEC.loader.exec_module(MODULE)


def report(path: Path, horizon: int, accepted: bool) -> tuple[Path, dict[str, object]]:
    payload = {
        "model_contract": {
            "model": "deep_cross",
            "target_horizon": horizon,
            "prediction_ema_span": horizon * 4,
            "seed": 7,
            "fold_count": 5,
        },
        "evaluation": {
            "ic_mean": 0.02,
            "ic_ir": 1.0,
            "sharpe": 1.0,
            "total_return": 0.3,
            "worst_fold_ic": -0.005,
        },
        "quality_gate": {"accepted": accepted},
    }
    path.write_text(json.dumps(payload), encoding="utf-8")
    return path, payload


class SpecificationNeighborhoodTests(unittest.TestCase):
    def test_adjacent_passing_pair_is_required(self):
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            reports = [
                report(root / "a.json", 1, False),
                report(root / "b.json", 3, True),
                report(root / "c.json", 5, True),
            ]
            result = MODULE.audit_reports(
                reports,
                axis="target_horizon",
                linked_fields=("prediction_ema_span",),
            )
            self.assertEqual(result["status"], "passed")
            self.assertEqual(result["adjacent_pass_pair_count"], 1)

    def test_isolated_pass_fails(self):
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            reports = [
                report(root / "a.json", 1, False),
                report(root / "b.json", 3, True),
                report(root / "c.json", 5, False),
            ]
            result = MODULE.audit_reports(
                reports,
                axis="target_horizon",
                linked_fields=("prediction_ema_span",),
            )
            self.assertEqual(result["status"], "failed")
            self.assertTrue(result["isolated_pass"])


if __name__ == "__main__":
    unittest.main()
