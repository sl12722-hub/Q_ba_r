from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
import sys


def _sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _signature(contract: dict[str, object], ignored: set[str]) -> str:
    reduced = {key: value for key, value in contract.items() if key not in ignored}
    encoded = json.dumps(reduced, ensure_ascii=False, sort_keys=True, separators=(",", ":"))
    return hashlib.sha256(encoded.encode("utf-8")).hexdigest()


def audit_reports(
    reports: list[tuple[Path, dict[str, object]]],
    *,
    axis: str,
    linked_fields: tuple[str, ...] = (),
    min_points: int = 3,
) -> dict[str, object]:
    if min_points < 3:
        raise ValueError("min_points must be at least three")
    ignored = {axis, "fold_count", *linked_fields}
    points: list[dict[str, object]] = []
    signatures: set[str] = set()
    for path, report in reports:
        contract = report.get("model_contract")
        evaluation = report.get("evaluation")
        quality = report.get("quality_gate")
        if not isinstance(contract, dict) or not isinstance(evaluation, dict):
            raise ValueError(f"{path} lacks model_contract or evaluation")
        if not isinstance(quality, dict) or not isinstance(quality.get("accepted"), bool):
            raise ValueError(f"{path} lacks a typed quality_gate decision")
        if axis not in contract:
            raise ValueError(f"{path} lacks model axis {axis}")
        signature = _signature(contract, ignored)
        signatures.add(signature)
        points.append(
            {
                "axis_value": float(contract[axis]),
                "quality_accepted": bool(quality["accepted"]),
                "ic_mean": float(evaluation["ic_mean"]),
                "ic_ir": float(evaluation["ic_ir"]),
                "net_sharpe": float(evaluation["sharpe"]),
                "total_return": float(evaluation["total_return"]),
                "worst_fold_ic": float(evaluation["worst_fold_ic"]),
                "source": str(path.resolve()),
                "source_sha256": _sha256(path),
            }
        )
    points.sort(key=lambda item: float(item["axis_value"]))
    distinct_values = {float(item["axis_value"]) for item in points}
    errors: list[str] = []
    if len(points) < min_points or len(distinct_values) < min_points:
        errors.append(
            f"incomplete neighborhood: need {min_points} distinct points, got {len(distinct_values)}"
        )
    if len(signatures) != 1:
        errors.append("reports do not share one structural model contract")
    adjacent_pass_pairs = sum(
        bool(left["quality_accepted"]) and bool(right["quality_accepted"])
        for left, right in zip(points, points[1:])
    )
    accepted_count = sum(bool(item["quality_accepted"]) for item in points)
    if adjacent_pass_pairs == 0:
        errors.append("no adjacent specification pair passes the complete quality gate")
    return {
        "schema_version": 1,
        "status": "passed" if not errors else "failed",
        "axis": axis,
        "linked_fields": list(linked_fields),
        "point_count": len(points),
        "accepted_point_count": accepted_count,
        "adjacent_pass_pair_count": adjacent_pass_pairs,
        "isolated_pass": accepted_count == 1,
        "neighborhood_exhausted": accepted_count == 0 and len(points) >= min_points,
        "points": points,
        "errors": errors,
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--reports", nargs="+", required=True)
    parser.add_argument("--axis", required=True)
    parser.add_argument("--linked-fields", nargs="*", default=[])
    parser.add_argument("--min-points", type=int, default=3)
    parser.add_argument("--output")
    args = parser.parse_args()
    loaded: list[tuple[Path, dict[str, object]]] = []
    for value in args.reports:
        path = Path(value).resolve()
        loaded.append((path, json.loads(path.read_text(encoding="utf-8"))))
    payload = audit_reports(
        loaded,
        axis=args.axis,
        linked_fields=tuple(args.linked_fields),
        min_points=args.min_points,
    )
    rendered = json.dumps(payload, ensure_ascii=False, indent=2) + "\n"
    if args.output:
        output = Path(args.output)
        output.parent.mkdir(parents=True, exist_ok=True)
        output.write_text(rendered, encoding="utf-8")
    print(rendered, end="")
    return 0 if payload["status"] == "passed" else 1


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except Exception as exc:
        print(f"error: {exc}", file=sys.stderr)
        raise
