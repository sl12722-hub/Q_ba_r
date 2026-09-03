from __future__ import annotations

import csv
import importlib.util
import json
from pathlib import Path
import sys
import tempfile
import unittest
from unittest.mock import patch


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


def write_capacity_csv(path: Path, rows: list[dict[str, str]]) -> None:
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(rows[0]))
        writer.writeheader()
        writer.writerows(rows)


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

    def test_cli_returns_failure_for_complete_rejected_anchor(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            research_path = root / "research.json"
            capacity_path = root / "capacity.csv"
            output_path = root / "anchor.json"
            research_path.write_text(json.dumps(RESEARCH), encoding="utf-8")
            write_capacity_csv(
                capacity_path,
                [row(100000, True), row(500000, False), row(1000000, True)],
            )

            argv = [
                "audit_research_policy_anchor.py",
                "--research-report",
                str(research_path),
                "--capacity-csv",
                str(capacity_path),
                "--expected-capitals",
                "100000",
                "500000",
                "1000000",
                "--output-json",
                str(output_path),
            ]
            with patch.object(sys, "argv", argv):
                self.assertEqual(MODULE.main(), 2)
            payload = json.loads(output_path.read_text(encoding="utf-8"))
            self.assertTrue(payload["anchor_complete"])
            self.assertFalse(payload["all_capitals_pass"])


if __name__ == "__main__":
    unittest.main()
