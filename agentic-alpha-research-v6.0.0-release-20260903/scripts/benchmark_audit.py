#!/usr/bin/env python3
"""Audit multi-factor walk-forward and capacity benchmark completeness."""

from __future__ import annotations

import argparse
import csv
import json
import math
import sys
from collections import Counter
from datetime import datetime, timezone
from pathlib import Path


EXPECTED_CAPITALS = {100000.0, 500000.0, 1000000.0}
EXPECTED_AXIS_VALUES = {
    "quantile": {0.01, 0.03},
    "participation_rate": {0.001, 0.005},
    "cost_bps": {5.0, 10.0, 20.0},
    "quote_threshold": {0.5, 0.7, 0.9},
}


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--benchmark-root", type=Path, required=True)
    parser.add_argument("--data-audit", type=Path, required=True)
    parser.add_argument("--protocol-audit", type=Path, required=True)
    parser.add_argument("--factors", nargs="+", required=True)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--expected-folds", type=int, default=4)
    return parser.parse_args()


def finite(value: object) -> bool:
    try:
        return math.isfinite(float(value))
    except (TypeError, ValueError):
        return False


def truthy(value: object) -> bool:
    return str(value).strip().lower() in {"1", "true", "yes"}


def policy_key(row: dict[str, str]) -> tuple[float, float, float, float]:
    return (
        float(row["quantile"]),
        float(row["participation_rate"]),
        float(row["cost_bps"]),
        float(row["quote_threshold"]),
    )


def summarize_policy(rows: list[dict[str, str]]) -> dict:
    return {
        "quantile": float(rows[0]["quantile"]),
        "participation_rate": float(rows[0]["participation_rate"]),
        "cost_bps": float(rows[0]["cost_bps"]),
        "quote_threshold": float(rows[0]["quote_threshold"]),
        "min_total_return": min(float(row["total_return"]) for row in rows),
        "min_sharpe": min(float(row["sharpe"]) for row in rows),
        "min_fill_rate": min(float(row["fill_rate"]) for row in rows),
        "accepted": all(truthy(row.get("gate_accepted")) for row in rows),
    }


def close_set(observed: set[float], expected: set[float]) -> bool:
    return all(
        any(math.isclose(left, right, rel_tol=1e-9, abs_tol=1e-12) for right in expected)
        for left in expected
    )


