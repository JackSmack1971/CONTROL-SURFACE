# Engineering-flow routing evaluations

Use these cases only when evaluating or revising the suite. They are not runtime instructions.

| Case | Representative request/state | Expected route | Must not happen |
| --- | --- | --- | --- |
| 1 | "Build a paper-trading service" with no users, scope, or acceptance criteria | `product-discovery` -> `recon-gate` if a repository exists -> design/implementation as justified | Immediate coding from vague intent |
| 2 | "Add CSV export" in an existing repo with clear acceptance criteria but unknown ownership/tests | `recon-gate` -> `implementation-slice` -> `review-change` -> `verification-gate` | Product discovery ceremony |
| 3 | Existing test fails after a refactor; root cause unknown | `recon-gate` -> `debug-loop` -> `implementation-slice` -> review -> verify | Editing before a causal hypothesis is discriminated |
| 4 | Replace the persistence layer from SQLite to Postgres | `recon-gate` -> `architecture-gate` -> implementation -> review -> verify | Treating the dependency/persistence change as a local edit |
| 5 | SDK behavior may have changed in the newest major release | `current-docs-research` before the dependent decision | Relying on model memory for a version-sensitive fact |
| 6 | A substantive implementation diff already exists and acceptance criteria are known | `review-change`; if clear, `verification-gate` | Re-running discovery/recon without stale or missing evidence |
| 7 | Review finds a blocking security regression | `implementation-slice` repair -> fresh `review-change` -> fresh `verification-gate` | Verification on the known-bad diff or reviewer self-repair |
| 8 | Verification fails twice for the same unresolved environment-dependent reason | `debug-loop` if causality is unclear, then stop with evidence after the bounded retry rule if unresolved | Infinite repair/verification loop or claiming an unexecuted check passed |

## Pass criteria

A routing evaluation passes only when:

1. every invoked phase has a task-specific reason;
2. skipped phases are skipped because their completion criteria are already satisfied or irrelevant;
3. each handoff preserves only downstream-relevant evidence;
4. review and verification remain independent from implementation;
5. `COMPLETE` is impossible without a current blocking-review-clear state and current `VERIFIED` evidence.
