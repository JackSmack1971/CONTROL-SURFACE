# Non-obvious control-plane improvement candidates

**Purpose:** decision barrier for a later implementation phase. This document records evidence-backed candidates; it does not authorize or implement them. The worktree already contained untracked `READ-ONLY-RECON.md`; that file remains untouched. The only file created for this phase is this document.

## Baseline and evidence limits

- **CURRENT:** repository root `C:/TEST repos/CONTROL-PLANE-SUPREME`, branch `main`, `HEAD ed4e38b22fbb27c3de6dd31e8c1d6f701bb65ff0`.
- **CURRENT:** before this document was created, `git status --short` showed only `?? READ-ONLY-RECON.md`. It is pre-existing local evidence and must remain untracked/local.
- **CURRENT:** the installed CLI was reported as Claude Code `2.1.290` by the reconnaissance. That identifies the binary version only.
- **CURRENT:** `python .claude/bin/statectl.py status` reports `baseline HEAD diverged`. The ignored runtime state’s `VERIFIED` label is stale and is not evidence of current verification.
- **CURRENT:** no self-tests or Claude live canaries were run in this phase. Effective managed/user settings, live event delivery, runtime root selection, and actual tool restrictions remain unverified.
- Claims about repository source below are **CURRENT** when directly located in the named file/line; causal interpretation is **DERIVED**; mechanisms and benefit targets are **RECOMMENDED**. Claude behavior drawn from official documentation is current documented behavior, not proof of behavior in this installed binary.

### Independent reasoning lanes

Three read-only lanes were used, with no shared conclusions before their reports: (A) ownership and coupling architecture, (B) empirical reliability and verification gaps, and (C) current Claude Code capability composition using official Anthropic documentation. The coordinator reconciled evidence and retains minority proposals as experiments rather than treating agreement as proof. No subagent edited files.

### Ranking scales

Each candidate has independent scores from 1 to 5. For **impact, evidence strength, risk reduction, context efficiency, maintainability, novelty**, higher is more; for **implementation cost**, 1 is low cost and 5 is high cost. Scores are comparative triage aids, not a combined score. Context efficiency means reduced unnecessary context or improved evidence-per-context, not smaller code size. Runtime-sensitive candidates require exact-version canaries before any compatibility claim.

## Candidate register

### C01 — Make task authority a single-owner, recoverable transition

- **PROBLEM:** Repeated or concurrent initialization can replace a task’s active baseline/scope, and interruption can leave a mismatched pair.
- **EVIDENCE:** `statectl.py:43–74` writes baseline and surface in separate operations; `:77–104` performs scope read/modify/write. `control_common.py:253–257` makes each individual JSON replacement atomic, not the two-file lifecycle. Current ignored state is HEAD-stale.
- **ROOT CAUSE:** Mutable shared task identity is represented in multiple independently updated files without a lifecycle lock or explicit replacement transition.
- **OWNING PLANE:** Governance/data plane; orchestration consumes its identity.
- **PROPOSED MECHANISM:** Reject `init` while an active state exists unless an explicit transition is recorded; serialize paired initialization and all read/modify/write operations; bind records to a task/session identity and provide a recoverable interrupted-transition state.
- **WHY CURRENT DESIGN CANNOT ALREADY SOLVE IT:** Per-file atomic replacement does not prevent last-writer-wins replacement, cross-file mismatch, or loss of the prior state.
- **EXPECTED MEASURABLE BENEFIT:** Zero silent active-task replacement or partial authority pairs in duplicate-init, concurrent-init, and injected-interruption fixtures.
- **COMPLEXITY:** Medium.
- **NEW FAILURE MODES:** Lock contention/stale recovery policy; unsafe recovery could become an alternate silent reset route.
- **COMPATIBILITY RISK:** Medium; scripts relying on repeated `init` would need an explicit lifecycle transition.
- **REVERSIBILITY:** High; CLI/state protocol changes can be reverted with schema migration support.
- **VALIDATION METHOD:** Temporary Git repositories; duplicate and concurrent init/update; injected interruption between writes; prove previous valid state remains recoverable. Then exercise the actual runtime path in a disposable live canary.
- **NOVELTY:** Medium.
- **CONFIDENCE:** High for the source-level defect; runtime interaction remains unverified.
- **RANKS (impact/evidence/risk reduction/context efficiency/maintainability/novelty/cost):** 5/5/5/4/4/3/3.

### C02 — Compare all captured Git dimensions after shell tools

