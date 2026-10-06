#!/usr/bin/env python3
"""Narrow deterministic Stop gate for active task state."""
from __future__ import annotations

import fnmatch
import json
import os
from pathlib import Path
import sys

from control_common import VERIFICATION_SCHEMA, deadline_after, find_project_root, read_baseline, read_json, read_surface, state_dir, validate_binding, validate_checks


def matches(path: str, patterns: list[str]) -> bool:
    return any(fnmatch.fnmatch(path, p.replace("\\", "/")) for p in patterns)


def block(reason: str) -> None:
    sys.stderr.write("COMPLETION BLOCKED: " + reason + "\n")
    raise SystemExit(2)


def main() -> None:
    try:
        payload = json.load(sys.stdin)
        root = find_project_root(payload.get("cwd") or os.getcwd())
    except Exception as exc:
        block(f"Stop hook input could not be parsed ({type(exc).__name__})")
    deadline = deadline_after(6.0)
    try:
        surface = read_surface(root)
    except Exception as exc:
        block(f"change-surface state is invalid: {exc}")
    if surface is None:
        raise SystemExit(0)
    try:
        baseline = read_baseline(root)
        current = validate_binding(root, surface, baseline, deadline)
    except Exception as exc:
        block(f"active task authority is stale/unhealthy: {exc}")

    expected = surface.get("expected", [])
    protected = surface.get("protected", [])
    baseline_dirty = baseline.get("preexisting_dirty", [])
    authorized = surface.get("authorized_dirty", [])
    for rel in current.get("entries", {}):
        if rel == ".claude/state" or rel.startswith(".claude/state/"):
            continue
        if matches(rel, protected):
            block(f"current diff includes protected path {rel}")
        if matches(rel, baseline_dirty) and not matches(rel, authorized):
            block(f"current diff touches unassigned pre-task dirty path {rel}")
        if expected and not matches(rel, expected):
            block(f"current diff includes path outside reviewed scope: {rel}")
        if not expected:
            block(f"active task has no expected paths but current diff includes {rel}")

    verification_path = state_dir(root) / "verification.json"
    if not verification_path.is_file():
        block("fresh structured verification evidence is missing; run verification-gate then seal it with statectl seal-verification")
    try:
        verification = read_json(verification_path)
    except Exception as exc:
        block(f"verification evidence is invalid: {exc}")
    if verification.get("schema_version") != VERIFICATION_SCHEMA or verification.get("verdict") != "VERIFIED":
        block("verification evidence does not record a VERIFIED verdict")
    if verification.get("baseline_id") != baseline["baseline_id"]:
        block("verification evidence belongs to a different ownership baseline")
    if verification.get("head") != current["head"] or verification.get("status_fingerprint") != current["fingerprint"]:
        block("working-tree state changed after verification was sealed; rerun affected checks and reseal")
    try:
        validate_checks(verification.get("checks"), baseline["baseline_id"], current)
    except ValueError as exc:
        block(f"verification execution evidence is invalid: {exc}")
    health_path = state_dir(root) / "control-plane-health.json"
    if health_path.is_file():
        try:
            health = read_json(health_path)
            if health.get("status") != "healthy":
                block("control-plane health is not healthy")
        except Exception as exc:
            block(f"control-plane health evidence is invalid: {exc}")
    raise SystemExit(0)


if __name__ == "__main__":
    main()
