#!/usr/bin/env python3
"""Govern file-tool writes against task scope and immutable ownership baseline."""
from __future__ import annotations

import fnmatch
import json
import os
from pathlib import Path
import sys

from control_common import deadline_after, find_project_root, read_baseline, read_surface, validate_binding


def emit(decision: str, reason: str) -> None:
    print(json.dumps({"hookSpecificOutput": {"hookEventName": "PreToolUse", "permissionDecision": decision, "permissionDecisionReason": reason}}))


def hard_block(reason: str) -> None:
    sys.stderr.write("BLOCKED by change-surface guard: " + reason + "\n")
    raise SystemExit(2)


def normalize_path(project_root: Path, candidate: str, cwd: str) -> str:
    path = Path(candidate)
    if not path.is_absolute():
        path = Path(cwd) / path
    full = path.resolve()
    root = project_root.resolve()
    try:
        rel = full.relative_to(root)
    except ValueError:
        return str(full).replace("\\", "/")
    return str(rel).replace("\\", "/")


def matches(path: str, patterns: list[str]) -> bool:
    return any(fnmatch.fnmatch(path, p.replace("\\", "/")) for p in patterns)


def extract_path(tool_name: str, tool_input: dict) -> str | None:
    keys = {"Edit": ("file_path", "path"), "Write": ("file_path", "path"), "NotebookEdit": ("notebook_path", "file_path", "path")}
    for key in keys.get(tool_name, ("file_path", "path")):
        value = tool_input.get(key)
        if isinstance(value, str) and value.strip():
            return value
    return None


def proposed_content(tool_name: str, tool_input: dict, current: str) -> str | None:
    if tool_name == "Write":
        value = tool_input.get("content")
        return value if isinstance(value, str) else None
    if tool_name == "Edit":
        old = tool_input.get("old_string")
        new = tool_input.get("new_string")
        if isinstance(old, str) and isinstance(new, str) and old in current:
            return current.replace(old, new, 1)
    return None


def authority_transition_requires_ask(root: Path, tool_name: str, tool_input: dict) -> tuple[bool, str]:
    path = root / ".claude" / "state" / "change-surface.json"
    if not path.exists():
        return True, "creating task authority should use .claude/bin/statectl.py init so the Git-derived ownership baseline is bound atomically"
    try:
        old = json.loads(path.read_text(encoding="utf-8"))
        content = proposed_content(tool_name, tool_input, path.read_text(encoding="utf-8"))
        if content is None:
            return True, "task authority edit cannot be proven to be a narrowing transition"
        new = json.loads(content)
        if not isinstance(old, dict) or not isinstance(new, dict):
            return True, "task authority replacement is not a valid object"
    except Exception:
        return True, "task authority transition could not be validated"

    old_expected, new_expected = set(old.get("expected", [])), set(new.get("expected", []))
    old_protected, new_protected = set(old.get("protected", [])), set(new.get("protected", []))
    old_auth, new_auth = set(old.get("authorized_dirty", [])), set(new.get("authorized_dirty", []))
    identity_changed = any(old.get(k) != new.get(k) for k in ("schema_version", "task_id", "baseline_id"))
    widened = bool(new_expected - old_expected) or bool(old_protected - new_protected) or bool(new_auth - old_auth)
    deactivated = bool(old.get("active", False)) and not bool(new.get("active", False))
    if identity_changed or widened or deactivated:
        return True, "task authority is being widened, reassigned, rebound, or deactivated; require an explicit auditable transition"
    return False, ""


def main() -> None:
    deadline = deadline_after(6.0)
    try:
        payload = json.load(sys.stdin)
        tool_name = payload["tool_name"]
        tool_input = payload["tool_input"]
        if tool_name not in {"Edit", "Write", "NotebookEdit"}:
            raise ValueError("unexpected tool_name")
        cwd = payload.get("cwd") or os.getcwd()
        root = find_project_root(cwd)
    except Exception as exc:
        hard_block(f"hook input could not be parsed ({type(exc).__name__})")

    target = extract_path(tool_name, tool_input)
    if not target:
        hard_block(f"could not identify target path for {tool_name}")
    rel = normalize_path(root, target, cwd)

    if rel == ".claude/state/ownership-baseline.json":
        emit("deny", "ownership-baseline.json is Git-derived authority; recreate it only through a fresh statectl init after reconnaissance")
        raise SystemExit(0)
    if rel == ".claude/state/change-surface.json":
        ask_needed, reason = authority_transition_requires_ask(root, tool_name, tool_input)
        if ask_needed:
            emit("ask", reason)
        raise SystemExit(0)

    try:
        surface = read_surface(root)
    except Exception as exc:
        hard_block(f"active change-surface state is invalid ({type(exc).__name__}: {exc})")
    if surface is None:
        raise SystemExit(0)

    try:
        baseline = read_baseline(root)
        validate_binding(root, surface, baseline, deadline)
    except Exception as exc:
        hard_block(f"active task authority is stale or invalid ({type(exc).__name__}: {exc})")

    # Non-authority state remains mutable; completion binds verification to the current Git state.
    if rel == ".claude/state" or rel.startswith(".claude/state/"):
        raise SystemExit(0)

    expected = surface.get("expected", [])
    protected = surface.get("protected", [])
    preexisting_dirty = baseline.get("preexisting_dirty", [])
    authorized_dirty = surface.get("authorized_dirty", [])

    if matches(rel, protected):
        emit("deny", f"{rel} is inside the task's protected change surface")
    elif matches(rel, preexisting_dirty) and not matches(rel, authorized_dirty):
        emit("ask", f"{rel} was dirty before this task and is user-owned; assign it deliberately before editing")
    elif expected and not matches(rel, expected):
        emit("ask", f"{rel} is outside the task's expected change surface; widen scope deliberately before editing")
    elif not expected:
        emit("ask", f"active change-surface state has no expected paths; confirm this edit to {rel}")
    raise SystemExit(0)


if __name__ == "__main__":
    main()
