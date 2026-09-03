from __future__ import annotations

import importlib.util
from pathlib import Path
import unittest


SCRIPT = Path(__file__).parents[1] / "scripts" / "audit_research_policy_anchor.py"
SPEC = importlib.util.spec_from_file_location("audit_research_policy_anchor", SCRIPT)
assert SPEC is not None and SPEC.loader is not None
MODULE = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(MODULE)


RESEARCH = {
    "portfolio_contract": {
        "quantile": 0.03,
        "one_way_cost_bps": 10.0,
    }
}


def row(capital: float, accepted: bool) -> dict[str, str]:
    return {
        "quantile": "0.03",
        "exit_quantile": "0.03",
        "rebalance_days": "1",
        "cost_bps": "10",
        "initial_capital": str(capital),
        "total_return": "1.2",
        "sharpe": "2.5",
        "fill_rate": "0.92",
        "gate_accepted": str(accepted),
    }


class ResearchPolicyAnchorTests(unittest.TestCase):
    def test_complete_passing_anchor_passes(self) -> None:
        result = MODULE.audit_anchor(
            RESEARCH,
            [row(100000, True), row(500000, True), row(1000000, True)],
            expected_capitals={100000, 500000, 1000000},
        )
        self.assertTrue(result["anchor_complete"])
        self.assertTrue(result["all_capitals_pass"])

    def test_complete_near_miss_remains_rejected(self) -> None:
        result = MODULE.audit_anchor(
            RESEARCH,
            [row(100000, True), row(500000, False), row(1000000, True)],
            expected_capitals={100000, 500000, 1000000},
        )
        self.assertTrue(result["anchor_complete"])
        self.assertFalse(result["all_capitals_pass"])
        self.assertEqual(result["decision"], "reject_executable_promotion")

    def test_missing_capital_fails_closed(self) -> None:
        result = MODULE.audit_anchor(
            RESEARCH,
            [row(100000, True), row(500000, True)],
            expected_capitals={100000, 500000, 1000000},
        )
        self.assertFalse(result["anchor_complete"])
        self.assertEqual(result["missing_capitals"], [1000000])


if __name__ == "__main__":
    unittest.main()
