# Herdr Suite Integration Program

**Status:** Wave 0 implemented on reviewed branches; merge/release gates pending; Wave 1 planned
**Date:** 2026-07-28  
**Repositories:** `herdr-browser`, `herdr-guard`, `herdr-swarm`, `herdr-conductor`, `herdr-suite-site`

## Goal

Make Browser, Guard, Swarm, and Conductor work together through a truthful, versioned local contract while preserving independent installation and each plugin's existing responsibility.

The target is not a new suite daemon or an automatic autonomous pipeline. It is a tested composition model:

- **Explore:** Swarm owns interchangeable candidates, worktree lifecycle, comparison facts, and review-first selection.
- **Deliver:** Conductor owns differentiated roles, task/report contracts, integration state, approval-aware reconciliation, and recovery.
- **Visibility:** Browser contributes operator-reviewable recordings and browser observations.
- **Policy evidence:** Guard contributes rendered-text observations, limitation states, and interrupt-request facts without claiming prevention.
- **Suite evidence:** The site owns schemas, pinned compatibility evidence, claim gates, and cross-plugin integration tests.

## Preserved Starting State

Wave 0 captured every repository's branch, HEAD, staged diff, working diff, and SHA-256 under `/tmp/herdr-wave0-preservation` before any plugin write.

| Repository | HEAD | Working state | Preserved working patch SHA-256 | Baseline tests |
| --- | --- | --- | --- | --- |
| Browser | `72b986e3a0233b938b0046806bc2aaeefb56e12e` | `tests/launchers.test.mjs` formatting-only diff | `663c533e27d1588696338d6e97862ecefa56110c990aded8eeb9ffb3e803abe0` | 122 passed |
| Guard | `fa8ebcaaf6731976b9c208ebb4bcd61339deac97` | four-file socket/lifecycle repair | `22b36a3f93058a755bf71e4818d53bc0071fbdd396a0010788d2efe0aeaeefa6` | 34 passed |
| Swarm | `0dc0a2b0a77e590d854fafd5eae0e76dbcc00017` | clean | empty patch | 198 passed |
| Conductor | `d4c6527e36991b234861781af34fe16c7ef16f4b` | clean | empty patch | 41 passed |

The Browser patch is formatting-only and should remain a separate commit. The Guard patch is a release-blocking compatibility repair: the released multiplexed socket fails on the second Herdr 0.7.5 RPC, while the preserved one-shot RPC/dedicated-subscription implementation succeeds.

Before the first write in either dirty repository, regenerate `git diff --binary`, verify it against the recorded SHA-256, record the prepared CI branch tip, and make the first mutation an isolated commit containing only the preserved files. Push or otherwise durably mirror that preservation commit before follow-on edits. `/tmp` is evidence, not durable recovery.

## Current Safety Priorities

These issues block mutating integration work:

1. **Swarm abort can delete ignored-only work.** Abort checks ordinary porcelain status but lacks Harvest's ignored-file inventory guard.
2. **Guard 0.1.0 transport is incompatible with observed Herdr 0.7.5 socket behavior.** The preserved repair must land and be live-smoked first. The site's current `tested_herdr_versions: ["0.7.5"]` evidence is invalid now and must be removed or marked pending in Wave 0, then restored only for the fixed release.
3. **Conductor active-run selection is global and workspace-blind.** Current status/harvest/stand-down can select another repository's newest run.
4. **Conductor state is executable shell data and teardown does not prove pane ownership.** Current stand-down must not be used as a cleanup mechanism for ambiguous legacy state.
5. **Conductor read-only mode is contradictory.** It neither enforces read-only launch behavior nor supplies a writable report outbox to a genuinely read-only reviewer.
6. **Conductor validator/reviewer do not consume the reconciled implementation SHA.** A gate can pass unchanged base code.
7. **Browser recording filenames use a configurable session as a path component.** Hostile local session names can escape the documented recordings directory.
8. **Swarm locks, active-run discovery, and prune protection are workspace-scoped rather than repository-scoped.**

Site copy remains bounded until these issues and the corresponding live gates close.

## Architecture Decisions

### ADR-1 — The site owns suite contracts and integration evidence

`herdr-suite-site` owns schemas, examples, compatibility pins, the stubbed E2E harness, and claim checks. This is a test/documentation responsibility, not a fifth runtime product.

No plugin imports site code at runtime. Canonical schemas remain in the site; plugin-local golden fixtures test exact emitted shapes without vendoring mutable site schemas into every repository.

### ADR-2 — Static descriptors first; one-shot adapters only with real operations

Wave 1 adds static capability descriptors derived from and tested against each plugin manifest/package. A plugin adds `bin/suite-adapter.mjs` only when its first concrete operation ships: Browser recording export, Guard bounded export, Swarm projection/preview, or Conductor report/reconciliation preview. There are no placeholder `negotiate`/`inspect` executables.

