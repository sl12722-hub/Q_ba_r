from __future__ import annotations

import importlib.util
from pathlib import Path
import unittest


SCRIPT = Path(__file__).parents[1] / "scripts" / "audit_experiment_contract.py"
SPEC = importlib.util.spec_from_file_location("audit_experiment_contract", SCRIPT)
assert SPEC is not None and SPEC.loader is not None
MODULE = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(MODULE)


def report(*, purge: int = 3, lookback: int = 0) -> dict:
    return {
        "evaluation_contract": {
            "version": 3,
            "portfolio_selection": "decision_time_fields_only",
            "future_target_availability_used_for_selection": False,
            "target_tradable_used_for_selection": False,
            "turnover_accounting": "full_one_way_traded_notional_over_nav",
        },
        "walkforward_contract": {
            "min_train_days": 252,
            "test_days": 63,
            "purge_days": purge,
            "embargo_days": 1,
        },
        "portfolio_contract": {
            "quantile": 0.03,
            "min_cross_section": 30,
            "one_way_cost_bps": 10.0,
        },
        "model_contract": {
            "model": "xgboost",
            "features": ["a", "b"],
            "target_horizon": 3,
            "prediction_ema_span": 15,
            "seed": 7,
            "train_lookback_days": lookback,
        },
    }


class ExperimentContractTests(unittest.TestCase):
    def test_complete_contract_passes(self) -> None:
        result = MODULE.audit_reports([report()], set())
        self.assertTrue(result["accepted"])

    def test_declared_model_axis_can_differ(self) -> None:
        result = MODULE.audit_reports(
            [report(lookback=0), report(lookback=504)],
            {"train_lookback_days"},
        )
        self.assertTrue(result["accepted"])

    def test_purge_mismatch_fails(self) -> None:
        result = MODULE.audit_reports([report(purge=1), report(purge=3)], set())
        self.assertFalse(result["accepted"])
        self.assertIn("reports disagree on walkforward_contract", result["reasons"])

    def test_missing_contract_fails(self) -> None:
        incomplete = report()
        del incomplete["portfolio_contract"]
        result = MODULE.audit_reports([incomplete], set())
        self.assertFalse(result["accepted"])
        self.assertIn("report 0 missing portfolio_contract", result["reasons"])


if __name__ == "__main__":
    unittest.main()