- **PROBLEM:** Post-shell drift reporting can miss index-only and HEAD-only changes although snapshots capture them.
- **EVIDENCE:** `control_common.py` snapshot/fingerprint includes `head`, `entries`, and `index` (see its Git snapshot/fingerprint functions); `posttool_scope_audit.py:62–64` computes changed paths from `entries` alone. Reconnaissance identifies the index-only gap.
- **ROOT CAUSE:** Snapshot producer and auditor have different definitions of relevant Git state.
- **OWNING PLANE:** Governance evidence, observed by policy hooks.
- **PROPOSED MECHANISM:** Use one shared Git-state classifier for HEAD, index, and worktree dimensions; report the affected dimension and path/commit delta against allowed/protected scope.
- **WHY CURRENT DESIGN CANNOT ALREADY SOLVE IT:** Recording index/head fields has no effect because the comparison path ignores them.
- **EXPECTED MEASURABLE BENEFIT:** All controlled worktree-only, index-only, HEAD-only, and combined deltas are classified correctly; zero silent changes in those dimensions.
- **COMPLEXITY:** Medium.
- **NEW FAILURE MODES:** Legitimate staging/commit commands may create noise unless expected Git metadata transitions are modeled.
- **COMPATIBILITY RISK:** Medium; current workflows may assume only worktree paths matter.
- **REVERSIBILITY:** High.
- **VALIDATION METHOD:** Temporary repository matrix for unstaged, staged, commit/HEAD, rename, mode, and combined changes with in-scope and protected paths.
- **NOVELTY:** Medium.
- **CONFIDENCE:** High.
- **RANKS:** 5/5/5/4/4/3/3.

### C03 — Audit failed shell outcomes and expose missing comparisons

