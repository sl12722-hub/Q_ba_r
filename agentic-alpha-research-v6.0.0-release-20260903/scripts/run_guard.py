#!/usr/bin/env python3
"""Enforce wall-clock and artifact-storage budgets for autonomous research."""

from __future__ import annotations

import argparse
import json
import os
import sys
from datetime import datetime, timezone
from pathlib import Path

GIB = 1024 ** 3
STATE_NAME = "run_state.json"


def utc_now() -> datetime:
    return datetime.now(timezone.utc)


def parse_utc(value: str) -> datetime:
    parsed = datetime.fromisoformat(value.replace("Z", "+00:00"))
    if parsed.tzinfo is None:
        raise ValueError("deadline must include a timezone")
    return parsed.astimezone(timezone.utc)


def tree_size(root: Path) -> int:
    total = 0
    if not root.exists():
        return total
    for directory, _, files in os.walk(root):
        for name in files:
            path = Path(directory) / name
            try:
                total += path.stat().st_size
            except FileNotFoundError:
                continue
    return total


def atomic_write(path: Path, payload: dict) -> None:
    temporary = path.with_suffix(path.suffix + ".tmp")
    temporary.write_text(
        json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
    )
    temporary.replace(path)


def load_state(run_root: Path) -> dict:
    state_path = run_root / STATE_NAME
    if not state_path.is_file():
        raise FileNotFoundError(f"run guard is not initialized: {state_path}")
    return json.loads(state_path.read_text(encoding="utf-8"))


def evaluate(state: dict, run_root: Path, reserve_bytes: int = 0) -> dict:
    now = utc_now()
    deadline = parse_utc(state["deadline_utc"])
    used = tree_size(run_root)
    maximum = int(state["max_artifact_bytes"])
    reasons: list[str] = []
    if now >= deadline:
        reasons.append("wall_clock_deadline_reached")
    if used >= maximum:
        reasons.append("artifact_cap_reached")
    if used + reserve_bytes > maximum:
        reasons.append("artifact_reservation_would_exceed_cap")
    state.update(
        {
            "last_checked_utc": now.isoformat(),
            "artifact_bytes": used,
            "artifact_gib": used / GIB,
            "remaining_bytes": max(0, maximum - used),
            "remaining_seconds": max(0.0, (deadline - now).total_seconds()),
            "status": "STOPPED" if reasons else "ACTIVE",
            "stop_reasons": reasons,
        }
    )
    atomic_write(run_root / STATE_NAME, state)
    return state


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    subparsers = parser.add_subparsers(dest="command", required=True)

    init_parser = subparsers.add_parser("init")
    init_parser.add_argument("--run-root", type=Path, required=True)
    init_parser.add_argument("--deadline-utc", required=True)
    init_parser.add_argument("--max-gib", type=float, required=True)
    init_parser.add_argument("--skill-version", required=True)

    status_parser = subparsers.add_parser("status")
    status_parser.add_argument("--run-root", type=Path, required=True)
    status_parser.add_argument("--reserve-bytes", type=int, default=0)

    stop_parser = subparsers.add_parser("stop")
    stop_parser.add_argument("--run-root", type=Path, required=True)
    stop_parser.add_argument("--reason", required=True)
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    run_root = args.run_root.resolve()
    run_root.mkdir(parents=True, exist_ok=True)

    if args.command == "init":
        state_path = run_root / STATE_NAME
        if state_path.exists():
            raise FileExistsError(f"refusing to reinitialize {state_path}")
        deadline = parse_utc(args.deadline_utc)
        if deadline <= utc_now():
            raise ValueError("deadline must be in the future")
        state = {
            "schema_version": 1,
            "run_id": run_root.name,
            "skill_version_at_start": args.skill_version,
            "started_at_utc": utc_now().isoformat(),
            "deadline_utc": deadline.isoformat(),
            "max_artifact_bytes": int(args.max_gib * GIB),
            "status": "ACTIVE",
            "stop_reasons": [],
        }
        atomic_write(state_path, state)
        state = evaluate(state, run_root)
    elif args.command == "status":
        state = evaluate(load_state(run_root), run_root, args.reserve_bytes)
    else:
        state = load_state(run_root)
        state.update(
            {
                "status": "STOPPED",
                "stopped_at_utc": utc_now().isoformat(),
                "stop_reasons": [args.reason],
            }
        )
        atomic_write(run_root / STATE_NAME, state)

    print(json.dumps(state, ensure_ascii=False, indent=2))
    return 3 if state["status"] == "STOPPED" else 0


if __name__ == "__main__":
    sys.exit(main())
