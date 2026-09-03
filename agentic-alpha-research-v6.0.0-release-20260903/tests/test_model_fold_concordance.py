from __future__ import annotations

import importlib.util
from pathlib import Path
import unittest


SCRIPT = Path(__file__).parents[1] / "scripts" / "audit_model_fold_concordance.py"
SPEC = importlib.util.spec_from_file_location("audit_model_fold_concordance", SCRIPT)
assert SPEC is not None and SPEC.loader is not None
MODULE = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(MODULE)


def report(values: list[float]) -> dict:
    return {
        "evaluation": {
            "fold_metrics": [
                {"fold_id": index, "test_ic_mean": value}
                for index, value in enumerate(values)
            ]
        }
    }


class ModelFoldConcordanceTests(unittest.TestCase):
    def test_shared_failure_closes_weight_tuning(self) -> None:
        members = [
            report([0.03, 0.02, -0.012, 0.01]),
            report([0.025, 0.018, -0.013, 0.009]),
            report([0.028, 0.021, -0.011, 0.011]),
        ]
        ensemble = report([0.029, 0.020, -0.016, 0.010])
        result = MODULE.audit(
            members,
            ensemble,
            fold_floor=-0.01,
            correlation_threshold=0.8,
        )
        self.assertTrue(result["close_weight_tuning_branch"])
        self.assertEqual(result["shared_floor_breach_folds"], [2])
        self.assertEqual(result["ensemble_worsened_shared_folds"], [2])

    def test_no_shared_floor_breach_does_not_close(self) -> None:
        members = [
            report([0.03, -0.012, 0.01, 0.02]),
            report([0.02, 0.01, -0.013, 0.03]),
        ]
        ensemble = report([0.025, -0.002, 0.001, 0.025])
        result = MODULE.audit(
            members,
            ensemble,
            fold_floor=-0.01,
            correlation_threshold=0.8,
        )
        self.assertFalse(result["close_weight_tuning_branch"])

    def test_mismatched_fold_sets_fail_closed(self) -> None:
        with self.assertRaisesRegex(ValueError, "fold sets differ"):
            MODULE.audit(
                [report([0.1, 0.2]), report([0.1, 0.2, 0.3])],
                report([0.1, 0.2]),
                fold_floor=-0.01,
                correlation_threshold=0.8,
            )


if __name__ == "__main__":
    unittest.main()