def audit_factor(root: Path, factor: str, expected_folds: int) -> dict:
    factor_root = root / factor
    research_path = factor_root / "research.json"
    frontier_path = factor_root / "capacity" / "capacity_frontier.csv"
    frontier_manifest_path = factor_root / "capacity" / "frontier_manifest.json"
    errors: list[str] = []
    blockers: list[str] = []
    research: dict = {}
    rows: list[dict[str, str]] = []
    frontier_manifest: dict = {}

    if research_path.is_file():
        research = json.loads(research_path.read_text(encoding="utf-8"))
    else:
        errors.append("missing research.json")
    if frontier_path.is_file():
        with frontier_path.open(newline="", encoding="utf-8-sig") as handle:
            rows = list(csv.DictReader(handle))
    else:
        errors.append("missing capacity_frontier.csv")
    if frontier_manifest_path.is_file():
        frontier_manifest = json.loads(frontier_manifest_path.read_text(encoding="utf-8"))
    else:
        errors.append("missing frontier_manifest.json")

    evaluation = research.get("evaluation", {})
    evaluation_contract = research.get("evaluation_contract", {})
    if evaluation_contract.get("version") != 3:
        errors.append("missing evaluation and cost contract version 3")
    if evaluation_contract.get("future_target_availability_used_for_selection") is not False:
        errors.append("research selection may use future target availability")
    if evaluation_contract.get("target_tradable_used_for_selection") is not False:
        errors.append("research selection may use target_tradable")
    if evaluation_contract.get("turnover_accounting") != (
        "full_one_way_traded_notional_over_nav"
    ):
        errors.append("research turnover does not use full one-way notional")
    fold_metrics = evaluation.get("fold_metrics", [])
    if len(fold_metrics) != expected_folds:
        errors.append(f"expected {expected_folds} folds, found {len(fold_metrics)}")
    required_metrics = (
        "ic_mean",
        "ic_ir",
        "sharpe",
        "worst_fold_ic",
        "turnover",
        "coverage",
        "total_return",
    )
    missing_metrics = [name for name in required_metrics if not finite(evaluation.get(name))]
    if missing_metrics:
        errors.append(f"missing/non-finite research metrics: {missing_metrics}")
    for reason in research.get("promotion_gate", {}).get("reasons", []):
        blockers.append(str(reason))

    axes: dict[str, set[float]] = {axis: set() for axis in EXPECTED_AXIS_VALUES}
    capitals_by_case: dict[tuple[str, float], set[float]] = {}
    for row in rows:
        axis = row.get("axis", "")
        if axis not in EXPECTED_AXIS_VALUES:
            continue
        axis_value = float(row["axis_value"])
        capital = float(row["initial_capital"])
        axes[axis].add(axis_value)
        capitals_by_case.setdefault((axis, axis_value), set()).add(capital)
        for metric in ("total_return", "sharpe", "fill_rate"):
            if not finite(row.get(metric)):
                errors.append(f"non-finite {metric} for {axis}={axis_value}, capital={capital}")
    for axis, expected_values in EXPECTED_AXIS_VALUES.items():
        if not close_set(axes[axis], expected_values):
            errors.append(
                f"incomplete {axis} stress values: observed={sorted(axes[axis])}, expected={sorted(expected_values)}"
            )
    for case, capitals in capitals_by_case.items():
        if capitals != EXPECTED_CAPITALS:
            errors.append(f"incomplete capital tiers for {case}: {sorted(capitals)}")

    expected_rows = frontier_manifest.get("row_count")
    if expected_rows != len(rows):
        errors.append(
            f"frontier manifest row_count={expected_rows}, observed={len(rows)}"
        )
    execution_contract = frontier_manifest.get("execution_contract", {})
    if execution_contract.get("version") != 3:
        errors.append("missing execution and cost contract version 3")
    if execution_contract.get("future_target_availability_used_for_selection") is not False:
        errors.append("capacity selection may use future target availability")
    if execution_contract.get("target_tradable_used_for_selection") is not False:
        errors.append("capacity selection may use target_tradable")
    if execution_contract.get("turnover_accounting") != (
        "full_one_way_traded_notional_over_nav"
    ):
        errors.append("capacity turnover does not use full one-way notional")

    policies: dict[tuple[float, float, float, float], list[dict[str, str]]] = {}
    for row in rows:
        try:
            policies.setdefault(policy_key(row), []).append(row)
        except (KeyError, TypeError, ValueError) as exc:
            errors.append(f"invalid capacity policy row: {exc}")
    policy_summaries: dict[tuple[float, float, float, float], dict] = {}
    for key, policy_rows in policies.items():
        capitals = {float(row["initial_capital"]) for row in policy_rows}
        if capitals != EXPECTED_CAPITALS:
            errors.append(f"incomplete capital tiers for policy {key}: {sorted(capitals)}")
        policy_summaries[key] = summarize_policy(policy_rows)

    accepted_policies = [
        policy for policy in policy_summaries.values() if policy["accepted"]
    ]
    baseline = frontier_manifest.get("baseline", {})
    try:
        baseline_key = (
            float(baseline["quantile"]),
            float(baseline["participation_rate"]),
            float(baseline["cost_bps"]),
            float(baseline["quote_threshold"]),
        )
    except (KeyError, TypeError, ValueError):
        baseline_key = None
        errors.append("frontier manifest has an invalid baseline policy")
    baseline_capacity_accepted = bool(
        baseline_key in policy_summaries and policy_summaries[baseline_key]["accepted"]
    )
    best_policy_pool = accepted_policies or list(policy_summaries.values())
    best_policy = max(
        best_policy_pool,
        key=lambda policy: (
            policy["min_sharpe"],
            policy["min_fill_rate"],
            policy["min_total_return"],
        ),
        default=None,
    )

    diagnostic_complete = not errors
    quality_gate_accepted = research.get("quality_gate", {}).get("accepted") is True
    executable_diagnostic_survivor = (
        diagnostic_complete and quality_gate_accepted and bool(accepted_policies)
    )
    formal_inputs_complete = (
        diagnostic_complete
        and research.get("membership") is not None
        and research.get("tradability", {}).get("price_limit_checked") is True
    )
    promotion_eligible = (
        executable_diagnostic_survivor
        and formal_inputs_complete
        and research.get("promotion_gate", {}).get("accepted") is True
    )
    if diagnostic_complete and not accepted_policies:
        blockers.append("no declared capacity policy passed every capital tier")
    return {
        "factor": factor,
        "expression_id": evaluation.get("expression_id"),
        "diagnostic_complete": diagnostic_complete,
        "formal_inputs_complete": formal_inputs_complete,
        "promotion_eligible": promotion_eligible,
        "quality_gate_accepted": quality_gate_accepted,
        "executable_diagnostic_survivor": executable_diagnostic_survivor,
        "fold_count": len(fold_metrics),
        "capacity_row_count": len(rows),
        "capacity_policy_count": len(policy_summaries),
        "accepted_capacity_policy_count": len(accepted_policies),
        "baseline_capacity_accepted": baseline_capacity_accepted,
        "best_capacity_policy": best_policy,
        "metrics": {name: evaluation.get(name) for name in required_metrics},
        "blockers": blockers,
        "errors": errors,
    }


