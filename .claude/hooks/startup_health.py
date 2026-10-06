#!/usr/bin/env python3
"""Lightweight SessionStart control-plane health diagnostic and live-hook canary."""
from __future__ import annotations

from datetime import datetime, timezone
import json
import os
import platform
from pathlib import Path
import shutil
import subprocess
import sys
from runtime_compatibility import compatibility

from control_common import deadline_after, find_project_root, read_baseline, read_surface, state_dir, validate_binding, write_json_atomic

REQUIRED = [
    "CLAUDE.md", ".claude/settings.json", ".claude/MANIFEST.json",
    ".claude/CONTROL-SURFACE.md", ".claude/EVALUATION.md",
    ".claude/hooks/pretool_guard.py", ".claude/hooks/change_surface_guard.py",
    ".claude/hooks/posttool_scope_audit.py", ".claude/hooks/completion_gate.py",
]


def now_iso() -> str:
    return datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")


def main() -> None:
    try:
        payload = json.load(sys.stdin)
        cwd = payload.get("cwd") if isinstance(payload, dict) else None
    except Exception:
        cwd = None
    root = find_project_root(cwd or os.getcwd())
    deadline = deadline_after(6.0)
    issues: list[str] = []
    missing = [p for p in REQUIRED if not (root / p).is_file()]
    if missing:
        issues.append("missing required files: " + ", ".join(missing))
    if shutil.which("git") is None:
        issues.append("git executable is unavailable")
    try:
        json.loads((root / ".claude/settings.json").read_text(encoding="utf-8"))
        manifest = json.loads((root / ".claude/MANIFEST.json").read_text(encoding="utf-8"))
    except Exception as exc:
        manifest = {}
        issues.append(f"settings/manifest parse failed: {type(exc).__name__}")

    active = False
    try:
        surface = read_surface(root)
        if surface is not None:
            active = True
            baseline = read_baseline(root)
            validate_binding(root, surface, baseline, deadline)
    except Exception as exc:
        issues.append(f"active task authority invalid/stale: {exc}")

    claude_version = None
    claude = shutil.which("claude")
    if claude:
        try:
            proc = subprocess.run([claude, "--version"], capture_output=True, text=True, timeout=2, check=False)
            if proc.returncode == 0:
                claude_version = proc.stdout.strip() or proc.stderr.strip()
        except Exception:
            pass

    windows = platform.system().lower() == "windows"
    posture = "defense-in-depth-only" if windows else "host-dependent"
    report = {
        "schema_version": 1,
        "observed_at": now_iso(),
        "status": "unhealthy" if issues else "healthy",
        "issues": issues,
        "python": sys.version.split()[0],
        "platform": platform.platform(),
        "claude_version_observed": claude_version,
        "runtime_compatibility": compatibility(root, claude_version),
        "live_session_start_hook_observed": True,
        "active_task_state": active,
        "containment_posture": posture,
        "containment_note": (
            "Native Windows project hooks/permissions are defense in depth and are not equivalent to an OS filesystem/network sandbox."
            if windows else "Effective filesystem/network/credential containment depends on the host Claude Code runtime and managed policy."
        ),
        "manifest_runtime_validation_status": manifest.get("runtime_validation", {}).get("status"),
    }
    write_json_atomic(state_dir(root) / "control-plane-health.json", report)
    if issues:
        sys.stderr.write("CONTROL PLANE UNHEALTHY: " + "; ".join(issues) + "\n")
        raise SystemExit(2)
    sys.stdout.write(
        "Control-plane startup health: healthy. Containment posture: " + posture
        + ". Runtime compatibility: " + report["runtime_compatibility"]["status"]
        + ". Live SessionStart hook executed; see RUNTIME-VALIDATION.md for evidence requirements.\n"
    )


if __name__ == "__main__":
    main()
