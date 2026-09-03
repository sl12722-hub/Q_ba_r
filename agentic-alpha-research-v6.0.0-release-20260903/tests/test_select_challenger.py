from __future__ import annotations

import csv
import importlib.util
import json
from pathlib import Path
import sys
import tempfile
import unittest
from unittest.mock import patch


SCRIPT = Path(__file__).parents[1] / "scripts" / "select_challenger.py"
SPEC = importlib.util.spec_from_file_location("select_challenger", SCRIPT)
assert SPEC is not None and SPEC.loader is not None
MODULE = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(MODULE)


def write_frontier(path: Path) -> None:
    rows = [
        {
            "axis": "quantile",
            "axis_value": "0.03",
            "initial_capital": str(capital),
            "total_return": "0.2",
            "sharpe": "2.1",
            "fill_rate": "0.95",
        }
        for capital in (100000, 500000, 1000000)
    ]
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(rows[0]))
        writer.writeheader()
        writer.writerows(rows)


class SelectChallengerTests(unittest.TestCase):
    def test_generation_labels_use_trial_namespace(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            frontier = root / "frontier.csv"
            output = root / "checkpoint.json"
            write_frontier(frontier)
            argv = [
                "select_challenger.py",
                "--frontier-csv",
                str(frontier),
                "--values",
                "0.03",
                "--output",
                str(output),
                "--factor-id",
                "demo_factor",
                "--protocol-id",
                "protocol_a",
            ]
            with patch.object(sys, "argv", argv):
                self.assertEqual(MODULE.main(), 0)
            checkpoint = json.loads(output.read_text(encoding="utf-8"))
            self.assertEqual(checkpoint["generations"][0]["label"], "T001")
            self.assertEqual(checkpoint["champion"]["label"], "T001")


if __name__ == "__main__":
    unittest.main()