Adapter rules:

- exactly one JSON object on stdin and stdout;
- human diagnostics only on stderr;
- no sibling checkout discovery or private sibling-state parsing;
- absent adapter means that suite operation is unsupported, not plugin failure;
- existing Herdr actions remain independently usable.

Typed exit classes:

| Exit | Meaning |
| --- | --- |
| `0` | success |
| `64` | invalid request or unsupported contract |
| `69` | requested capability unavailable |
| `70` | internal failure |
| `75` | stale or retryable state |
| `77` | approval refused or already consumed |

### ADR-3 — Two small public contracts

The first public contract family contains:

1. `herdr-suite-capabilities/v1` — static descriptors and operation availability.
2. `herdr-suite-evidence/v1` — producer operation/evidence receipts, artifact references, limitations, and scoped approval receipts.

The E2E harness may keep private fixture run state and transitions under temporary test state, but there is no public coordinator/run lifecycle API until a second real coordinator needs one.

Required common identity:

- `contract`, `schema_version`, `run_id`, `plugin_id`, `plugin_version`;
- `repo_id`, `workspace_id`, `base_ref`, `base_sha` where Git applies;
- stable evidence/operation IDs and coordinator sequence;
- explicit outcome: `observed`, `passed`, `failed`, `inconclusive`, or `unavailable`;
- normalized POSIX-style relative artifact path, SHA-256, media type, and byte count; paths reject backslashes, percent-encoded separators or dot segments, empty segments, controls, absolute prefixes, and `.`/`..` segments;
- structured limitations.

Only a named test/check can report `passed`. Browser recordings and Guard observations normally report `observed`. SHA-256 proves content integrity after capture, not identity, provenance, or correctness.

### ADR-4 — The test coordinator is the sole bundle writer

The E2E harness is non-installed test code, not a general-purpose run/resume/apply CLI. It alone writes its private fixture state, approvals, imported receipt index, and artifacts. Plugins retain private operational state and return normalized receipts; they never write another plugin's state or artifact directory.

Artifact import is fail-closed: validate bounded ASCII path-derived IDs; resolve only beneath a negotiated plugin-owned export root; reject absolute/parent/control paths, empty segments, intermediate or leaf symlinks, non-regular files, duplicate destinations, and files over capability-specific limits. Copy from a no-follow source descriptor where available into a private sibling temp, enforce the byte cap while streaming, fsync, compare actual size/SHA-256, then atomically rename. Failure removes only the temp and does not publish a success receipt.

Fixture/bundle directories are `0700`, files are `0600`, and diagnostics never print artifact contents or secrets. Browser recordings, Guard text/process metadata, repository paths, reports, and logs are sensitive local data. Default retention is explicit retain; deletion requires a separate inventory preview and approval.

### ADR-5 — Capability negotiation is explicit

Descriptors separate plugin release, Herdr compatibility, suite contract version, capability version, availability, and limitations.

Examples:

- `browser.recording/1`
- `guard.rendered-text-audit/1`
- `explore.candidates/1`
- `explore.preview/1`
- `explore.apply/1`
- `deliver.roles/1`
- `deliver.reports/1`
- `deliver.preview/1`
- `deliver.apply/1`

Unknown required capability IDs or contract majors fail closed. Optional missing capabilities become `unavailable`, never silently successful.

### ADR-6 — Approval-aware mutators use explicit, atomic state

Approval binds actor kind (`human` or `trusted-orchestrator`), operation, preview evidence digest, expected base SHA/target ref, exact candidate or branch-tip set, and a one-use nonce.

Under the owning plugin's repository mutation lock, `apply` atomically transitions `{approved, nonce: unused, revision: N}` to `{consuming, operation_id, revision: N+1}` before any side effect. A retry with the same operation ID may only recover/return the journaled result; another replay is refused. A crash after consumption becomes `needs_attention` and cannot silently reapply. Failed precondition checks before consumption leave the nonce unused; any ambiguous crash or side effect requires a fresh preview and approval.

Immediately before mutation, the adapter re-computes the preview subject. Any changed base, branch tip, report digest, config digest, integration SHA, cleanup inventory, or revision performs zero external/repository mutation and supersedes the approval. Private approval state may record the superseded decision and revision; it may not consume the nonce or journal an external side effect.

V1 actor kinds are cooperative same-user assertions, not authentication against a malicious same-UID process. Approvals live outside declared worker writable roots with private modes, but hashes and permissions do not create an authorization boundary.

### ADR-7 — Swarm and Conductor remain separate owners

Swarm does not become Conductor's hidden worktree backend. Conductor does not read Swarm manifests.

The supported composition is sequential:

```text
Swarm explores interchangeable candidates
    -> explicit human-selected SHA
    -> Conductor coordinates differentiated delivery roles

Guard may observe either workflow; native harness/OS controls enforce.
Browser may contribute reviewable observation artifacts to either workflow.
```

