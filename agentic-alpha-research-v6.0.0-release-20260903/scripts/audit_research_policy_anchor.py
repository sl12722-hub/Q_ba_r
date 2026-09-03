from __future__ import annotations

import argparse
import csv
import hashlib
import json
import math
from pathlib import Path
import sys


def file_sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def audit_anchor(
    research: dict,
    rows: list[dict[str, str]],
    *,
    expected_capitals: set[float],
) -> dict[str, object]:
    contract = research.get("portfolio_contract")
    if not isinstance(contract, dict):
        raise ValueError("research report lacks portfolio_contract")
    quantile = float(contract["quantile"])
    cost_bps = float(contract["one_way_cost_bps"])
    anchor_rows = [
        row
        for row in rows
        if math.isclose(float(row["quantile"]), quantile, abs_tol=1e-12)
        and math.isclose(float(row["exit_quantile"]), quantile, abs_tol=1e-12)
        and int(float(row["rebalance_days"])) == 1
        and math.isclose(float(row["cost_bps"]), cost_bps, abs_tol=1e-12)
    ]
    counts: dict[float, int] = {}
    for row in anchor_rows:
        capital = float(row["initial_capital"])
        counts[capital] = counts.get(capital, 0) + 1
    missing = sorted(expected_capitals - set(counts))
    unexpected = sorted(set(counts) - expected_capitals)
    duplicates = sorted(capital for capital, count in counts.items() if count != 1)
    complete = not missing and not unexpected and not duplicates
    all_capitals_pass = complete and all(
        row.get("gate_accepted", "").strip().lower() == "true"
        for row in anchor_rows
    )
    metrics = [
        {
            "capital": float(row["initial_capital"]),
            "total_return": float(row["total_return"]),
            "sharpe": float(row["sharpe"]),
            "fill_rate": float(row["fill_rate"]),
            "gate_accepted": row.get("gate_accepted", "").strip().lower() == "true",
        }
        for row in sorted(anchor_rows, key=lambda item: float(item["initial_capital"]))
    ]
    return {
        "schema_version": 1,
        "anchor_policy": {
            "quantile": quantile,
            "exit_quantile": quantile,
            "rebalance_days": 1,
            "cost_bps": cost_bps,
        },
        "expected_capitals": sorted(expected_capitals),
        "anchor_row_count": len(anchor_rows),
        "missing_capitals": missing,
        "unexpected_capitals": unexpected,
        "duplicate_capitals": duplicates,
        "anchor_complete": complete,
        "all_capitals_pass": all_capitals_pass,
        "metrics": metrics,
        "decision": (
            "capacity_anchor_passed"
            if all_capitals_pass
            else "reject_executable_promotion"
        ),
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--research-report", required=True)
    parser.add_argument("--capacity-csv", required=True)
    parser.add_argument("--expected-capitals", nargs="+", type=float, required=True)
    parser.add_argument("--output-json")
    args = parser.parse_args()
    research_path = Path(args.research_report).resolve()
    capacity_path = Path(args.capacity_csv).resolve()
    research = json.loads(research_path.read_text(encoding="utf-8"))
    with capacity_path.open("r", encoding="utf-8", newline="") as handle:
        rows = list(csv.DictReader(handle))
    result = audit_anchor(
        research,
        rows,
        expected_capitals=set(args.expected_capitals),
    )
    result["sources"] = {
        "research_report": {"path": str(research_path), "sha256": file_sha256(research_path)},
        "capacity_csv": {"path": str(capacity_path), "sha256": file_sha256(capacity_path)},
    }
    rendered = json.dumps(result, ensure_ascii=False, indent=2) + "\n"
    if args.output_json:
        Path(args.output_json).write_text(rendered, encoding="utf-8")
    print(rendered, end="")
    return 0 if result["all_capitals_pass"] else 2


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except Exception as exc:
        print(f"error: {exc}", file=sys.stderr)
        raise
