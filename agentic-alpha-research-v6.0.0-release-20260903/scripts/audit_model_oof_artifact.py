from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path

import numpy as np
import pandas as pd


def _sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for block in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--research-report", required=True)
    parser.add_argument("--output")
    args = parser.parse_args()

    report_path = Path(args.research_report).resolve()
    report = json.loads(report_path.read_text(encoding="utf-8"))
    oof_path = report_path.parent / "oof_predictions.parquet"
    errors: list[str] = []
    if not oof_path.is_file():
        raise ValueError(f"missing OOF artifact: {oof_path}")

    required = {"date", "instrument", "factor", "target", "fold_id"}
    frame = pd.read_parquet(oof_path, columns=sorted(required))
    missing = sorted(required - set(frame.columns))
    if missing:
        errors.append(f"missing columns: {missing}")
    frame["date"] = pd.to_datetime(frame["date"], errors="coerce").dt.normalize()
    expected_rows = int(report.get("oof_rows", -1))
    if expected_rows != len(frame):
        errors.append(f"OOF row mismatch: report={expected_rows}, artifact={len(frame)}")
    duplicate_count = int(frame.duplicated(["date", "instrument"]).sum())
    if duplicate_count:
        errors.append(f"duplicate date/instrument keys: {duplicate_count}")
    folds_per_date = frame.groupby("date", observed=True)["fold_id"].nunique()
    overlapping_dates = int((folds_per_date > 1).sum())
    if overlapping_dates:
        errors.append(f"test dates assigned to multiple folds: {overlapping_dates}")
    expected_folds = int(report.get("model_contract", {}).get("fold_count", -1))
    actual_folds = int(frame["fold_id"].nunique())
    if expected_folds != actual_folds:
        errors.append(f"fold mismatch: report={expected_folds}, artifact={actual_folds}")
    holdout_rows = int((frame["date"].dt.year == 2023).sum())
    if holdout_rows:
        errors.append(f"2023 holdout rows present: {holdout_rows}")
    nonfinite_factors = int((~np.isfinite(pd.to_numeric(frame["factor"], errors="coerce"))).sum())
    if nonfinite_factors:
        errors.append(f"non-finite factor predictions: {nonfinite_factors}")

    result = {
        "schema_version": 1,
        "status": "passed" if not errors else "failed",
        "research_report": str(report_path),
        "oof_artifact": str(oof_path),
        "oof_sha256": _sha256(oof_path),
        "rows": len(frame),
        "unique_dates": int(frame["date"].nunique()),
        "first_date": frame["date"].min().date().isoformat(),
        "last_date": frame["date"].max().date().isoformat(),
        "fold_count": actual_folds,
        "duplicate_key_count": duplicate_count,
        "overlapping_fold_date_count": overlapping_dates,
        "holdout_2023_rows": holdout_rows,
        "nonfinite_factor_count": nonfinite_factors,
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