Concurrent Swarm and Conductor mutation of one Git common directory is unsupported. The harness executes them sequentially, and each plugin keeps its own repository-scoped lock/active-run refusal. A shared cross-plugin lease is deferred unless concurrent independent mutation becomes a real supported scenario.

## Fail-Closed Security Invariants

- Every mutator requires one exact, schema-valid, regular non-symlink state generation whose repo/workspace/run identity matches the request. Missing, truncated, duplicate, incompatible, symlinked, or mismatched state returns `state_unknown`/`bookkeeping_unknown` with zero external/repository mutation. Private diagnostic state may record the refusal; `.bak` is recovery inventory, never automatic mutation authority.
- Destructive cleanup is preview/apply. The preview emits a canonical recursive inventory digest bound to physical Git common-dir identity, run, resource, and operation ID. Apply re-verifies ownership and re-computes inventory immediately before removal; any change refuses without deletion.
- Conductor pane identity includes workspace ID, pane ID, terminal ID, agent session/name, canonical cwd, run ID, and resource generation. Worktree identity includes canonical path, physical Git common dir, exact full branch ref, fork/head SHA, and `git worktree list --porcelain` membership. Missing, duplicate, changed, or foreign identity performs no close/remove.
- Stand-down closes only identity-proven panes and archives state. It does not delete worktrees, branches, or artifacts. Deletion is a separate future design.
- Private legacy state is not silently migrated or adopted. Finish a proven live Swarm v0 run with current code or start a fresh format; Conductor legacy state is read-only administrative inventory.

## Repository Tracks

### Browser

**Wave 0:** preserve the formatting-only test patch as its own commit; review the prepared CI branch rather than duplicate it; correct minor documentation/runtime drift.

**Wave 2:** replace the recording path with a run-scoped bundle:

```text
<plugin-state>/runs/run-<run-id>/browser/
  evidence.json
  recording.webm
<plugin-state>/runs/active-<workspace-key>.json
```

`record-stop` must use the start pointer's pinned session, require a non-empty artifact, compute bytes/SHA-256, atomically mark complete, and retain retry state on failure. Session names remain metadata only. Legacy recordings remain unscoped and untouched.

### Guard

**Wave 0A:** commit the preserved one-shot RPC/dedicated-subscription repair unchanged; add the missing project-subscription replacement test/fix; merge the non-overlapping prepared CI branch; live-smoke Herdr 0.7.5; release a truthful 0.1.1 hotfix.

**Wave 0B:** correct the demo and audit vocabulary. Record interrupt decision, request acceptance/failure, and `prevention: unknown` separately. Never say Guard cancelled or prevented a command.

**Wave 2:** add one bounded immutable export receipt over selected sanitized events, with producer version, policy digest, coordinator-supplied correlation, explicit omission/corruption limitations, and truthful decision/request/prevention fields. Every string leaf uses the same sanitize/redact/truncate pipeline. Keep operational rotating JSONL as the one Guard log system; defer producer run/event journals until a replay/resume consumer exists.

### Swarm

**Track 0 must land before adapters:**

- shared ignored-file inventory for Abort and Harvest;
- repository-scoped identity, locks, active-run discovery, and backup protection;
- fail-closed prune when bookkeeping is corrupt or unknown;
- idempotent full-harvest run finalization/archive and exclude cleanup.

**Wave 1/2:** add a read-only JSON projection/preview over the existing private manifest. Report recorded fork, current base, candidate head, dirty state, diff/comparison facts, and limitations. Keep candidate selection and evidence in the fixture/coordinator receipt; defer internal manifest migration, producer event journals, and readiness state until a real non-human resumable consumer needs them.

**Wave 3:** add approval-aware apply bound to expected base and expected candidate head, with idempotency keys, one JSON result envelope, and stable failure codes. Swarm never ranks or selects a winner.

### Conductor

**Stage 0:** land CI, correct README/site overclaims, archive unrelated Flotion scaffolding, and stop presenting legacy plans as current runtime contracts. Do not run current stand-down against ambiguous legacy state.

**Stage 1:** replace newest-global/PID state with strict JSON state keyed by workspace and Git common-directory; atomic writes; run-unique branches/agent names; fixed fork SHA; mutation locks; write-ahead resource journal; fail-closed pane/worktree identity.

**Stage 2:** add strict task/report schemas and atomic report outbox. Review runs against the exact integration SHA with source read-only and a separate writable outbox. Validate runs at the exact integration SHA and fails on tracked or non-allowlisted source changes.

**Stage 3:** add deterministic preview, validated verdicts, explicit approval receipts, approval-aware reconcile/apply, crash recovery, identity-checked stand-down, and archived state. Deletion/prune is deferred; E2E verifies retained cleanup inventory.

Conductor remains an advanced assembly pattern until a live E2E proves these stages.

