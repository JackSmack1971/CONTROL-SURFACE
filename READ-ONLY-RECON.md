Read-only reconnaissance is complete. **No files were changed and no audit artifacts were created.** Three read-only subagents inspected the definition, policy/hook, and orchestration/governance surfaces in parallel.

## A. CONTROL PLANE TOPOLOGY

| Component | Purpose and plane | Activation, dependencies, and downstream effects | Authority and validation |
|---|---|---|---|
| Instruction kernel: /C:/TEST repos/CONTROL-PLANE-SUPREME/CLAUDE.md | **DEFINITION** — universal workflow routing and engineering guidance | Intended as project instructions; routes work to skills and agents; references task state and self-checks | **CURRENT:** advisory guidance by its own description. No `@AGENTS.md` import found. Actual loading was not verified. |
| Path-scoped rules: `.claude/rules/*.md` | **DEFINITION** — guidance for security/contracts, sensitive areas, and testing | Path globs scope rules; loaded behavior depends on Claude Code | Self-tests inspect structure and paths; runtime loading remains unverified. |
| Skills: `.claude/skills/*/SKILL.md` and `engineering-flow/references/routing-evals.md` | **DEFINITION / ORCHESTRATION** — reusable procedures, handoffs, routing | Invoked by kernel, parent, or runtime selection; some declare `context: fork`, specialist roles, or `allowed-tools` | Skill text and tool preapprovals do not grant task authority. Manifest/self-tests check declarations, not runtime acceptance. |
| Specialist definitions: `.claude/agents/*.md` | **ORCHESTRATION** — research, architecture, debugging, review, verification roles | Selected by parent/runtime; depend on role instructions and task handoffs; some tools permit shell execution | Tool declarations are not proof of an isolated security boundary. Self-tests inspect definitions; actual spawned-agent constraints were not tested. |
| Settings: /C:/TEST repos/CONTROL-PLANE-SUPREME/.claude/settings.json | **POLICY** — project permission rules and lifecycle hook bindings | Intended to be read by Claude Code; hooks require Python, Git, filesystem access, and `${CLAUDE_PROJECT_DIR}` | **CURRENT:** declarations exist. Effective settings and host enforcement were not inspected. |
| Hooks and shared helpers: `.claude/hooks/*.py` | **POLICY / GOVERNANCE / DATA PLANE** — pre-tool checks, startup diagnostics, resume context, post-shell drift reporting, and Stop checks | Bound by settings; read Git and ignored task state. Shell pre-guard writes temporary snapshots; session/startup hooks write diagnostics; post-tool hook reports after the shell command | Hook effects exist only if the runtime invokes and accepts them. Post-tool detection occurs after execution and does not undo it. Offline self-tests invoke scripts directly. |
| Task-state utility: `.claude/bin/statectl.py`, `control_common.py`, `.claude/state/*` | **GOVERNANCE / DATA PLANE** — records ownership baseline, expected/protected scope, check evidence, verification seals, and continuation data | Utility reads Git and writes ignored state; hooks consume that state to guard edits, detect drift, and gate Stop | Records are mutable local data, not authenticated provenance or authorization. `statectl status` currently rejects the active state because its baseline HEAD diverges. |
| Validation and contracts: `.claude/selftest/*`, `MANIFEST.json`, `CONTROL-SURFACE.md`, `EVALUATION.md`, `RUNTIME-VALIDATION.md` | **GOVERNANCE** — structural checks, declared invariants, measurements, and live-canary procedure | Self-tests use Python and temporary Git repositories; live validation requires a disposable repository and the actual Claude binary | No checks were run as part of this reconnaissance. Documentation explicitly says offline checks do not prove live compatibility. |
| External/host controls | **POLICY / DATA PLANE** — managed settings, OS containment, credentials, network, user-level integrations | Outside the repository; may affect effective instructions, permissions, tools, and external effects | Not inspected. Repository documentation says native Windows project hooks and permissions are not an OS sandbox. |

Evidence labels: **CURRENT** means directly observed in repository state or command output; **DERIVED** means inferred from those observations; **SPECULATIVE** means plausible but not established.

## B. FILE/COMPONENT INVENTORY

**CURRENT — Git baseline:** root `C:/TEST repos/CONTROL-PLANE-SUPREME`, branch `main`, HEAD `ed4e38b22fbb27c3de6dd31e8c1d6f701bb65ff0`, tracking `origin/main`. Git status was clean; there are 40 tracked files. `git diff --check` produced no findings.

The tracked control-plane inventory contains:

- `CLAUDE.md`; three path-scoped rules.
- Ten skills and one skill reference document.
- Five specialist agent definitions.
- `.claude/settings.json`; eight hook/helper Python files; `statectl.py`.
- Four self-test/measurement scripts.
- `MANIFEST.json` and three control-plane documents, plus state README and `.gitignore`.

No tracked `.claude/CLAUDE.md`, `CLAUDE.local.md`, `.claude/settings.local.json`, `.claude/commands/`, output style, `.mcp.json`, plugin configuration, or general build/test configuration was found. This describes the repository, not machine- or user-level configuration.

`AGENTS.md` is ignored by `.git/info/exclude` and is not part of the 40 tracked files. I treated the supplied root `AGENTS.md` as maintainer guidance, not as a Claude control-plane artifact.

**CURRENT — ignored runtime data:** `.claude/state` contains an active change surface, ownership baseline, check evidence, and a `VERIFIED` verification record. `runtime-validation.json` and `control-plane-health.json` are absent. `statectl status` failed with `baseline HEAD diverged`; therefore the existing task-state seal cannot be treated as current evidence for this checkout.

The installed CLI reports `Claude Code 2.1.290`. That version was queried, but no live canary was run.

## C. EFFECTIVE DATA FLOWS

1. **Instructions to workflow:** `CLAUDE.md` routes tasks to rules, skills, or specialist roles. These provide model guidance; actual instruction selection is unknown.
2. **Settings to hooks:** `.claude/settings.json` binds shell and file tools to pre-tool hooks, lifecycle events to startup/context hooks, shell tools to a post-tool audit, and Stop to a completion gate.
3. **Git to task authority:** `statectl.py init` derives a baseline and scope from Git. Shared helpers validate repository root, branch, and HEAD. The scope and baseline are then consumed by file guards, shell snapshots, drift reporting, and completion checks.
4. **Checks to verification:** `run-check` records command results against a full-content fingerprint; `seal-verification` records a state-bound seal. The completion gate checks it. The records are local and can be modified outside the claimed flow.
5. **Runtime state to resumed context:** session context selects bounded JSON fields and labels them as data. The actual host invocation and its effective instruction selection were not observed.
6. **External controls to effects:** host/managed settings, OS policy, credentials, network access, and user-level configuration may affect actual capabilities and authorization. Repository evidence does not establish those effective values.

## D. AUTHORITY BOUNDARIES

- **CURRENT:** repository documentation distinguishes model instructions from permissions, runtime execution, and managed/OS controls. Skills, agent definitions, and tool registrations are not described as authorization.
- **CURRENT:** settings contain declared deny/ask rules for secret paths, selected shell patterns, destructive Git/filesystem commands, package operations, publishing, GitHub, infrastructure, Kubernetes, and Helm effects.
- **DERIVED:** settings are intended policy declarations, but their effective status is unverified without runtime diagnostics or canaries.
- **CURRENT:** pre-tool guards may block or ask for selected command patterns; the file guard checks task scope when active state is valid.
- **CURRENT:** the post-tool hook reports scope drift after a shell command has run; its own message says it did not prevent or revert the effect.
- **CURRENT:** the manifest and docs label regex checks as defense in depth and native Windows containment as degraded. No OS/managed containment evidence was gathered.
- **CURRENT:** repository state is clean, but ignored state exists. Git cleanliness does not establish runtime-state freshness; the state status command confirms a HEAD binding failure.
- **UNKNOWN:** which project, user, or managed configuration is effective, what tools are exposed, whether the hooks fire, and whether agent tool restrictions are enforced at runtime.

## E. DUPLICATION / CONFLICT MAP

- **DERIVED — potential policy overlap:** `.claude/settings.json` and `pretool_guard.py` cover overlapping command classes. The hook appears intended to add pattern-based defense in depth; actual combined behavior was not exercised.
- **DERIVED — potential inventory drift:** the manifest, self-tests, and documentation each enumerate required files or surfaces. The runtime-validation document mentions `.mcp.json` as an inventory input, but that file is absent here.
- **DERIVED — wording ambiguity:** `CLAUDE.md` says nontrivial writes initialize task authority, while `recon-gate` describes task authority as optional/conditional. The intended condition is unclear from those passages.
- **DERIVED — role overlap to examine:** architecture and evidence-research roles can both touch external facts; reviewer and verifier both contribute evidence but have different stated jobs.
- No direct contradiction in effective runtime behavior was established. Runtime behavior itself remains unverified.

## F. VALIDATION SURFACES

**CURRENT — declared offline checks:** `.claude/selftest/selftest.py` covers structure and hook/state behavior using direct script invocation and temporary repositories; `skill_policy.py` checks declared tool preapprovals; `test_runtime_compatibility.py` checks inventory/binding evidence; `metrics.py` reports advisory counts and budgets.

**CURRENT — declared live validation:** `.claude/RUNTIME-VALIDATION.md` prescribes canaries for permission patterns, hook events/output, instructions, scope guards, and completion behavior in disposable repositories. The runtime evidence file required for a compatibility claim is absent.

**Executed for this reconnaissance:** Git root/branch/HEAD/status and inventory queries; installed `claude --version`; read-only `statectl status` (failed because baseline HEAD diverged); `git diff --check` (no findings). Self-tests and live canaries were not run.

## G. UNKNOWN / UNVERIFIED BEHAVIOR

- Effective instruction sources, settings, permissions, managed policy, and tool visibility.
- Whether Claude Code 2.1.290 accepts and invokes the configured event names, matchers, permission expressions, and hook output schemas.
- Whether specialist agent tool restrictions are effective in spawned sessions.
- Whether MCP, plugins, or other integrations are supplied outside this checkout.
- Whether hooks and shell patterns resist bypasses beyond the offline probes described in tests.
- Whether ignored task-state records can be changed or raced between checks and sealing; documentation itself disclaims authentication and atomic snapshots.
- Whether the documented research-coverage behavior works beyond its evaluation specification.

**CURRENT:** the active ignored task state is stale with respect to this checkout’s HEAD. Its `VERIFIED` label is not evidence of current verification.

## H. 10 QUESTIONS FOR THE NEXT RESEARCH PHASE

1. What exact Claude Code build and effective user/project/managed settings are active for this repository?
2. Which instruction files does that runtime actually load, including whether `AGENTS.md` is selected?
3. Which configured permission expressions, hook events, matchers, and output schemas fire as intended on 2.1.290?
4. Do the shell and file pre-tool guards block or ask for the documented cases in the live runtime?
5. Are custom agent tool declarations enforced in spawned sessions, and which roles actually receive shell tools?
6. What external MCP, plugin, or integration configuration is active, if any?
7. How and when should stale ignored task state be invalidated or reinitialized, and can its seal be altered outside `statectl`?
8. Can state capture, check execution, and sealing race with concurrent changes or other processes?
9. What primary documentation supports the version-sensitive settings, hook, skill, and agent fields in this installed release?
10. Beyond structural tests, has the documented source-coverage ablation case or other behavioral evaluation been run with retained evidence?

# PRODUCT-SEMANTICS DELTA REPORT

**Scope:** Read-only audit of repository Claude Code declarations and their product semantics. No files were edited. The working tree was clean at `ed4e38b22fbb27c3de6dd31e8c1d6f701bb65ff0` on branch `main`.

