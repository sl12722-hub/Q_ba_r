from __future__ import annotations

import argparse
import json
import math
from pathlib import Path
import sys


def classify_alignment(
    evaluation: dict[str, object],
    *,
    quality_accepted: bool,
    min_positive_fold_share: float,
    min_gross_sharpe: float,
    min_ic_mean: float,
    min_ic_ir: float,
    min_net_sharpe: float,
    min_total_return: float,
    min_worst_fold_ic: float,
    max_turnover: float,
) -> tuple[str, tuple[str, ...], str, float]:
    folds = evaluation.get("fold_metrics")
    if not isinstance(folds, list) or not folds:
        raise ValueError("research report lacks fold_metrics")
    gross_by_fold = [float(item["gross_sharpe"]) for item in folds]
    positive_share = sum(value > 0.0 for value in gross_by_fold) / len(gross_by_fold)
    metrics = {
        "ic_mean": float(evaluation["ic_mean"]),
        "ic_ir": float(evaluation["ic_ir"]),
        "gross_sharpe": float(evaluation["gross_sharpe"]),
        "net_sharpe": float(evaluation["sharpe"]),
        "total_return": float(evaluation["total_return"]),
        "worst_fold_ic": float(evaluation["worst_fold_ic"]),
        "turnover": float(evaluation["turnover"]),
    }
    if not all(math.isfinite(value) for value in (*metrics.values(), *gross_by_fold)):
        return "invalid_evidence", ("invalid_evidence",), "repair_research_report", positive_share

    failures: list[str] = []
    if metrics["ic_mean"] > 0.0 and metrics["gross_sharpe"] <= min_gross_sharpe:
        failures.append("rank_tail_mismatch")
    if positive_share < min_positive_fold_share:
        failures.append("tail_instability")
    if metrics["worst_fold_ic"] < min_worst_fold_ic:
        failures.append("regime_concentration")
    if (
        metrics["net_sharpe"] < min_net_sharpe
        or metrics["total_return"] < min_total_return
        or metrics["turnover"] > max_turnover
    ):
        failures.append("execution_cost_failure")
    if metrics["ic_mean"] < min_ic_mean or metrics["ic_ir"] < min_ic_ir:
        failures.append("weak_rank_signal")

    if not failures and quality_accepted:
        return (
            "proceed_capacity",
            (),
            "run_precomputed_prediction_capacity_frontier",
            positive_share,
        )
    if not failures:
        failures.append("research_gate_failure")
    primary = failures[0]
    actions = {
        "rank_tail_mismatch": "revise_label_loss_or_portfolio_head",
        "tail_instability": "diagnose_regime_concentration",
        "regime_concentration": "add_causal_regime_conditioning_and_retest_neighbors",
        "execution_cost_failure": "revise_causal_execution_policy",
        "weak_rank_signal": "change_causal_representation_or_label",
        "research_gate_failure": "inspect_remaining_quality_gates",
        "invalid_evidence": "repair_research_report",
    }
    return primary, tuple(failures), actions[primary], positive_share


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--research-report", required=True)
    parser.add_argument("--output")
    parser.add_argument("--min-positive-fold-share", type=float, default=0.60)
    parser.add_argument("--min-gross-sharpe", type=float, default=0.0)
    parser.add_argument("--min-ic-mean", type=float, default=0.01)
    parser.add_argument("--min-ic-ir", type=float, default=0.5)
    parser.add_argument("--min-net-sharpe", type=float, default=0.5)
    parser.add_argument("--min-total-return", type=float, default=0.0)
    parser.add_argument("--min-worst-fold-ic", type=float, default=-0.01)
    parser.add_argument("--max-turnover", type=float, default=1.5)
    args = parser.parse_args()

    report_path = Path(args.research_report).resolve()
    report = json.loads(report_path.read_text(encoding="utf-8"))
    evaluation = report.get("evaluation")
    quality = report.get("quality_gate")
    model_contract = report.get("model_contract")
    if not isinstance(evaluation, dict) or not isinstance(quality, dict):
        raise ValueError("research report lacks evaluation or quality_gate")
    if not isinstance(model_contract, dict):
        raise ValueError("research report lacks model_contract")

    classification, failure_modes, action, positive_share = classify_alignment(
        evaluation,
        quality_accepted=bool(quality.get("accepted")),
        min_positive_fold_share=args.min_positive_fold_share,
        min_gross_sharpe=args.min_gross_sharpe,
        min_ic_mean=args.min_ic_mean,
        min_ic_ir=args.min_ic_ir,
        min_net_sharpe=args.min_net_sharpe,
        min_total_return=args.min_total_return,
        min_worst_fold_ic=args.min_worst_fold_ic,
        max_turnover=args.max_turnover,
    )

    payload = {
        "schema_version": 1,
        "source_report": str(report_path),
        "classification": classification,
        "failure_modes": list(failure_modes),
        "recommended_action": action,
        "capacity_eligible": classification == "proceed_capacity",
        "metrics": {
            "ic_mean": float(evaluation["ic_mean"]),
            "ic_ir": float(evaluation["ic_ir"]),
            "gross_sharpe": float(evaluation["gross_sharpe"]),
            "net_sharpe": float(evaluation["sharpe"]),
            "total_return": float(evaluation["total_return"]),
            "worst_fold_ic": float(evaluation["worst_fold_ic"]),
            "turnover": float(evaluation["turnover"]),
            "positive_gross_fold_share": positive_share,
            "fold_count": len(evaluation["fold_metrics"]),
        },
        "thresholds": {
            "min_gross_sharpe": args.min_gross_sharpe,
            "min_positive_fold_share": args.min_positive_fold_share,
            "min_ic_mean": args.min_ic_mean,
            "min_ic_ir": args.min_ic_ir,
            "min_net_sharpe": args.min_net_sharpe,
            "min_total_return": args.min_total_return,
            "min_worst_fold_ic": args.min_worst_fold_ic,
            "max_turnover": args.max_turnover,
        },
    }
    rendered = json.dumps(payload, ensure_ascii=False, indent=2) + "\n"
    if args.output:
        output = Path(args.output)
        output.parent.mkdir(parents=True, exist_ok=True)
        output.write_text(rendered, encoding="utf-8")
    print(rendered, end="")
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except Exception as exc:
        print(f"error: {exc}", file=sys.stderr)
        raise
