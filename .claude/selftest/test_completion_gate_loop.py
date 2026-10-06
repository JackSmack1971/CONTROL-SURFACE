"""Regression coverage for repeated Stop-hook blocks."""
from __future__ import annotations

import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest


ROOT = Path(__file__).resolve().parents[2]
HOOK = ROOT / ".claude" / "hooks" / "completion_gate.py"


class CompletionGateLoopTests(unittest.TestCase):
    def test_continued_stop_does_not_block_again(self) -> None:
        with tempfile.TemporaryDirectory() as temp:
            result = subprocess.run(
                [sys.executable, str(HOOK)],
                input=json.dumps({"cwd": temp, "stop_hook_active": True}),
                text=True,
                capture_output=True,
                check=False,
            )

        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertEqual(result.stderr, "")

    def test_first_stop_still_runs_gate(self) -> None:
        result = subprocess.run(
            [sys.executable, str(HOOK)],
            input=json.dumps({"cwd": str(ROOT), "stop_hook_active": False}),
            text=True,
            capture_output=True,
            check=False,
        )

        self.assertEqual(result.returncode, 2)
        self.assertIn("COMPLETION BLOCKED:", result.stderr)


if __name__ == "__main__":
    unittest.main()
