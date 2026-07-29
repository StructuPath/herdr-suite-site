# 🎩 Deliver with Conductor (`structupath.conductor`)

**Attended Stage 1 delivery.** Conductor `0.2.0` runs a role-differentiated team—such as builder, validator, and reviewer—as visible Herdr agent panes. A human or trusted orchestrating agent explicitly drives every action. This release is operational for its strict five-action lifecycle on exactly Herdr `0.7.5`; it is not an approval system, suite adapter, unattended pipeline, automatic recovery service, or same-user security boundary.

Repo: [StructuPath/herdr-conductor](https://github.com/StructuPath/herdr-conductor) · [Release `v0.2.0`](https://github.com/StructuPath/herdr-conductor/releases/tag/v0.2.0) · Detailed reference: the repo [README](https://github.com/StructuPath/herdr-conductor#readme)

## Pinned evidence

| Field | Value |
| --- | --- |
| Plugin release | `0.2.0` |
| Minimum Herdr | `0.7.5` |
| Explicitly tested Herdr | `0.7.5` |
| Evidence commit | `c982b61d6d55fa2e6ea9771b2e981fd6abe53ef8` |
| Manifest SHA-256 | `ad8719baa0d08b23b85dfb41811256c244ea96fefe24ea5a072477b0ad0d7fc3` |

The release retains its [B0 identity-capability evidence](https://github.com/StructuPath/herdr-conductor/blob/v0.2.0/docs/evidence/2026-07-28-herdr-0.7.5-identity-capability.md) and [B4 live lifecycle report](https://github.com/StructuPath/herdr-conductor/blob/v0.2.0/docs/evidence/2026-07-28-stage1-b4-live-smoke.md). The live report is sanitized, operator-observed local evidence—not cryptographic remote attestation or authentication against malicious same-UID processes.

## All five actions

| Action ID | Attended behavior |
| --- | --- |
| `structupath.conductor.assemble` | Resolve the exact repository/workspace, record a fixed fork, create run-unique writer worktrees/refs, start named agent panes, and journal exact observed identities. |
| `structupath.conductor.board` | Print one JSON snapshot for the invoking repository/workspace; it does not open or focus a pane. |
| `structupath.conductor.status` | Print the same context-bound run as a table after re-reading live pane and named-agent identity. |
| `structupath.conductor.harvest` | Under the repository mutation lock, validate exact source/target identities, compute from immutable SHAs, and compare-and-swap the assemble-bound target ref. |
| `structupath.conductor.stand-down` | Revalidate the complete live pane/agent tuple immediately before close, archive strict state, and retain worktrees, branches, reports, recordings, logs, artifacts, and Guard files. |

Conductor owns this lifecycle. It does **not** invoke Swarm or provide an automatic Conductor→Swarm pipeline. The supported composition remains human-selected and sequential.

## Attended quickstart

Create `.herdr-conductor.json` in a clean Git repository:

```json
{
  "version": 1,
  "roles": [
    { "name": "builder", "kind": "pi", "mode": "write" },
    { "name": "reviewer", "kind": "codex", "mode": "read-only" }
  ]
}
```

Then explicitly drive the lifecycle from that Herdr workspace:

```bash
herdr plugin action invoke assemble --plugin structupath.conductor
herdr plugin action invoke status --plugin structupath.conductor
herdr plugin action invoke board --plugin structupath.conductor
# Interact with and inspect the visible role panes and writer branches.
herdr plugin action invoke harvest --plugin structupath.conductor
herdr plugin action invoke stand-down --plugin structupath.conductor
```

Harvest and stand-down are mutating attended actions. Inspect status, exact branches, and retained evidence before invoking them. Failed or timed-out external effects become `needs_attention` and are not silently replayed.

## Trust and completion limits

- State is strict, non-executable private JSON indexed by physical Git common-directory and Herdr workspace identity. Atomic writes, repository locks, generations, and hash-chained journals are cooperative coordination controls—not authentication.
- Missing, malformed, duplicate, foreign, stale, or ambiguous identity fails closed. Negative fixtures cover cross-repository/workspace selection, recycled panes, moved worktrees, changed refs/heads, corrupt journals, and concurrent reconciliation.
- Herdr `0.7.5` accepts only `pane_id` for close. Conductor re-reads workspace, pane, terminal, agent session/name, canonical `cwd` and `foreground_cwd`, run ID, and generation immediately before close, but a same-user TOCTOU window remains.
- The Conductor repository lock does not stop unrelated Git or same-user processes. Harvest uses immutable source SHAs, target-ref compare-and-swap, and final identity/index/worktree checks, but these are still attended coordination semantics.
- Role modes and launch arguments are cooperative configuration. Worktrees are review boundaries, not sandboxes. Guard observes rendered text and cannot prove filesystem prevention.
- Stage 1 does not provide strict task/report schemas, writable report outboxes, approval receipts, automatic apply, suite adapters, unattended orchestration, or automatic recovery. Those remain later-stage work.
- Stand-down archives Conductor state and closes only identity-proven panes. It does not remove worktrees, branches, reports, artifacts, recordings, logs, or Guard files.
