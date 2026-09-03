from __future__ import annotations

import argparse
import hashlib
import json
import math
from pathlib import Path
import statistics
import sys


def file_sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def fold_vector(report: dict) -> dict[int, float]:
    metrics = report.get("evaluation", {}).get("fold_metrics")
    if not isinstance(metrics, list) or not metrics:
        raise ValueError("report has no fold_metrics")
    values: dict[int, float] = {}
    for item in metrics:
        fold_id = int(item["fold_id"])
        value = float(item["test_ic_mean"])
        if fold_id in values:
            raise ValueError(f"duplicate fold_id {fold_id}")
        if not math.isfinite(value):
            raise ValueError(f"non-finite fold IC for fold {fold_id}")
        values[fold_id] = value
    return values


def correlation(left: list[float], right: list[float]) -> float:
    if len(left) != len(right) or len(left) < 2:
        raise ValueError("correlation vectors must have equal length >= 2")
    left_mean = statistics.fmean(left)
    right_mean = statistics.fmean(right)
    left_centered = [value - left_mean for value in left]
    right_centered = [value - right_mean for value in right]
    denominator = math.sqrt(
        sum(value * value for value in left_centered)
        * sum(value * value for value in right_centered)
    )
    if denominator <= 0:
        raise ValueError("constant fold vector cannot establish diversification")
    return sum(a * b for a, b in zip(left_centered, right_centered)) / denominator


def audit(
    members: list[dict],
    ensemble: dict,
    *,
    fold_floor: float,
    correlation_threshold: float,
) -> dict[str, object]:
    if len(members) < 2:
        raise ValueError("at least two members are required")
    member_vectors = [fold_vector(report) for report in members]
    ensemble_vector = fold_vector(ensemble)
    fold_ids = sorted(member_vectors[0])
    expected = set(fold_ids)
    if any(set(vector) != expected for vector in member_vectors[1:]):
        raise ValueError("member fold sets differ")
    if set(ensemble_vector) != expected:
        raise ValueError("ensemble fold set differs from members")
    correlations: list[float] = []
    for left_index in range(len(member_vectors)):
        for right_index in range(left_index + 1, len(member_vectors)):
            correlations.append(
                correlation(
                    [member_vectors[left_index][fold] for fold in fold_ids],
                    [member_vectors[right_index][fold] for fold in fold_ids],
                )
            )
    mean_correlation = statistics.fmean(correlations)
    shared_floor_breaches = [
        fold
        for fold in fold_ids
        if all(vector[fold] < fold_floor for vector in member_vectors)
    ]
    worsened_shared_folds = [
        fold
        for fold in shared_floor_breaches
        if ensemble_vector[fold] <= min(vector[fold] for vector in member_vectors)
    ]
    ensemble_failed_shared_folds = [
        fold for fold in shared_floor_breaches if ensemble_vector[fold] < fold_floor
    ]
    close_branch = bool(
        mean_correlation >= correlation_threshold
        and shared_floor_breaches
        and ensemble_failed_shared_folds
    )
    return {
        "schema_version": 1,
        "member_count": len(members),
        "fold_count": len(fold_ids),
        "fold_floor": fold_floor,
        "correlation_threshold": correlation_threshold,
        "pairwise_fold_ic_correlations": correlations,
        "mean_pairwise_fold_ic_correlation": mean_correlation,
        "shared_floor_breach_folds": shared_floor_breaches,
        "ensemble_failed_shared_folds": ensemble_failed_shared_folds,
        "ensemble_worsened_shared_folds": worsened_shared_folds,
        "close_weight_tuning_branch": close_branch,
        "decision": (
            "change_causal_representation"
            if close_branch
            else "no_structural_closure_from_fold_concordance"
        ),
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--member-research-json", nargs="+", required=True)
    parser.add_argument("--ensemble-research-json", required=True)
    parser.add_argument("--fold-floor", type=float, default=-0.01)
    parser.add_argument("--correlation-threshold", type=float, default=0.8)
    parser.add_argument("--output-json")
    args = parser.parse_args()
    member_paths = [Path(value).resolve() for value in args.member_research_json]
    ensemble_path = Path(args.ensemble_research_json).resolve()
    members = [json.loads(path.read_text(encoding="utf-8")) for path in member_paths]
    ensemble = json.loads(ensemble_path.read_text(encoding="utf-8"))
    result = audit(
        members,
        ensemble,
        fold_floor=args.fold_floor,
        correlation_threshold=args.correlation_threshold,
    )
    result["sources"] = {
        "members": [
            {"path": str(path), "sha256": file_sha256(path)} for path in member_paths
        ],
        "ensemble": {
            "path": str(ensemble_path),
            "sha256": file_sha256(ensemble_path),
        },
    }
    rendered = json.dumps(result, ensure_ascii=False, indent=2) + "\n"
    if args.output_json:
        Path(args.output_json).write_text(rendered, encoding="utf-8")
    print(rendered, end="")
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except Exception as exc:
        print(f"error: {exc}", file=sys.stderr)
        raise
