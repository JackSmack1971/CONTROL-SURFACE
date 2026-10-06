#!/usr/bin/env python3
"""Create and govern task-local control-plane state without shell redirection."""
from __future__ import annotations

import argparse
from datetime import datetime, timezone
import hashlib
import json
import os
from pathlib import Path
import sys
import subprocess
import uuid

HOOKS = Path(__file__).resolve().parents[1] / "hooks"
sys.path.insert(0, str(HOOKS))
from control_common import (  # noqa: E402
    BASELINE_SCHEMA,
    FINGERPRINT_VERSION,
    STATE_SCHEMA,
    VERIFICATION_SCHEMA,
    capture_git_state,
    deadline_after,
    find_project_root,
    read_baseline,
    read_surface,
    state_dir,
    validate_binding,
    validate_checks,
    read_json,
    write_json_atomic,
)


def now_iso() -> str:
    return datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")


def root() -> Path:
    return find_project_root(os.getcwd())


def cmd_init(args: argparse.Namespace) -> None:
    repo = root()
    deadline = deadline_after()
    current = capture_git_state(repo, deadline)
    if current is None:
        raise SystemExit("statectl: Git worktree required")
    baseline_id = uuid.uuid4().hex
    baseline = {
        "schema_version": BASELINE_SCHEMA,
        "baseline_id": baseline_id,
        "repository_root": str(repo.resolve()),
        "branch": current.get("branch"),
        "baseline_head": current["head"],
        "preexisting_dirty": sorted(current["entries"]),
        "created_at": now_iso(),
    }
    surface = {
        "schema_version": STATE_SCHEMA,
        "active": True,
        "task_id": args.task_id or uuid.uuid4().hex,
        "task": args.task,
        "baseline_id": baseline_id,
        "expected": args.expected,
        "protected": args.protected,
        "authorized_dirty": [],
        "created_at": now_iso(),
        "updated_at": now_iso(),
    }
    sd = state_dir(repo)
    write_json_atomic(sd / "ownership-baseline.json", baseline)
    write_json_atomic(sd / "change-surface.json", surface)
    print(json.dumps({"baseline": baseline, "surface": surface}, indent=2))


def cmd_recover(args: argparse.Namespace) -> None:
    """Replace stale authority after fresh reconnaissance and explicit hook approval."""
    repo = root()
    sd = state_dir(repo)
    old_surface = read_surface(repo)
    old_baseline = read_baseline(repo)
    if old_surface is None:
        raise SystemExit("statectl: no active stale task authority to recover")
    try:
        validate_binding(repo, old_surface, old_baseline, deadline_after())
    except ValueError:
        pass
    else:
        raise SystemExit("statectl: active authority is current; use init only when no active task exists")
    current = capture_git_state(repo, deadline_after())
    if current is None:
        raise SystemExit("statectl: Git worktree required")
    prior = {"baseline_id": old_baseline["baseline_id"], "task_id": old_surface["task_id"],
             "baseline_head": old_baseline["baseline_head"]}
    # Build fresh authority with a new identity; never carry forward verification claims.
    baseline_id = uuid.uuid4().hex
    baseline = {"schema_version": BASELINE_SCHEMA, "baseline_id": baseline_id,
                "repository_root": str(repo.resolve()), "branch": current.get("branch"),
                "baseline_head": current["head"], "preexisting_dirty": sorted(current["entries"]),
                "created_at": now_iso()}
    surface = {"schema_version": STATE_SCHEMA, "active": True,
               "task_id": args.task_id or uuid.uuid4().hex, "task": args.task,
               "baseline_id": baseline_id, "expected": args.expected,
               "protected": args.protected, "authorized_dirty": [],
               "created_at": now_iso(), "updated_at": now_iso()}
    write_json_atomic(sd / "ownership-baseline.json", baseline)
    write_json_atomic(sd / "change-surface.json", surface)
    write_json_atomic(sd / "verification.json", {"verdict": "INVALIDATED", "reason": "stale authority recovery",
                      "invalidated_at": now_iso(), "prior_baseline_id": prior["baseline_id"]})
    write_json_atomic(sd / "check-evidence.json", {"checks": [], "invalidated_at": now_iso(),
                      "reason": "stale authority recovery", "prior_baseline_id": prior["baseline_id"]})
    write_json_atomic(sd / "recovery.json", {"transition": "stale-authority-recovery", "prior": prior,
                      "baseline_id": baseline_id, "task_id": surface["task_id"],
                      "head": current["head"], "branch": current.get("branch"),
                      "expected": args.expected, "protected": args.protected, "recorded_at": now_iso()})
    snapshots = sd / ".hook-snapshots"
    if snapshots.is_dir():
        for path in snapshots.glob("*.json"):
            path.unlink()
    print(json.dumps({"baseline": baseline, "surface": surface, "recovery": "recorded",
                      "prior": prior, "verification": "invalidated"}, indent=2))


