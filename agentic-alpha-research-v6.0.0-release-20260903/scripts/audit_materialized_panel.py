#!/usr/bin/env python3
"""Fail-closed audit for a materialized Agentic Alpha daily panel."""

from __future__ import annotations

import argparse
import hashlib
import json
import sys
from collections import Counter
from datetime import datetime, timezone
from pathlib import Path

import numpy as np
import pyarrow.parquet as pq

from agentic_alpha.config import load_project_config
from agentic_alpha.firewall import TimeFirewall
from agentic_alpha.materializer import _content_hash


METADATA_KEYS = (
    b"agentic_alpha.materializer_version",
    b"agentic_alpha.source",
    b"agentic_alpha.source_date",
    b"agentic_alpha.content_hash",
)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--project-root", type=Path, required=True)
    parser.add_argument("--panel-root", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--purpose", choices=("development", "audit"), default="development")
    parser.add_argument("--ledger", type=Path)
    parser.add_argument(
        "--expected-dates-file",
        type=Path,
        help="Regression fixtures only; one ISO date per line.",
    )
    return parser.parse_args()


def decode_metadata(raw: dict[bytes, bytes] | None) -> dict[str, str]:
    metadata = raw or {}
    return {
        key.decode("ascii"): metadata.get(key, b"").decode("utf-8", errors="replace")
        for key in METADATA_KEYS
    }


def schema_id(parquet_file: pq.ParquetFile) -> str:
    schema_text = str(parquet_file.schema_arrow.remove_metadata()).encode("utf-8")
    return hashlib.sha256(schema_text).hexdigest()[:16]


def load_expected_sources(args: argparse.Namespace) -> dict[str, Path]:
    config = load_project_config(args.project_root / "configs" / "project.toml")
    sources = TimeFirewall(config).discover(config.bar1m_root, args.purpose)
    by_date = {source.stem.rsplit("_", maxsplit=1)[-1]: source for source in sources}
    if len(by_date) != len(sources):
        raise ValueError("source discovery contains duplicate dates")
    if args.expected_dates_file is None:
        return by_date
    requested = {
        line.strip()
        for line in args.expected_dates_file.read_text(encoding="utf-8").splitlines()
        if line.strip()
    }
    unknown = sorted(requested.difference(by_date))
    if unknown:
        raise ValueError(f"expected-dates fixture contains unknown dates: {unknown}")
    return {date: by_date[date] for date in sorted(requested)}


def load_ledger(path: Path) -> tuple[list[dict], list[str]]:
    records: list[dict] = []
    errors: list[str] = []
    if not path.exists():
        return records, [f"missing ledger: {path}"]
    for line_number, line in enumerate(path.read_text(encoding="utf-8").splitlines(), start=1):
        if not line.strip():
            continue
        try:
            value = json.loads(line)
        except json.JSONDecodeError as exc:
            errors.append(f"ledger line {line_number}: {exc.msg}")
            continue
        if not isinstance(value, dict):
            errors.append(f"ledger line {line_number}: expected object")
            continue
        records.append(value)
    return records, errors


def audit(args: argparse.Namespace) -> dict:
    expected_sources = load_expected_sources(args)
    expected_dates = set(expected_sources)
    parquet_paths = sorted(args.panel_root.rglob("daily_primitives_*.parquet"))
    actual_dates = {
        path.stem.rsplit("_", maxsplit=1)[-1]
        for path in parquet_paths
    }
    errors: list[str] = []
    missing_dates = sorted(expected_dates.difference(actual_dates))
    extra_dates = sorted(actual_dates.difference(expected_dates))
    if missing_dates:
        errors.append(f"missing dates: {missing_dates[:20]} (count={len(missing_dates)})")
    if extra_dates:
        errors.append(f"extra dates: {extra_dates[:20]} (count={len(extra_dates)})")
    if len(actual_dates) != len(parquet_paths):
        errors.append("duplicate output date shards detected")

    schema_counts: Counter[str] = Counter()
    version_counts: Counter[str] = Counter()
    total_rows = 0
    checked_files = 0
    for path in parquet_paths:
        date_token = path.stem.rsplit("_", maxsplit=1)[-1]
        local_errors: list[str] = []
        try:
            parquet_file = pq.ParquetFile(path)
            metadata = decode_metadata(parquet_file.metadata.metadata)
            rows = parquet_file.metadata.num_rows
            total_rows += rows
            if rows <= 0:
                local_errors.append("empty shard")
            if path.parent.name != date_token[:4]:
                local_errors.append("year directory disagrees with filename")
            if metadata["agentic_alpha.source_date"] != date_token:
                local_errors.append("source_date metadata disagrees with filename")
            expected_source = expected_sources.get(date_token)
            if expected_source is None:
                local_errors.append("date is not admitted by active source discovery")
            elif metadata["agentic_alpha.source"] != expected_source.name:
                local_errors.append("source metadata disagrees with admitted source")
            if not metadata["agentic_alpha.materializer_version"]:
                local_errors.append("missing materializer version")
            if len(metadata["agentic_alpha.content_hash"]) != 64:
                local_errors.append("missing or malformed content hash")

            table = pq.read_table(path, use_threads=False)
            frame = table.to_pandas(split_blocks=True, self_destruct=True)
            if len(frame) != rows:
                local_errors.append("table row count disagrees with parquet metadata")
            required = {"date", "instrument"}
            if not required.issubset(frame.columns):
                local_errors.append("missing date or instrument key column")
            else:
                normalized_dates = frame["date"].dt.normalize().dt.date.astype(str).unique()
                if len(normalized_dates) != 1 or normalized_dates[0] != date_token:
                    local_errors.append("data date values disagree with shard date")
                if frame.duplicated(["date", "instrument"]).any():
                    local_errors.append("duplicate (date, instrument) keys")
                if frame["instrument"].isna().any():
                    local_errors.append("null instrument keys")
            numeric = frame.select_dtypes(include=["number"])
            if numeric.size and np.isinf(numeric.to_numpy(dtype="float64", copy=False)).any():
                local_errors.append("infinite numeric value")
            recomputed = _content_hash(frame)
            if recomputed != metadata["agentic_alpha.content_hash"]:
                local_errors.append("recomputed content hash mismatch")
            schema_counts[schema_id(parquet_file)] += 1
            version_counts[metadata["agentic_alpha.materializer_version"]] += 1
            checked_files += 1
        except Exception as exc:  # report every bad shard instead of stopping early
            local_errors.append(f"read failure: {type(exc).__name__}: {exc}")
        errors.extend(f"{path}: {message}" for message in local_errors)

    if len(schema_counts) != 1:
        errors.append(f"schema drift detected: {dict(schema_counts)}")

    ledger_path = args.ledger or (args.panel_root / "materialization_ledger.jsonl")
    ledger_records, ledger_errors = load_ledger(ledger_path)
    errors.extend(ledger_errors)
    ledger_dates = {
        str(record.get("source_date", ""))
        for record in ledger_records
        if record.get("source_date")
    }
    ledger_missing_dates = sorted(expected_dates.difference(ledger_dates))
    if ledger_missing_dates:
        errors.append(
            f"ledger missing dates: {ledger_missing_dates[:20]} (count={len(ledger_missing_dates)})"
        )

    result = {
        "schema_version": 1,
        "audited_at_utc": datetime.now(timezone.utc).isoformat(),
        "status": "passed" if not errors else "failed",
        "purpose": args.purpose,
        "project_root": str(args.project_root.resolve()),
        "panel_root": str(args.panel_root.resolve()),
        "fixture_date_override": args.expected_dates_file is not None,
        "expected_date_count": len(expected_dates),
        "actual_date_count": len(actual_dates),
        "checked_file_count": checked_files,
        "total_rows": total_rows,
        "first_date": min(actual_dates) if actual_dates else None,
        "last_date": max(actual_dates) if actual_dates else None,
        "year_counts": dict(sorted(Counter(date[:4] for date in actual_dates).items())),
        "schema_counts": dict(schema_counts),
        "materializer_version_counts": dict(version_counts),
        "ledger_record_count": len(ledger_records),
        "missing_dates": missing_dates,
        "extra_dates": extra_dates,
        "ledger_missing_dates": ledger_missing_dates,
        "errors": errors,
    }
    args.output.parent.mkdir(parents=True, exist_ok=True)
    temporary = args.output.with_suffix(args.output.suffix + ".tmp")
    temporary.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    temporary.replace(args.output)
    return result


def main() -> int:
    args = parse_args()
    result = audit(args)
    print(json.dumps(result, indent=2, sort_keys=True))
    return 0 if result["status"] == "passed" else 1


if __name__ == "__main__":
    sys.exit(main())
