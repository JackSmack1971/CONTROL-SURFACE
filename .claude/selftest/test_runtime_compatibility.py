"""Offline evidence regressions; no Claude/model invocation."""
import json
from datetime import datetime, timedelta, timezone
from pathlib import Path
import sys
import tempfile
import unittest
from unittest.mock import patch

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "hooks"))
from runtime_compatibility import SURFACES, binding, compatibility


class CompatibilityTests(unittest.TestCase):
    def test_evidence_lifecycle(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            state = root / ".claude/state"
            state.mkdir(parents=True)
            instruction = root / "CLAUDE.md"
            instruction.write_text("canary", encoding="utf-8")
            evidence_path = state / "runtime-validation.json"
            self.assertEqual(compatibility(root, "v1")["status"], "missing")
            evidence = {"schema_version": 2, "binding": binding(root, "v1"),
                        "validated_at": (datetime.now(timezone.utc) - timedelta(minutes=1)).isoformat(),
                        "surfaces": dict.fromkeys(SURFACES, "pass")}
            def save():
                evidence_path.write_text(json.dumps(evidence), encoding="utf-8")
            save()
            self.assertEqual(compatibility(root, "v1")["status"], "verified")
            evidence["surfaces"].pop("shell_permission_forms")
            save()
            self.assertEqual(compatibility(root, "v1")["status"], "invalid")
            evidence["surfaces"]["shell_permission_forms"] = "skip"
            save()
            self.assertEqual(compatibility(root, "v1")["status"], "invalid")
            evidence["surfaces"]["shell_permission_forms"] = "pass"
            save()
            self.assertEqual(compatibility(root, "v1")["status"], "verified")
            self.assertEqual(compatibility(root, "v2")["status"], "stale")
            self.assertEqual(compatibility(root, None)["status"], "stale")
            instruction.write_text("edited", encoding="utf-8")
            self.assertEqual(compatibility(root, "v1")["status"], "stale")
            instruction.write_text("canary", encoding="utf-8")
            for name in ("settings.json", "hooks/guard.py", "skills/demo/SKILL.md",
                         "rules/demo.md", "agents/demo.md", "bin/helper.py"):
                control = root / ".claude" / name
                control.parent.mkdir(parents=True, exist_ok=True)
                control.write_text("original", encoding="utf-8")
                evidence["binding"] = binding(root, "v1")
                save()
                self.assertEqual(compatibility(root, "v1")["status"], "verified")
                control.write_text("changed", encoding="utf-8")
                self.assertEqual(compatibility(root, "v1")["status"], "stale")
                control.unlink()
            evidence["binding"] = binding(root, "v1")
            save()
            agent = root / ".claude/agents/new.md"
            agent.parent.mkdir(exist_ok=True)
            agent.write_text("new", encoding="utf-8")
            self.assertEqual(compatibility(root, "v1")["status"], "stale")
            agent.unlink()
            instruction.unlink()
            self.assertEqual(compatibility(root, "v1")["status"], "stale")
            instruction.write_text("canary", encoding="utf-8")
            evidence["binding"]["platform"] = "another platform"
            save()
            self.assertEqual(compatibility(root, "v1")["status"], "stale")
            evidence["surfaces"]["instruction_symlink_denied"] = "skip"
            save()
            self.assertEqual(compatibility(root, "v1")["status"], "invalid")
            evidence_path.write_text("{", encoding="utf-8")
            self.assertEqual(compatibility(root, "v1")["status"], "invalid")
            evidence_path.write_text('{"schema_version": 1}', encoding="utf-8")
            self.assertEqual(compatibility(root, "v1")["status"], "invalid")

    def test_evidence_freshness(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            state = root / ".claude/state"
            state.mkdir(parents=True)
            (root / "CLAUDE.md").write_text("canary", encoding="utf-8")
            evidence_path = state / "runtime-validation.json"
            evidence = {"schema_version": 2, "binding": binding(root, "v1"),
                        "validated_at": "", "surfaces": dict.fromkeys(SURFACES, "pass")}

            evidence["validated_at"] = (
                datetime.now(timezone.utc) - timedelta(days=90, seconds=1)
            ).isoformat()
            evidence_path.write_text(json.dumps(evidence), encoding="utf-8")
            result = compatibility(root, "v1")
            self.assertEqual(result["status"], "stale")
            self.assertIn("runtime evidence is older than 90 days", result["reasons"])

            evidence["validated_at"] = (
                datetime.now(timezone.utc) + timedelta(seconds=1)
            ).isoformat()
            evidence_path.write_text(json.dumps(evidence), encoding="utf-8")
            self.assertEqual(compatibility(root, "v1")["status"], "invalid")

    def test_exactly_90_days_old_evidence_is_fresh(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            state = root / ".claude/state"
            state.mkdir(parents=True)
            (root / "CLAUDE.md").write_text("canary", encoding="utf-8")
            now = datetime(2030, 1, 1, tzinfo=timezone.utc)
            evidence_path = state / "runtime-validation.json"
            evidence = {"schema_version": 2, "binding": binding(root, "v1"),
                        "validated_at": (now - timedelta(days=90)).isoformat(),
                        "surfaces": dict.fromkeys(SURFACES, "pass")}
            evidence_path.write_text(json.dumps(evidence), encoding="utf-8")

            with patch("runtime_compatibility.datetime") as mocked_datetime:
                mocked_datetime.now.return_value = now
                mocked_datetime.fromisoformat.side_effect = datetime.fromisoformat
                self.assertEqual(compatibility(root, "v1")["status"], "verified")


if __name__ == "__main__":
    unittest.main()