def cmd_update_scope(args: argparse.Namespace) -> None:
    repo = root()
    deadline = deadline_after()
    surface = read_surface(repo)
    if surface is None:
        raise SystemExit("statectl: no active change surface")
    baseline = read_baseline(repo)
    validate_binding(repo, surface, baseline, deadline)
    expected = set(surface.get("expected", []))
    protected = set(surface.get("protected", []))
    authorized = set(surface.get("authorized_dirty", []))
    expected.update(args.add_expected)
    expected.difference_update(args.remove_expected)
    protected.update(args.add_protected)
    protected.difference_update(args.remove_protected)
    authorized.update(args.authorize_dirty)
    authorized.difference_update(args.deauthorize_dirty)
    baseline_dirty = set(baseline.get("preexisting_dirty", []))
    invalid_auth = sorted(authorized - baseline_dirty)
    if invalid_auth:
        raise SystemExit(f"statectl: authorized_dirty must come from baseline preexisting_dirty: {invalid_auth}")
    surface.update({
        "expected": sorted(expected),
        "protected": sorted(protected),
        "authorized_dirty": sorted(authorized),
        "updated_at": now_iso(),
    })
    write_json_atomic(state_dir(repo) / "change-surface.json", surface)
    print(json.dumps(surface, indent=2))


def cmd_deactivate(_: argparse.Namespace) -> None:
    repo = root()
    path = state_dir(repo) / "change-surface.json"
    if not path.is_file():
        return
    raw = json.loads(path.read_text(encoding="utf-8"))
    if isinstance(raw, dict):
        raw["active"] = False
        raw["updated_at"] = now_iso()
        write_json_atomic(path, raw)


def cmd_run_check(args: argparse.Namespace) -> None:
    repo = root()
    surface = read_surface(repo)
    if surface is None:
        raise SystemExit("statectl: no active change surface")
    baseline = read_baseline(repo)
    before = validate_binding(repo, surface, baseline, deadline_after(), full_content=True)
    argv = args.command
    if argv and argv[0] == "--":
        argv = argv[1:]
    if not argv or not args.criterion.strip() or not 1 <= args.timeout <= 3600:
        raise SystemExit("statectl: command, criterion, and timeout in 1-3600 seconds required")
    started = now_iso()
    timed_out = False
    try:
        result = subprocess.run(argv, cwd=repo, timeout=args.timeout, check=False)
        exit_code = result.returncode
    except subprocess.TimeoutExpired:
        timed_out, exit_code = True, None
    except OSError as exc:
        raise SystemExit(f"statectl: check could not start: {exc}")
    after = validate_binding(repo, surface, baseline, deadline_after(), full_content=True)
    path = state_dir(repo) / "check-evidence.json"
    previous = read_json(path).get("checks", []) if path.is_file() else []
    # Keep only checks against this exact state, including failures until rerun.
    previous = [c for c in previous if isinstance(c, dict) and c.get("fingerprint_version") == FINGERPRINT_VERSION and c.get("baseline_id") == baseline["baseline_id"] and c.get("after_fingerprint") == before["fingerprint"]]
    previous = [c for c in previous if c.get("argv") != argv or c.get("criterion") != args.criterion]
    record = {"fingerprint_version": FINGERPRINT_VERSION, "argv": argv, "criterion": args.criterion, "exit_code": exit_code,
              "timed_out": timed_out, "started_at": started, "finished_at": now_iso(),
              "baseline_id": baseline["baseline_id"], "head": before["head"],
              "before_fingerprint": before["fingerprint"], "after_fingerprint": after["fingerprint"]}
    if len(previous) >= 64:
        raise SystemExit("statectl: check evidence limit reached; narrow the verification plan")
    write_json_atomic(path, {"checks": previous + [record]})
    print(json.dumps(record, indent=2))
    if timed_out or exit_code != 0 or before["fingerprint"] != after["fingerprint"]:
        raise SystemExit("statectl: check failed, timed out, or changed working state")


