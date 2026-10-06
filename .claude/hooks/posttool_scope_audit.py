#!/usr/bin/env python3
"""Detect shell-side scope drift by comparing bounded pre/post Git state."""
from __future__ import annotations

import fnmatch
import hashlib
import json
import os
from pathlib import Path
import sys

from control_common import capture_git_state, classify_git_state_changes, deadline_after, find_project_root


def matches(path: str, patterns: list[str]) -> bool:
    return any(fnmatch.fnmatch(path, p.replace("\\", "/")) for p in patterns)


def emit_block(reasons: list[str]) -> None:
    reason = (
        "Shell-side file effects deviated from the pre-command task boundary. The command has already run; "
        "this hook did not prevent or revert it. Inspect the diff/state and recover safely or obtain authorization. Deviations: "
        + "; ".join(reasons[:12])
    )
    if len(reasons) > 12:
        reason += f"; plus {len(reasons) - 12} more"
    print(json.dumps({"decision": "block", "reason": reason}))


def main() -> None:
    deadline = deadline_after(6.0)
    try:
        payload = json.load(sys.stdin)
        if payload.get("tool_name") not in {"Bash", "PowerShell"}:
            raise ValueError("unexpected tool_name")
        tool_use_id = payload.get("tool_use_id")
        if not isinstance(tool_use_id, str) or not tool_use_id:
            raise ValueError("missing tool_use_id")
        root = find_project_root(payload.get("cwd") or os.getcwd())
    except Exception:
        raise SystemExit(0)

    snapshot_path = root / ".claude" / "state" / ".hook-snapshots" / (hashlib.sha256(tool_use_id.encode("utf-8")).hexdigest() + ".json")
    if not snapshot_path.is_file():
        raise SystemExit(0)

    try:
        snapshot = json.loads(snapshot_path.read_text(encoding="utf-8"))
        snapshot_path.unlink(missing_ok=True)
        before = snapshot.get("git", {})
        surface = snapshot.get("state", {})
        baseline = snapshot.get("baseline", {})
        if not isinstance(before, dict) or not isinstance(surface, dict) or not isinstance(baseline, dict):
            raise ValueError("invalid snapshot")
        after = capture_git_state(root, deadline)
        if after is None:
            raise ValueError("Git worktree unavailable after command")
        dimensions = classify_git_state_changes(before, after, root, deadline)
    except Exception as exc:
        emit_block([f"scope audit could not compare bounded Git state ({type(exc).__name__}: {exc})"])
        raise SystemExit(0)

    changed = sorted({path for paths in dimensions.values() for path in paths})
    if not changed and before.get("head") == after.get("head"):
        raise SystemExit(0)

    expected = surface.get("expected", [])
    protected = surface.get("protected", [])
    preexisting_dirty = baseline.get("preexisting_dirty", [])
    authorized_dirty = surface.get("authorized_dirty", [])
    reasons: list[str] = []
    for rel in changed:
        changed_dimensions = [name for name, paths in dimensions.items() if rel in paths]
        label = "/".join(changed_dimensions)
        if rel.startswith(".claude/state/.hook-snapshots/"):
            continue
        if rel in {".claude/state/change-surface.json", ".claude/state/ownership-baseline.json"}:
            reasons.append(f"{label} delta: {rel} changed from the shell outside statectl governance")
            continue
        if rel == ".claude/state" or rel.startswith(".claude/state/"):
            continue
        if matches(rel, protected):
            reasons.append(f"{label} delta: {rel} is protected")
        elif matches(rel, preexisting_dirty) and not matches(rel, authorized_dirty):
            reasons.append(f"{label} delta: {rel} was pre-task dirty/user-owned and was not assigned to this task")
        elif not expected:
            reasons.append(f"{label} delta: {rel} changed while the active surface had no expected paths")
        elif not matches(rel, expected):
            reasons.append(f"{label} delta: {rel} is outside the expected surface")
    if before.get("head") != after.get("head") and not dimensions["HEAD"]:
        reasons.append("HEAD changed without a commit path delta; scope cannot be classified")
    if reasons:
        emit_block(reasons)
    raise SystemExit(0)


if __name__ == "__main__":
    main()
