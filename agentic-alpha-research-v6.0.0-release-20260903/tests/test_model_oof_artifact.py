from __future__ import annotations

import importlib.util
import json
from pathlib import Path
import sys
import tempfile
import unittest
from unittest.mock import patch

try:
    import pandas as pd
    import pyarrow  # noqa: F401
except ImportError:  # pragma: no cover - optional project dependency
    pd = None


SCRIPT = Path(__file__).parents[1] / "scripts" / "audit_model_oof_artifact.py"
if pd is not None:
    SPEC = importlib.util.spec_from_file_location("audit_model_oof_artifact", SCRIPT)
    assert SPEC is not None and SPEC.loader is not None
    MODULE = importlib.util.module_from_spec(SPEC)
    SPEC.loader.exec_module(MODULE)
else:
    MODULE = None


@unittest.skipIf(pd is None, "pandas is not installed")
class ModelOofArtifactTests(unittest.TestCase):
    def test_missing_oof_columns_are_reported_without_crashing(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            report_path = root / "research.json"
            output_path = root / "oof_audit.json"
            report_path.write_text(
                json.dumps({"oof_rows": 1, "model_contract": {"fold_count": 1}}),
                encoding="utf-8",
            )
            pd.DataFrame(
                {
                    "date": ["2024-01-02"],
                    "instrument": ["000001.SZ"],
                    "factor": [0.1],
                    "fold_id": [1],
                }
            ).to_parquet(root / "oof_predictions.parquet")

            argv = [
                "audit_model_oof_artifact.py",
                "--research-report",
                str(report_path),
                "--output",
                str(output_path),
            ]
            with patch.object(sys, "argv", argv):
                assert MODULE is not None
                self.assertEqual(MODULE.main(), 1)
            payload = json.loads(output_path.read_text(encoding="utf-8"))
            self.assertEqual(payload["status"], "failed")
            self.assertIn("missing columns: ['target']", payload["errors"])


if __name__ == "__main__":
    unittest.main()
