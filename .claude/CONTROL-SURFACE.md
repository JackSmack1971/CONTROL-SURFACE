# Control-surface inventory

This inventory names the package mechanisms that can affect behavior. It is descriptive, not proof that the host Claude Code runtime accepted each surface; see `RUNTIME-VALIDATION.md`.

| Surface | Files | Purpose | Failure posture |
|---|---|---|---|
| Instruction kernel | `CLAUDE.md` | Small universal engineering policy and workflow routing | Advisory unless backed by lower layers |
| Path-scoped rules | `.claude/rules/*.md` | Local policy for sensitive repository areas | Advisory/runtime-dependent |
| Skills | `.claude/skills/*/SKILL.md` | Progressive workflow disclosure | Advisory/runtime-dependent |
| Specialists | `.claude/agents/*.md` | Fresh-context, bounded read/review/verification roles | Advisory/runtime-dependent |
| Declarative permissions | `.claude/settings.json` | Static deny/ask policy | Runtime-enforced if accepted by Claude Code |
| Shell pre-guard | `.claude/hooks/pretool_guard.py` | Normalization gaps, direct secret probes, consequential effects, bounded pre-command Git snapshot | Fails closed on malformed input, stale task authority, or snapshot failure |
| File-scope guard | `.claude/hooks/change_surface_guard.py` | Expected/protected scope and pre-task ownership enforcement | Fails closed on invalid/stale active state |
| Shell post-audit | `.claude/hooks/posttool_scope_audit.py` | Detects shell-created scope/ownership drift after execution | Reports block; never claims rollback/prevention |
| Startup health | `.claude/hooks/startup_health.py` | Checks required files, Git, active-state binding, records effective containment posture for startup, resume, clear, compact, and fork | Fails hook when unhealthy |
| Resume context | `.claude/hooks/session_context.py` | Reinjects bounded structured task facts as data | Omits missing/invalid optional state |
| Stop gate | `.claude/hooks/completion_gate.py` | Requires current scope conformance and state-bound fresh verification | Exits nonzero while active task evidence is stale/missing |
| Task state utility | `.claude/bin/statectl.py` | Atomically creates Git-derived ownership baseline, updates governed scope, seals verification | Scope/ownership-changing commands are subject to explicit approval |
| Offline checks | `.claude/selftest/*.py` | Structural/invariant regression checks and measurements | Must pass after control-plane edits |

## Authority hierarchy

1. User/system/platform policy and managed/OS containment.
2. Declarative permissions and host sandboxing where actually enforced.
3. Immutable task ownership baseline (`ownership-baseline.json`) derived from Git through `statectl init`.
4. Mutable but governed task scope (`change-surface.json`).
5. Contextual pre-tool guards and post-action drift detection.
6. Independent review/verification evidence bound to the current Git state.
7. Instructional rules/skills/agents.

Do not describe regex interception as a credential boundary. On native Windows, project hooks and permissions are defense in depth only unless separate OS/managed controls provide filesystem, egress, and credential isolation.

Skill `allowed-tools` entries are explicit narrow runtime preapprovals, checked against the manifest policy; they do not override managed policy or authorize task effects. `oracle-design` uses a requirements-only verifier handoff before implementation. Verification schema 2 requires runner-produced successful current-state records; local record mutability and oracle adequacy remain outside the deterministic guarantee.
