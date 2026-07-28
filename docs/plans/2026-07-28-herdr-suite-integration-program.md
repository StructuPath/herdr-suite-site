# Herdr Suite Integration Program

**Status:** approved Wave 0 plan  
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

## Current Safety Priorities

These issues block mutating integration work:

1. **Swarm abort can delete ignored-only work.** Abort checks ordinary porcelain status but lacks Harvest's ignored-file inventory guard.
2. **Guard 0.1.0 transport is incompatible with observed Herdr 0.7.5 socket behavior.** The preserved repair must land and be live-smoked first.
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

No plugin imports site code at runtime. Released schema copies are validated locally by each plugin's tests and pinned by digest in the site.

### ADR-2 — Plugins expose one-shot adapters

Each plugin exposes a zero-dependency command with strict JSON stdin/stdout:

```text
node bin/suite-adapter.mjs negotiate
node bin/suite-adapter.mjs inspect
node bin/suite-adapter.mjs preview   # mutators only
node bin/suite-adapter.mjs apply     # mutators only; approval required
```

Rules:

- exactly one JSON object on stdin and stdout;
- human diagnostics only on stderr;
- no sibling checkout discovery or private sibling-state parsing;
- absent adapter means suite contract unsupported, not plugin failure;
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

### ADR-3 — Three small versioned contracts

The first public contract family contains:

1. `herdr-suite-capabilities/v1` — static descriptor and live negotiation result.
2. `herdr-suite-run/v1` — coordinator-owned run snapshot and transition history.
3. `herdr-suite-evidence/v1` — immutable producer receipt, artifact references, limitations, and scoped approval receipts.

Required common identity:

- `contract`, `schema_version`, `run_id`, `plugin_id`, `plugin_version`;
- `repo_id`, `workspace_id`, `base_ref`, `base_sha` where Git applies;
- stable evidence/operation IDs and coordinator sequence;
- explicit outcome: `observed`, `passed`, `failed`, `inconclusive`, or `unavailable`;
- relative artifact URI, SHA-256, media type, and byte count;
- structured limitations.

Only a named test/check can report `passed`. Browser recordings and Guard observations normally report `observed`. SHA-256 proves content integrity after capture, not identity, provenance, or correctness.

### ADR-4 — The coordinator is the sole suite-run writer

The human helper, trusted orchestrator, or E2E harness that starts a run is the sole writer of the portable run bundle:

```text
run.json
transitions.ndjson
approvals/
evidence/
artifacts/browser/
artifacts/guard/
artifacts/swarm/
artifacts/conductor/
```

Plugins retain their private operational state and return normalized receipts. The coordinator validates and copies artifacts, rejects symlinks/path traversal, and re-hashes after copy. Plugins never write another plugin's state or artifact directory.

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

Unknown required capability IDs or contract majors fail closed. Optional missing capabilities become `skipped` or `unavailable`, never silently successful.

### ADR-6 — Lifecycle and approval are explicit

Run lifecycle:

```text
declared -> negotiating -> running -> awaiting_review
awaiting_review -> approved | rejected | cancelled
approved -> applying
applying -> succeeded | needs_attention | failed
needs_attention -> awaiting_review | cancelled
```

Approval binds:

- actor kind (`human` or `trusted-orchestrator`);
- operation;
- preview evidence digest;
- expected base SHA and target ref;
- exact candidate or branch-tip set;
- one-use nonce.

Before mutation, the owning adapter re-computes the preview subject. Any changed base, branch tip, report digest, config digest, or integration SHA supersedes the approval and performs zero mutation.

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

A neutral repository-mutation lease keyed by physical Git common-directory identity prevents concurrent Swarm and Conductor mutation without creating a runtime dependency.

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

**Wave 2:** add strict versioned run evidence with run/event IDs, monotonic sequence, producer version, policy digest, limitation states, and bounded immutable export. Every string leaf uses the same sanitize/redact/truncate pipeline. Legacy JSONL remains unversioned diagnostics.

### Swarm

**Track 0 must land before adapters:**

- shared ignored-file inventory for Abort and Harvest;
- repository-scoped identity, locks, active-run discovery, and backup protection;
- fail-closed prune when bookkeeping is corrupt or unknown;
- idempotent full-harvest run finalization/archive and exclude cleanup.

**Wave 1/2:** add semantic manifest versioning, a read-only adapter, explicit candidate submission/readiness bound to `head_sha`, normalized comparison facts, evidence references, and append-only events.

**Wave 3:** add approval-aware apply with expected revision/base/head, idempotency keys, one JSON result envelope, and stable failure codes. Swarm never ranks or selects a winner.

### Conductor

**Stage 0:** land CI, correct README/site overclaims, archive unrelated Flotion scaffolding, and stop presenting legacy plans as current runtime contracts. Do not run current stand-down against ambiguous legacy state.

