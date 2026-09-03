from __future__ import annotations

import csv
import importlib.util
from pathlib import Path
import tempfile
import unittest


SCRIPT = Path(__file__).parents[1] / "scripts" / "audit_capacity_cartesian.py"
SPEC = importlib.util.spec_from_file_location("audit_capacity_cartesian", SCRIPT)
assert SPEC is not None and SPEC.loader is not None
MODULE = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(MODULE)


class CartesianAuditTests(unittest.TestCase):
    def test_policy_summary_requires_all_capitals(self) -> None:
        rows = [
            {
                "quantile": "0.03",
                "exit_quantile": "0.05",
                "rebalance_days": "3",
                "participation_rate": "0.05",
                "cost_bps": "10",
                "initial_capital": str(capital),
                "total_return": "0.2",
                "sharpe": "2.1",
                "fill_rate": "0.95",
                "gate_accepted": "True",
            }
            for capital in (100000.0, 500000.0, 1000000.0)
        ]
        errors: list[str] = []
        summary = MODULE._policy_summary(
            rows,
            tag="Q03_E05_R03",
            quantile=0.03,
            exit_quantile=0.05,
            rebalance_days=3,
            participation_rate=0.05,
            cost_bps=10.0,
            expected_capitals=[100000.0, 500000.0, 1000000.0],
            errors=errors,
        )
        self.assertEqual(errors, [])
        self.assertIsNotNone(summary)
        self.assertTrue(summary["accepted_all_capitals"])

        errors = []
        missing = MODULE._policy_summary(
            rows[:-1],
            tag="Q03_E05_R03",
            quantile=0.03,
            exit_quantile=0.05,
            rebalance_days=3,
            participation_rate=0.05,
            cost_bps=10.0,
            expected_capitals=[100000.0, 500000.0, 1000000.0],
            errors=errors,
        )
        self.assertIsNone(missing)
        self.assertTrue(errors)


if __name__ == "__main__":
    unittest.main()