def cmd_seal_verification(args: argparse.Namespace) -> None:
    repo = root()
    deadline = deadline_after()
    surface = read_surface(repo)
    if surface is None:
        raise SystemExit("statectl: no active change surface")
    baseline = read_baseline(repo)
    current = validate_binding(repo, surface, baseline, deadline, full_content=True)
    checks = read_json(state_dir(repo) / "check-evidence.json").get("checks")
    validate_checks(checks, baseline["baseline_id"], current)
    if not args.summary.strip():
        raise SystemExit("statectl: verification summary must be non-empty")
    verification = {
        "schema_version": VERIFICATION_SCHEMA,
        "fingerprint_version": FINGERPRINT_VERSION,
        "verdict": "VERIFIED",
        "baseline_id": baseline["baseline_id"],
        "head": current["head"],
        "status_fingerprint": current["fingerprint"],
        "checks": checks,
        "summary": args.summary,
        "sealed_at": now_iso(),
    }
    write_json_atomic(state_dir(repo) / "verification.json", verification)
    print(json.dumps(verification, indent=2))


def cmd_status(_: argparse.Namespace) -> None:
    repo = root()
    deadline = deadline_after()
    surface = read_surface(repo)
    if surface is None:
        print(json.dumps({"active": False}, indent=2))
        return
    baseline = read_baseline(repo)
    try:
        current = validate_binding(repo, surface, baseline, deadline)
    except Exception as exc:
        current = capture_git_state(repo, deadline)
        print(json.dumps({"active": True, "status": "stale", "surface": surface,
                          "baseline": baseline, "current": current,
                          "diagnostic": f"{type(exc).__name__}: {exc}",
                          "recovery": "perform fresh reconnaissance, then use statectl recover after explicit approval"}, indent=2))
        return
    print(json.dumps({"active": True, "status": "current", "surface": surface, "baseline": baseline, "current": current}, indent=2))


def parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser()
    sub = p.add_subparsers(dest="cmd", required=True)
    init = sub.add_parser("init")
    init.add_argument("--task", required=True)
    init.add_argument("--task-id")
    init.add_argument("--expected", action="append", default=[])
    init.add_argument("--protected", action="append", default=[])
    init.set_defaults(func=cmd_init)

    recover = sub.add_parser("recover", help="replace stale task authority after fresh reconnaissance")
    recover.add_argument("--task", required=True)
    recover.add_argument("--task-id")
    recover.add_argument("--expected", action="append", default=[])
    recover.add_argument("--protected", action="append", default=[])
    recover.set_defaults(func=cmd_recover)

    upd = sub.add_parser("update-scope")
    for name in ("add-expected", "remove-expected", "add-protected", "remove-protected", "authorize-dirty", "deauthorize-dirty"):
        upd.add_argument("--" + name, action="append", default=[])
    upd.set_defaults(func=cmd_update_scope)

    deact = sub.add_parser("deactivate")
    deact.set_defaults(func=cmd_deactivate)

    seal = sub.add_parser("seal-verification")
    seal.add_argument("--summary", required=True)
    seal.set_defaults(func=cmd_seal_verification)

    run = sub.add_parser("run-check")
    run.add_argument("--criterion", required=True)
    run.add_argument("--timeout", type=int, default=300)
    run.add_argument("command", nargs=argparse.REMAINDER)
    run.set_defaults(func=cmd_run_check)

    status = sub.add_parser("status")
    status.set_defaults(func=cmd_status)
    return p


if __name__ == "__main__":
    args = parser().parse_args()
    args.func(args)
