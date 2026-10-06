#!/usr/bin/env python3
"""Report control-plane invariants and advisory complexity measurements."""
from __future__ import annotations

import json
from skill_policy import preapprovals_match
from pathlib import Path
import re

ROOT = Path(__file__).resolve().parents[2]
CLAUDE = ROOT / ".claude"


def frontmatter(path: Path) -> dict[str, str]:
    lines = path.read_text(encoding="utf-8").splitlines()
    if not lines or lines[0].strip() != "---":
        return {}
    out: dict[str, str] = {}
    for line in lines[1:]:
        if line.strip() == "---":
            break
        m = re.match(r"^([A-Za-z0-9_-]+):\s*(.*)$", line)
        if m:
            out[m.group(1)] = m.group(2).strip().strip('"').strip("'")
    return out


def tools(value: str) -> set[str]:
    return {x.strip() for x in value.split(",") if x.strip()}


manifest = json.loads((CLAUDE / "MANIFEST.json").read_text(encoding="utf-8"))
settings = json.loads((CLAUDE / "settings.json").read_text(encoding="utf-8"))
agent_files = sorted((CLAUDE / "agents").glob("*.md"))
skill_files = sorted((CLAUDE / "skills").glob("*/SKILL.md"))
rule_files = sorted((CLAUDE / "rules").glob("*.md"))
agent_meta = [frontmatter(p) for p in agent_files]
skill_meta = [frontmatter(p) for p in skill_files]
write_tools = {"Edit", "Write", "NotebookEdit"}
write_capable = sum(bool(write_tools & tools(meta.get("tools", ""))) for meta in agent_meta)
recursive_capable = sum("Agent" not in tools(meta.get("disallowedTools", "")) for meta in agent_meta)
bounded_agents = sum(meta.get("maxTurns", "").isdigit() for meta in agent_meta)
path_scoped_rules = sum(bool(re.search(r"(?m)^paths:\s*$", p.read_text(encoding="utf-8"))) for p in rule_files)
invalid_preapprovals = sum(not preapprovals_match(p, manifest) for p in skill_files)
permission_block = settings.get("permissions", {})

bound_commands: list[str] = []
for groups in settings.get("hooks", {}).values():
    if isinstance(groups, list):
        for group in groups:
            if isinstance(group, dict):
                for hook in group.get("hooks", []):
                    if isinstance(hook, dict) and hook.get("type") == "command":
                        bound_commands.append(str(hook.get("command", "")))
required_bound = ["pretool_guard.py", "change_surface_guard.py", "posttool_scope_audit.py", "startup_health.py", "session_context.py", "completion_gate.py"]
required_control = [CLAUDE / p for p in ("MANIFEST.json", "CONTROL-SURFACE.md", "EVALUATION.md", "RUNTIME-VALIDATION.md")]

metrics = {
    "root_claude_lines": len((ROOT / "CLAUDE.md").read_text(encoding="utf-8").splitlines()),
    "bespoke_agents": len(agent_files),
    "hook_python_files": len(list((CLAUDE / "hooks").glob("*.py"))),
    "bound_command_hooks": len(bound_commands),
    "skills": len(skill_files),
    "rules": len(rule_files),
    "total_agent_description_chars": sum(len(m.get("description", "")) for m in agent_meta),
    "total_skill_description_chars": sum(len(m.get("description", "")) for m in skill_meta),
    "permission_deny_rules": len(permission_block.get("deny", [])),
    "permission_ask_rules": len(permission_block.get("ask", [])),
}

hard_gates = {
    "required_control_contracts_present": all(p.is_file() for p in required_control),
    "agents_have_no_direct_file_write_tools": write_capable == 0,
    "agents_cannot_recursively_spawn": recursive_capable == 0,
    "all_agents_bounded": bounded_agents == len(agent_files),
    "manifest_agent_inventory_matches": set(manifest.get("bespoke_agents", [])) == {m.get("name", "") for m in agent_meta},
    "required_skills_complete": {m.get("name", "") for m in skill_meta} == set(manifest.get("required_skills", [])),
    "skill_preapprovals_match_policy": invalid_preapprovals == 0,
    "all_rules_path_scoped": bool(rule_files) and path_scoped_rules == len(rule_files),
    "deny_and_ask_layers_present": bool(permission_block.get("deny")) and bool(permission_block.get("ask")),
    "required_hooks_bound": all(any(name in cmd for cmd in bound_commands) for name in required_bound),
    "stop_gate_present": "Stop" in settings.get("hooks", {}),
    "no_unsupported_exact_runtime_claim": manifest.get("runtime_validation", {}).get("exact_version_claim") is None,
}

advisory = {
    "root_claude_lines": metrics["root_claude_lines"],
    "bespoke_agent_count": metrics["bespoke_agents"],
    "hook_file_count": metrics["hook_python_files"],
    "bound_hook_count": metrics["bound_command_hooks"],
    "agent_description_chars": metrics["total_agent_description_chars"],
    "skill_description_chars": metrics["total_skill_description_chars"],
    "note": "These are measured for ablation/context-cost review; fixed count/character budgets are not release gates without evaluation evidence."
}

report = {"metrics": metrics, "hard_gates": hard_gates, "advisory": advisory, "healthy": all(hard_gates.values())}
print(json.dumps(report, indent=2, sort_keys=True))
if not report["healthy"]:
    print("METRICS FAILED")
    raise SystemExit(1)
print("METRICS HEALTHY")
