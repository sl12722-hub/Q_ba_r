#!/usr/bin/env python3
"""Audit the local Agentic Alpha data split before an experiment starts."""

from __future__ import annotations

import argparse
import hashlib
import json
import re
import sys
from datetime import date
from pathlib import Path

try:
    import tomllib
except ModuleNotFoundError:  # pragma: no cover - Python 3.10 compatibility
    import tomli as tomllib


DATE_RE = re.compile(r"(20\d{2}-\d{2}-\d{2})")
EXPECTED_DEVELOPMENT = (
    (date(2019, 1, 1), date(2022, 12, 31)),
    (date(2024, 1, 1), date(2024, 12, 31)),
)
EXPECTED_AUDIT = (date(2023, 1, 1), date(2023, 12, 31))


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--project-root",
        type=Path,
        required=True,
        help="Agentic Alpha project containing configs/project.toml.",
    )
    parser.add_argument("--json-output", type=Path)
    return parser.parse_args()


def parse_day(value: str) -> date:
    return date.fromisoformat(value)


def normalized_ranges(config: dict) -> tuple[tuple[date, date], ...]:
    ranges = config["periods"]["development"].get("ranges", [])
    return tuple((parse_day(item["start"]), parse_day(item["end"])) for item in ranges)


def discover_dates(root: Path) -> list[date]:
    found: set[date] = set()
    for path in root.rglob("*.parquet"):
        match = DATE_RE.search(path.name)
        if match:
            found.add(parse_day(match.group(1)))
    return sorted(found)


def in_ranges(day: date, ranges: tuple[tuple[date, date], ...]) -> bool:
    return any(start <= day <= end for start, end in ranges)


def main() -> int:
    args = parse_args()
    project_root = args.project_root.resolve()
    config_path = project_root / "configs" / "project.toml"
    errors: list[str] = []
    warnings: list[str] = []

    if not config_path.is_file():
        print(json.dumps({"status": "failed", "errors": [f"missing {config_path}"]}))
        return 2

    raw_config = config_path.read_bytes()
    config = tomllib.loads(raw_config.decode("utf-8"))
    development = normalized_ranges(config)
    audit_cfg = config["periods"]["audit"]
    audit = (parse_day(audit_cfg["start"]), parse_day(audit_cfg["end"]))
    bar_root = Path(config["paths"]["bar1m_root"])
    hsjday_root = Path(config["paths"]["hsjday_root"])

    if development != EXPECTED_DEVELOPMENT:
        errors.append(f"development ranges drifted: {development!r}")
    if audit != EXPECTED_AUDIT:
        errors.append(f"audit range drifted: {audit!r}")
    if config["periods"]["development"].get("feedback_allowed") is not True:
        errors.append("development.feedback_allowed must be true")
    if audit_cfg.get("feedback_allowed") is not False:
        errors.append("audit.feedback_allowed must be false")
    if config.get("protocol", {}).get("chronological_oos") is not False:
        errors.append("protocol must state chronological_oos=false")
    if not bar_root.is_dir():
        errors.append(f"bar1m_root is unavailable: {bar_root}")
    if not hsjday_root.is_dir():
        errors.append(f"hsjday_root is unavailable: {hsjday_root}")

    dates = discover_dates(bar_root) if bar_root.is_dir() else []
    development_dates = [day for day in dates if in_ranges(day, development)]
    audit_dates = [day for day in dates if audit[0] <= day <= audit[1]]
    overlap = sorted(set(development_dates).intersection(audit_dates))
    if overlap:
        errors.append(f"development/audit date overlap: {overlap[:3]}")
    if not development_dates:
        errors.append("no development parquet dates discovered")
    if not audit_dates:
        errors.append("no audit parquet dates discovered")
    if len(development_dates) != 1214:
        warnings.append(f"expected 1214 development dates, found {len(development_dates)}")
    if len(audit_dates) != 242:
        warnings.append(f"expected 242 audit dates, found {len(audit_dates)}")

    protocol_material = {
        "development": [[str(start), str(end)] for start, end in development],
        "audit": [str(audit[0]), str(audit[1])],
        "chronological_oos": config.get("protocol", {}).get("chronological_oos"),
        "bar1m_root": str(bar_root),
        "hsjday_root": str(hsjday_root),
    }
    protocol_id = hashlib.sha256(
        json.dumps(protocol_material, sort_keys=True).encode("utf-8")
    ).hexdigest()[:16]
    result = {
        "status": "passed" if not errors else "failed",
        "protocol_id": protocol_id,
        "project_root": str(project_root),
        "development_date_count": len(development_dates),
        "development_first": str(development_dates[0]) if development_dates else None,
        "development_last": str(development_dates[-1]) if development_dates else None,
        "audit_date_count": len(audit_dates),
        "audit_first": str(audit_dates[0]) if audit_dates else None,
        "audit_last": str(audit_dates[-1]) if audit_dates else None,
        "config_sha256": hashlib.sha256(raw_config).hexdigest(),
        "warnings": warnings,
        "errors": errors,
    }
    rendered = json.dumps(result, ensure_ascii=False, indent=2)
    print(rendered)
    if args.json_output:
        args.json_output.parent.mkdir(parents=True, exist_ok=True)
        args.json_output.write_text(rendered + "\n", encoding="utf-8")
    return 0 if not errors else 1


if __name__ == "__main__":
    sys.exit(main())