### Suite Site

Add:

- `contracts/capabilities-v1.schema.json`
- `contracts/evidence-v1.schema.json`
- `contracts/examples/`
- `scripts/validate_suite_contract.py`
- `scripts/suite_e2e.py` (non-installed test code with private fixture state)
- descriptor digests and E2E evidence pins in `data/plugins.json`

`check_docs.py` continues rejecting unsupported automatic, unattended, secure, enforced, prevented, or attested-pipeline claims.

## Cross-Plugin E2E

After Waves 1–3, the neutral harness runs with explicit repository roots in a temporary HOME/state/Git repository and deterministic fake Herdr/agent-browser executables.

Scenario:

1. Validate all four exact static descriptors; invoke only adapters whose real operations have shipped; record limitations.
2. Start Browser recording; later import it as `observed` evidence.
3. Start Guard observer, inject one visible dangerous line and one unseen popup-equivalent event; require an interrupt-attempt observation plus `inconclusive` coverage.
4. Create two Swarm candidates from the same base: fixture candidate A passes and candidate B fails. Retain both receipts.
5. The fixture predeclares candidate A's ID/SHA and supplies a test approval; the harness never infers or ranks the winner. Apply A with expected-base/head/journal guards.
6. Assemble Conductor against the selected SHA; produce writer, validator, and reviewer reports bound to exact input/output SHAs.
7. Preview Conductor reconciliation and grant scoped approval.
8. Inject target/base drift after approval. First apply must return stale approval and perform zero external/repository mutation; private approval state may record the superseded refusal without consuming the nonce.
9. Re-preview, re-approve, and apply successfully.
10. Import Browser and Guard bounded artifacts, validate every digest, assert the exact Conductor validator receipt already produced, and verify retained cleanup inventory. The harness does not become a generic test runner or product orchestrator.

Required assertions:

- all receipts share one run ID and validate against pinned schemas;
- Guard absence/unseen behavior is never converted to `passed`;
- Browser evidence remains observational;
- failed candidate evidence remains visible;
- stale approval and replay perform zero external/repository mutation; private refusal/replay evidence is permitted;
- no plugin reads/writes another plugin's private state;
- final Git ref equals the approved apply result;
- real developer state and preservation artifacts remain untouched.

A separate opt-in live Herdr matrix is required before changing public readiness claims. Stubbed E2E proves contract behavior, not live compatibility.

## Execution Waves and Gates

### Wave 0 — preserve, repair, and freeze truthful boundaries

- Before any dirty-repo write, re-hash Browser/Guard diffs, record CI branch tips, make isolated preservation commits, and durably mirror them.
- Immediately remove or mark pending the invalid Guard 0.1.0 / Herdr 0.7.5 tested-version evidence in `data/plugins.json`, canonical Guard docs, and generated output.
- Land minimal CI/static validation tracks.
- Fix Swarm's current destructive/lifecycle blockers.
- Correct Conductor claims and remove/archival-label unrelated or stale material.
- Commit this ADR/program plan in the site.

**Gate:** preservation hashes still match; all current tests pass; no staged/unrelated files; Guard hotfix live-smoked; site still says no automatic pipeline.

### Wave 1 — schemas and static capability descriptors

- Add site capability/evidence schemas, examples, and validator.
- Add static descriptors in all four plugins, derived from/tested against manifests and package metadata.
- Do not add placeholder adapters or change plugin lifecycle/mutation behavior.

**Gate:** positive/negative schema corpus, major mismatch, missing optional/required descriptor, descriptor digest pins, and isolated plugin tests with siblings absent.

### Wave 2 — observational evidence

- Browser run-scoped recording receipt.
- Guard bounded immutable evidence export with limitations.
- Swarm candidate projection/preview receipts over its private manifest.
- Conductor report completion and reconciliation preview receipts.

**Gate:** traversal/symlink rejection, copy/re-hash validation, corrupt-state handling, no private cross-read, and no evidence outcome inflated to approval or pass.

### Wave 3 — approval-aware mutation and stubbed E2E

- Add Swarm/Conductor suite apply paths with scoped one-use approvals and atomic consume/journal semantics under each plugin's own repository lock.
- Keep Swarm and Conductor sequential; concurrent cross-plugin mutation remains unsupported.
- Run stale/concurrent approval, crash-after-consume, drift, conflict, failure, replay, corrupt-state, foreign-resource, artifact-import, and inventory-change scenarios.

**Gate:** stale apply performs zero external/repository mutation; replay is refused while private refusal evidence is permitted; failures remain recoverable; final fixture tests pass; all four receipts correlate.

### Wave 4 — live compatibility, releases, and claim updates

- Run a common live Herdr matrix against exact commits.
- Pin descriptor hashes, plugin commits/versions, and reviewed E2E evidence.
- Update canonical docs and regenerate site output.

