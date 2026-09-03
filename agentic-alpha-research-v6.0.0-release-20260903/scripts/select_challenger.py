#!/usr/bin/env python3
"""Select champion generations from a capacity-frontier CSV and checkpoint state."""

from __future__ import annotations

import argparse
import csv
import hashlib
import json
import math
import sys
from datetime import datetime, timezone
from pathlib import Path


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--frontier-csv", type=Path, required=True)
    parser.add_argument("--axis", default="quantile")
    parser.add_argument(
        "--values",
        nargs="+",
        required=True,
        help="Ordered axis values representing T001, T002, ...",
    )
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--factor-id", required=True)
    parser.add_argument("--protocol-id", required=True)
    parser.add_argument(
        "--checkpoint-input",
        type=Path,
        help="Prior checkpoint to resume; output must be a new file.",
    )
    parser.add_argument(
        "--new-hypothesis",
        help="Falsifiable branch hypothesis. Supplying it resets branch failure count.",
    )
    parser.add_argument("--min-return", type=float, default=0.10)
    parser.add_argument("--min-sharpe", type=float, default=2.0)
    parser.add_argument("--min-fill", type=float, default=0.90)
    parser.add_argument("--min-improvement", type=float, default=0.01)
    parser.add_argument("--overwrite", action="store_true")
    return parser.parse_args()


def number(value: str) -> float:
    parsed = float(value)
    if not math.isfinite(parsed):
        raise ValueError(f"non-finite value: {value}")
    return parsed


def same_value(left: str, right: str) -> bool:
    return math.isclose(number(left), number(right), rel_tol=1e-10, abs_tol=1e-12)


def summarize(rows: list[dict[str, str]]) -> dict:
    returns = [number(row["total_return"]) for row in rows]
    sharpes = [number(row["sharpe"]) for row in rows]
    fills = [number(row["fill_rate"]) for row in rows]
    capitals = {
        row["initial_capital"]: {
            "total_return": number(row["total_return"]),
            "sharpe": number(row["sharpe"]),
            "fill_rate": number(row["fill_rate"]),
        }
        for row in rows
    }
    return {
        "capital_count": len(rows),
        "min_total_return": min(returns),
        "mean_total_return": sum(returns) / len(returns),
        "min_sharpe": min(sharpes),
        "min_fill_rate": min(fills),
        "by_capital": capitals,
    }


def main() -> int:
    args = parse_args()
    if args.output.exists() and not args.overwrite:
        raise FileExistsError(f"refusing to overwrite checkpoint: {args.output}")
    raw_csv = args.frontier_csv.read_bytes()
    with args.frontier_csv.open(newline="", encoding="utf-8-sig") as handle:
        source_rows = list(csv.DictReader(handle))

    selected_rows = [row for row in source_rows if row.get("axis") == args.axis]
    generations: list[dict] = []
    champion: dict | None = None
    failure_streak = 0
    open_hypotheses: list[str] = []
    exhausted_branches: list[dict] = []
    if args.checkpoint_input:
        prior = json.loads(args.checkpoint_input.read_text(encoding="utf-8"))
        if prior.get("factor_id") != args.factor_id:
            raise ValueError("checkpoint factor_id does not match")
        if prior.get("protocol_id") != args.protocol_id:
            raise ValueError("checkpoint protocol_id does not match")
        generations = list(prior.get("generations", []))
        champion = prior.get("champion")
        failure_streak = int(prior.get("consecutive_failure_count", 0))
        open_hypotheses = list(prior.get("open_hypotheses", []))
        exhausted_branches = list(prior.get("exhausted_branches", []))
        if args.new_hypothesis:
            exhausted_branches.append(
                {
                    "ended_after_generation": len(generations),
                    "failure_count": failure_streak,
                    "reason": "new falsifiable hypothesis opened",
                }
            )
            failure_streak = 0
            open_hypotheses.append(args.new_hypothesis)

    start_generation = len(generations) + 1
    for index, requested_value in enumerate(args.values, start=start_generation):
        rows = [
            row
            for row in selected_rows
            if same_value(row.get("axis_value", "nan"), requested_value)
        ]
        record = {
            "generation": index,
            "label": f"T{index:03d}",
            "axis": args.axis,
            "axis_value": number(requested_value),
        }
        if not rows:
            record.update({"status": "missing", "reasons": ["axis value absent from frontier"]})
            failure_streak += 1
            generations.append(record)
            continue

        metrics = summarize(rows)
        gate_reasons: list[str] = []
        if metrics["min_total_return"] < args.min_return:
            gate_reasons.append("minimum capital return below gate")
        if metrics["min_sharpe"] < args.min_sharpe:
            gate_reasons.append("minimum capital Sharpe below gate")
        if metrics["min_fill_rate"] < args.min_fill:
            gate_reasons.append("minimum capital fill rate below gate")

        promoted = False
        if not gate_reasons:
            if champion is None:
                promoted = True
            else:
                improvement = (
                    metrics["mean_total_return"]
                    - champion["metrics"]["mean_total_return"]
                )
                if improvement >= args.min_improvement:
                    promoted = True
                else:
                    gate_reasons.append(
                        f"mean return improvement {improvement:.6f} below {args.min_improvement:.6f}"
                    )

        record.update(
            {
                "status": "promoted" if promoted else "rejected",
                "metrics": metrics,
                "reasons": gate_reasons,
            }
        )
        if promoted:
            champion = record
            failure_streak = 0
        else:
            failure_streak += 1
        generations.append(record)

    checkpoint = {
        "schema_version": 1,
        "created_at_utc": datetime.now(timezone.utc).isoformat(),
        "factor_id": args.factor_id,
        "protocol_id": args.protocol_id,
        "source_csv": str(args.frontier_csv.resolve()),
        "source_csv_sha256": hashlib.sha256(raw_csv).hexdigest(),
        "evidence_label": "diagnostic_only",
        "objective": "maximize mean total return subject to all-capital gates",
        "gates": {
            "min_total_return": args.min_return,
            "min_sharpe": args.min_sharpe,
            "min_fill_rate": args.min_fill,
            "min_improvement": args.min_improvement,
        },
        "generations": generations,
        "champion": champion,
        "next_generation": len(generations) + 1,
        "consecutive_failure_count": failure_streak,
        "stop_recommended": failure_streak >= 3,
        "open_hypotheses": open_hypotheses,
        "exhausted_branches": exhausted_branches,
    }
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(
        json.dumps(checkpoint, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
    )
    print(json.dumps(checkpoint, ensure_ascii=False, indent=2))
    return 0 if champion else 1


if __name__ == "__main__":
    sys.exit(main())
