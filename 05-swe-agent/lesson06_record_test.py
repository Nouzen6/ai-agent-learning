import json
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

import lesson06_run_record as records


class TestRunRecord(unittest.TestCase):
    def test_results_roundtrip_without_overwriting(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            log_dir = Path(temp_dir) / "logs"
            saved_paths = []

            with patch.object(records, "LOG_DIR", log_dir):
                for status in ("completed", "tool_limit"):
                    result = {
                        "status": status,
                        "answer": None,
                        "steps": 1,
                        "reason": "中文说明",
                        "trace": [
                            {
                                "step": 1,
                                "event": "model_request",
                            },
                        ],
                    }

                    record_path = records.save_run_record(result)
                    saved_paths.append(record_path)

                    text = record_path.read_text(encoding="utf-8")
                    loaded = json.loads(text)

                    self.assertEqual(loaded["result"], result)
                    self.assertIn("中文说明", text)
                    self.assertTrue(
                        loaded["saved_at"].endswith("+00:00")
                    )
                    self.assertEqual(record_path.parent, log_dir)

            self.assertNotEqual(saved_paths[0], saved_paths[1])
            self.assertEqual(len(list(log_dir.glob("*.json"))), 2)


if __name__ == "__main__":
    unittest.main()