- **PROBLEM:** A shell process can fail after partial effects; its success-only post-hook may not compare the resulting state. Missing/malformed snapshot paths currently return quietly.
- **EVIDENCE:** `.claude/settings.json:203–213` binds `PostToolUse` for Bash/PowerShell only. `posttool_scope_audit.py:30–60` handles the post-use snapshot and returns for missing/invalid inputs. Current official [Hooks reference](https://code.claude.com/docs/en/hooks#posttoolusefailure) documents `PostToolUseFailure` as a separate event after tool failure; it excludes some denials/rejections. Exact installed-version behavior is **UNVERIFIED**.
- **ROOT CAUSE:** Audit lifecycle binding covers successful completion and treats absent evidence as a no-op.
- **OWNING PLANE:** Policy hook binding and governance evidence.
- **PROPOSED MECHANISM:** Reuse the audit comparison for `PostToolUseFailure`; for an active task, record or visibly report missing snapshot/payload as incomplete audit evidence. Do not imply rollback.
- **WHY CURRENT DESIGN CANNOT ALREADY SOLVE IT:** A success-path event does not execute on tool failure; current missing-snapshot handling cannot distinguish a clean result from absent evidence.
- **EXPECTED MEASURABLE BENEFIT:** In a disposable runtime canary, 100% of failed commands that create out-of-scope Git changes are surfaced; benign failures are reported without false scope alerts.
- **COMPLEXITY:** Low to medium.
- **NEW FAILURE MODES:** Duplicate or racing event delivery, absent tool-use identifiers, noisy concurrent deltas, and failure-hook timeouts.
- **COMPATIBILITY RISK:** Medium; event is currently documented, but exact payload and invocation must be checked in 2.1.290.
- **REVERSIBILITY:** High.
- **VALIDATION METHOD:** Direct fixtures for malformed/missing snapshots plus live disposable canary: failed command with partial mutation, failed no-op, denied command, and permission/schema rejection; retain version and observed payload evidence.
- **NOVELTY:** Low.
- **CONFIDENCE:** High for repository gap; medium for runtime compatibility.
- **RANKS:** 4/5/4/5/5/1/2.

### C04 — Resolve and validate one project root for every hook

- **PROBLEM:** A hook can infer the target root from event `cwd` and nearest `.claude` ancestor, while settings invoke the script from `CLAUDE_PROJECT_DIR`; nested repositories can select another project’s state or no active state.
- **EVIDENCE:** `control_common.py:37–43` selects nearest `.claude`; `pretool_guard.py:119–120` and `posttool_scope_audit.py:39` pass event cwd; settings use `${CLAUDE_PROJECT_DIR}` in hook commands. Reconnaissance marks wrong-root selection as a possible fail-open path.
- **ROOT CAUSE:** Multiple root signals are accepted without a shared agreement check.
- **OWNING PLANE:** Policy/runtime integration and governance.
- **PROPOSED MECHANISM:** Centralize root resolution and compare canonical project root, Git top-level, and event cwd containment; return an explicit mismatch diagnostic or block according to a documented policy.
- **WHY CURRENT DESIGN CANNOT ALREADY SOLVE IT:** Current helper chooses a nearest marker rather than requiring agreement among identity sources.
- **EXPECTED MEASURABLE BENEFIT:** Nested-project and mismatched-cwd canaries deterministically identify the intended root or produce a mismatch, never silently use another task surface.
- **COMPLEXITY:** Medium.
- **NEW FAILURE MODES:** False rejection for legitimate nested repositories, linked worktrees, junctions, or symlink paths if canonicalization is underspecified.
- **COMPATIBILITY RISK:** Medium.
- **REVERSIBILITY:** High.
- **VALIDATION METHOD:** Temporary parent/child repositories with different `.claude` directories, varying cwd/env/Git top-level, plus symlink and worktree cases; then live canary.
- **NOVELTY:** Medium.
- **CONFIDENCE:** Medium-high; source facts are direct, runtime values unverified.
- **RANKS:** 4/5/4/3/4/3/3.

### C05 — Stop accepting stale startup-health records as current-session evidence

- **PROBLEM:** Completion may accept an old healthy health file or no health file, despite a later startup check failing or not running.
- **EVIDENCE:** `startup_health.py` writes timestamped health state; `completion_gate.py:77–84` accepts a present record by status without checking freshness/session identity and does not reject absence. Recon’s product-semantics section records that SessionStart diagnostics do not prevent session startup under documented behavior.
- **ROOT CAUSE:** Cached diagnostics are interpreted as lifecycle evidence for another session without a freshness binding.
- **OWNING PLANE:** Governance/runtime lifecycle evidence.
- **PROPOSED MECHANISM:** Decide whether startup health is diagnostic only or a completion precondition. If it is a precondition, bind it to a reliable runtime session identifier and require a current-session result; otherwise remove it from completion acceptance while retaining diagnostics.
- **WHY CURRENT DESIGN CANNOT ALREADY SOLVE IT:** A timestamp is written but not consulted; status alone does not establish which session produced it.
- **EXPECTED MEASURABLE BENEFIT:** Prior healthy records cannot satisfy a later session’s health condition; tests distinguish absent, stale, unhealthy, and current-session records.
- **COMPLEXITY:** Low-medium, depending on an available reliable session identifier.
- **NEW FAILURE MODES:** Strict current-session requirements can block after benign resume/compact transitions or when the runtime omits identifiers.
- **COMPATIBILITY RISK:** Medium; intent of “health” in Stop must be explicit.
- **REVERSIBILITY:** High.
- **VALIDATION METHOD:** Unit fixtures for missing/stale/unhealthy/mismatched records and exact-version disposable session/resume canaries.
- **NOVELTY:** Medium.
- **CONFIDENCE:** Medium.
- **RANKS:** 4/4/4/4/4/3/2.

### C06 — Preserve raw Git path identity across platforms

- **PROBLEM:** POSIX/WSL filenames containing backslash can alias slash paths when Git output is normalized unconditionally.
- **EVIDENCE:** `control_common.py:76,83` replaces backslashes with slashes while decoding Git paths. The FMEA in `READ-ONLY-RECON.md` identifies a possible WSL/POSIX scope collision; practical exposure is platform-conditional and not reproduced here.
- **ROOT CAUSE:** Windows separator normalization is applied to repository path names without retaining raw identity.
- **OWNING PLANE:** Governance/data integrity and portability.
- **PROPOSED MECHANISM:** Preserve Git path identity internally (bytes or lossless escaped representation); normalize user-supplied patterns at an OS-aware boundary only.
- **WHY CURRENT DESIGN CANNOT ALREADY SOLVE IT:** Once two raw names normalize to the same key, later scope checks cannot recover the distinction.
- **EXPECTED MEASURABLE BENEFIT:** A POSIX fixture with `a/b` and `a\\b` keeps separate keys and correct scope decisions; ordinary Windows paths remain compatible.
- **COMPLEXITY:** Medium.
- **NEW FAILURE MODES:** Encoding, display, and glob semantics become more complex; existing scope patterns may depend on slash canonicalization.
- **COMPATIBILITY RISK:** Medium.
- **REVERSIBILITY:** High.
- **VALIDATION METHOD:** POSIX temporary Git repository with colliding spellings and Windows ordinary-path fixtures; assert distinct path accounting.
- **NOVELTY:** Medium.
- **CONFIDENCE:** Medium-high for transformation; medium for likelihood of operational exposure.
- **RANKS:** 3/5/3/3/3/3/3.

### C07 — Move detailed reconnaissance procedure out of always-on instructions

- **PROBLEM:** The kernel loads a nontrivial-write checklist and authority procedure that substantially repeats `recon-gate`, charging unrelated/read-only turns for procedure.
- **EVIDENCE:** `CLAUDE.md` “Evidence before nontrivial writes” and task-authority sections overlap `.claude/skills/recon-gate/SKILL.md`; the context audit in `READ-ONLY-RECON.md` estimates about 250–350 heuristic tokens could be removed while retaining the trigger and core ownership invariant.
- **ROOT CAUSE:** Universal policy and phase-specific procedure share the same instruction layer.
- **OWNING PLANE:** Definition/context.
- **PROPOSED MECHANISM:** Keep concise always-on trigger, user-work protection, and “never claim unrun checks” invariant in `CLAUDE.md`; move checklist sequencing and statectl steps to `recon-gate`.
- **WHY CURRENT DESIGN CANNOT ALREADY SOLVE IT:** Current duplication still loads kernel content every session; a Skill only helps when invoked.
- **EXPECTED MEASURABLE BENEFIT:** Reduce ordinary project instruction context by roughly 250–350 heuristic tokens without reducing required checklist coverage on nontrivial writes.
- **COMPLEXITY:** Low-medium.
- **NEW FAILURE MODES:** If routing fails, a consequential checklist may not load; preserve the trigger and critical invariants globally.
- **COMPATIBILITY RISK:** Low-medium; model adherence and trigger quality must be checked.
- **REVERSIBILITY:** High.
- **VALIDATION METHOD:** Compare loaded kernel token/character count and run blinded task-routing evaluation on read-only, trivial-write, and nontrivial-write cases.
- **NOVELTY:** Low.
- **CONFIDENCE:** High for duplication; medium for adherence outcome.
- **RANKS:** 2/4/2/5/4/1/1.

### C08 — Give lifecycle routing one canonical owner

- **PROBLEM:** `CLAUDE.md`, `engineering-flow`, and `implementation-slice` overlap lifecycle routing and repair/review/verification handoffs.
- **EVIDENCE:** Skills audit in `READ-ONLY-RECON.md` identifies `CLAUDE.md` routing, `engineering-flow` routing, and lifecycle/retry overlap with `implementation-slice`; ten Skills exist and routing metadata costs about 520 heuristic tokens across Skill descriptions.
- **ROOT CAUSE:** Coordinator behavior is repeated across kernel and two workflow Skills.
- **OWNING PLANE:** Definition/orchestration.
- **PROPOSED MECHANISM:** Retain short universal entry-point triggers in the kernel, assign multi-stage orchestration to `engineering-flow`, and keep `implementation-slice` bounded to implementation readiness, execution, and its handoff. Remove duplicated retry/routing instructions only after an evaluation confirms coverage.
- **WHY CURRENT DESIGN CANNOT ALREADY SOLVE IT:** Duplicated routes can diverge and make it ambiguous which sequence governs; present evaluation descriptions are not enforcement.
- **EXPECTED MEASURABLE BENEFIT:** Fewer conflicting route statements and equal or better correct workflow selection in a fixed evaluation set.
- **COMPLEXITY:** Medium.
- **NEW FAILURE MODES:** Over-centralizing can hide appropriate shortcuts or make the coordinator Skill a mandatory ceremony.
- **COMPATIBILITY RISK:** Medium; automatic Skill selection is model/runtime-dependent.
- **REVERSIBILITY:** High.
- **VALIDATION METHOD:** Route-choice cases across trivial, read-only, bug, feature, architecture, and end-to-end requests; compare correct phase selection, unnecessary steps, and omitted gates before/after.
- **NOVELTY:** Low.
- **CONFIDENCE:** Medium-high.
- **RANKS:** 3/4/2/4/4/1/2.

### C09 — Remove duplicated control-surface inventories or derive them

- **PROBLEM:** Manifest, self-tests, runtime validation, and docs separately enumerate control-plane files and evidence surfaces, creating drift risk.
- **EVIDENCE:** `.claude/MANIFEST.json`, `.claude/RUNTIME-VALIDATION.md`, self-tests, and docs each contain inventory/required-surface statements; recon’s duplication map identifies possible inventory drift, including `.mcp.json` being mentioned though absent.
- **ROOT CAUSE:** Inventory facts have multiple manually maintained owners.
- **OWNING PLANE:** Governance.
- **PROPOSED MECHANISM:** Choose one narrow authoritative inventory for release claims and derive structural checks from it, or let tests discover files and keep the manifest limited to intended required surfaces. Do not create another registry.
- **WHY CURRENT DESIGN CANNOT ALREADY SOLVE IT:** Present checks do not demonstrate a derivation contract among the copies.
- **EXPECTED MEASURABLE BENEFIT:** Every add/remove of a control file either updates the canonical inventory or yields one precise drift failure; reduce duplicated entries maintained by hand.
- **COMPLEXITY:** Low-medium.
- **NEW FAILURE MODES:** Discovery can mask accidental files; a canonical manifest can become an overbroad schema.
- **COMPATIBILITY RISK:** Low-medium; unknown external consumers of manifest.
- **REVERSIBILITY:** High.
- **VALIDATION METHOD:** Add/delete fixture files and prove the chosen source detects intended omissions while excluding state/runtime output.
- **NOVELTY:** Low.
- **CONFIDENCE:** Medium; duplication is visible, but a damaging drift incident is not demonstrated.
- **RANKS:** 2/3/2/4/4/2/2.

### C10 — Record observed instruction loads as partial session telemetry

- **PROBLEM:** Repository diagnostics can check that files exist but cannot show which project CLAUDE.md/rules were actually loaded, eagerly or lazily.
- **EVIDENCE:** `startup_health.py` validates required files rather than session load events; `.claude/RUNTIME-VALIDATION.md` asks maintainers to record instruction selection separately. Current official [InstructionsLoaded hook documentation](https://code.claude.com/docs/en/hooks#instructionsloaded) describes an observability event for CLAUDE.md and `.claude/rules` loads, but not direct AGENTS.md configuration loads. Exact 2.1.290 behavior is **UNVERIFIED**.
- **ROOT CAUSE:** File presence and runtime context selection are currently conflated in diagnostics.
- **OWNING PLANE:** Governance/observability, not enforcement.
- **PROPOSED MECHANISM:** Optional bounded, session-keyed telemetry of path, load reason, and timestamp, with diagnostics comparing observed project loads to an expected set. State explicitly that managed/user prompts and direct AGENTS loads may be absent.
- **WHY CURRENT DESIGN CANNOT ALREADY SOLVE IT:** File existence cannot distinguish loaded, shadowed, skipped, or lazy-loaded content; no load event is configured.
- **EXPECTED MEASURABLE BENEFIT:** A live canary identifies expected versus observed project instruction loads and explains a deliberately unscoped/missing rule.
- **COMPLEXITY:** Medium.
- **NEW FAILURE MODES:** Partial telemetry may be misread as a complete effective-policy inventory; stale/unbounded records or sensitive paths.
- **COMPATIBILITY RISK:** Medium; exact event availability/payload requires a canary.
- **REVERSIBILITY:** High.
- **VALIDATION METHOD:** Disposable exact-version session loading root instructions and triggering a path rule; compare event records with runtime diagnostics and known exclusions.
- **NOVELTY:** Medium.
- **CONFIDENCE:** Medium.
- **RANKS:** 3/4/2/4/3/3/3.

### C11 — Evaluate batch-level auditing only if parallel calls reproduce races

- **PROBLEM:** Per-call pre/post comparisons may observe intermediate Git state while sibling shell calls are still running, leading to ambiguous attribution or transient alerts.
- **EVIDENCE:** Settings bind per-tool pre/post hooks; snapshots are keyed per tool call in `pretool_guard.py`; current official [PostToolBatch documentation](https://code.claude.com/docs/en/hooks#posttoolbatch) describes one event after a batch resolves. Recon/capability lane flags the race as a hypothesis, not a reproduced defect.
- **ROOT CAUSE:** Audit comparison is scoped to one tool call despite concurrent execution potentially affecting shared repository state.
- **OWNING PLANE:** Governance/evidence.
- **PROPOSED MECHANISM:** First instrument/reproduce; if confirmed, prototype batch-start to batch-end comparison with attribution to participating shell calls. Retain after-effect labeling; do not treat it as pre-execution enforcement.
- **WHY CURRENT DESIGN CANNOT ALREADY SOLVE IT:** Per-call PostToolUse has no sibling-completion boundary; however, a defect is not established until reproduction.
- **EXPECTED MEASURABLE BENEFIT:** Fewer transient false alerts while preserving detection of an out-of-scope delta introduced in a parallel batch.
- **COMPLEXITY:** Medium-high.
- **NEW FAILURE MODES:** Lost/duplicated batch records, weak attribution, unrelated external edits, and delayed alerting.
- **COMPATIBILITY RISK:** Medium; event contract is documented, installed behavior unverified.
- **REVERSIBILITY:** Medium-high.
- **VALIDATION METHOD:** Controlled parallel tool canaries with known disjoint and overlapping deltas; require reproducible false alert or attribution gap before building.
- **NOVELTY:** High.
- **CONFIDENCE:** Medium-low until a race is demonstrated.
- **RANKS:** 3/4/3/3/2/5/4.

### C12 — Establish a versioned runtime canary ledger as evidence, not a claim

- **PROBLEM:** Offline self-tests establish script/structure properties but do not show that the exact Claude binary loads settings, fires events, honors hook output, or selects instructions.
- **EVIDENCE:** `.claude/RUNTIME-VALIDATION.md` distinguishes live canaries from offline checks; `runtime-validation.json` is absent; recon records no canary run and installed 2.1.290 only. The self-test suite validates local logic, not runtime semantics.
- **ROOT CAUSE:** Runtime compatibility is described as a procedure but has no current retained evidence artifact in this checkout.
- **OWNING PLANE:** Governance/validation.
- **PROPOSED MECHANISM:** Define a small, disposable-repository canary matrix and versioned evidence record (CLI version, platform, observed events/settings/instruction loads, cases run, failures, timestamp); mark missing or expired evidence `UNVERIFIED`, never pass by absence.
- **WHY CURRENT DESIGN CANNOT ALREADY SOLVE IT:** Structural checks do not execute inside Claude Code, and version query alone proves only the binary’s reported version.
- **EXPECTED MEASURABLE BENEFIT:** Every version-sensitive compatibility claim links to a current evidence record; report canary coverage and stale-evidence rate.
- **COMPLEXITY:** Medium.
- **NEW FAILURE MODES:** Stale passing records or overclaiming scope; control by expiration/version/platform binding and explicit coverage list.
- **COMPATIBILITY RISK:** Low for documentation/evidence format; medium for automating interactive cases.
- **REVERSIBILITY:** High.
- **VALIDATION METHOD:** Run focused disposable canaries for permission matching, hook event/output, instruction selection, failed tool path, and completion behavior on supported platforms; verify a missing/old record remains unverified.
- **NOVELTY:** Medium.
- **CONFIDENCE:** High that evidence gap exists; medium about best automation boundary.
- **RANKS:** 4/5/4/3/4/3/3.

### C13 — Evaluate dynamic workflows for wide, read-heavy audits only

- **PROBLEM:** A coordinator may spend substantial context collecting repetitive independent findings from many files.
- **EVIDENCE:** Current Skills and agents use bounded central coordination; the orchestration audit in `READ-ONLY-RECON.md` describes dynamic workflows as promising for large homogeneous read-heavy work. Official capability semantics must be checked against current Anthropic docs before trial; no demonstrated recurring workload metrics are retained yet.
- **ROOT CAUSE:** Fixed handoffs may require the coordinator to mediate repetitive independent units.
- **OWNING PLANE:** Orchestration.
- **PROPOSED MECHANISM:** Run an opt-in comparison experiment for a representative broad audit, requiring a generated script, bounded concurrency, collection, explicit synthesis, and no implicit write/publish actions.
- **WHY CURRENT DESIGN CANNOT ALREADY SOLVE IT:** Existing handoffs do not automatically split and collect arbitrarily many similar units; whether this is materially costly remains to be measured.
- **EXPECTED MEASURABLE BENEFIT:** Compare coverage, false findings, source quality, coordinator tokens, latency, and recovery against current capped fan-out; adopt only with net improvement and equal acceptance coverage.
- **COMPLEXITY:** Medium-high.
- **NEW FAILURE MODES:** Generated orchestration errors, missing units, nondeterministic retries, context loss, and accidental external effects.
- **COMPATIBILITY RISK:** High until availability and exact workflow semantics are verified for target runtime/version.
- **REVERSIBILITY:** High; keep opt-in and remove after experiment.
- **VALIDATION METHOD:** Paired benchmark on the same fixed audit corpus with capped concurrency, inspect generated code before execution, and independently check coverage/results.
- **NOVELTY:** High.
- **CONFIDENCE:** Low-medium; candidate is workload-dependent and not an observed current failure.
- **RANKS:** 3/3/2/4/2/5/4.

### C14 — Keep resume context freshness-bound and evidence-selective

- **PROBLEM:** Resume/compact output can spend about 1,871 characters on stored verification details that may be stale; bounded context is useful but not self-validating.
- **EVIDENCE:** Context audit in `READ-ONLY-RECON.md` measures current excerpt and notes `session_context.py` labels it as data while not validating freshness; completion gate has separate current-state fingerprint checks.
- **ROOT CAUSE:** Context restoration presents cached evidence with weaker freshness semantics than the completion gate.
- **OWNING PLANE:** Definition/context plus governance evidence.
- **PROPOSED MECHANISM:** Include compact check names/results only when fingerprints match current Git state; otherwise emit a short stale marker and next action. Keep any unvalidated content explicitly labeled as historical data.
- **WHY CURRENT DESIGN CANNOT ALREADY SOLVE IT:** Existing bounded output limits size but does not itself establish freshness at emission time.
- **EXPECTED MEASURABLE BENEFIT:** Lower resume payload size when stale, zero stale checks presented without a stale label, and no increase in repeated verification caused by removed useful context.
- **COMPLEXITY:** Low-medium.
- **NEW FAILURE MODES:** Fingerprint lookup failure can hide useful history; overly terse context can increase repeated work.
- **COMPATIBILITY RISK:** Low.
- **REVERSIBILITY:** High.
- **VALIDATION METHOD:** Fixtures with matching, mismatched, and unavailable fingerprints; measure emitted bytes and task continuation/recheck rate in representative resume cases.
- **NOVELTY:** Low-medium.
- **CONFIDENCE:** Medium-high.
- **RANKS:** 2/4/2/4/4/2/2.

### C15 — Make platform support claims follow platform-specific evidence

- **PROBLEM:** Control-plane behavior depends on Python/Git paths, separators, hook invocation, and potentially WSL versus native Windows; structural checks can pass on one host while path semantics differ on another.
- **EVIDENCE:** `.claude/MANIFEST.json` labels native Windows as degraded; runtime validation is not retained; `control_common.py` applies backslash conversion; recon lists Windows, WSL, and other external/runtime uncertainty.
- **ROOT CAUSE:** Portability is represented as general guidance without a retained per-platform behavioral matrix.
- **OWNING PLANE:** Governance/portability and runtime integration.
- **PROPOSED MECHANISM:** State supported/degraded platforms explicitly and run path/state/hook canaries on each claimed platform; report unsupported combinations rather than infer parity.
- **WHY CURRENT DESIGN CANNOT ALREADY SOLVE IT:** A native Windows version query or Python self-test cannot prove WSL/POSIX path identity or Claude hook execution there.
- **EXPECTED MEASURABLE BENEFIT:** Every platform support claim has a current platform/version evidence row; reduce platform-specific escaping/scope regressions.
- **COMPLEXITY:** Medium.
- **NEW FAILURE MODES:** Matrix maintenance and false support confidence from too few cases.
- **COMPATIBILITY RISK:** Low to medium; documentation may narrow an existing implied support surface.
- **REVERSIBILITY:** High.
- **VALIDATION METHOD:** Platform matrix for native Windows, WSL/POSIX if claimed, and supported runtime hosts; test path identity, command invocation, hook event delivery, and stale state behavior.
- **NOVELTY:** Medium.
- **CONFIDENCE:** High for evidence gap; medium for operational priority.
- **RANKS:** 3/4/4/3/3/3/3.

### C16 — Deliberately do not add more hooks merely for surface coverage

- **PROBLEM:** Adding lifecycle events or hooks without a reproduced gap increases event/version/payload and failure surface without necessarily improving enforcement.
- **EVIDENCE:** The current configured events are recognized in the reconnaissance’s current-docs review; current inventory already contains eight hook/helper files and one control common module. One narrowly grounded addition (failed-shell audit) is distinct from blanket event expansion.
- **ROOT CAUSE:** Feature availability can be mistaken for a need or a control improvement.
- **OWNING PLANE:** Policy and governance.
- **PROPOSED MECHANISM:** Require a named failure mode, owner, measurable acceptance target, and exact-version canary before adding each hook. Treat observational events as telemetry, not enforcement.
- **WHY CURRENT DESIGN CANNOT ALREADY SOLVE IT:** Existing core hooks cannot address every distinct event gap, but adding unrelated hooks does not fix those specific gaps and creates more code/config to validate.
- **EXPECTED MEASURABLE BENEFIT:** No growth in hook count without demonstrated coverage gain; maintain or improve failure-mode coverage per hook and validation burden.
- **COMPLEXITY:** Low (decision rule).
- **NEW FAILURE MODES:** Overly strict gate could reject useful observability or a real documented failure-path fix.
- **COMPATIBILITY RISK:** Low.
- **REVERSIBILITY:** High.
- **VALIDATION METHOD:** For every proposed event, map its distinct trigger to an uncovered failure case and canary that case; decline proposals with no distinct measurable case.
- **NOVELTY:** Low.
- **CONFIDENCE:** High.
- **RANKS:** 2/4/3/2/4/1/1.

### C17 — Do not add MAC/cryptographic “seals” without an independent trust root

- **PROBLEM:** Local verification JSON could be mistaken for authenticated proof; adding a local key might appear to solve tampering while providing no separate trust boundary.
- **EVIDENCE:** Recon and control-surface docs say state records are mutable local data, not authenticated provenance or authorization. The same user/process can modify repository-local state and any colocated secret.
- **ROOT CAUSE:** Integrity metadata is being asked to prove claims against an actor that controls both data and key.
- **OWNING PLANE:** Governance/trust model.
- **PROPOSED MECHANISM:** Keep seals as freshness-bound workflow evidence with explicit trust limitations; do not add cryptographic signing unless key custody is outside the mutable project/runtime boundary and a threat model needs it.
- **WHY CURRENT DESIGN CANNOT ALREADY SOLVE IT:** Hashing or local signing cannot authenticate against the same principal that can change the data and signer.
- **EXPECTED MEASURABLE BENEFIT:** Avoid false attestation claims and needless key-management code; if an external trust root is later required, define a verifiable attacker model first.
- **COMPLEXITY:** Low now; external signing would be high.
- **NEW FAILURE MODES:** Omitting a cryptographic feature could leave a genuine multi-principal tampering threat untreated; reassess if custody assumptions change.
- **COMPATIBILITY RISK:** Low.
- **REVERSIBILITY:** High.
- **VALIDATION METHOD:** Review threat model and custody boundary; demonstrate which actor can alter both state and key before proposing signing.
- **NOVELTY:** Low.
- **CONFIDENCE:** High under current local-state trust model.
- **RANKS:** 2/4/3/3/4/1/1.

### C18 — Do not enable agent teams/worktree writers by default

- **PROBLEM:** Extra orchestration or isolation machinery may add state and merge failure modes without addressing an observed routine need.
- **EVIDENCE:** Current project agents are specialist/read-oriented; `CLAUDE.md` assigns one implementation owner and requires isolated worktrees only for concurrent writers. Orchestration audit in recon found no present interdependent peer-write case.
- **ROOT CAUSE:** Agent count or new capability can be mistaken for throughput or safety.
- **OWNING PLANE:** Orchestration.
- **PROPOSED MECHANISM:** Retain central coordinator and bounded read-only fan-out as default; revisit isolation only when independent parallel writers have a real, measured task class. Where used, validate worktree base, ignored-file behavior, merge, and cleanup.
- **WHY CURRENT DESIGN CANNOT ALREADY SOLVE IT:** Current specialist roles already cover independent read-heavy work; they do not require peer messaging or parallel writes. If such work emerges, default coordinator is not sufficient, but that condition is not evidenced now.
- **EXPECTED MEASURABLE BENEFIT:** Avoid added setup/merge/cleanup cost and write collisions without reducing current audit throughput; future adoption tied to measured latency/conflict evidence.
- **COMPLEXITY:** Low to preserve; high to introduce.
- **NEW FAILURE MODES:** A blanket prohibition could slow a future genuinely parallel workload.
- **COMPATIBILITY RISK:** Low now; revisit when runtime semantics and a use case are known.
- **REVERSIBILITY:** High.
- **VALIDATION METHOD:** Measure a representative future task’s independent work units, coordination overhead, conflicts, latency, recovery, and ignored-state handling before enabling.
- **NOVELTY:** Low.
- **CONFIDENCE:** High for current topology; medium for future workload.
- **RANKS:** 2/4/2/3/4/1/1.

### C19 — Do not broaden shell regexes as a substitute for host containment

- **PROBLEM:** More command-pattern deny rules can create a false impression of security while remaining bypassable through shell syntax, alternate tools, hooks, or other capabilities.
- **EVIDENCE:** `pretool_guard.py` contains pattern-based command rules; `.claude/MANIFEST.json` describes native Windows hooks/permissions as degraded and not an OS sandbox; control-surface documentation distinguishes permissions/hooks from host containment.
- **ROOT CAUSE:** Behavioral/request-level interception is being asked to provide an effect boundary it does not own.
- **OWNING PLANE:** Policy/security boundary.
- **PROPOSED MECHANISM:** Add a regex only for a concrete, tested tool-request gap; use managed policy/OS sandbox/credential and egress controls for boundaries requiring deterministic effect containment. Make no host policy changes in this proposal.
- **WHY CURRENT DESIGN CANNOT ALREADY SOLVE IT:** Pattern matching covers known textual forms, not all ways to produce an effect; repository config cannot establish host-managed containment.
- **EXPECTED MEASURABLE BENEFIT:** Avoid unbounded regex growth and measure bypass coverage per rule; clarify unsupported containment claims.
- **COMPLEXITY:** Low for restraint; high for a real host boundary (outside this repo’s scope).
- **NEW FAILURE MODES:** Under-blocking a newly demonstrated command spelling if local rules are kept narrow.
- **COMPATIBILITY RISK:** Low for current rules; host controls vary by platform/runtime.
- **REVERSIBILITY:** High.
- **VALIDATION METHOD:** For each proposed pattern, establish exact request coverage and bypass set; separately validate host boundary in an authorized disposable environment.
- **NOVELTY:** Low.
- **CONFIDENCE:** High.
- **RANKS:** 3/5/4/3/4/1/1.

## Independent ranking ledger

The vectors below use the axis order `impact / evidence / risk reduction / context efficiency / maintainability / novelty / cost`. They are deliberately not summed or weighted.

| ID | Impact | Evidence | Risk reduction | Context efficiency | Maintainability | Novelty | Cost |
|---|---:|---:|---:|---:|---:|---:|---:|
| C01 | 5 | 5 | 5 | 4 | 4 | 3 | 3 |
| C02 | 5 | 5 | 5 | 4 | 4 | 3 | 3 |
| C03 | 4 | 5 | 4 | 5 | 5 | 1 | 2 |
| C04 | 4 | 5 | 4 | 3 | 4 | 3 | 3 |
| C05 | 4 | 4 | 4 | 4 | 4 | 3 | 2 |
| C06 | 3 | 5 | 3 | 3 | 3 | 3 | 3 |
| C07 | 2 | 4 | 2 | 5 | 4 | 1 | 1 |
| C08 | 3 | 4 | 2 | 4 | 4 | 1 | 2 |
| C09 | 2 | 3 | 2 | 4 | 4 | 2 | 2 |
| C10 | 3 | 4 | 2 | 4 | 3 | 3 | 3 |
| C11 | 3 | 4 | 3 | 3 | 2 | 5 | 4 |
| C12 | 4 | 5 | 4 | 3 | 4 | 3 | 3 |
| C13 | 3 | 3 | 2 | 4 | 2 | 5 | 4 |
| C14 | 2 | 4 | 2 | 4 | 4 | 2 | 2 |
| C15 | 3 | 4 | 4 | 3 | 3 | 3 | 3 |
| C16 | 2 | 4 | 3 | 2 | 4 | 1 | 1 |
| C17 | 2 | 4 | 3 | 3 | 4 | 1 | 1 |
| C18 | 2 | 4 | 2 | 3 | 4 | 1 | 1 |
| C19 | 3 | 5 | 4 | 3 | 4 | 1 | 1 |

## Synthesis and barrier decisions

1. **Most directly evidenced implementation candidates:** C01 (authority lifecycle), C02 (full Git-state comparison), C03 (failed-call audit), and C04 (project-root identity). They address distinct reliability gaps and should not be merged into one broad refactor.
2. **Resolve policy intent before implementation:** C05 needs an explicit decision about whether startup health is a completion precondition or diagnostics only. Current code treats it inconsistently.
3. **Experiment before building:** C10, C11, and C13 depend on exact runtime behavior or a workload/race that has not been demonstrated. C11 specifically requires reproducing a concurrent-audit defect first.
4. **Context/simplification candidates:** C07–C09 and C14 have measurable but smaller benefits. Evaluate with route-quality/freshness outcomes; token savings alone are insufficient.
5. **Portability and evidence:** C06 and C15 warrant platform-specific fixtures/canaries before claiming support or prioritizing broad changes.
6. **Negative improvements:** C16–C19 are deliberate non-build positions under the current evidence. Reopen them only when a concrete, measurable uncovered failure mode or threat-model change appears.
7. **No candidate authorizes implementation.** This artifact is the requested synthesis barrier; selection, sequencing, and implementation belong to a later explicit work phase.

## Validation performed for this phase

- Read the supplied task file and `READ-ONLY-RECON.md`.
- Inspected Git root, branch, HEAD, and status; preserved the pre-existing untracked recon file.
- Three independent read-only agent reports completed; they inspected repository evidence and, for the capability lane, current official Anthropic documentation.
- Confirmed task-state status is stale in the recon evidence; did not use its old `VERIFIED` marker as current proof.
- No repository tests, self-tests, or live Claude canaries were run. No Claude control-plane implementation files were changed.
- The final diff should contain only this new untracked synthesis artifact; recon remains untracked local data.