**Gate:** live artifacts reviewed; action IDs still register; plugin limitations remain visible; no automatic/unattended/secure/attested pipeline language without separately implemented evidence.

## Non-Goals

- No central daemon, database, event bus, monorepo, or fifth runtime product.
- No plugin imports another plugin's code or parses another plugin's private files.
- No autonomous decomposition or unattended approval.
- No claim that Guard is a sandbox or proves prevention.
- No claim that Browser recording proves correctness or source provenance.
- No claim that worktrees isolate same-user filesystem/process access.
- No cryptographic worker identity or report attestation in v1.
- No automatic base update, push, PR, deployment, or branch deletion.
- No speculative compatibility shims for unsupported contract majors.
- No public coordinator/run lifecycle API from the test harness.
- No runtime migration, backfill, or silent adoption of private legacy Swarm/Conductor state.
- No concurrent Swarm/Conductor mutation support.
- No automatic deletion or cleanup under a selection/reconcile approval.

## Wave 0 Acceptance

Wave 0 is complete only when:

1. Browser and Guard preservation hashes are rechecked before the first write and after every write; exact preserved commits are durably mirrored before follow-on edits.
2. Browser formatting and Guard transport changes are committed independently and remain recoverable from remote branches.
3. The invalid Guard 0.1.0 / Herdr 0.7.5 tested-version evidence is removed or marked pending until the fixed release is live-smoked.
4. Swarm's digest-bound ignored-file cleanup, repo-scoped mutation identity, full-run finalization, and fail-closed backup protection have negative regression tests.
5. Conductor's public docs no longer claim Swarm-backed lifecycle, Guard enforcement, verified pane ownership, durable recovery, or enforced read-only behavior.
6. All plugin tests, shell/static checks, site generation, and site claim checks pass.
7. No integration-runtime claim is added to the site.

## Execution Checkpoint — 2026-07-28

Wave 0 implementation is complete on isolated, pushed branches. This checkpoint does not mean the plugin branches are merged, released, or site-pinned.

| Repository | Reviewed commit | Hosted CI | Current gate |
| --- | --- | --- | --- |
| Suite site | `6f1ecd36c767df75d4ca5e6f99bdf19252c747fd` | `30344745398` | Deployed; current public boundaries are truthful |
| Browser | `8ccc8b8764ad269ba4e7c4468bff3a0f21dde4e0` | `30348362562` | Held Wave 2 precursor layered on completed Wave 0 preservation/CI; hold merge/promotion until Wave 1 schemas and later evidence/live gates |
| Guard | `7aba52b4394d376bbdcf517fa5a5581686344798` | `30349007126` | Code ready; merge, manual smoke, `v0.1.1`, and atomic site repin remain |
| Swarm | `18fcc7b2958ff6001831d7986ab8f2e3dfe7b7ba` | `30349398711` | Exact reviewed tree is ready to merge |
| Conductor | `3e3eb80b3604c76f6b65f1f6169c17804d7cbe78` | `30343274295` | Stage 0 exact reviewed tree is ready to merge; Stage 1 remains required |

Independent final reviews for all four plugin heads reported no blocker, high, or medium findings in their approved scope. Browser and Guard preservation commits still reproduce the original recorded patch hashes exactly. All local review branches were restored to their exact remote heads after generated review artifacts were preserved separately.

### Phase A — Maintainer merge and Guard release gates

These are repository operations, not implementation work, and require explicit maintainer approval.

1. Open pull requests for exact Guard `7aba52b`, Swarm `18fcc7b`, and Conductor `3e3eb80` heads. Preserve the reviewed trees and commit history; if a merge strategy changes the resulting tree, rerun repository validation and independent review against the merge tree.
2. Keep Browser `8ccc8b8` on its integration branch. Do not merge, release, or site-pin Browser 0.6.0 during Wave 1.
3. After Guard merges, run the non-destructive manual smoke matrix in `herdr-guard/docs/SPEC.md` against the final merge tree. The transport portion is already verified against Herdr 0.7.5; live interrupt-key delivery remains optional and must not be inferred.
4. Create and verify Guard `v0.1.1` only after the smoke passes. Recompute `herdr-plugin.toml` SHA-256 from the final tag target and require it to equal the reviewed digest `36cd8ab09f82f07f56e08d15013221d4f5a46a8c2d3aca1255581b24c70dc50b`; any mismatch blocks release/site repin and requires updated review evidence. Then atomically update the site to the tag target, version `0.1.1`, recomputed manifest digest, evidence date, and `tested_herdr_versions: ["0.7.5"]`. Use “best-effort request; prevention unknown” wording.
5. If any Guard merge, smoke, or tag gate is incomplete, retain the current site withdrawal. Do not partially restore compatibility evidence.

### Phase B — Conductor Stage 1 control plane

Implement `TODO-9a1de9c8` on a new branch from the Stage-0-updated Conductor main. Stage 1 remains private plugin state; it is not a suite public contract.