**Version evidence:** `claude --version` returned **2\.1.290 (Claude Code)**. The official changelog lists 2.1.290 as its current release. That establishes the installed CLI’s reported version; it does **not** establish that this repository’s hooks, permissions, or instruction selection have passed live runtime canaries. The repository’s own validation document correctly distinguishes those claims. [Official changelog](<https://code.claude.com/docs/en/changelog>)

## Ranked findings

### 1\. High — SessionStart failure is not a documented startup gate

**Repository assumption:** `.claude/CONTROL-SURFACE.md` says the startup health hook “Fails hook when unhealthy.” `.claude/RUNTIME-VALIDATION.md` asks for confirmation that the SessionStart hook executes successfully.

**Current documented contract:** `SessionStart` can add context, but its output cannot block or control the session. A nonzero exit can therefore indicate hook failure without preventing session startup.

**Version compatibility:** This is the current documented contract; the installed version is 2.1.290. I did not run a live session to observe this hook.

**Status: AMBIGUOUS.** The repository’s wording is accurate if “fails” means the hook reports failure. It would be inaccurate if read as “prevents an unhealthy session from starting.” The control-surface inventory describes it as a health check, so I found no explicit claim that it blocks startup. [Hooks reference](<https://code.claude.com/docs/en/hooks>)

### 2\. High — Permissions and hooks are not OS containment

**Repository assumption:** `.claude/CONTROL-SURFACE.md` separates behavioral policy, permissions, and sandboxing; it also says native-Windows hooks and permissions are defense in depth.

**Current documented contract:** Permission rules match Claude Code tool requests; they are not a general boundary around arbitrary programs. The OS sandbox applies to supported shell tools and depends on platform. Claude’s file tools, MCP tools, and hooks are outside that shell sandbox.

**Version compatibility:** These are current documented semantics. The installed version is identified, but this audit did not inspect effective user or managed settings, establish the runtime platform mode, or run sandbox canaries.

**Status: MATCH, with runtime applicability unverified.** The repository’s separation is sound. Its native-Windows caveat matters because this checkout is being maintained from Windows, but the CLI version query alone does not establish how a Claude Code session would be hosted. [Permissions](<https://code.claude.com/docs/en/permissions>), [sandboxing](<https://code.claude.com/docs/en/sandboxing>)

### 3\. Moderate — PostToolUse “block” reports after execution

**Repository assumption:** `posttool_scope_audit.py` is described as detecting shell-created scope drift after execution and reporting a block without claiming rollback or prevention.

**Current documented contract:** `PostToolUse` runs after a tool succeeds. A blocking decision can give Claude feedback, but it does not undo the completed tool action.

**Version compatibility:** Matches the current documented contract. No live hook invocation was performed.

**Status: MATCH.** The repository describes this as post-action detection, not a pre-execution enforcement gate. [Hooks reference](<https://code.claude.com/docs/en/hooks>)

### 4\. Moderate — Skill `allowed-tools` changes tool approval for the skill turn

**Repository assumption:** The control-surface document calls Skill `allowed-tools` entries “runtime preapprovals,” and says they do not override managed policy or authorize task effects.

**Current documented contract:** `allowed-tools` can preapprove listed tools while a Skill is active; it does not restrict Claude’s available tools. This changes whether those tool calls require approval, subject to the applicable settings and policy. `compatibility` is accepted metadata, but Claude Code does not use it as a version gate.

**Version compatibility:** The inspected Skill fields and frontmatter are supported by current docs. The repository’s target-version text in `compatibility` is descriptive, not an enforced minimum.

**Status: MATCH, with terminology worth reading narrowly.** “Does not authorize task effects” is consistent with separating tool invocation from broader authority, but should not be taken to mean `allowed-tools` has no effect on runtime approval. [Skills](<https://code.claude.com/docs/en/skills>)

### 5\. Moderate — AGENTS.md loading is now native and selection-dependent

**Repository assumption:** The repository keeps Codex `AGENTS.md` and Claude `CLAUDE.md` boundaries explicit, avoids importing `@AGENTS.md`, and requests a runtime canary rather than assuming `CLAUDE.md` excludes `AGENTS.md`.

**Current documented contract:** Current Claude Code supports `AGENTS.md` directly. The documented default selection reads it when no `CLAUDE.md` or `CLAUDE.local.md` exists at or above the working directory; user or managed Project Instructions configuration can change which instruction files load. Current docs also describe AGENTS support from v2.1.277.

**Version compatibility:** Installed 2.1.290 is above that documented minimum. The checkout has a root `CLAUDE.md`, so under the documented default selection root `AGENTS.md` is not expected to load. Effective Project Instructions settings were not inspected or tested in a Claude session.

**Status: MATCH.** The repo’s warning against assuming permanent exclusion is justified. Its runtime canary is the right kind of evidence for the effective selection. [Memory and instruction loading](<https://code.claude.com/docs/en/memory>)

### 6\. Low — Current hook surface is larger than the repository uses

**Repository assumption:** `.claude/settings.json` uses `SessionStart`, `PreToolUse`, `PostToolUse`, and `Stop`; its matchers cover the configured tools and SessionStart reasons.

**Current documented contract:** These events and matcher forms remain supported. Current Claude Code also documents events such as `InstructionsLoaded`, `PostToolUseFailure`, `PermissionDenied`, `TaskCreated`, `TaskCompleted`, `WorktreeCreate`, and `WorktreeRemove`.

**Version compatibility:** The configured events and matcher forms match current docs. I found no unsupported configured hook event or obsolete hook output key in the inspected settings and scripts. The additional events are not evidence that this repo needs them.

**Status: MATCH.** Current documentation does not show a newer hook mechanism superseding the repository’s existing gates. `InstructionsLoaded` can provide loading diagnostics, but it is observational and does not replace runtime enforcement or canaries. [Hooks reference](<https://code.claude.com/docs/en/hooks>)

### 7\. Low — Instruction loading and context cost are mostly described consistently

**Repository assumption:** The control plane distinguishes always-on instructions from scoped rules and Skills, and treats instructions as context rather than enforcement.

**Current documented contract:** `CLAUDE.md` files are concatenated from ancestor directories, with nested files loaded when relevant files are read or edited. `.claude/rules` files without path scope load each session; path-scoped rules load for matching files. Skills expose descriptions at session start and load their full content when invoked or selected. Claude recommends keeping each `CLAUDE.md` under 200 lines.

**Version compatibility:** These are current documented semantics. The inspected root `CLAUDE.md` is within the documented size target. Actual context-token cost and which files load in a live session were not measured.

**Status: MATCH; effective loading unverified.** The audit found no stale precedence claim that a more-specific instruction mechanically overrides an earlier one; Claude treats these files as context, not configuration. [Memory and instruction loading](<https://code.claude.com/docs/en/memory>), [Skills](<https://code.claude.com/docs/en/skills>)

### 8\. Low — Native prompt audit is available on the installed version

**Repository assumption:** `.claude/RUNTIME-VALIDATION.md` requires live evidence for compatibility. Repository evaluation material treats a `/claude-api prompt-audit` dependency as undeclared.

**Current documented contract:** `/doctor prompt-audit` reports stale or conflicting instruction material and proposed edits; it does not apply them unless asked. It requires Claude Code v2.1.283 or later and runs through the bundled `/claude-api` Skill.

**Version compatibility:** Installed 2.1.290 meets the documented minimum. The command was not run.

**Status: AMBIGUOUS.** There is a current native diagnostic available to this version. The documented entry point is `/doctor prompt-audit`; `/claude-api` is the bundled Skill it uses internally, not the user-facing command. This diagnostic can inform an audit, but does not demonstrate runtime hook or permission behavior. [Prompt audit documentation](<https://code.claude.com/docs/en/memory>)

## Mechanism inventory

| Mechanism | Repository assumption → current documented contract | Version compatibility | Result |
|---|---|---|---|
| `CLAUDE.md` | Persistent guidance → loaded as context, not enforced policy | Current docs; no incompatible assumption found | **MATCH** |
| `.claude/rules`, path scope | Modular guidance → unscoped rules load each session; path rules load for matching files | Current docs; inspected `paths` frontmatter is supported | **MATCH** |
| Skills | Progressive workflow disclosure → current frontmatter includes the inspected fields; `compatibility` does not gate versions | Current docs; not all semantics empirically exercised | **MATCH**, with preapproval nuance above |
| Legacy custom commands | No `.claude/commands/` found → commands still work and are merged into Skills; not obsolete | Current docs | **NOT PRESENT** |
| Subagents | Bounded roles and tool pools → current fields include `tools`, `disallowedTools`, `model`, `effort`, and `maxTurns` | Current docs; installed version is newer than the documented historical `disallowedTools` correction at v2.1.208 | **MATCH** |
| Agent teams | No team configuration found → experimental, disabled by default, with documented limits and added cost | Current docs | **NOT PRESENT; no supersession indicated** |
| Dynamic workflows | No `.claude/workflows/` found → script-based orchestration for larger parallel workflows | Current docs; documented workflow capabilities predate 2.1.290 | **NOT PRESENT; no demonstrated replacement need** |
| Permissions/settings | Static `ask`/`deny` and `blockReadsOutsideWorkingDirectories` → current keys and matching model support the inspected declarations | Current docs; effective merged settings not observed | **MATCH, runtime unverified** |
| MCP | No project `.mcp.json` found → MCP can be configured at project, user, managed, or plugin scope | Current docs; user/managed configuration not inspected | **NOT PRESENT at project scope; effective state unknown** |
| Plugins | No plugin package/config found → plugins can bundle Skills, agents, hooks, MCP, and LSP | Current docs | **NOT PRESENT in inspected project surfaces** |
| Code intelligence | No LSP/code-intelligence plugin found → Claude documents this as an optional plugin capability | Current docs | **NOT PRESENT; no repository mechanism to supersede** |
| Worktrees/background execution | No agent `isolation: worktree` configuration found; CLAUDE instructions call for isolated concurrent writers → CLI and agents support worktree/background modes | Current docs; exact runtime behavior untested | **MATCH as guidance; isolation is not configured by these agent definitions** |
| Project/user/managed precedence | Repository distinguishes managed/OS authority from project policy → current settings precedence is managed, CLI, local, project, user, with permission-specific merge behavior | Current docs; effective settings unavailable | **MATCH at the policy-layer level; no claim of an observed effective order** |

Sources: [settings](<https://code.claude.com/docs/en/settings>), [subagents](<https://code.claude.com/docs/en/sub-agents>), [agent teams](<https://code.claude.com/docs/en/agent-teams>), [dynamic workflows](<https://code.claude.com/docs/en/workflows>), [MCP](<https://code.claude.com/docs/en/mcp>), [plugins](<https://code.claude.com/docs/en/plugins>), [worktree workflow](<https://code.claude.com/docs/en/common-workflows>).

## Version-sensitive and unverified points

- The official 2.1.290 changelog says it fixed an instruction-loading issue involving external symlinks and `blockReadsOutsideWorkingDirectories`/Read denies. That is release-note evidence, not proof the fix works in this runtime; the repository’s symlink canary remains unrun.
- `/doctor prompt-audit` is documented for v2.1.283+, so it is version-compatible by the stated minimum, but was not run.
- The installed version alone does not reveal effective user, local, CLI, or managed settings; active MCP servers; selected project instruction sources; or the host sandbox mode.
- No live Claude session was launched. Hook decisions, settings parsing by the installed binary, actual context loading, and platform-specific enforcement remain **not empirically verified**. [2\.1.290 changelog](<https://code.claude.com/docs/en/changelog>)

**Overall:** I found no obsolete configured hook events, deprecated command structures, stale agent fields, or unsupported Skill frontmatter among the inspected repository mechanisms. The material semantic deltas are the limits of `SessionStart` and post-tool blocking, the approval effect of Skill `allowed-tools`, native AGENTS selection behavior, and the availability—but untested status—of `/doctor prompt-audit`.


# Architectural gap model

**Scope and baseline:** Read-only review of `C:\TEST repos\CONTROL-PLANE-SUPREME`, branch `main`, HEAD `ed4e38b22fbb27c3de6dd31e8c1d6f701bb65ff0`; the tracked working tree was clean. Claude Code reports version **2\.1.290**. I read the repository’s instructions, settings, agents, rules, Skills, hooks, state tooling and records, validation documentation, and evaluation contract. I also ran the architecture skill’s read-only structural scanner; its output is a lead list, not proof of architecture quality. No tests or live Claude session were run.

## Smallest coherent architecture

```
User request + repository + external runtime configuration
                         │
                         ▼
        Resolve instructions, settings, tools, and environment
                         │
                         ▼
    Behavioral guidance ──► Orchestrator ──► Claude Code runtime
     CLAUDE/rules/Skills      + specialists      │
                                                 ▼
                             Tools ──► hooks/helpers ──► Git/task state
                                                 │
                                                 ▼
                                execution and review evidence
```

The intended ownership model is:

| Concern | Coherent owner |
|---|---|
| Persistent and path-specific behavioral guidance | `CLAUDE.md` and scoped rules |
| Reusable procedures and role specialization | Skills and custom agents |
| Phase selection and handoffs | One coordinator |
| Deterministic lifecycle actions | Hooks and their executable helpers |
| Tool permissions and OS containment | Claude Code settings, managed policy, and host controls |
| Tool integrations and environment assumptions | Runtime configuration plus declared prerequisites |
| Change ownership | Git baseline and task-local scope |
| Validation and observability | Independent acceptance evidence plus runtime diagnostics |

This is broadly how the repository is organized. Current Anthropic docs likewise treat `CLAUDE.md` as context rather than enforcement, and describe configurable `AGENTS.md` loading, so the repository’s separation of guidance from runtime authority is well founded. [Claude memory and instruction loading](<https://code.claude.com/docs/en/memory>), [settings](<https://code.claude.com/docs/en/settings>)

## Ranked architectural gaps

### 1\. High — Effective runtime state cannot be reconstructed from the package

**Why this matters:** The repository can describe its intended settings and bind runtime evidence to repository files, CLI version, and platform. It cannot establish the complete settings, instruction selection, integrations, or containment that a session actually resolved.

**Failure mode:** Two sessions using the same commit and Claude Code version can have different behavior due to user, local, CLI, managed, or Project Instructions configuration. A diagnostic may report a platform-derived posture without establishing which sandbox or policy is effective.

**Evidence:** /C:/TEST repos/CONTROL-PLANE-SUPREME/.claude/hooks/runtime\_compatibility.py binds version, platform, and project files, while its documented inventory excludes external user/managed configuration. /C:/TEST repos/CONTROL-PLANE-SUPREME/.claude/hooks/startup\_health.py sets `containment_posture` from `platform.system()`; it does not inspect effective sandbox settings. Yet /C:/TEST repos/CONTROL-PLANE-SUPREME/.claude/CONTROL-SURFACE.md describes startup health as recording “effective containment posture.”

**Cleaner ownership model:** Project artifacts own desired project configuration. A separate runtime observation owns claims about resolved instructions, settings, integrations, and host containment. Keep those claims distinct: Anthropic documents that settings sources merge with defined precedence, and that project instructions can be selected differently by configuration. [Settings precedence](<https://code.claude.com/docs/en/settings>), [instruction loading](<https://code.claude.com/docs/en/memory>)

### 2\. Moderate–high — A task’s “VERIFIED” seal represents execution records, not the full verification workflow

**Why this matters:** The workflow requires independent review and verification, while the deterministic gate validates successful execution records. The evidence artifact does not encode enough to establish that the documented workflow occurred.

**Failure mode:** A successful command with a criterion label can be sealed as `VERIFIED`; the gate has no durable review result or acceptance-matrix evidence to distinguish that from a complete independent verification. This does not invalidate correct use of the workflow, but the gate’s claim is weaker than the workflow’s semantic claim.

**Evidence:** /C:/TEST repos/CONTROL-PLANE-SUPREME/.claude/bin/statectl.py records command execution in `run-check`; `seal-verification` validates those records and writes `"verdict": "VERIFIED"`. /C:/TEST repos/CONTROL-PLANE-SUPREME/.claude/hooks/completion\_gate.py checks that seal and its execution records. The workflow assigns review and verification to separate stages, but the seal has no corresponding reviewer result. Repository docs already acknowledge that local evidence is mutable and oracle adequacy is outside the deterministic guarantee.

**Cleaner ownership model:** The runner owns facts about which commands ran and how they exited. The independent verifier owns the acceptance verdict and its requirement-to-evidence mapping. The completion gate can validate that those evidence types refer to the same state without presenting command success as proof of semantic acceptance.

### 3\. Moderate — Ignored task state persists across Git changes and is stale in this checkout

**Why this matters:** Task state is operational input to hooks, but is intentionally excluded from Git. That lets it outlive the repository state to which it was bound.

**Failure mode:** A previously active task can make later unrelated work appear governed by stale authority. In this checkout, ignored `change-surface.json` is active and bound to HEAD `b020765276ddd724c1ef38b9d4f56e0053397cb8`; current HEAD is `ed4e38b22fbb27c3de6dd31e8c1d6f701bb65ff0`. The guards validate this binding. Stale state is rejected by the file-scope guard and prevents shell scope snapshots; the Stop gate also rejects stale authority.

**Evidence:** /C:/TEST repos/CONTROL-PLANE-SUPREME/.claude/state/README.md says task state is ignored and ephemeral. The current ignored /C:/TEST repos/CONTROL-PLANE-SUPREME/.claude/state/change-surface.json and /C:/TEST repos/CONTROL-PLANE-SUPREME/.claude/state/ownership-baseline.json show the old binding. /C:/TEST repos/CONTROL-PLANE-SUPREME/.claude/hooks/control\_common.py compares active task HEAD with current HEAD; /C:/TEST repos/CONTROL-PLANE-SUPREME/.claude/hooks/pretool\_guard.py and /C:/TEST repos/CONTROL-PLANE-SUPREME/.claude/hooks/change\_surface\_guard.py fail closed on invalid state.

**Cleaner ownership model:** Task-local authority should have an explicit lifecycle owner and be visibly distinct from durable project configuration. Its scope and binding should make clear when it applies and when it has become stale. I did not invoke the hooks, so their behavior here is derived from source and state, not runtime-observed.

### 4\. Low–moderate — The Codex/Claude instruction boundary depends partly on local runtime selection

**Why this matters:** The repository intends `AGENTS.md` to be Codex maintainer guidance, but an ignored root `AGENTS.md` exists in this checkout. Whether Claude reads it depends on effective instruction selection.

**Failure mode:** Different local or managed Project Instructions settings can cause sessions to have different instruction inputs even with identical tracked files. A tracked project cannot by itself reproduce this checkout’s ignored AGENTS content.

**Evidence:** `git check-ignore -v` reports `.git/info/exclude` excludes root `AGENTS.md`. Root `CLAUDE.md` does not import it, and `RUNTIME-VALIDATION.md` explicitly calls for a boundary canary. Current Anthropic docs say AGENTS support is native and that the default selection depends on whether CLAUDE files exist; configurable selection can change that behavior. [AGENTS.md support](<https://code.claude.com/docs/en/memory>)

**Cleaner ownership model:** Codex maintainer instructions belong to the maintainer environment; Claude project instructions belong to the tracked Claude package. Runtime selection is an external input that should be treated as observed state rather than inferred solely from file presence.

## Areas with no demonstrated architectural gap

- **Definition plane:** The root instructions, path-scoped rules, Skills, and agent definitions have distinct stated roles. The inspected rules are path-scoped, and the agents have bounded tool declarations. I found no evidence that an agent-team or dynamic-workflow feature is needed to replace this setup.
- **Execution and authority:** Hooks separate pre-tool checks, post-tool drift detection, startup diagnostics, and Stop checks. The repository acknowledges that post-tool feedback cannot undo an action and that native-Windows hooks are not OS containment.
- **Project integrations:** No project `.mcp.json`, plugin configuration, workflow scripts, code-intelligence plugin, or legacy command directory appeared in the inspected tree. User- or managed-level integrations remain unknown.
- **Prompt diagnostics:** Current docs provide `/doctor prompt-audit` for stale or conflicting instruction files; the installed 2.1.290 meets its documented v2.1.283 minimum. It was not run, and it would not establish effective permissions or hook behavior. [Prompt audit](<https://code.claude.com/docs/en/memory>)

The main architectural uncertainty is therefore the boundary between **declared project state**, **resolved runtime state**, and **evidence strong enough to support a completion claim**. The current design names those distinctions, but runtime configuration and task-local state can still make them diverge.


# Read-only context audit

## Findings

1. **Conditional cross-runtime context leak — medium.** This repository has both `CLAUDE.md` and a 16,099-character `AGENTS.md` (2,036 words; roughly 3,200 tokens by a heuristic count). Claude Code’s current default loads `CLAUDE.md` and leaves `AGENTS.md` out when both exist. However, user or managed Project instructions can configure it to load both. Under that configuration, Claude could receive the Codex maintainer document despite its stated boundary. The repository has no `@AGENTS.md` import. Current docs describe the default and the opt-in behavior; the installed Claude Code version is 2.1.290. [Anthropic’s memory and instruction-file documentation](<https://code.claude.com/docs/en/memory>)
2. **The always-on kernel contains workflow detail duplicated in Skills — medium.** CLAUDE.md is 73 lines, 8,636 characters, and 1,173 words—about 1,650 heuristic tokens. It is below Anthropic’s suggested 200-line target, and much of it is valuable persistent guidance. The “Evidence before nontrivial writes” checklist and task-authority procedure, however, overlap with `recon-gate`; completion and verification details also recur in the verification workflow. This loads procedural detail during unrelated or read-only tasks. Anthropic recommends keeping persistent files to facts needed every session and moving multi-step procedures to Skills. [Memory and instruction-file guidance](<https://code.claude.com/docs/en/memory>)
3. **Skill routing descriptions add a modest, purposeful startup cost — low.** Ten Skills contribute about 3,672 characters of `description` and `when_to_use` metadata—roughly 520 heuristic tokens. Five agent descriptions add about 68 more. The descriptions are generally specific, and I found no clearly bad overlap among the Skills. Some agent descriptions restate the Skill they specialize in (review, verification, debugging, and research), but that duplication appears to support delegation routing and is small. Skill bodies total 30,803 characters and load on invocation, not as part of the ordinary startup cost. Anthropic documents this distinction and advises keeping descriptions clear because they drive activation. [Skills documentation](<https://code.claude.com/docs/en/skills>) · [Subagent documentation](<https://code.claude.com/docs/en/sub-agents>)
4. **Hook output is bounded and mostly decision-relevant — low.** The startup health hook emits a short status line on matching session starts and writes a structured report to state. The resume/compact hook emits at most 6,500 characters; with the current state files, its available verification excerpt is about 1,871 characters. It labels that material as data and says it does not prove the repository is unchanged. This is deferred context, not a normal-session tax. A useful future evaluation would check whether including the stored check details on resume improves continuity enough to justify their cost. Anthropic confirms hook stdout can enter context. [Hooks documentation](<https://code.claude.com/docs/en/hooks>)
5. **Path-scoped rules are correctly kept out of the global kernel — positive.** All three `.claude/rules/*.md` files declare `paths`; none is an unconditional startup rule. Their combined size is 3,483 characters (about 822 heuristic tokens), available only when matching files are read or edited. Some paths intentionally overlap—for example, migrations match both contracts/security and sensitive-area guidance. There are no nested `CLAUDE.md` files, `.claude/CLAUDE.md`, local instruction files, or active `@` imports. Current docs confirm that nested instruction files load on demand and path-scoped rules activate for matching files. [Memory and rule-loading documentation](<https://code.claude.com/docs/en/memory>)
6. **No project-defined MCP context was found.** There is no `.mcp.json` or MCP server declaration in project settings. User or managed MCP configuration and the live session’s built-in tools were outside this repository-only inspection, so their actual context cost is unknown. Current docs say MCP tool names and server instructions load at startup while full schemas are deferred until needed. [MCP documentation](<https://code.claude.com/docs/en/mcp>)

## Approximate context cost

The ordinary project-specific startup estimate is roughly **2,300 heuristic tokens**: the root `CLAUDE.md`, Skill descriptions, agent descriptions, and the short startup-hook message. This excludes Claude’s system prompt and any user/managed instructions, MCP configuration, or other runtime-provided context. It also excludes the path-scoped rules and full Skill/agent bodies.

If Project instructions are configured to load both `CLAUDE.md` and `AGENTS.md`, the AGENTS file could add roughly **3,200 more heuristic tokens**. These token estimates are approximations derived from repository text, not Claude’s measured `/context` output.

## Candidate transformations

| Candidate | Current cost or problem | Semantic owner and proposed destination | Expected context reduction | Possible adherence loss | Migration risk and evidence |
|---|---|---|---:|---|---|
| Move the detailed nontrivial-write checklist and `statectl` procedure from `CLAUDE.md` into `recon-gate`; retain a short always-on trigger and critical ownership invariant in `CLAUDE.md`. | The 1,446-character “Evidence before nontrivial writes” section overlaps the Skill’s checklist and task-authority guidance. | Reconnaissance and task-boundary procedure → `recon-gate`. | Roughly 250–350 tokens from ordinary sessions, depending on the retained invariant. | A change could reach implementation without loading the detailed procedure if Skill routing fails. | **Moderate.** Authority initialization and user-work ownership are consequential. Keep the trigger and strongest invariant persistent; rely on the Skill for the checklist. Repository evidence: `CLAUDE.md` and `.claude/skills/recon-gate/SKILL.md`. |
| Consolidate phase routing between the root classification list and `engineering-flow`. | The root lists the lifecycle routes; `engineering-flow` describes and routes much of the same lifecycle. | Universal entry-point routing → concise kernel; detailed phase selection and handoffs → `engineering-flow`. | About 100–170 tokens. | Less direct routing if a task spans phases but the Skill is not selected. | **Low to moderate.** Current descriptions already expose when the Skill applies, and the Skill contains the detailed route. Evidence: `CLAUDE.md`, `.claude/skills/engineering-flow/SKILL.md`, and its routing-evaluation reference. |
| Move task-specific completion/sealing instructions from the kernel into the verification workflow, retaining the concise universal completion standard. | Completion requirements and verification sealing are described in both the kernel and verification Skill. | Evidence sealing and structured verification procedure → `verification-gate`; universal “do not claim unrun checks passed” invariant → kernel. | Roughly 80–150 tokens. | Verification may be skipped if the handoff route is missed. | **Moderate.** The Stop hook enforces some active-task evidence conditions, but it is not a universal quality check. Evidence: `CLAUDE.md`, `.claude/skills/verification-gate/SKILL.md`, and `.claude/hooks/completion_gate.py`. |
| Keep `AGENTS.md` outside Claude’s loaded instructions unless shared loading is intentional. | Conditional extra context of roughly 3,200 tokens, with a potential Codex/Claude boundary mismatch. | Codex maintainer guidance → remain an independent artifact; any shared Claude guidance should be deliberately authored as a small shared surface. | Zero in the current documented default; up to roughly 3,200 tokens under “load both.” | None under the default. With shared loading, separating guidance requires explicitly deciding which common facts Claude needs. | **Configuration-dependent.** No import exists and the current default excludes `AGENTS.md`; user or managed settings can opt in. Evidence: current Anthropic instruction-file behavior and the repository’s explicit boundary language. |
| Evaluate trimming or freshness-labeling verification details in resume/compact hook output. | The current stored verification excerpt costs about 1,871 characters when emitted; the hook does not validate freshness before displaying it. | Current-task continuity → session-context hook; evidence validity → existing verification/Stop gate. | Up to roughly 450–500 tokens on resume/compact, depending on content and trimming. | Less useful handoff context and possible repeated checks. | **Low to moderate.** Output is bounded, explicitly labeled data, and does not claim to prove the current repository state. Retain a clear freshness caveat if changed. Evidence: `.claude/hooks/session_context.py` and `.claude/hooks/completion_gate.py`. |

## Proposed context architecture

- Keep `CLAUDE.md` as the short, universally useful kernel: repository identity, core invariants, concise workflow triggers, and the control-plane boundary.
- Keep multi-step checklists, authority initialization, review procedures, and verification sealing in the relevant Skills.
- Keep path-scoped rules as they are; they already defer policy to matching work areas.
- Keep agent descriptions brief for routing, with role constraints and report formats in their isolated prompts. The current descriptions are small and do not justify a broad rewrite.
- Preserve resume context as bounded data, with freshness clearly distinguished from validity.
- Keep `AGENTS.md` separate from Claude’s loaded instruction set unless the project explicitly chooses a shared instruction configuration.
- Add no project MCP guidance or metadata unless the project actually configures an MCP server.

## Evidence and limits

The worktree was clean on branch `main` at `ed4e38b22fbb27c3de6dd31e8c1d6f701bb65ff0`. I ran `claude --version` and observed **2\.1.290**, and inspected the repository’s instruction, rules, Skills, agents, settings, and relevant hook sources. I did not edit files or run tests. I did not inspect user or managed Claude settings, query a live Claude session with `/context`, or execute hooks in Claude Code; therefore effective instruction selection and measured runtime token usage remain unverified.



# Skills subsystem audit

**Scope and evidence.** Read-only audit of the clean repository at `ed4e38b` on `main`. It contains ten Skills under `.claude/skills/`, one Skill reference file, and no `.claude/commands/` directory. `claude --version` returned **2\.1.290**; that confirms the installed CLI version, but does not verify that it loads or executes these Skills correctly. No files were changed and no tests were run.

Anthropic’s current documentation says custom commands and Skills share the same invocation model, existing `.claude/commands/` files continue to work, and Skills can also be invoked automatically when relevant. It documents `allowed-tools` as a temporary permission preapproval for the invoking turn, subject to the runtime’s permission settings—not as a grant of task authority. The Agent Skills standard specifies portable `SKILL.md` metadata and resources, but Claude-specific frontmatter and field formats are not necessarily portable. [Claude Code Skills documentation](<https://code.claude.com/docs/en/skills>), [Agent Skills specification](<https://agentskills.io/specification>).

## 1\. Current Skill graph

`engineering-flow` routes lifecycle work to discovery, reconnaissance, debugging, architecture, research, implementation, review, and verification. `implementation-slice` also routes to most of those specialists, including the requirements-only oracle. The specialist Skills then hand work to custom agents or the local state utility.

| Skill | Role, trigger, and composition | Assessment |
|---|---|---|
| product-discovery (/C:/TEST repos/CONTROL-PLANE-SUPREME/.claude/skills/product-discovery/SKILL.md:3) | Underspecified product or feature intent → bounded outcome and acceptance criteria; can invoke current-docs research. | Description and exclusion are clear. Appropriate for automatic invocation when intent is vague. Mostly judgment-led; no script needed. Requires user input only for consequential unresolved decisions. |
| recon-gate (/C:/TEST repos/CONTROL-PLANE-SUPREME/.claude/skills/recon-gate/SKILL.md:3) | Nontrivial repository writes lacking baseline, ownership, scope, or oracle evidence → reconnaissance handoff; can initialize/update `statectl` task state. | Strong, bounded procedure and useful handoff. Fits automatic routing before writes. Local state changes are concrete side effects and depend on normal runtime authorization and project hooks. |
| architecture-gate (/C:/TEST repos/CONTROL-PLANE-SUPREME/.claude/skills/architecture-gate/SKILL.md:3) | Material long-lived boundary or platform decisions → compare options and record a decision; may invoke recon, research, or architect agent. | Good exclusions protect routine work from ceremony. Clear procedure. `allowed-tools` preapproves recon/research Skill calls for the invocation turn. |
| current-docs-research (/C:/TEST repos/CONTROL-PLANE-SUPREME/.claude/skills/current-docs-research/SKILL.md:3) | Time-sensitive technical claims → primary-source evidence and coverage report; runs with `evidence-researcher` in isolated context. | Strong source-coverage and uncertainty handling. Appropriate as an automatically invoked supporting skill when external facts could change a decision. Depends on Claude’s fork/agent and web-tool support. Its `background: false` requires Claude Code v2.1.218 or later; the installed version is newer, but no runtime compatibility canary was run. |
| debug-loop (/C:/TEST repos/CONTROL-PLANE-SUPREME/.claude/skills/debug-loop/SKILL.md:3) | Unknown-cause bugs/failures → reproduce, discriminate hypotheses, identify root cause and regression oracle; runs with `root-cause-debugger`. | Clear trigger, exclusion, and stopping condition. Context isolation is useful for diagnosis. Depends on forked custom agent and read/execute tools, but has no direct edit tools in that agent definition. |
| oracle-design (/C:/TEST repos/CONTROL-PLANE-SUPREME/.claude/skills/oracle-design/SKILL.md:3) | Requirements-only acceptance oracle → matrix without implementation/tests; runs with the read-only `verifier` agent. | Distinct purpose from post-change verification and a useful separation against implementation-biased expectations. Description is precise despite no `when_to_use`. Claude-specific fork/agent routing. |
| implementation-slice (/C:/TEST repos/CONTROL-PLANE-SUPREME/.claude/skills/implementation-slice/SKILL.md:3) | Bounded, evidenced change → implementation, then review and verification. | Strong safeguards and completion evidence. Appropriate for automatic use once readiness is established. **Largest overlap:** it duplicates routing, handoff, retry, review, and verification logic owned by `engineering-flow` and `CLAUDE.md`. |
| review-change (/C:/TEST repos/CONTROL-PLANE-SUPREME/.claude/skills/review-change/SKILL.md:3) | Existing diff before final verification → independent review by `code-reviewer`. | Precise trigger, read-only role, and bounded Git context. Eight explicit Bash/PowerShell Git preapprovals are narrow; they avoid prompts for those inspection commands during invocation, not for other actions. |
| verification-gate (/C:/TEST repos/CONTROL-PLANE-SUPREME/.claude/skills/verification-gate/SKILL.md:3) | Review-clear current change → execute acceptance checks and return `VERIFIED` or `NOT VERIFIED` via `verifier`. | Clear evidence standard and failure reporting. It can execute repository-controlled commands, so execution remains subject to normal tool permissions and task authorization. Appropriate for lifecycle routing; not appropriate to treat a Skill call or successful command as authority or proof by itself. |
| engineering-flow (/C:/TEST repos/CONTROL-PLANE-SUPREME/.claude/skills/engineering-flow/SKILL.md:3) | Multi-stage/end-to-end engineering request → coordinate specialist Skills and track lifecycle state. | Useful explicit coordinator for multi-stage requests, but overlaps substantially with always-on routing and implementation’s own lifecycle loop. Its `allowed-tools` preapproves calls to eight lifecycle Skills for the invocation turn. |

The Skill graph uses both reusable knowledge/workflow and executable capabilities, but those remain distinct. Custom agent definitions shape context and tools; they do not establish an OS security boundary. The project’s control-surface documentation already describes skill tool entries as narrow runtime preapprovals, while `.claude/settings.json` holds separate deny/ask rules.

## 2\. Duplication graph

- **Routing:** `CLAUDE.md` lines 6–13 → `engineering-flow` lines 24–37 → partial duplicate in `implementation-slice` lines 19–30. The first two both route discovery, recon, architecture, debugging, research, implementation, review, and verification.
- **Lifecycle completion and retries:** `engineering-flow` lines 58–79 and `implementation-slice` lines 45–58 both define review/repair/reverification cycles, evidence freshness, and stopping after repeated blockers. `CLAUDE.md` also defines completion requirements.
- **Scope and user-work preservation:** repeated in `CLAUDE.md`, `recon-gate`, `implementation-slice`, and `engineering-flow`. Some repetition is useful at phase boundaries, but the same universal policy appears across layers.
- **Inspect before executing repository commands:** appears in always-on guidance, `recon-gate`, `debug-loop`, and `verification-gate`, and again in debugger/verifier agent instructions.
- **Handoff shape:** all workflow Skills define custom status/evidence/scope/next fields. This supports phase separation, though adjacent handoffs could be standardized or at least checked for consistency.
- **Oracle and verification:** `oracle-design` derives requirements-based checks; `verification-gate` runs them. This is meaningful composition rather than redundant ownership, but `implementation-slice` repeats the connection and its invalidation rules.

The repository’s `routing-evals.md` contains eight expected routing cases, but it is designated for evaluation/revision and is not itself evidence that routing behavior was evaluated.

## 3\. Trigger-quality analysis

Most descriptions say what the Skill does and `when_to_use` adds positive and negative boundaries. This fits the standard’s recommendation that descriptions contain both purpose and trigger cues. Strong boundaries include `architecture-gate` excluding routine choices, `recon-gate` excluding read-only/trivial work, and `review-change` excluding design review and changes without a diff.

Trigger risks and opportunities:

- **`engineering-flow`** can match broadly because “two or more lifecycle stages” covers much ordinary engineering work. `CLAUDE.md` already routes individual stages; the flow Skill needs evidence of added value beyond repeating that router.
- **`implementation-slice`** is likely to activate for many implementation requests. Its readiness criteria constrain execution, but its body also coordinates review and verification, making a broad trigger more consequential.
- **`verification-gate`** executes checks and can consume time or mutate local state through repository commands. Claude documentation recommends manual-only invocation for workflows whose timing the user should control. Whether automatic routing should remain enabled is a repository policy choice; current always-on instructions call for verification on substantive changes.
- **`current-docs-research`** has a suitably narrow freshness criterion, but its compatibility metadata names a minimum runtime/custom-agent requirement rather than reporting tested compatibility.
- **`oracle-design`** has no separate `when_to_use`; its description and body still establish a strong requirements-only boundary.

All Skills currently permit model invocation by default. That is coherent with the always-on lifecycle router, but trigger quality and false-positive/false-negative behavior are not empirically established.

## 4\. Missing reusable workflows

These are hypotheses grounded in existing recurring repository material, not recommendations to add machinery without evaluation.

- **Control-plane change validation/evidence sealing:** `CLAUDE.md` repeatedly prescribes selftests, metrics, runtime validation, Git-diff review, and state sealing. This could be a reusable maintainer workflow if control-plane maintenance recurs often. It should call deterministic checks rather than copy their procedures.
- **Claude runtime compatibility validation:** `.claude/RUNTIME-VALIDATION.md` describes a detailed multi-surface canary. It could be exposed as an explicit, manually invoked Skill because it is a costly, deliberate validation procedure. This is not a routine workflow and involves fixture mutation, so current manual timing control is appropriate.
- **Repository-specific verify/run recipe:** Current Claude docs describe Skills that record run/verify recipes for nonstandard applications, but this repo is a control-plane repository, not the governed application. No repo-specific app launch workflow is evidenced here; do not add one based on that feature alone.
- **No recurring README workflow found:** There is no README in the tracked file inventory, and no `.claude/commands/` legacy command content to migrate or preserve.

## 5\. Candidate consolidation or splits

- **Assess whether `engineering-flow` adds enough beyond `CLAUDE.md` plus specialist Skills.** If retained, keep it as the explicit multi-stage coordinator and reduce duplicated lifecycle logic elsewhere. If not, the always-on router already covers task routing. Evidence does not establish which variant performs better; the routing eval cases could form a behavioral comparison.
- **Separate implementation from orchestration only if overlap causes measurable confusion.** `implementation-slice` currently owns changes and describes review/verification coordination. One plausible architecture is implementation-only instructions plus coordinator-owned phase routing. This would be a meaningful ownership change, so it requires evidence rather than cosmetic splitting.
- **Keep `oracle-design` and `verification-gate` separate.** Their isolation requirements differ: one must not inspect implementation or tests; the other must execute against the current changed state.
- **Keep `review-change` and `verification-gate` separate.** Review is read-only judgment; verification executes checks.
- **No basis to merge architecture, recon, and current-docs research.** Their decision scopes differ and their handoffs compose cleanly.

## 6\. Portability opportunities

The portable core is the directory-based package, Markdown procedures, `name`, and `description`. The Agent Skills standard supports optional references, scripts, and assets, as well as `compatibility`, but broader Claude-specific behavior should be treated as an adapter surface.

Claude-specific or nonportable elements in this suite include:

- `.claude/skills/` discovery location and `/skill-name` invocation;
- `when_to_use`, `argument-hint`, `context`, `agent`, and `background` frontmatter;
- Claude’s `Skill(...)` tool-preapproval syntax and current list-form `allowed-tools`;
- `$ARGUMENTS` substitution;
- dynamic context injection in `review-change`;
- custom-agent names and role capabilities.

The standard describes `allowed-tools` as a space-separated string and notes that support varies; Claude Code’s current docs accept a list. Thus list-form preapprovals are a compatibility portability risk, not evidence that Claude currently rejects them. A second risk is top-level Claude-specific metadata: Claude recognizes `when_to_use`, but it is not part of the standard’s portable field set. Portability work should preserve Claude behavior while explicitly identifying these extensions; converting frontmatter blindly could lose routing or preapproval behavior.

`compatibility: "Targets Claude Code v2.1.218+ ..."` is consistent with the documented minimum for `background: false`, but it does not establish that these Skills have been tested on all versions at or above that threshold.

## 7\. Validation gaps

Static validation in `.claude/selftest/selftest.py` checks the required Skill inventory, nonempty name/description, uniqueness, exact preapproval lists, and bounded Git context for review (`lines 451–471`). It does **not** establish:

- YAML/frontmatter validity against the Agent Skills spec or Claude’s current schema;
- frontmatter `name` matching the directory name;
- validity of Skill/agent references, `Skill(...)` patterns, `$ARGUMENTS`, or Markdown links;
- existence and validity of legacy command files (none exist now);
- routing quality, over-triggering, missed triggers, or adherence to the routing eval corpus;
- behavioral completion, handoff compatibility, or side-effect behavior;
- cross-client portability or current Claude runtime loading.

The only packaged Skill reference is `engineering-flow/references/routing-evals.md`; it is linked from the Skill and appears present. No Skill package includes `scripts/`, assets, or a deterministic Skill-specific validator. That is reasonable for mostly judgment-heavy workflows, but frontmatter/reference checking is mechanical and is a strong candidate for deterministic validation.

`.claude/EVALUATION.md` describes a behavioral evaluation approach and one documentation-research coverage case, but the case is expressly a specification, not an executed result. The repository contains no recorded runtime-validation evidence file. No live Skill loading, invocation, or agent handoff was verified in Claude Code 2.1.290.

## 8\. High-value Skill hypotheses

1. **Control-plane maintainer validation:** Reusable workflow for maintaining this control plane, invoking existing static checks and compatibility validation and explaining their evidence limits. Its value depends on recurring use; avoid duplicating `CLAUDE.md`.
2. **Runtime compatibility canary:** Explicit, user-invoked wrapper around the existing runtime-validation procedure. High value where compatibility claims matter; keep the detailed procedure/reference lazy-loaded and make the side effects and prerequisites obvious.
3. **Skill package integrity checker:** Prefer a deterministic script or extension to the existing selftest over a prose Skill. It could validate spec/Claude frontmatter, directory/name correspondence, references, and known extension use. This addresses a concrete static validation gap.
4. **Routing evaluation runner:** Only if repeated behavioral evaluations become a real maintenance need. The current eight cases are a useful seed, but should not become a claimed quality score without executed comparisons and adjudicated outcomes.


## Current orchestration graph

```
User
 └─ Main session: CLAUDE.md routes work
     ├─ Vague product intent → product-discovery Skill
     ├─ Existing repo / unclear baseline → recon-gate Skill
     ├─ Material design choice → architecture-gate
     │    ├─ Optional system-architect agent
     │    └─ Current external fact → current-docs-research
     │         └─ evidence-researcher agent
     ├─ Unproven bug cause → debug-loop (forked context)
     │    └─ root-cause-debugger agent
     └─ Bounded implementation → implementation-slice
          ├─ Optional requirements-only oracle-design
          │    └─ verifier agent
          ├─ Primary session implements and adjudicates
          ├─ review-change (fresh fork)
          │    └─ code-reviewer agent
          └─ verification-gate (fresh fork)
               └─ verifier agent
```

The intended workflow and handoffs are explicit in /C:/TEST repos/CONTROL-PLANE-SUPREME/CLAUDE.md:49 and engineering-flow (/C:/TEST repos/CONTROL-PLANE-SUPREME/.claude/skills/engineering-flow/SKILL.md:43). The primary session owns synthesis, implementation, and adjudication. The lifecycle Skills describe a review-and-repair loop; the Stop hook and `statectl` add machine-checkable evidence gates.

This is a good fit for ordinary repository changes: bounded specialist tasks, one implementation owner, a fresh review, and a separate verification pass. It follows the proposed topology in substance. Reconnaissance, design, and debugging occur when needed; parallel exploration is optional and capped by project guidance. Verification is **not fully deterministic by itself**: the verifier agent chooses and interprets checks, while the checks and state-bound records provide deterministic evidence.

## Project agents

All five agents inherit their model (`model: inherit`). All set high effort except the evidence researcher, which uses medium effort. None declares a `skills` preload or `permissionMode`; available permissions therefore depend on the session’s effective policy. Agents can invoke Skills when their tool list includes `Skill`. Their project prompt and applicable persistent instructions provide further guidance.

| Agent | Trigger and responsibility | Tools and permissions | Input and expected output | Write authority and relationships |
|---|---|---|---|---|
| `system-architect` (definition (/C:/TEST repos/CONTROL-PLANE-SUPREME/.claude/agents/system-architect.md:1)) | Optional independent view on material architecture and boundaries | Read/search/LSP, web, Skill; denies Edit, Write, NotebookEdit, Agent. No shell. | Decision, relevant paths and constraints → compact decision record with options, tradeoffs, recommendation, verification, and unresolved decisions | No direct write tools. Used by `architecture-gate`; its result is evidence, not authorization. |
| `evidence-researcher` (definition (/C:/TEST repos/CONTROL-PLANE-SUPREME/.claude/agents/evidence-researcher.md:1)) | Current official documentation and primary evidence | Read/search, web, Skill; denies Edit, Write, NotebookEdit, Bash, PowerShell, Agent | Focused technical question → claims, source locators and coverage, verified/inferred status, compatibility, and consequences | No direct write or shell tools. Invoked by `current-docs-research`. |
| `root-cause-debugger` (definition (/C:/TEST repos/CONTROL-PLANE-SUPREME/.claude/agents/root-cause-debugger.md:1)) | Reproduce and diagnose a failure before edits | Read/search/LSP, Bash, PowerShell, Skill; denies Edit, Write, NotebookEdit, Agent | Symptom and repository context → reproduced evidence, hypotheses, likely cause, minimal correction boundary, regression oracle | No direct edit tools, but shell execution can potentially write. Its no-patch constraint is partly behavioral and depends on session permissions/hooks. Used by `debug-loop`. |
| `code-reviewer` (definition (/C:/TEST repos/CONTROL-PLANE-SUPREME/.claude/agents/code-reviewer.md:1)) | Independent review of an existing diff | Read/search/LSP, Skill; denies Edit, Write, NotebookEdit, Bash, PowerShell, Agent | Objective, acceptance criteria, and current diff → severity-ranked findings, concrete evidence, and limitations | Strongest direct write restriction: no file-edit or command tools. Invoked by `review-change`. |
| `verifier` (definition (/C:/TEST repos/CONTROL-PLANE-SUPREME/.claude/agents/verifier.md:1)) | Execute acceptance/regression checks and report evidence | Read/search/LSP, Bash, PowerShell, Skill; denies Edit, Write, NotebookEdit, Agent | Criteria, relevant boundaries, and commands → exact checks/outcomes, proof, failures, unverified items, verdict | No direct edit tools, but shell execution can potentially write. Used by both `verification-gate` and `oracle-design`. |

Per Anthropic’s current [subagent documentation](<https://code.claude.com/docs/en/sub-agents>), custom subagents load project instructions unless configured otherwise, and subagents can spawn nested subagents when `Agent` is available. Here, all five definitions deny `Agent`, which matches the project’s nonrecursive policy. All forked Skills set `background: false`, so their results are awaited rather than continuing as unattended writers.

## Findings

### Medium: oracle design and verification reuse the same agent role

`oracle-design` and `verification-gate` both use the `verifier` agent. The Skills distinguish the phases: oracle design forbids inspecting implementation and existing tests, while verification asks the agent to derive and execute checks from the changed boundaries. Because the agent’s persistent prompt is written for post-implementation verification, this pairing puts differently scoped work under the same role instructions. The fresh fork and explicit Skill prompt reduce the risk, but do not eliminate the instruction tension.

**Recommendation:** consider a distinct requirements-oracle role only if evaluation shows oracle design is contaminated by implementation/test knowledge or repeatedly requires coordinator correction. The evaluation contract (/C:/TEST repos/CONTROL-PLANE-SUPREME/.claude/EVALUATION.md:1) already gives a suitable way to test that hypothesis.

### Medium: shell-capable “no edit” specialists have execution, not zero-write, capability

The debugger and verifier deny direct file-edit tools but retain Bash and PowerShell for reproductions and checks. Their prompts prohibit editing; the project settings also provide permission rules and hooks. Still, “no direct file-edit tools” is not equivalent to “cannot write”: shell commands can alter files if effective runtime controls permit them. This is an intentional capability tradeoff for executing checks, not evidence of an actual write.

**Recommendation:** preserve this arrangement while tests need command execution, but describe these roles as _no direct edit tools; shell constrained by session controls and role instructions_. If a future task requires stronger isolation, validate runtime enforcement or use a separate worktree and explicit output review.

### Low: workflow procedure is repeated across Skills and agent prompts

The `debug-loop` Skill and debugger prompt both prescribe reproduction, hypothesis discrimination, and a regression oracle. The review and verification Skills also repeat much of their agents’ checklists and return formats. This is not a hidden full-lifecycle workflow in an agent: `engineering-flow` clearly owns routing, and each agent’s procedure is bounded to its specialist task. Some duplication appears intentional to keep each role self-contained, but it increases maintenance drift risk.

**Recommendation:** retain role-specific constraints and output contracts in agent prompts. When editing this suite, check that duplicated procedural details stay aligned; do not consolidate solely to reduce line count.

No redundant personas or overlapping implementation writers were found. Architecture review and current-docs research can touch similar subject matter, but their intended outputs differ: design choices versus verified external facts. The reviewer and verifier also inspect some of the same risk areas, but one performs a no-shell diff review and the other executes checks. Review is fresh-context and separate from implementation; the main session remains responsible for resolving disagreements and deciding completion.

## Current Claude capabilities and fit

Anthropic’s current [dynamic workflows documentation](<https://code.claude.com/docs/en/workflows>) describes a materially different orchestration primitive: Claude writes a JavaScript orchestration script; the runtime runs agent fan-out, branching, and synthesis in the background. Workflow state lives in script variables, runs are resumable within the session, and the documented default limit is up to 16 concurrent agents. The built-in `/deep-research` workflow fans out research, cross-checks sources, and returns a cited report. The installed 2.1.290 CLI is newer than the documented version threshold for configurable workflow concurrency, but whether workflows are available in a particular account or provider is unverified.

**Fit:** potentially useful for large, homogeneous, read-heavy audits or research where each unit can be independently processed and mechanically collected. It could solve token-heavy fan-out and repeated synthesis work. It does not replace the current normal-change lifecycle: the workflow runtime has no direct filesystem or shell access, but its agents do; it does not accept user input mid-run except for permission prompts or usage limits; and automatic `ultracode` mode removes the ordinary concurrent-subagent cap and launch approval described in the docs. Those properties conflict with this repository’s cautious routing if enabled as a default. **Do not enable that default based on this audit.**

Anthropic describes `/batch` as decomposing a large codebase change into 5–30 units, assigning each to an isolated worktree, then implementing, testing, and publishing each unit ([commands reference](<https://code.claude.com/docs/en/commands>)). This could help broad migrations with genuinely independent modules, but its publication behavior is an external side effect and requires separate authorization under this repository’s policy. It is not a fit for ordinary bounded changes.

[Agent teams](<https://code.claude.com/docs/en/agent-teams>) provide peer messaging and a shared task list. Anthropic calls them experimental and documents coordination overhead, task status lag, lack of session resumption for in-process teammates, and no nested teams. They could help long-running peer work with interdependent tasks, but add little to the current central synthesis barrier and would complicate information flow. No adoption case is established here.

[Cross-session messaging](<https://code.claude.com/docs/en/cross-session-messaging>) passes text between sessions without transferring conversation history or files. Permission rules remain per-session, and incoming messages cannot approve permissions or change configuration. It could be useful to hand off a concrete finding between sessions working in separate worktrees, but it does not provide shared state or prove that a reported change landed. Treat messages as evidence leads that the receiver must verify against repository state.

Claude worktrees isolate working files and branches but share Git history. Subagent worktrees default to the repository’s configured base behavior, which can be the default branch rather than the parent session’s current `HEAD`; `.worktreeinclude` can copy ignored files into each worktree ([worktrees documentation](<https://code.claude.com/docs/en/worktrees>)). No project agent currently declares `isolation: worktree`, and none has direct write tools. The project instruction that concurrent/background writers need separate worktrees is therefore a behavioral rule for future writers, not automatic isolation configured on current specialists.

## Concurrency, failure, and information flow

- **Concurrency/write conflicts:** Current Skills direct the primary session to be the single implementation owner and serialize overlapping writes. They require worktrees for concurrent/background writers. The five bespoke agents cannot recursively delegate and none is an intended writer. Git status, scoped hooks, and task authority provide additional state evidence, but do not turn behavioral orchestration rules into universal enforcement.
- **Delegation failure modes:** missing specialist agent or Skill; stale fork context because it does not inherit the conversation; incomplete/failed command or API calls; shell side effects from debugger/verifier; findings based on a diff that changes after review; and handoff omissions. The Skills explicitly require self-contained fork payloads and current-state review/verification.
- **Information flow:** the main session passes bounded task inputs to forked agents; agents return summaries to the coordinator. Forked workers do not inherit conversation history, though project instructions load. Researcher output and tool results are evidence, not instructions. Review and verification inspect repository state independently, so their findings must be rebound to the exact current diff. Cross-session messages, if used, carry only text and should not be treated as a file transfer or authenticated state update.
- **Synthesis responsibility:** clear and centralized. The main session adjudicates agent findings; no project agent is assigned synthesis authority.

## Candidate experiments

| Experiment | Problem it could solve | Evidence required before adopting |
|---|---|---|
| Dynamic workflow for a large, read-only audit | Coordinator context becomes dominated by repetitive per-file findings | Compare against the existing capped fan-out on the same representative audit: coverage, false findings, citation/source quality, token cost, latency, failure recovery, and whether the script preserves an explicit synthesis/check stage. Inspect the generated script before launch; keep concurrency bounded and opt-in. |
| Dynamic workflow for a large migration | Many independent files can be transformed and verified separately | Prove the units are actually independent, verify worktree base and ignored-file behavior, measure conflict/rework and test coverage, and confirm publish/PR behavior is not triggered without authorization. |
| Cross-session message between separate worktrees | A breaking discovery or decision must reach another active worker promptly | Run a controlled case showing delivery and receiver-side verification against Git state; test held/refused messages and avoid sending secrets or permission requests. |
| Agent team for interdependent peer tasks | Several long-running workers need to coordinate directly | Demonstrate a real dependency that central handoffs cannot handle efficiently; measure coordination overhead, stale tasks, recovery after resume, and write conflicts. Current experimental limitations make this a weak default. |
| Separate requirements-oracle agent | Shared verifier role may bias oracle design toward existing implementation/tests | Evaluate representative tasks blind to implementation, record whether it inspects forbidden artifacts or derives implementation-shaped expectations, and compare requirement coverage with the current verifier-based fork. |

**Overall:** the repository’s central-coordinator structure remains the better default. Dynamic workflows are the most promising capability for a specific class of wide, repeatable, read-heavy work; agent teams and cross-session messaging do not presently solve an observed routine orchestration problem. No repository edits or runtime acceptance checks were performed, as requested.


## Findings

1. **HIGH — `statectl init` can silently replace active task authority.** The shell guard recognizes `statectl.py` as a trusted route and asks for approval on `update-scope` and `deactivate`, but not `init` (/C:/TEST repos/CONTROL-PLANE-SUPREME/.claude/hooks/pretool\_guard.py:68). `init` overwrites both the ownership baseline and change surface (/C:/TEST repos/CONTROL-PLANE-SUPREME/.claude/bin/statectl.py:43). That can replace the active scope and its record of pre-existing dirty work without the “explicit transition” described in /C:/TEST repos/CONTROL-PLANE-SUPREME/CLAUDE.md:30 and state README (/C:/TEST repos/CONTROL-PLANE-SUPREME/.claude/state/README.md:16). This is a gap between behavioral policy and the configured guard; the utility itself does not authorize that rebind.
2. **HIGH, conditional — repository settings do not provide an OS enforcement boundary.** The project config has no `sandbox` settings; Claude Code’s shell sandbox is off by default and is unsupported on native Windows. The project’s shell rules and hooks therefore cannot enforce filesystem or network isolation against arbitrary subprocesses. The installed CLI is `claude.exe` on Windows, but the effective Claude session environment and any managed policy were not inspected, so whether separate containment exists is **unverified**. Anthropic documents that sandboxing is OS enforced, applies to shell processes, and requires managed settings to enforce centrally; its permission rules are not a boundary around alternate command spellings or arbitrary scripts ([sandbox docs](<https://code.claude.com/docs/en/sandboxing>), [permissions docs](<https://code.claude.com/docs/en/permissions>)). The repository correctly describes Windows hooks and permissions as defense in depth in /C:/TEST repos/CONTROL-PLANE-SUPREME/.claude/CONTROL-SURFACE.md:31.
3. **MEDIUM — active scope can be absent in a worktree.** Hooks locate the project from the event’s `cwd`; `find_project_root` selects the nearest ancestor containing `.claude` before consulting `CLAUDE_PROJECT_DIR` (/C:/TEST repos/CONTROL-PLANE-SUPREME/.claude/hooks/control\_common.py:37). Task state is ignored and stored per worktree. A worktree with `.claude` but without copied or initialized state therefore has no active surface: the file guard returns without applying task scope, and the shell guard skips its snapshot. The current config has no `WorktreeCreate` hook to establish or diagnose that state. Claude’s docs distinguish the fixed `CLAUDE_PROJECT_DIR` from the worktree-following `cwd` ([hooks docs](<https://code.claude.com/docs/en/hooks>)). This matters when the project’s stated worktree workflow expects the parent task’s protections to carry over.
4. **MEDIUM — failing shell commands receive no post-command scope audit.** The shell snapshot is created in `PreToolUse`, but only `PostToolUse` is configured for Bash and PowerShell. That event runs after success; partial file changes made by a command that exits with an error are not checked by the current post-hook (/C:/TEST repos/CONTROL-PLANE-SUPREME/.claude/settings.json:203, /C:/TEST repos/CONTROL-PLANE-SUPREME/.claude/hooks/posttool\_scope\_audit.py:30). The documented `PostToolUseFailure` event receives the same tool input and ID, so it could reconcile the snapshot after failures ([hooks docs](<https://code.claude.com/docs/en/hooks>)).
5. **MEDIUM — startup health is diagnostic, not a session gate.** `CONTROL-SURFACE.md` says the startup hook “fails” when unhealthy, but the hook is on `SessionStart`; current Claude Code documentation says that event cannot block session startup. Its nonzero result is shown as a hook error to the user, while the session proceeds (/C:/TEST repos/CONTROL-PLANE-SUPREME/.claude/CONTROL-SURFACE.md:15, /C:/TEST repos/CONTROL-PLANE-SUPREME/.claude/hooks/startup\_health.py:91, [hooks docs](<https://code.claude.com/docs/en/hooks>)). A later `Stop` check can block completion if it sees an unhealthy health file, but that does not prevent tool use earlier in the session. This is a **category error** if “fails” is meant to claim enforcement; it is accurate only as a failing hook result and recorded diagnostic.
6. **MEDIUM — command-hook failure and timeout are fail-open for pre-tool policy.** `PreToolUse` is the correct event for blocking a tool call, and the scripts use exit code 2 for hard blocks. But current Claude Code proceeds through normal permission handling if a command hook times out or cannot start. Both configured hooks have 10-second timeouts, and their enforcement also depends on the runtime resolving the quoted `${CLAUDE_PROJECT_DIR}` command and finding `python` on `PATH` (/C:/TEST repos/CONTROL-PLANE-SUPREME/.claude/settings.json:159; [hooks docs](<https://code.claude.com/docs/en/hooks>)). A missing Python interpreter or hook launch failure therefore does not itself enforce the project policy. The manifest declares Python 3 and Git prerequisites, but not the `python` command spelling or a minimum Python version; the source uses Python 3.10 union syntax. The current shell reports Python 3.14.3 and Git 2.53.0.

## Policy and enforcement matrix

| Surface | Event, matcher, handler | Inputs and result semantics | Mutation, side effect, failure behavior | Classification and evidence |
|---|---|---|---|---|
| Shell guard | `PreToolUse`, `Bash\|PowerShell` → `python .../pretool_guard.py` | Reads tool name, command, `cwd`, and tool-use ID. Hard matches exit 2; ask matches emit a `permissionDecision: ask` JSON result; otherwise silent exit 0. | Captures a bounded Git snapshot under ignored `.claude/state/.hook-snapshots/` before checking ask patterns. Parse, authority, or snapshot errors exit 2. A runtime timeout or launch failure proceeds normally. | Deterministic pre-tool decision **when the hook runs**; ask requests approval but does not itself grant authorization. Regex checks are defense in depth, not complete command containment. |
| File scope guard | `PreToolUse`, `Edit\|Write\|NotebookEdit` → `change_surface_guard.py` | Reads tool/path input and `cwd`; resolves target path. Protected paths and ownership baseline return deny JSON; user-owned dirty or unexpected paths return ask JSON; otherwise exit 0 without overriding normal permission flow. | No intended state mutation. Invalid active state or missing target exits 2. If no active change surface exists, file scope is not constrained by this hook. | Deterministic gate for covered file tools with valid active state; ask is a request for user approval. It does not cover shell writes or every external tool. |
| Startup health | `SessionStart`, `startup\|resume\|clear\|compact\|fork` → `startup_health.py` | Reads `cwd`; checks required files, settings/manifest JSON, Git, optional active state, and CLI version. | Writes `.claude/state/control-plane-health.json`. On issues exits 2, but `SessionStart` cannot block startup. Invokes `claude --version` with a 2-second timeout; failure leaves version unknown. | Observation/diagnostics, **not startup enforcement**. No managed-policy state is inspected. |
| Resume context | `SessionStart`, `compact\|resume` → `session_context.py` | Reads selected fields from optional structured state; writes plain text to stdout, capped at 6,500 characters. | No intended state mutation. Missing state is omitted; malformed files log only the exception type to stderr. | Context guidance/data reinjection, not authorization or proof of current repository state. |
| Shell scope audit | `PostToolUse`, `Bash\|PowerShell` → `posttool_scope_audit.py` | Reads tool-use ID and `cwd`, loads the matching pre-tool snapshot, compares bounded Git state, and emits a top-level block decision when it detects drift. | Deletes the matched snapshot, then observes effects after the command. It explicitly cannot prevent or roll back changes. Missing input or snapshot exits silently; comparison errors report a block. It does not run on command failure. | Post-action observation and stop-before-next-model feedback, not prevention or rollback. |
| Completion gate | `Stop`, no matcher → `completion_gate.py` | Reads current full-content Git state, task scope, verification record, and health file if present. Exit 2 prevents the agent from stopping; exit 0 allows it. | No intended mutation. Missing/stale active-task verification blocks. A missing health file is accepted; an existing unhealthy or invalid one blocks. | Deterministic completion gate for a valid active task. It does not establish that the evidence’s oracle was adequate or that the evidence is authenticated. |
| Static permissions | Project `permissions.deny`, `permissions.ask`, and `blockReadsOutsideWorkingDirectories` | Deny and ask rules are runtime permission policy when the runtime loads and applies them. There are no project `allow` rules. | No repository-side effect. Effective rules can depend on other settings, session mode, and managed policy. No live effective-settings check was performed. | Permission enforcement/approval workflow at the Claude tool layer—not OS authorization, and an `ask` rule is not itself approval. |

All configured hooks are command hooks. There are no configured prompt hooks or agent hooks.

### Permission inventory

/C:/TEST repos/CONTROL-PLANE-SUPREME/.claude/settings.json:4 declares 34 deny entries and 114 ask entries. The 114 asks are 57 command patterns duplicated for `Bash` and `PowerShell`.

- **Read denies:** `.env`, `.env.*`, with carve-outs for `.env.example`, `.env.sample`, and `.env.template`; home credential/config paths `~/.ssh/**`, `~/.aws/**`, `~/.gnupg/**`, `~/.kube/**`, `~/.docker/config.json`, `~/.config/gh/hosts.yml`, `~/.config/gcloud/**`, `~/.azure/**`, `~/.git-credentials`, `~/.npmrc`, `~/.pypirc`, and `~/.claude.json`.
- **Edit denies:** `.env`, `.env.*`, with the same three carve-outs; project-root `/.claude/settings.json` and `/.claude/hooks/**`.
- **Shell denies:** both Bash and PowerShell patterns for `*.claude/settings.json*` and `*.claude/hooks/*`; Bash patterns for `cat .env*`, `cat */.env*`, and `printenv *`; PowerShell patterns for `Get-Content .env*`, `Get-Content */.env*`, and `Get-ChildItem Env:*`.
- **Ask patterns, each configured for both Bash and PowerShell:** `git push *`; `npm install *`, `npm i *`, `pnpm add *`, `yarn add *`, `pip install *`, `pip3 install *`, `uv add *`, `cargo add *`, `poetry add *`; `npm publish *`, `pnpm publish *`, `yarn publish *`, `twine upload *`, `cargo publish *`, `docker push *`; `gh pr create *`, `gh pr merge *`, `gh issue create *`, `gh issue close *`, `gh release create *`, `gh release delete *`, `gh repo create *`, `gh repo delete *`, `gh repo archive *`; `terraform apply *`, `terraform destroy *`, `terraform import *`, and the corresponding `tofu` forms; `kubectl apply *`, `create *`, `delete *`, `patch *`, `replace *`, `scale *`, `set *`, `rollout restart *`, `rollout undo *`; `helm install *`, `upgrade *`, `uninstall *`, `rollback *`; `npx -y *`, `npx --yes *`, `pnpm dlx *`, `yarn dlx *`, `uvx *`, `pipx run *`; `git reset --hard *`, `git clean -*`, `git branch -D *`, `git stash drop *`, `git stash clear`; and `rm -rf *`, `rm -fr *`, plus PowerShell `Remove-Item * -Recurse * -Force*` and `Set-ExecutionPolicy *`.

The configured `.env` carve-outs use `!` negation. Current permission documentation confirms that syntax and says it carves paths out of earlier rules in the same source ([permissions docs](<https://code.claude.com/docs/en/permissions>)). The configured `blockReadsOutsideWorkingDirectories` is also a documented setting; I found no category error in its presence.

## Lifecycle events with potential value

The current official hook reference includes `PostToolUseFailure`, `PostToolBatch`, `ConfigChange`, `WorktreeCreate`, `WorktreeRemove`, `InstructionsLoaded`, and many other events beyond this package’s four configured event types ([hooks reference](<https://code.claude.com/docs/en/hooks>)).

- **`PostToolUseFailure`** is the clearest addition for the existing scope-audit requirement: it can examine partial effects from failed Bash/PowerShell calls and reconcile their snapshots. It provides observation and feedback, not prevention.
- **`WorktreeCreate`** could detect or provision task-scoped state for new worktrees; current code otherwise treats missing state as no active scope. Its nonzero exit can fail worktree creation, so it has stronger creation-time control semantics.
- **`ConfigChange`** can audit and block in-session settings changes from project, local, or user settings. It cannot block managed `policy_settings` changes, and server-managed settings refreshes do not trigger it. This is useful for effective-state observability; it cannot replace managed policy.
- **`InstructionsLoaded`** can observe which `CLAUDE.md` and `.claude/rules/*.md` files load, but cannot block loading and does not fire for `AGENTS.md` read directly through the Project Instructions setting.
- **`PostToolBatch`** can consolidate post-tool analysis across a parallel batch and stop the next model call, but actions in the batch have already happened; it is a possible audit-efficiency improvement, not a stronger pre-execution boundary.

## Verification and limits

Repository baseline is branch `main`, `HEAD` `ed4e38b22fbb27c3de6dd31e8c1d6f701bb65ff0`, with a clean working tree. The installed CLI reported `2.1.290 (Claude Code)`. I inspected the settings, hooks, state utility, control-surface inventory, runtime-validation plan, manifest, and relevant current official Anthropic documentation.



## CAPABILITY INVENTORY

The project contains no tracked `.mcp.json`, plugin manifest, marketplace declaration, or `settings.local.json`. Its package manifest lists Python 3 and Git as prerequisites. The inventory below distinguishes repository declarations from capabilities whose effective runtime state depends on the user’s machine.

| Canonical identity | Source and scope | Enablement and model exposure | Auth, approval, network, effects, failure, updates, trust and provenance |
|---|---|---|---|
| `Bash`, `PowerShell` | Claude Code host tools; project policy in .claude/settings.json | No project-level tool allowlist. Many named high-impact commands appear in `ask` rules; the tools remain broadly available, with effective decisions also depending on session mode and other settings. | Shell commands can access files, run local programs, reach networks, and use credentials available to the process. Approval varies by command and effective policy. The project’s command patterns and hooks are not a complete sandbox. Failures include missing executables, denied calls, hook errors, or external service failures. Tool implementation and updates belong to the host runtime. |
| `Read`, `Grep`, `Glob`, `Edit`, `Write`, `NotebookEdit` | Claude Code host file tools, subject to project settings and runtime | Available according to the host and effective policy; project settings deny selected paths and editing selected control-plane files. | Read/write effects are local to accessible paths; no separate credentials or network dependency. Approval depends on policy and session mode. A path deny rule is distinct from filesystem isolation. Runtime owns tool implementation. |
| `WebSearch`, `WebFetch` | Claude Code host tools; also named in research/architecture agent definitions | Declared for selected agents. Actual availability depends on the session and host. No project restriction confines research to particular domains. | External network and returned untrusted content; no repository-specific credentials declared. Approval depends on runtime policy. Failures include unavailable tools, fetch/search errors, or incomplete results. Host owns updates. |
| `LSP` | Named in four agent tool lists; no project LSP server or plugin is packaged | Conditional: declarations do not establish that a language server is installed or exposed in a session. | Any language-server behavior and filesystem scope depend on host integration. Missing server or language support is the main fallback. No project credentials or update mechanism. |
| `Skill` and ten project skills | .claude/skills | Skills are instruction packages available when loaded/invoked; they are not executables by themselves. Names: `architecture-gate`, `current-docs-research`, `debug-loop`, `engineering-flow`, `implementation-slice`, `oracle-design`, `product-discovery`, `recon-gate`, `review-change`, `verification-gate`. Several declare narrow `Skill(...)` preapprovals in frontmatter and the manifest. | No credentials or network access inherent to a skill; effects come from tools it directs Claude to use. Failures include missing skills or referenced agents. Source/update mechanism is the checked-out repository. Skill frontmatter can grant turn-scoped tool permission, but does not constrain tool availability or replace settings policy. |
| Five bespoke agents | .claude/agents | `code-reviewer`, `evidence-researcher`, `root-cause-debugger`, `system-architect`, `verifier`. Their frontmatter names their tools and, in several cases, disallows editing or shell tools. Whether each is invoked depends on Claude’s routing and task. | Agent instructions are not an independent security boundary. `root-cause-debugger` and `verifier` include shell tools; the research agent includes web tools. Effects, auth, approval, and network follow those tools and host policy. Failure modes include unavailable agents/tools and instruction noncompliance. Repository owns definitions; runtime owns execution. |
| Seven configured hook entry points | .claude/settings.json invokes `pretool_guard.py`, `change_surface_guard.py`, `startup_health.py`, `session_context.py`, `posttool_scope_audit.py`, and `completion_gate.py` | Configured for `PreToolUse`, `SessionStart`, `PostToolUse`, and `Stop`; exact acceptance and execution were not tested in Claude Code. | Local Python subprocesses; no external credentials or network dependency declared. They inspect Git/task state, block or report selected operations, and may write local task evidence/snapshots. Failures include Python/path errors, malformed input, or stale state. They update with repository changes. They are runtime-triggered controls, not proof that an operation was prevented or rolled back. |
| `statectl.py`, `control_common.py`, `runtime_compatibility.py` | Project helpers under `.claude/bin` and `.claude/hooks` | Available as repository code; the manifest identifies `statectl.py` as the task-state mechanism. | Local Python/Git effects; no declared network/auth dependency. Failure depends on input, Git state, and Python. Updated with the repository. They are executable capabilities, not merely instructions. |
| Python 3, Git | `.claude/MANIFEST.json` external prerequisites | Required by the project manifest; installed versions are not constrained there. | Git reads/writes repository state; Python runs hooks and helpers. No project credentials required. Failure means hooks or state operations may not work. Updates are machine-managed, not pinned by the repository. |
| Claude Code runtime and account/provider connection | External host dependency, not project-owned | Version observed: `2.1.290`; sign-in/provider configuration and effective settings were not inspected. | Requires network and authentication for model use; exact provider, credentials, and current account state are unknown. Runtime auto-update behavior is host-managed. |

**MCP, plugins, marketplaces:** no project declarations were found. User-scoped, local, managed, account-synced, or session-supplied integrations were not inventoried on this machine. Current Claude Code docs describe distinct configured, enabled, connected, and available states for MCP servers, including project approval and disable controls; plugin availability likewise depends on settings, installed files, and session loading. Thus absence from this checkout cannot establish absence from a session. [MCP configuration and status](<https://code.claude.com/docs/en/mcp>), [plugin loading and scopes](<https://code.claude.com/docs/en/plugins>).

## TRUST MODEL

**CURRENT:** The project commits declarative permissions and hook commands, but runtime acceptance and enforcement depend on Claude Code and higher-level settings. The repository’s control-surface inventory (.claude/CONTROL-SURFACE.md) explicitly calls instructions advisory and describes shell post-audit as detection rather than rollback.

**DERIVED:** Trust is split among repository authors (instructions, agents, hooks), the host runtime (tool execution and permission handling), machine/account configuration (user plugins, MCP, credentials), and external services (MCP endpoints and package sources). A repository clone does not establish trust in external capability providers.

**CURRENT:** Anthropic documents that MCP servers may read or act on connected systems, recommends verifying server trust, and requires approval for project-scoped MCP configuration; it also documents plugins as capable of running code with user privileges. [MCP trust and project approval](<https://code.claude.com/docs/en/mcp>), [plugin security model](<https://code.claude.com/docs/en/plugins/security>).

## AUTHORITY MODEL

The repository’s central invariant is sound: **registered ≠ enabled ≠ visible ≠ authorized**. Settings and agent tool declarations describe policy or requested tool sets; they do not prove effective runtime authorization. Anthropic’s current permissions documentation states that permission rules govern approval, not whether tools are available. Skill `allowed-tools` grants permission for listed tools during the invoking turn, but does not restrict the available tool pool; settings still govern other tools. [Permissions](<https://code.claude.com/docs/en/permissions>), [skill tool permissions](<https://code.claude.com/docs/en/skills>).

The project also does not equate its `114` `ask` entries with a complete allowlist: there are `34` deny entries and no `allow` array. Shell remains the broadest authority surface. Project hooks can provide checks and detection, but their presence alone does not establish operating-system filesystem, network, or credential isolation. This matches the project’s stated native-Windows degraded-containment posture in .claude/MANIFEST.json.

## SUPPLY-CHAIN RISKS

- **Project-level risk is limited:** no MCP package, plugin, marketplace, third-party runtime dependency, or package lock was found in the checked-in capability configuration.
- **External extension risk remains unknown:** MCP servers and plugins may arrive through user, managed, account-synced, or session configuration.
- **Mutable plugin supply chain:** marketplaces can point to Git refs or hosted manifests; plugin updates may be automatic. Current docs say official marketplace auto-update is on by default, while third-party marketplace auto-update defaults off. Plugin installation can also install declared dependencies. [Marketplace sources and updates](<https://code.claude.com/docs/en/plugins/install>).
- **Unpinned prerequisites/runtime:** the manifest requires Python 3 and Git without version constraints; the repo does not pin the Claude Code runtime. The observed CLI version does not establish reproducible behavior.
- **MCP command drift:** no project `npx`/`uvx` MCP launch is declared. If one is supplied globally, package tags and local command resolution become external supply-chain inputs.
- **Provenance is partly local:** Git identifies project code, but cannot establish provenance or integrity of machine-installed plugins, MCP binaries, account connectors, or managed settings.

## PORTABILITY RISKS

- No project-owned integration is declared, so the repository itself does not assume a global MCP server or plugin installation.
- Effective capabilities can still differ by developer machine, account, managed policy, session flags, installed language servers, and credentials. Claude Code docs place MCP user-scope configuration and sign-in state outside the clone, and plugin user scope in machine settings/cache. [Settings scopes](<https://code.claude.com/docs/en/settings>), [plugin scopes](<https://code.claude.com/docs/en/plugins/install>).
- Manifest prerequisites are version-unpinned. Hook commands invoke `python`; environments where only `python3` is available may fail.
- Skills declare compatibility with Claude Code `v2.1.218+`; this machine’s `2.1.290` meets the textual minimum, but `.claude/RUNTIME-VALIDATION.md` says exact compatibility requires live canaries. Those canaries were not run, so compatibility is **unverified**.

## OVEREXPOSURE FINDINGS

1. **High — broad shell capability.** `Bash` and `PowerShell` are not globally denied or narrowed to purpose-built operations. The settings enumerate many risky command prefixes for `ask`, but that does not cover all ways shell commands can read files, reach the network, use available credentials, or mutate external systems. Anthropic documents that shell pattern restrictions have bypass gaps and that allowing shell can still permit network access despite WebFetch restrictions. [Permission pattern limitations](<https://code.claude.com/docs/en/permissions>).
2. **Medium — broad web reach.** Research agents can use `WebSearch` and `WebFetch`; no project domain policy is evident. These tools are useful for current documentation, but returned content is untrusted and network reach is not an authorization grant for external actions.
3. **Medium — conditional LSP exposure.** Agent definitions list `LSP`, but the repository supplies no LSP server/plugin. This can create machine-dependent availability or a silent fallback to other tools.
4. **Low — no project MCP/plugin reduction mechanism.** The repository has no project MCP/plugin integrations, so no present project-declared integration is overexposed. It also does not establish a minimum or deny policy for user/global integrations; actual exposure is unknown.

## CANDIDATE MINIMUM CAPABILITY SET

**RECOMMENDED:** Keep the project’s local read/search and file-edit tools, `Skill`, and the project hooks needed for its workflow. Retain shell only where repository work or the Git/Python helpers require it, with consequential commands subject to explicit runtime policy and host containment. Keep `WebSearch`/`WebFetch` for tasks that require current external sources; defer their use to those tasks. Treat `LSP` as optional and report an absent integration rather than assuming it exists. Add no MCP server, plugin, or marketplace unless a concrete workflow requires it; if one is proposed, identify its source, exact tools/effects, auth, approval, versioning, and update path before enabling it.

**Checks actually performed:** repository inventory and Git status; JSON parsing through PowerShell for settings counts; `claude --version`; current official Claude Code documentation review. No runtime canaries, MCP/plugin enumeration, tests, or files were changed.



# Read-only control-plane FMEA

I read the attachment and completed its requested adversarial failure-mode analysis. **No files were modified.** The worktree is clean on `main` at `ed4e38b22fbb27c3de6dd31e8c1d6f701bb65ff0`.

**CURRENT:** `claude --version` reports `2.1.290`; Python is `3.14.3`, Git is `2.53.0.windows.2`, and WSL is installed. This verifies the available versions only; I did not run a Claude session, live canaries, or self-tests. The expected ignored runtime-validation and health evidence files are absent. The repo’s live-runtime validation contract says offline checks cannot establish runtime compatibility in /C:/TEST repos/CONTROL-PLANE-SUPREME/.claude/RUNTIME-VALIDATION.md:1.

**CURRENT:** The ignored task state is active but stale. Running the read-only `python .claude/bin/statectl.py status` failed because its stored baseline HEAD differs from the worktree HEAD. If those hooks run against this state, authority validation should reject the task as stale. I left the state untouched.

## Highest-risk failure modes

Severity and detectability below are qualitative. Runtime behavior is **UNVERIFIED** wherever noted.

| Scenario | Intended → likely actual behavior | Blast radius | Observable? | Failure posture | Recovery and surviving evidence |
|---|---|---|---|---|---|
| **Multiple sessions/workers** | Separate task ownership → sessions share one `.claude/state`; `init` overwrites active authority, scope updates are read/modify/write, and the fixed `.tmp` filename can race. | Lost scope/protection, mixed task identities, invalid seals. | Corruption often surfaces; last-writer-wins replacement may not. | Mixed: validation fails closed after detectable corruption; silent replacement can fail open relative to the intended task. | Reconcile and reinitialize; overwritten evidence may be unrecoverable. |
| **Re-run or interrupted `statectl init`** | Deliberate transition → `init` has no active-state guard or explicit-transition requirement and writes baseline and surface separately. PreToolUse only asks for `update-scope` or `deactivate`. | Current dirty work can become the new baseline; prior protections disappear. | Mismatched files fail later; a successful replacement is not itself reported as a transition. | Potentially silent scope reset; partial pair usually fails closed. | Fresh reconnaissance and reinit; previous authority can be lost. |
| **Shell changes staged index/HEAD only** | Report all Git-state drift → post-audit compares only dirty-path `entries`, not `index` or `head`, despite snapshots containing them. | Staged content/mode/path changes can evade scope reporting. | Often only caught later by full verification fingerprint. | Fail-open for post-action detection. | Re-run verification; the missing audit event is not reconstructed. |
| **SessionStart health failure** | Unhealthy startup should stop work → the hook exits 2, but current Claude docs say `SessionStart` exit 2 is diagnostic and the session proceeds. `completion_gate` also accepts absent health evidence. | Work may proceed without an active health check. | Hook error may appear; enforcement is not guaranteed. | Fail-open at startup; Stop gate can use stale healthy state. | Inspect runtime diagnostics and rerun health; absent/stale evidence may not show why startup failed. |
| **Hook timeout, missing Python/Git, bad path, malformed output** | Gates should enforce → settings call literal `python`; each hook has a 10-second timeout. Current docs say timed-out command hooks on `PreToolUse` do not block, and most nonzero/error cases do not block. | Scope, command, or completion gates can be bypassed when dependencies or hooks fail. | Runtime may report an error; a missing gate can be overlooked. | **Fail-open** for many hook failure modes. | Restore dependencies and inspect effective hooks; no reliable decision record if the hook never ran. |
| **PostToolUse failure/interruption** | Preserve audit after every shell attempt → only `PostToolUse` is configured; docs specify it follows successful tool completion. Missing payload or snapshot returns silently, and the effect already occurred. | Partial mutations from failed/interrupted commands may not be compared. | Missing audit can be silent; stale snapshots are best-effort cleanup. | Fail-open detection; no rollback. | Inspect Git state manually. Evidence of the missed comparison may be absent. |
| **Unexpected cwd / nested `.claude`** | Enforce against the intended project root → root discovery chooses the nearest ancestor containing `.claude`; hooks trust event `cwd`. If that resolves to another project with no active surface, file guard allows the edit. | Wrong project’s authority, or no scope guard. | May be visible only by inspecting which root was selected. | Can fail open when wrong root has no active state. | Re-establish correct root and authority; attribution may be ambiguous. |
| **WSL filename with backslash** | Preserve exact Git path identity → Git path parsing replaces every backslash with `/`; POSIX/WSL permits backslash in filenames. Distinct paths can alias in scope checks and snapshots. | Ownership/protection misclassification and lost path evidence. | Can be silent if the alias matches an allowed path. | Fail-open on a colliding path. | Manual path reconciliation; original name may be lost in the transformed snapshot. |
| **Dirty worktree / detached HEAD** | Preserve user work and bind checks to a baseline → baseline captures dirty paths and HEAD; unassigned paths are guarded. HEAD divergence is rejected; detached HEAD itself is not clearly rejected, but different commits are detected. | Stale authority blocks work; an authorized dirty path can be modified deliberately. | Usually observable through stale/binding errors. | Mostly fail-closed. | Reconnaissance and reinit; ignored local evidence survives only if not overwritten or removed. |
| **Partial checkout / missing dependency** | Detect unavailable surfaces → startup health checks required files and Git, but itself needs Python; configured hooks that cannot start may be nonblocking. | Entire protection layer can be absent. | Runtime may show hook errors; partial checkout can go unnoticed. | Usually fail-open at the runtime hook boundary. | Restore checkout/dependencies and inspect `/hooks`, `/status`, `claude doctor`; no evidence from missing hooks. |
| **Malformed JSON / YAML/frontmatter / invalid Skill** | Reject invalid config → Claude reports settings errors/warnings and can continue without broken settings or skip individual entries; repo self-tests use JSON parsing and regex/simple frontmatter checks, not Claude’s parser. | A gate, skill, or agent may be absent while other control-plane parts still load. | Interactive settings issues can be visible; silently ignored metadata may not be. | Mixed, often fail-open for skipped entries. | Correct config and verify effective runtime state; no proof from structural self-tests alone. |
| **Stale Claude version / model switch / compaction** | Preserve workflow semantics → installed CLI version is known, but compatibility evidence is absent. Skills and agent definitions remain model guidance; compaction can truncate reattached skill context. | Workflow drift, skipped gates, different tool/model behavior. | Version is observable; semantic drift is not necessarily. | Advisory/fail-open for behavioral constraints; deterministic hooks still depend on runtime. | Re-run live canaries after version/config changes; prior evidence absent here. |
| **Unavailable MCP / network / denied permission** | Complete research or specialist workflow → no project `.mcp.json` exists; workflows may depend on WebFetch/WebSearch or normal permissions. Offline/restricted execution can prevent evidence gathering or checks. | Decisions may be delayed, incomplete, or incorrectly declared complete if the coordinator overstates results. | Denials/network errors are usually visible, but scope coverage gaps depend on reporting. | Safe only if the skill’s partial/blocked result is respected; otherwise model-dependent. | Retry when available or report `PARTIAL`; evidence is primarily conversational unless recorded. |
| **Interrupted subagent / fork context** | Get isolated, bounded evidence → forked skills do not inherit parent conversation; instructions require self-contained payloads. Interrupted agents may leave no durable report. | Missing task facts or an incomplete independent review. | Agent failure is visible if checked; omitted context may not be. | Intended safe-stop; model may continue without specialist evidence. | Reconstruct payload and rerun; unsent findings do not survive. |
| **Untrusted repository / local settings overrides** | Project controls remain effective → project settings are subject to trust and precedence; local/CLI/managed settings can alter effective behavior. Skills’ `allowed-tools` are a distinct preapproval surface and are not gated by workspace trust. | Runtime differs from checked-in assumptions. | `/status`, `/hooks`, and diagnostics can reveal sources, but repo state alone cannot. | Depends on effective settings; cannot classify from repo config alone. | Inspect actual loaded sources and permissions; effective external configuration is not captured by repository evidence. |

Repository evidence for the systemic findings is in /C:/TEST repos/CONTROL-PLANE-SUPREME/.claude/bin/statectl.py:43, /C:/TEST repos/CONTROL-PLANE-SUPREME/.claude/hooks/control\_common.py:37, /C:/TEST repos/CONTROL-PLANE-SUPREME/.claude/hooks/posttool\_scope\_audit.py:62, /C:/TEST repos/CONTROL-PLANE-SUPREME/.claude/hooks/startup\_health.py:75, /C:/TEST repos/CONTROL-PLANE-SUPREME/.claude/hooks/completion\_gate.py:77, /C:/TEST repos/CONTROL-PLANE-SUPREME/.claude/hooks/pretool\_guard.py:76, and /C:/TEST repos/CONTROL-PLANE-SUPREME/.claude/settings.json:158.

## Emergent failures

- A failed shell command plus the absence of `PostToolUseFailure` means partial effects can remain while the configured audit never compares them.
- An unhealthy `SessionStart` can proceed, and a missing health file does not itself block Stop. If a previous healthy file remains after a hook failure, Stop can see old health evidence.
- Parallel sessions can overwrite authority while another session’s check or seal is running; fingerprints detect some movement, but they do not provide mutual exclusion or recover overwritten task records.
- The index-only drift gap is especially consequential because full verification fingerprints include index blob/mode/path data, while the post-action scope audit ignores those fields.
- Platform-specific path normalization can undermine the otherwise careful NUL-delimited Git path handling on WSL/POSIX.
- A static self-test pass would not establish any of these live runtime behaviors. No tests were run in this audit.

Current Anthropic docs confirm the key runtime distinctions: [hook exit codes and timeouts](<https://code.claude.com/docs/en/hooks>), [settings precedence and diagnostics](<https://code.claude.com/docs/en/settings>), [skill tool grants and compaction behavior](<https://code.claude.com/docs/en/skills>), and [subagent model/tool behavior](<https://code.claude.com/docs/en/sub-agents>).

## Smallest architectural changes with broad effect

1. **Make task authority single-owner and transactional:** reject `init` when active authority exists; add a lock or atomic paired state transition; bind state to a task/session identity. This removes the class of concurrent overwrite and half-initialized authority failures.
2. **Audit the complete Git snapshot after every shell outcome:** compare HEAD, index, and worktree; configure failure-path auditing; make missing snapshot/payload a reported audit failure rather than silent success.
3. **Bind hooks to one explicit root:** require agreement between `CLAUDE_PROJECT_DIR`, Git top-level, and event cwd; fail closed on mismatch.
4. **Define runtime failure policy for gates:** health must be established for the current session before consequential tools proceed; choose and document a deterministic timeout/missing-dependency posture, then verify it with live canaries on supported runtimes.
5. **Preserve raw Git path bytes/names internally:** normalize separators only at a platform-specific boundary, avoiding POSIX backslash collisions.

**Evidence limit:** I did not run the live canaries, tests, or inspect the active session’s effective Claude settings. Thus exact behavior for this installed binary, its trust state, user-local overrides, and hook delivery remains **UNVERIFIED**. The audit changed no files.