"""Offline evidence regressions; no Claude/model invocation."""
import json
from pathlib import Path
import sys
import tempfile
import unittest

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
                        "validated_at": "2026-10-05T00:00:00Z",
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


if __name__ == "__main__":
    unittest.main()