#### B0. Live identity capability discovery

Before designing state fields or mutators, probe the exact supported Herdr version in a disposable workspace and record which identity fields are available from plugin context, pane/session/process inspection, and agent listings. Required pane-close identity remains workspace ID, pane ID, terminal identity, agent session/name, canonical cwd, run ID, and resource generation.

Missing, malformed, ambiguous, or unavailable required identity is a Stage 1 no-go for that mutator. Do not fall back to `CONDUCTOR_REPO`, `$PWD`, newest-global state, names, or recorded pane IDs. If Herdr 0.7.5 cannot expose the required identity, preserve the inspected capability artifact, return capability unavailable, and keep stand-down disabled rather than weakening the contract.

**Gate:** an independently reviewed live capability report maps every required identity field to an exact source and negative fixture; absent or duplicate fields produce zero close/remove/merge.

**B0 checkpoint — 2026-07-28:** PASS on Conductor branch
`stage1/b0-live-identity-probe` at
`28d518c036b9dfae76f3f7313d15db70f99712fc`. A disposable Herdr `0.7.5`
workspace (protocol `17`) exposed workspace, pane, terminal, named-agent session,
cwd, and foreground-cwd identity. Conductor-owned run/generation tokens were
published through pane metadata and read back from both pane and agent views.
The retained 32-case harness proves its positive mutation spies are observable
and all 31 missing, malformed, duplicate, foreign, or stale fixtures reach zero
mock close/remove/merge attempts. Independent re-review reported no blocker,
high, or medium findings. B1 may proceed under the report's strict tuple and
read-back constraints; pane close remains disabled until B3 production mutation
seams and immediately-before-close revalidation pass. Herdr `0.7.5` has no
conditional close parameter beyond `pane_id`, so the same-user TOCTOU boundary
remains explicit. This checkpoint does not authorize Browser promotion, runtime
evidence repinning, or any public readiness claim.

#### B1. Strict state and identity kernel

Add a private strict JSON state schema and a zero-dependency state helper. State is keyed by physical Git common-directory identity, workspace ID, run ID, and resource generation. Require exact keys/types/versions, bounded IDs, `0700` directories, `0600` files, no-follow regular-file reads, atomic temp/fsync/rename/directory-fsync writes, repository-scoped locks, and write-ahead resource journals.

Legacy shell state is read-only administrative inventory. Never source, migrate, adopt, or use it as mutation authority.

**Gate:** malformed, truncated, extra-key, wrong-version, symlinked, duplicate-active, foreign-repo/workspace, stale-generation, and lock-race inputs perform zero external mutation. Pre-intent durability failures also perform zero external mutation. A failure after state publication or an external side effect leaves the operation journaled as ambiguous/`needs_attention`, prohibits replay, and requires explicit recovery; temporary or published private state files are not counted as external mutation.

**B1 checkpoint — 2026-07-28:** PASS on Conductor branch
`stage1/b1-state-identity-kernel` at
`68d4ebefe0dd2361da6a754987f8829c52f8825a`. The additive, zero-dependency
kernel provides duplicate-key-rejecting strict JSON, physical Git common-dir
identity, private `0700`/`0600` no-follow state, file/directory-fsynced atomic
publication, repository-scoped locks, exclusive active-run identity, and guarded
hash-chained write-ahead journals. Durable activation and operation uncertainty
guards prevent partially published state from authorizing effects; run,
generation, pointer, journal, and guard paths are bound to their validated
document identity. Legacy shell state remains untouched and no current plugin
action imports the kernel. The exact head passed all 88 repository tests and
static gates on the current Node runtime, 35 targeted B1 tests on Node `20.20.2`,
ShellCheck, Actionlint, LSP/lens diagnostics, and independent security review with
no blocker, high, or medium findings. B2 may proceed; B1 does not authorize pane
close, reconcile, runtime evidence repinning, Browser promotion, or a public
readiness claim.

#### B2. Context-bound assemble, board, and status

Replace newest-global selection with explicit `HERDR_PLUGIN_CONTEXT_JSON` repository/workspace resolution. Record a fixed fork SHA before side effects; use run-unique full branch refs and agent names; journal intent before each pane/worktree/agent operation and exact observed identity afterward. Never adopt a same-named resource without exact journal proof.

**Gate:** two repositories sharing one state root and two workspaces sharing one repository cannot observe or mutate each other's runs. Crash injection after every intent/result boundary leaves truthful, non-replayed journal state.

#### B3. Identity-checked reconcile and stand-down

Hold the repository mutation lock across reconciliation preflight and Git mutation. Verify canonical worktree path, common directory, full branch ref, fork/head SHA, and registered worktree membership. Before pane close, compare workspace, pane, terminal, agent session/name, canonical cwd, run ID, and generation with live Herdr data.

