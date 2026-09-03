#!/usr/bin/env python3
"""Audit bar1m Parquet and hsjday binary sources without copying raw data."""

from __future__ import annotations

import argparse
import csv
import hashlib
import json
import re
import struct
import sys
from collections import Counter, defaultdict
from datetime import date, datetime, timezone
from pathlib import Path

import pyarrow.parquet as pq

try:
    import tomllib
except ModuleNotFoundError:  # pragma: no cover
    import tomli as tomllib


PARQUET_DATE_RE = re.compile(r"(20\d{2}-\d{2}-\d{2})")
DAY_FILE_RE = re.compile(r"^(bj|sh|sz)\d{6}\.day$", re.IGNORECASE)
DAY_RECORD = struct.Struct("<5if2i")
REQUIRED_BAR_FIELDS = {
    "date",
    "instrument",
    "open",
    "high",
    "low",
    "close",
    "volume",
    "amount",
    "deal_number",
    "ask_price1",
    "bid_price1",
    "ask_volume1",
    "bid_volume1",
}


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--project-root", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--sample-per-year", type=int, default=3)
    parser.add_argument("--day-files-per-exchange", type=int, default=8)
    return parser.parse_args()


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def choose_evenly(paths: list[Path], count: int) -> list[Path]:
    if len(paths) <= count:
        return paths
    if count <= 1:
        return [paths[len(paths) // 2]]
    indexes = {round(index * (len(paths) - 1) / (count - 1)) for index in range(count)}
    return [paths[index] for index in sorted(indexes)]


def parquet_audit(root: Path, sample_per_year: int) -> dict:
    errors: list[str] = []
    warnings: list[str] = []
    manifest_path = root / "manifest.csv"
    manifest_rows: dict[str, dict[str, str]] = {}
    if not manifest_path.is_file():
        errors.append(f"missing manifest: {manifest_path}")
    else:
        with manifest_path.open(newline="", encoding="utf-8-sig") as handle:
            for row in csv.DictReader(handle):
                day = row.get("day", "")
                if day in manifest_rows:
                    errors.append(f"duplicate manifest day: {day}")
                manifest_rows[day] = row
                if row.get("status") != "ok":
                    errors.append(f"manifest status is not ok: {day}")

    files = sorted(root.rglob("*.parquet"))
    by_day: dict[str, Path] = {}
    by_year: defaultdict[int, list[Path]] = defaultdict(list)
    for path in files:
        match = PARQUET_DATE_RE.search(path.name)
        if not match:
            warnings.append(f"unrecognized parquet filename: {path.name}")
            continue
        day = match.group(1)
        if day in by_day:
            errors.append(f"duplicate parquet date: {day}")
        by_day[day] = path
        by_year[int(day[:4])].append(path)

    missing_files = sorted(set(manifest_rows).difference(by_day))
    missing_manifest = sorted(set(by_day).difference(manifest_rows))
    if missing_files:
        errors.append(f"manifest dates without parquet: {missing_files[:5]}")
    if missing_manifest:
        errors.append(f"parquet dates absent from manifest: {missing_manifest[:5]}")

    samples: list[Path] = []
    for year in sorted(by_year):
        samples.extend(choose_evenly(sorted(by_year[year]), sample_per_year))

    schema_fingerprints: Counter[str] = Counter()
    sample_results: list[dict] = []
    for path in samples:
        match = PARQUET_DATE_RE.search(path.name)
        expected_day = match.group(1) if match else ""
        parquet = pq.ParquetFile(path)
        schema_text = str(parquet.schema_arrow)
        schema_id = hashlib.sha256(schema_text.encode("utf-8")).hexdigest()[:16]
        schema_fingerprints[schema_id] += 1
        fields = set(parquet.schema_arrow.names)
        absent = sorted(REQUIRED_BAR_FIELDS.difference(fields))
        if absent:
            errors.append(f"required fields missing in {path.name}: {absent}")
        manifest_row = manifest_rows.get(expected_day)
        expected_rows = int(manifest_row["rows"]) if manifest_row else None
        if expected_rows is not None and expected_rows != parquet.metadata.num_rows:
            errors.append(
                f"row-count mismatch {path.name}: manifest={expected_rows}, parquet={parquet.metadata.num_rows}"
            )
        date_table = pq.read_table(path, columns=["date"])
        values = date_table.column("date")
        first_value = values[0].as_py() if len(values) else None
        last_value = values[-1].as_py() if len(values) else None
        observed_days = {
            value.date().isoformat() if isinstance(value, datetime) else str(value)[:10]
            for value in (first_value, last_value)
            if value is not None
        }
        if observed_days != {expected_day}:
            errors.append(
                f"timestamp/file-date mismatch {path.name}: observed={sorted(observed_days)}"
            )
        sample_results.append(
            {
                "file": str(path),
                "day": expected_day,
                "rows": parquet.metadata.num_rows,
                "schema_id": schema_id,
            }
        )

    if len(schema_fingerprints) > 1:
        errors.append(f"sampled Parquet schema drift: {dict(schema_fingerprints)}")
    days = sorted(by_day)
    return {
        "status": "passed" if not errors else "failed",
        "root": str(root),
        "manifest_sha256": sha256(manifest_path) if manifest_path.is_file() else None,
        "manifest_rows": len(manifest_rows),
        "parquet_files": len(files),
        "first_day": days[0] if days else None,
        "last_day": days[-1] if days else None,
        "files_by_year": {str(year): len(paths) for year, paths in sorted(by_year.items())},
        "sample_count": len(samples),
        "sample_results": sample_results,
        "schema_fingerprints": dict(schema_fingerprints),
        "warnings": warnings,
        "errors": errors,
    }


def valid_yyyymmdd(raw: int) -> bool:
    try:
        date.fromisoformat(f"{raw:08d}"[:4] + "-" + f"{raw:08d}"[4:6] + "-" + f"{raw:08d}"[6:])
        return True
    except ValueError:
        return False


def inspect_day_file(path: Path) -> tuple[dict, list[str]]:
    errors: list[str] = []
    size = path.stat().st_size
    if size % DAY_RECORD.size:
        errors.append(f"record-size remainder in {path.name}: {size % DAY_RECORD.size}")
    count = size // DAY_RECORD.size
    records = []
    if count:
        with path.open("rb") as handle:
            offsets = sorted({0, max(0, count // 2), max(0, count - 1)})
            for offset in offsets:
                handle.seek(offset * DAY_RECORD.size)
                raw = handle.read(DAY_RECORD.size)
                if len(raw) == DAY_RECORD.size:
                    records.append(DAY_RECORD.unpack(raw))
    sampled_dates: list[int] = []
    for raw_date, open_, high, low, close, amount, volume, _ in records:
        sampled_dates.append(raw_date)
        if not valid_yyyymmdd(raw_date):
            errors.append(f"invalid date {raw_date} in {path.name}")
        if high < max(open_, close, low) or low > min(open_, close, high):
            errors.append(f"invalid OHLC relation on {raw_date} in {path.name}")
        if amount < 0 or volume < 0:
            errors.append(f"negative amount/volume on {raw_date} in {path.name}")
    return {
        "file": str(path),
        "bytes": size,
        "records": count,
        "sampled_dates": sampled_dates,
    }, errors


def hsjday_audit(root: Path, files_per_exchange: int) -> dict:
    errors: list[str] = []
    warnings: list[str] = []
    exchange_counts: dict[str, int] = {}
    samples: list[dict] = []
    fingerprint_material: list[str] = []
    for exchange in ("bj", "sh", "sz"):
        directory = root / exchange / "lday"
        files = sorted(directory.glob("*.day")) if directory.is_dir() else []
        exchange_counts[exchange] = len(files)
        if not files:
            errors.append(f"no .day files for exchange {exchange}")
            continue
        malformed = [path.name for path in files if not DAY_FILE_RE.match(path.name)]
        if malformed:
            warnings.append(f"unexpected {exchange} filenames: {malformed[:5]}")
        for path in files:
            size = path.stat().st_size
            fingerprint_material.append(f"{path.relative_to(root).as_posix()}:{size}")
            if size % DAY_RECORD.size:
                errors.append(f"record-size remainder in {path.name}: {size % DAY_RECORD.size}")
        for path in choose_evenly(files, files_per_exchange):
            result, sample_errors = inspect_day_file(path)
            samples.append(result)
            errors.extend(sample_errors)
    source_id = hashlib.sha256("\n".join(fingerprint_material).encode("utf-8")).hexdigest()
    return {
        "status": "passed" if not errors else "failed",
        "root": str(root),
        "record_size": DAY_RECORD.size,
        "files_by_exchange": exchange_counts,
        "size_manifest_sha256": source_id,
        "sample_count": len(samples),
        "sample_results": samples,
        "warnings": warnings,
        "errors": errors,
    }


def main() -> int:
    args = parse_args()
    project_root = args.project_root.resolve()
    config_path = project_root / "configs" / "project.toml"
    config = tomllib.loads(config_path.read_text(encoding="utf-8"))
    bar_root = Path(config["paths"]["bar1m_root"])
    hsjday_root = Path(config["paths"]["hsjday_root"])
    result = {
        "schema_version": 1,
        "audited_at_utc": datetime.now(timezone.utc).isoformat(),
        "project_config_sha256": sha256(config_path),
        "bar1m": parquet_audit(bar_root, args.sample_per_year),
        "hsjday": hsjday_audit(hsjday_root, args.day_files_per_exchange),
    }
    result["status"] = (
        "passed"
        if result["bar1m"]["status"] == "passed" and result["hsjday"]["status"] == "passed"
        else "failed"
    )
    args.output.parent.mkdir(parents=True, exist_ok=True)
    rendered = json.dumps(result, ensure_ascii=False, indent=2)
    args.output.write_text(rendered + "\n", encoding="utf-8")
    print(rendered)
    return 0 if result["status"] == "passed" else 1


if __name__ == "__main__":
    sys.exit(main())
