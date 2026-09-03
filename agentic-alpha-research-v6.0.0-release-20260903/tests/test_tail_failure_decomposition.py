from __future__ import annotations

import importlib.util
from pathlib import Path
import unittest


SCRIPT = Path(__file__).parents[1] / "scripts" / "audit_model_tail_alignment.py"
SPEC = importlib.util.spec_from_file_location("tail_audit_candidate", SCRIPT)
MODULE = importlib.util.module_from_spec(SPEC)
assert SPEC.loader is not None
SPEC.loader.exec_module(MODULE)


def evaluation(**updates):
    payload = {
        "ic_mean": 0.02,
        "ic_ir": 1.0,
        "gross_sharpe": 2.0,
        "sharpe": 1.0,
        "total_return": 0.5,
        "worst_fold_ic": 0.0,
        "turnover": 0.8,
        "fold_metrics": [{"gross_sharpe": 1.0} for _ in range(5)],
    }
    payload.update(updates)
    return payload


def classify(payload, accepted=False):
    return MODULE.classify_alignment(
        payload,
        quality_accepted=accepted,
        min_positive_fold_share=0.6,
        min_gross_sharpe=0.0,
        min_ic_mean=0.01,
        min_ic_ir=0.5,
        min_net_sharpe=0.5,
        min_total_return=0.0,
        min_worst_fold_ic=-0.01,
        max_turnover=1.5,
    )


class TailFailureDecompositionTests(unittest.TestCase):
    def test_profitable_but_unstable_model_is_not_called_cost_failure(self):
        primary, failures, _, _ = classify(
            evaluation(ic_mean=0.001, ic_ir=0.2, worst_fold_ic=-0.035)
        )
        self.assertEqual(primary, "regime_concentration")
        self.assertIn("weak_rank_signal", failures)
        self.assertNotIn("execution_cost_failure", failures)

    def test_net_failure_is_explicit(self):
        _, failures, _, _ = classify(
            evaluation(sharpe=-0.2, total_return=-0.1, turnover=1.7)
        )
        self.assertIn("execution_cost_failure", failures)

    def test_complete_quality_pass_proceeds(self):
        primary, failures, _, _ = classify(evaluation(), accepted=True)
        self.assertEqual(primary, "proceed_capacity")
        self.assertEqual(failures, ())


if __name__ == "__main__":
    unittest.main()