Stage 1 reconciliation remains an explicitly invoked, attended native Conductor action. It has no suite adapter, public suite receipt, coordinator trigger, or automatic composition; Stage 3 alone adds the suite approval-aware apply path.

Stand-down may archive state and close identity-proven panes only. It must not delete worktrees, branches, artifacts, reports, recordings, logs, or Guard files.

**Gate:** foreign/recycled pane, changed branch/head, moved or unregistered worktree, corrupt journal, concurrent reconcile, and second-repository fixtures perform zero close/remove/merge. If Herdr cannot expose the required identity, return capability unavailable rather than weakening the check.

#### B4. Stage 1 release gate

Run Node 20/current LTS, macOS Bash 3.2, ShellCheck, Actionlint, manifest/docs gates, destructive negative tests, and independent review. Recommend Conductor `0.2.0` for the private-state break, but do not tag or repin until the maintainer approves that version and the exact tree passes an opt-in disposable-repository live smoke.

**Stage 1 release checkpoint — 2026-07-29:** PASS. Clean candidate
`274f809192fd2bfa82b3fc5922cc6710c058ef0f` passed the opt-in Herdr
`0.7.5`/protocol `17` lifecycle through all five installed actions. The retained
operator-observed evidence records thirteen strict action invocations, eight
same-repository/second-repository mutation refusals with unchanged live authority
snapshots, retained worktree/branch/artifact inventory, and zero exact-run cleanup
residue. Current Node and Node `20.20.2` passed 94 tests; macOS Bash `3.2`,
ShellCheck, Actionlint, manifest, documentation, B0, and B4 evidence gates passed.
Independent final review reported no blocker, high, or medium findings. PR
[#3](https://github.com/StructuPath/herdr-conductor/pull/3) merged as
`c982b61d6d55fa2e6ea9771b2e981fd6abe53ef8`; main CI run
[`30432652345`](https://github.com/StructuPath/herdr-conductor/actions/runs/30432652345)
passed, and release [`v0.2.0`](https://github.com/StructuPath/herdr-conductor/releases/tag/v0.2.0)
was published. Stage 1 is attended-operational, not Stage 2 approval/reporting,
a suite adapter, unattended automation, automatic recovery, or protection against
malicious same-UID processes. Browser promotion remains held.

### Phase C — Wave 1 canonical schemas and static descriptors

Implement `TODO-14dd2716` only after the schema semantics below are reviewed and frozen.

#### C1. Site-owned schemas and corpus

Add canonical `capabilities-v1` and `evidence-v1` schemas, positive examples, invalid mutation fixtures, and a pinned development-only validator. Schemas use closed objects, bounded ASCII IDs, explicit contract majors, separate plugin-release/Herdr compatibility fields, explicit outcomes, normalized POSIX relative artifact paths, and structured limitations.

Freeze these evidence kinds before implementation:

- `observation` — outcomes `observed`, `inconclusive`, or `unavailable`; zero to sixteen artifacts; approval fields forbidden;
- `check_result` — the only kind allowed outcomes `passed` or `failed`, plus `inconclusive`/`unavailable`; requires a named check ID and subject digest; zero to sixteen artifacts; approval fields forbidden;
- `operation_preview` — outcomes `observed`, `inconclusive`, or `unavailable`; requires operation ID, preview digest, revision, explicit preconditions, and `mutation_kind: read_only | mutating`;
- `operation_result` — outcomes `observed`, `inconclusive`, or `unavailable`; requires operation status (`succeeded`, `failed`, `stale`, `refused`, or `needs_attention`), journal identity, and the same mutation kind;
- `approval_receipt` — outcome `observed`, `inconclusive`, or `unavailable`; requires actor kind, scoped preview digest, expected revision, one-use nonce digest, and approval status.

Operation conditionals are closed and explicit:

- `read_only` preview/result objects forbid `approval_scope` and `approval_consumption`;
- `mutating` previews require `approval_scope` with `operation_id`, `preview_digest`, nonnegative `expected_revision`, and one to sixty-four bounded `subject_ids`; Git subjects additionally require a full expected base SHA and full target ref, while non-Git subjects forbid them;
- `mutating` results require `approval_consumption` with `approval_id`, `operation_id`, nonce SHA-256, `revision_before`, `revision_after`, and status `not_consumed | consuming | consumed | refused | needs_attention`;
- `succeeded` requires `consumed`; `stale` requires `not_consumed`; `refused` requires `refused` or `not_consumed`; `needs_attention` requires `consuming` or `needs_attention`; `failed` records whether failure occurred before consumption (`not_consumed`) or after it (`consumed | needs_attention`);
- approval receipts use status `approved | refused | superseded | consumed | needs_attention`; only `approved` carries an unused nonce, and only `consumed` names the exact consuming operation ID.

Every evidence object also declares `subject_kind: git | non_git`. Git subjects require repository/workspace/base identity; non-Git subjects forbid those fields. IDs are 1–128 characters from the contract's bounded ASCII grammar. `limitations` contains at most thirty-two closed objects with bounded code, severity (`info | warning | blocking`), and sanitized message. Artifact arrays contain at most sixteen entries; artifact-free receipts use an empty array. Artifact paths are at most 512 characters with 1–128-character slash-separated ASCII segments and reject backslashes, percent-encoded separators/dot segments, empty segments, controls, absolute prefixes, and `.`/`..`.

Static capability availability is exactly one of:

- `native` — informational support through explicit `supporting_refs`; action references are `{kind: "action", id}` and startup references are `{kind: "startup", index, command}`, where the zero-based index and exact command must match one `[[startup]]` manifest entry. Native support is human/Herdr-action-facing and never a normalized coordinator invocation surface;
- `adapter` — a real one-shot coordinator-callable executable operation exists;
- `unavailable` — the operation cannot run and cannot silently pass.

No placeholder adapter is allowed. Wave 1 validates evidence examples but does not add producer adapters.

**Gate:** positive corpus passes; unknown kind/major, duplicate IDs, missing required capability, unsupported required descriptor, invalid kind/outcome combination, missing/forbidden Git or approval fields, outcome inflation, invalid artifact cardinality/path, malformed digests, and unknown fields fail.

#### C2. Plugin static descriptors

After schema review, add static descriptors in this order: Guard, Swarm, Conductor, Browser. Every descriptor is derived from and tested against its plugin manifest/package, lists exact `supporting_refs` for each `native` capability (action ID or startup index plus exact command), and passes with sibling checkouts absent.

Required descriptor bases are:

- Guard: verified `v0.1.1` tag target; `guard.rendered-text-audit/1` native; bounded export unavailable.
- Swarm: main containing merged reviewed safety tree `18fcc7b`; `explore.candidates/1` native; suite preview/apply unavailable.
- Conductor: reviewed Stage 1 main, not Stage 0; `deliver.roles/1` native; reports/preview/apply unavailable until later stages.
- Browser: released Browser main/0.5.x, not `8ccc8b8`; native recording actions, suite export unavailable.

Every adapter field remains null and no `bin/suite-adapter.mjs` is created in Wave 1. Before any later Browser 0.6 promotion, integrate the reviewed Browser descriptor commit into the held `8ccc8b8` tree (or rebase the equivalent trees), then rerun the complete test/static/live-evidence matrix and independent review against the composite commit.

#### C3. Descriptor evidence matrix

Store descriptor evidence in a nested `suite_descriptor` object in each `data/plugins.json` plugin record: `contract`, `commit`, `path`, `sha256`, and reviewed evidence date. Updating `suite_descriptor` is atomic and must not alter or imply the runtime release commit, manifest digest, minimum/tested Herdr versions, or compatibility evidence. Site CI checks out each exact plugin descriptor commit into a temporary path, validates schema and digest, cross-checks package/manifest identity, and proves sibling repositories are unnecessary.

**Gate:** all four exact descriptors validate in clean checkouts; mutated digest, commit, path, version, missing required capability, and false availability fixtures fail. Do not add automatic composition, adapter-operation, or E2E-readiness claims.

## Current Holds and Decisions

The following remain intentionally unmerged or unpinned:

- Browser 0.6.0 evidence work until Wave 1 schemas and later receipt/live gates;
- Guard site compatibility restoration until merge, manual smoke, and `v0.1.1` exist;
- Swarm projection/apply under `TODO-4b31f11e` until Wave 2/3;
- Guard export under `TODO-ec8596c2` until Wave 2;
- public coordinator/run lifecycle, automatic Conductor→Swarm composition, and concurrent cross-plugin mutation.

Maintainer decisions required before execution:

1. approve merging exact Guard, Swarm, and Conductor reviewed heads;
2. choose a merge strategy that preserves the reviewed trees, or accept revalidation of changed merge trees;
3. approve Guard's non-destructive manual smoke and `v0.1.1` tag/release;
4. approve a read-only site CI workflow plus a pinned development-only JSON Schema dependency;
5. **Resolved 2026-07-29:** Conductor Stage 1 targets and released `0.2.0`.

## Next Go/No-Go Order

1. **GO only with maintainer approval:** merge reviewed Guard, Swarm, and Conductor heads.
2. **GO after Guard smoke:** tag/release 0.1.1 and repin the site atomically.
3. **DONE 2026-07-29:** Conductor Stage 1 B0→B4 released as `v0.2.0` after exact-tree live evidence, independent review, merge, and green main CI.
4. **GO after schema review:** implement site schemas/corpus, then isolated static descriptors.
5. **NO-GO throughout Wave 1:** Browser 0.6.0 promotion, suite adapters, approval-aware mutators, automatic pipeline claims, or E2E-readiness claims.
