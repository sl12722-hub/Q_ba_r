from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
from typing import Any


def _load(path: Path) -> dict[str, Any]:
    payload = json.loads(path.read_text(encoding="utf-8"))
    model = payload.get("model_contract")
    evaluation = payload.get("evaluation")
    contract = payload.get("evaluation_contract")
    if not isinstance(model, dict) or not isinstance(evaluation, dict):
        raise ValueError(f"incomplete learned-model report: {path}")
    if not isinstance(contract, dict) or contract.get("version") != 3:
        raise ValueError(f"unsupported evaluation contract: {path}")
    if contract.get("turnover_accounting") != "full_one_way_traded_notional_over_nav":
        raise ValueError(f"invalid turnover accounting: {path}")
    if "gross_sharpe" not in evaluation or "fold_metrics" not in evaluation:
        raise ValueError(f"missing gross or fold evidence: {path}")
    return payload


def _objective_family(model: dict[str, Any]) -> str:
    mode = model.get("target_mode")
    if mode:
        return str(mode)
    target = str(model.get("training_target", ""))
    if "pairwise" in target:
        return "tail_pairwise_rank"
    if "binary" in target or "classification" in target:
        return "tail_classification"
    return "daily_rank_regression"


def _canonical_hash(payload: dict[str, Any]) -> str:
    encoded = json.dumps(payload, sort_keys=True, separators=(",", ":")).encode()
    return hashlib.sha256(encoded).hexdigest().upper()


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--research-report", action="append", required=True)
    parser.add_argument("--output")
    parser.add_argument("--min-objective-families", type=int, default=3)
    args = parser.parse_args()
    if args.min_objective_families < 2:
        raise ValueError("min-objective-families must be at least two")

    reports: list[dict[str, Any]] = []
    families: set[str] = set()
    for raw_path in args.research_report:
        path = Path(raw_path).resolve()
        payload = _load(path)
        model = payload["model_contract"]
        evaluation = payload["evaluation"]
        family = _objective_family(model)
        families.add(family)
        fold_metrics = evaluation["fold_metrics"]
        positive_fold_share = sum(
            float(fold.get("gross_sharpe", 0.0)) > 0.0 for fold in fold_metrics
        ) / max(len(fold_metrics), 1)
        reports.append(
            {
                "path": str(path),
                "objective_family": family,
                "gross_sharpe": float(evaluation["gross_sharpe"]),
                "net_sharpe": float(evaluation["sharpe"]),
                "ic_mean": float(evaluation["ic_mean"]),
                "worst_fold_ic": float(evaluation["worst_fold_ic"]),
                "positive_gross_fold_share": positive_fold_share,
            }
        )

    enough_families = len(families) >= args.min_objective_families
    any_gross_positive = any(item["gross_sharpe"] > 0.0 for item in reports)
    exhausted = enough_families and not any_gross_positive
    result: dict[str, Any] = {
        "schema_version": 1,
        "classification": "objective_neighborhood_exhausted" if exhausted else "continue_objective_research",
        "recommended_action": (
            "change_feature_mechanism_or_causal_representation"
            if exhausted
            else "complete_structural_objectives_or_audit_gross_positive_candidate"
        ),
        "objective_family_count": len(families),
        "objective_families": sorted(families),
        "report_count": len(reports),
        "all_gross_non_positive": not any_gross_positive,
        "thresholds": {"min_objective_families": args.min_objective_families},
        "reports": sorted(reports, key=lambda item: (item["objective_family"], item["path"])),
    }
    result["deterministic_sha256"] = _canonical_hash(result)
    rendered = json.dumps(result, ensure_ascii=False, indent=2) + "\n"
    if args.output:
        output = Path(args.output)
        output.parent.mkdir(parents=True, exist_ok=True)
        output.write_text(rendered, encoding="utf-8")
    print(rendered, end="")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