**Stage 1:** replace newest-global/PID state with strict JSON state keyed by workspace and Git common-directory; atomic writes; run-unique branches/agent names; fixed fork SHA; mutation locks; write-ahead resource journal; fail-closed pane/worktree identity.

**Stage 2:** add strict task/report schemas and atomic report outbox. Review runs against the exact integration SHA with source read-only and a separate writable outbox. Validate runs at the exact integration SHA and fails on tracked or non-allowlisted source changes.

**Stage 3:** add deterministic preview, validated verdicts, explicit approval receipts, approval-aware reconcile/apply, crash recovery, identity-checked stand-down, archived state, and dry-run-first prune.

Conductor remains an advanced assembly pattern until a live E2E proves these stages.

### Suite Site

Add:

- `contracts/capabilities-v1.schema.json`
- `contracts/run-v1.schema.json`
- `contracts/evidence-v1.schema.json`
- `contracts/examples/`
- `scripts/validate_suite_contract.py`
- `scripts/suite_e2e.py`
- descriptor digests and E2E evidence pins in `data/plugins.json`

`check_docs.py` continues rejecting unsupported automatic, unattended, secure, enforced, prevented, or attested-pipeline claims.

## Cross-Plugin E2E

After Waves 1–3, the neutral harness runs with explicit repository roots in a temporary HOME/state/Git repository and deterministic fake Herdr/agent-browser executables.

Scenario:

1. Negotiate all four exact adapters and record limitations.
2. Start Browser recording; later import it as `observed` evidence.
3. Start Guard observer, inject one visible dangerous line and one unseen popup-equivalent event; require an interrupt-attempt observation plus `inconclusive` coverage.
4. Create two Swarm candidates from the same base: one passing and one failing. Retain evidence for both.
5. Record a trusted selection approval for the passing candidate; apply it with expected-base/journal guards.
6. Assemble Conductor against the selected SHA; produce writer, validator, and reviewer reports bound to exact input/output SHAs.
7. Preview Conductor reconciliation and grant scoped approval.
8. Inject target/base drift after approval. First apply must return stale approval and perform zero mutation.
9. Re-preview, re-approve, and apply successfully.
10. Import Browser and Guard bounded artifacts, validate every digest, run final tests, and verify cleanup inventory.

Required assertions:

- all receipts share one run ID and validate against pinned schemas;
- Guard absence/unseen behavior is never converted to `passed`;
- Browser evidence remains observational;
- failed candidate evidence remains visible;
- stale approval and replay perform zero mutation;
- no plugin reads/writes another plugin's private state;
- final Git ref equals the approved apply result;
- real developer state and preservation artifacts remain untouched.

A separate opt-in live Herdr matrix is required before changing public readiness claims. Stubbed E2E proves contract behavior, not live compatibility.

## Execution Waves and Gates

### Wave 0 — preserve, repair, and freeze truthful boundaries

- Commit/preserve Browser formatting and Guard transport work separately.
- Land minimal CI/static validation tracks.
- Fix Swarm's current destructive/lifecycle blockers.
- Correct Conductor claims and remove/archival-label unrelated or stale material.
- Commit this ADR/program plan in the site.

**Gate:** preservation hashes still match; all current tests pass; no staged/unrelated files; Guard hotfix live-smoked; site still says no automatic pipeline.

### Wave 1 — schemas and negotiation only

- Add site schemas/examples/validator.
- Add capability descriptors and `negotiate` adapters in all four plugins.
- Do not change plugin mutation behavior.

**Gate:** positive/negative schema corpus, major mismatch, missing optional/required plugin, descriptor digest pins, and isolated installation tests with siblings absent.

### Wave 2 — observational evidence

- Browser run-scoped recording receipt.
- Guard bounded immutable evidence export with limitations.
- Swarm candidate projection/preview/readiness/evidence receipts.
- Conductor report completion and reconciliation preview receipts.

**Gate:** traversal/symlink rejection, copy/re-hash validation, corrupt-state handling, no private cross-read, and no evidence outcome inflated to approval or pass.

### Wave 3 — approval-aware mutation and stubbed E2E

- Add Swarm/Conductor suite apply paths with scoped one-use approvals.
- Add neutral repo mutation lease.
- Run stale-approval, drift, conflict, failure, replay, and cleanup scenarios.

**Gate:** stale apply performs zero mutation; replay is refused; failures remain recoverable; final fixture tests pass; all four receipts correlate.

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

## Wave 0 Acceptance

Wave 0 is complete only when:

1. Browser and Guard preservation hashes are rechecked after every write.
2. Browser formatting and Guard transport changes are committed independently and remain recoverable from remote branches.
3. Swarm's ignored-file Abort, repo-scoped mutation identity, full-run finalization, and fail-closed backup protection have regression tests.
4. Conductor's public docs no longer claim Swarm-backed lifecycle, Guard enforcement, verified pane ownership, durable recovery, or enforced read-only behavior.
5. All plugin tests, shell/static checks, site generation, and site claim checks pass.
6. No integration-runtime claim is added to the site.