def main() -> int:
    args = parse_args()
    data_audit = json.loads(args.data_audit.read_text(encoding="utf-8"))
    protocol_audit = json.loads(args.protocol_audit.read_text(encoding="utf-8"))
    factors = [
        audit_factor(args.benchmark_root, factor, args.expected_folds)
        for factor in args.factors
    ]
    blocker_counts = Counter(
        blocker for factor in factors for blocker in factor.get("blockers", [])
    )
    diagnostic_complete = (
        data_audit.get("status") == "passed"
        and protocol_audit.get("status") == "passed"
        and all(factor["diagnostic_complete"] for factor in factors)
    )
    formal_backtest_complete = diagnostic_complete and all(
        factor["formal_inputs_complete"] for factor in factors
    )
    executable_survivor_count = sum(
        factor["executable_diagnostic_survivor"] for factor in factors
    )
    promotable_factor_count = sum(factor["promotion_eligible"] for factor in factors)
    if not diagnostic_complete:
        promotion_decision = "incomplete"
    elif executable_survivor_count == 0:
        promotion_decision = "no_executable_survivor"
    elif not formal_backtest_complete:
        promotion_decision = "blocked_missing_formal_inputs"
    elif promotable_factor_count == 0:
        promotion_decision = "no_promotable_factor"
    else:
        promotion_decision = "survivors_available"
    result = {
        "schema_version": 1,
        "audited_at_utc": datetime.now(timezone.utc).isoformat(),
        "benchmark_root": str(args.benchmark_root.resolve()),
        "data_source_status": data_audit.get("status"),
        "protocol_status": protocol_audit.get("status"),
        "diagnostic_suite_complete": diagnostic_complete,
        "formal_backtest_complete": formal_backtest_complete,
        "executable_diagnostic_survivor_count": executable_survivor_count,
        "promotable_factor_count": promotable_factor_count,
        "factor_count": len(factors),
        "factors": factors,
        "global_blockers": dict(blocker_counts),
        "promotion_decision": promotion_decision,
    }
    args.output.parent.mkdir(parents=True, exist_ok=True)
    rendered = json.dumps(result, ensure_ascii=False, indent=2)
    args.output.write_text(rendered + "\n", encoding="utf-8")
    print(rendered)
    return 0 if diagnostic_complete else 1


if __name__ == "__main__":
    sys.exit(main())
