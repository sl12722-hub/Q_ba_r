from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
import sys


REQUIRED_FIELDS = {
    "evaluation_contract": (
        "version",
        "portfolio_selection",
        "future_target_availability_used_for_selection",
        "target_tradable_used_for_selection",
        "turnover_accounting",
    ),
    "walkforward_contract": (
        "min_train_days",
        "test_days",
        "purge_days",
        "embargo_days",
    ),
    "portfolio_contract": (
        "quantile",
        "min_cross_section",
        "one_way_cost_bps",
    ),
    "model_contract": (
        "model",
        "features",
        "target_horizon",
        "prediction_ema_span",
        "seed",
    ),
}


def canonical(value: object) -> str:
    return json.dumps(value, sort_keys=True, separators=(",", ":"))


def file_sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def audit_reports(
    reports: list[dict], allowed_model_differences: set[str]
) -> dict[str, object]:
    reasons: list[str] = []
    for index, report in enumerate(reports):
        for section, required in REQUIRED_FIELDS.items():
            value = report.get(section)
            if not isinstance(value, dict):
                reasons.append(f"report {index} missing {section}")
                continue
            missing = [field for field in required if field not in value]
            if missing:
                reasons.append(
                    f"report {index} {section} missing fields: {','.join(missing)}"
                )
    if not reasons and len(reports) > 1:
        for section in ("evaluation_contract", "walkforward_contract", "portfolio_contract"):
            if len({canonical(report[section]) for report in reports}) != 1:
                reasons.append(f"reports disagree on {section}")
        reduced = []
        for report in reports:
            reduced.append(
                {
                    key: value
                    for key, value in report["model_contract"].items()
                    if key not in allowed_model_differences
                }
            )
        if len({canonical(value) for value in reduced}) != 1:
            reasons.append("reports disagree on undeclared model-contract fields")
    return {
        "schema_version": 1,
        "accepted": not reasons,
        "report_count": len(reports),
        "allowed_model_differences": sorted(allowed_model_differences),
        "reasons": reasons,
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--research-json", nargs="+", required=True)
    parser.add_argument("--allowed-model-differences", nargs="*", default=[])
    parser.add_argument("--output-json")
    args = parser.parse_args()
    paths = [Path(value).resolve() for value in args.research_json]
    reports = [json.loads(path.read_text(encoding="utf-8")) for path in paths]
    result = audit_reports(reports, set(args.allowed_model_differences))
    result["sources"] = [
        {"path": str(path), "sha256": file_sha256(path)} for path in paths
    ]
    rendered = json.dumps(result, ensure_ascii=False, indent=2) + "\n"
    if args.output_json:
        Path(args.output_json).write_text(rendered, encoding="utf-8")
    print(rendered, end="")
    return 0 if result["accepted"] else 2


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except Exception as exc:
        print(f"error: {exc}", file=sys.stderr)
        raise
