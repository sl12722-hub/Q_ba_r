from __future__ import annotations

import argparse
import csv
import hashlib
import json
from pathlib import Path


def _close(left: float, right: float) -> bool:
    return abs(left - right) <= 1e-10


def _hash(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _read(path: Path) -> list[dict[str, str]]:
    with path.open("r", encoding="utf-8-sig", newline="") as stream:
        return list(csv.DictReader(stream))


def _policy_summary(
    rows: list[dict[str, str]],
    *,
    tag: str,
    quantile: float,
    exit_quantile: float,
    rebalance_days: int,
    participation_rate: float,
    cost_bps: float,
    expected_capitals: list[float],
    errors: list[str],
) -> dict[str, object] | None:
    matched: dict[float, dict[str, str]] = {}
    for row in rows:
        if not (
            _close(float(row["quantile"]), quantile)
            and _close(float(row["exit_quantile"]), exit_quantile)
            and int(float(row["rebalance_days"])) == rebalance_days
            and _close(float(row["participation_rate"]), participation_rate)
            and _close(float(row["cost_bps"]), cost_bps)
        ):
            continue
        capital = float(row["initial_capital"])
        previous = matched.get(capital)
        if previous is not None:
            comparable = ("total_return", "sharpe", "fill_rate", "gate_accepted")
            if any(previous[field] != row[field] for field in comparable):
                errors.append(f"conflicting duplicate rows: {tag}, capital={capital}")
        matched[capital] = row
    capitals = sorted(matched)
    if capitals != expected_capitals:
        errors.append(
            f"capital coverage mismatch for {tag}: "
            f"expected={expected_capitals}, actual={capitals}"
        )
        return None
    values = list(matched.values())
    return {
        "tag": tag,
        "quantile": quantile,
        "exit_quantile": exit_quantile,
        "rebalance_days": rebalance_days,
        "capital_count": len(values),
        "min_sharpe": min(float(row["sharpe"]) for row in values),
        "min_total_return": min(float(row["total_return"]) for row in values),
        "min_fill_rate": min(float(row["fill_rate"]) for row in values),
        "accepted_all_capitals": all(
            row["gate_accepted"].strip().lower() == "true" for row in values
        ),
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    source = parser.add_mutually_exclusive_group(required=True)
    source.add_argument("--grid-root")
    source.add_argument("--frontier-csv")
    parser.add_argument("--exit-quantiles", nargs="+", type=float, required=True)
    parser.add_argument("--rebalance-days", nargs="+", type=int, required=True)
    parser.add_argument("--capitals", nargs="+", type=float, required=True)
    parser.add_argument("--quantile", type=float)
    parser.add_argument("--quantiles", nargs="+", type=float)
    parser.add_argument("--participation-rate", type=float, required=True)
    parser.add_argument("--cost-bps", type=float, required=True)
    parser.add_argument("--output")
    args = parser.parse_args()

    quantiles = sorted(
        set(args.quantiles or ([] if args.quantile is None else [args.quantile]))
    )
    if not quantiles:
        parser.error("one of --quantile or --quantiles is required")
    if args.grid_root and len(quantiles) != 1:
        parser.error("legacy --grid-root mode accepts exactly one quantile")

    errors: list[str] = []
    policies: list[dict[str, object]] = []
    expected_capitals = sorted(set(args.capitals))
    expected: list[tuple[float, float, int]] = [
        (quantile, exit_quantile, rebalance_days)
        for quantile in quantiles
        for exit_quantile in sorted(set(args.exit_quantiles))
        if exit_quantile >= quantile
        for rebalance_days in sorted(set(args.rebalance_days))
    ]

    if args.frontier_csv:
        source_path = Path(args.frontier_csv).resolve()
        if not source_path.is_file():
            errors.append(f"missing frontier csv: {source_path}")
            raw_rows: list[dict[str, str]] = []
        else:
            raw_rows = _read(source_path)
        for quantile, exit_quantile, rebalance_days in expected:
            tag = (
                f"Q{round(quantile * 100):02d}_"
                f"E{round(exit_quantile * 100):02d}_R{rebalance_days:02d}"
            )
            summary = _policy_summary(
                raw_rows,
                tag=tag,
                quantile=quantile,
                exit_quantile=exit_quantile,
                rebalance_days=rebalance_days,
                participation_rate=args.participation_rate,
                cost_bps=args.cost_bps,
                expected_capitals=expected_capitals,
                errors=errors,
            )
            if summary is not None:
                summary["source_csv_sha256"] = _hash(source_path)
                policies.append(summary)
        source_description = str(source_path)
        source_mode = "single_cartesian_frontier"
    else:
        root = Path(args.grid_root).resolve()
        quantile = quantiles[0]
        for _, exit_quantile, rebalance_days in expected:
            tag = f"E{round(exit_quantile * 100):02d}_R{rebalance_days:02d}"
            csv_path = root / tag / "capacity_frontier.csv"
            if not csv_path.is_file():
                errors.append(f"missing policy artifact: {tag}")
                continue
            summary = _policy_summary(
                _read(csv_path),
                tag=tag,
                quantile=quantile,
                exit_quantile=exit_quantile,
                rebalance_days=rebalance_days,
                participation_rate=args.participation_rate,
                cost_bps=args.cost_bps,
                expected_capitals=expected_capitals,
                errors=errors,
            )
            if summary is not None:
                summary["source_csv_sha256"] = _hash(csv_path)
                policies.append(summary)
        source_description = str(root)
        source_mode = "legacy_policy_directories"

    expected_policy_count = len(expected)
    if len(policies) != expected_policy_count:
        errors.append(
            f"policy coverage mismatch: expected={expected_policy_count}, "
            f"actual={len(policies)}"
        )
    result = {
        "schema_version": 2,
        "status": "passed" if not errors else "failed",
        "source": source_description,
        "source_mode": source_mode,
        "expected_policy_count": expected_policy_count,
        "actual_policy_count": len(policies),
        "expected_row_count": expected_policy_count * len(expected_capitals),
        "actual_row_count": sum(int(item["capital_count"]) for item in policies),
        "accepted_policy_count": sum(bool(item["accepted_all_capitals"]) for item in policies),
        "policies": sorted(
            policies,
            key=lambda item: (
                item["quantile"], item["exit_quantile"], item["rebalance_days"]
            ),
        ),
        "errors": errors,
    }
    rendered = json.dumps(result, ensure_ascii=False, indent=2) + "\n"
    if args.output:
        output = Path(args.output)
        output.parent.mkdir(parents=True, exist_ok=True)
        output.write_text(rendered, encoding="utf-8")
    print(rendered, end="")
    return 0 if not errors else 1


if __name__ == "__main__":
    raise SystemExit(main())
