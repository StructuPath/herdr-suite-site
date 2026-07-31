# 🎩 Deliver with Conductor (`structupath.conductor`)

**Attended Stage 2 delivery.** Conductor `0.3.0` coordinates task-bound builders, validators, and reviewers as visible Herdr agent panes. A human or trusted orchestrating agent explicitly drives every transition. This release is operational for strict task/report contracts and exact-SHA gates on exactly Herdr `0.7.5`; it is not an approval system, suite adapter, unattended pipeline, automatic recovery service, cryptographic attestation system, or same-user security boundary.

Repo: [StructuPath/herdr-conductor](https://github.com/StructuPath/herdr-conductor) · [Release `v0.3.0`](https://github.com/StructuPath/herdr-conductor/releases/tag/v0.3.0) · Detailed reference: the repo [README](https://github.com/StructuPath/herdr-conductor/tree/v0.3.0#readme)

## Pinned evidence

| Field | Value |
| --- | --- |
| Plugin release | `0.3.0` |
| Minimum Herdr | `0.7.5` |
| Explicitly tested Herdr | `0.7.5` |
| Runtime candidate | `0ed952992ef1559808da4d25a2e7166d075b1ce9` |
| Evidence commit | `712863c34d6126c9d95fa3b9bd6caf5220cbfc43` |
| Manifest SHA-256 | `95958ade511f422b65a07f3d4a305581cdb236e1cd616da7d6c57aa0660aa35e` |
| Live evidence digest | `8547d5cd3215bf79cdb973437de867e803baba1a86d80916eb0ca8b5f2d8bcfd` |

The release retains an immutable [Stage 2 source manifest](https://github.com/StructuPath/herdr-conductor/blob/v0.3.0/docs/evidence/stage2-runtime-source-manifest.json) and [installed-Herdr live contract report](https://github.com/StructuPath/herdr-conductor/blob/v0.3.0/docs/evidence/2026-07-28-stage2-live-contracts.md). Historical [B0 identity-capability evidence](https://github.com/StructuPath/herdr-conductor/blob/v0.3.0/docs/evidence/2026-07-28-herdr-0.7.5-identity-capability.md) and the [Stage 1 B4 lifecycle report](https://github.com/StructuPath/herdr-conductor/blob/v0.3.0/docs/evidence/2026-07-28-stage1-b4-live-smoke.md) remain compatibility evidence. These are sanitized, operator-observed local records—not cryptographic remote attestation or authentication against malicious same-UID processes.

## All five actions

| Action ID | Attended behavior |
| --- | --- |
| `structupath.conductor.assemble` | Bind the exact repository/workspace, publish immutable producer tasks and private report outboxes, create run-unique worktrees/refs, then start task-bound panes and agents. |
| `structupath.conductor.board` | Print one passive lifecycle snapshot for the invoking repository/workspace; it does not open, focus, or mutate a pane. |
| `structupath.conductor.status` | Print context-bound task, report, integration, gate, and exact live-identity status. |
| `structupath.conductor.harvest` | Collect terminal reports, reject invalid committed reports durably, perform deterministic zero-or-one-CAS integration, and dispatch reviewer/validator tasks at the exact observed integration SHA. |
| `structupath.conductor.stand-down` | Revalidate each complete live pane/agent tuple before close, archive strict authority, and retain all worktrees, branches, tasks, reports, outboxes, gate sources, recordings, logs, artifacts, and Guard files. |

Conductor owns this lifecycle. It does **not** invoke Swarm or provide an automatic Conductor→Swarm pipeline. Supported composition remains human-selected and sequential.

## Attended quickstart

Create `.herdr-conductor.json` in a clean Git repository:

```json
{
  "version": 2,
  "state_root": { "kind": "default" },
  "worktree_root": ".conductor-worktrees",
  "roles": [
    {
      "name": "builder",
      "contract_role": "builder",
      "kind": "pi",
      "mode": "write",
      "assignment": {
        "title": "Implement the owned change",
        "mission": "Complete only the attended task.",
        "acceptance_criteria": [
          { "id": "behavior", "text": "The requested behavior is verified." }
        ],
        "owned_paths": ["src"],
        "forbidden_paths": ["secrets"],
        "required_commands": [
          { "id": "test", "command": "npm test" }
        ]
      },
      "validator_artifacts": []
    },
    {
      "name": "validator",
      "contract_role": "validator",
      "kind": "pi",
      "mode": "gated",
      "assignment": {
        "title": "Validate the exact integration",
        "mission": "Run the attended exact-SHA gate.",
        "acceptance_criteria": [],
        "owned_paths": [],
        "forbidden_paths": [],
        "required_commands": []
      },
      "validator_artifacts": []
    }
  ]
}
```

Then explicitly drive the lifecycle from that Herdr workspace:

```bash
herdr plugin action invoke assemble --plugin structupath.conductor
herdr plugin action invoke status --plugin structupath.conductor
herdr plugin action invoke board --plugin structupath.conductor
# Complete the published task and pipe canonical report JSON to the returned publisher command.
herdr plugin action invoke harvest --plugin structupath.conductor
# Complete exact-SHA gate tasks, publish their reports, and harvest again.
herdr plugin action invoke harvest --plugin structupath.conductor
herdr plugin action invoke stand-down --plugin structupath.conductor
```

`assemble` returns exact task paths, source roots, outbox slots, and task-bound publisher commands. Reports are closed canonical JSON supplied through bounded stdin. Producer collection and exact-SHA gate collection may require separate attended `harvest` invocations. Harvest and stand-down are mutating attended actions. Failed or uncertain external effects become `needs_attention` and are never silently replayed.

## Trust and completion limits

- State is strict, non-executable private JSON indexed by physical Git common-directory and Herdr workspace identity. Atomic writes, repository locks, generations, canonical digests, and hash-chained journals are cooperative coordination controls—not authentication.
- Tasks and reports are closed, bounded, duplicate-key-rejecting, identity-bound documents. Worker command results, criteria, `delivered`, `approve`, and `pass` values remain unauthenticated assertions—not proof, approval receipts, or authorization.
- Reviewer and validator sources are retained detached worktrees at the exact observed integration SHA. Read-only modes and separate writable outboxes prevent ordinary accidental writes; they do not constrain a malicious same-UID process.
- Missing, malformed, duplicate, foreign, stale, replayed, ambiguous, dirty, or durability-uncertain authority fails closed. Integration performs exactly zero or one target compare-and-swap.
- Herdr `0.7.5` closes by `pane_id`. Conductor re-reads the full workspace, pane, terminal, agent, cwd, run, and generation tuple immediately before close, but a same-user TOCTOU window remains.
- The repository lock does not stop unrelated Git or same-user processes. Worktrees are review boundaries, not sandboxes. Guard observes rendered text and cannot prove prevention.
- Stage 2 does not provide approval receipts, approval consumption, approval-aware apply, automatic recovery, suite adapters, unattended orchestration, automatic cleanup/prune, or Browser promotion. Those remain later-stage work.
- Stand-down closes only identity-proven panes and archives authority. It does not remove worktrees, branches, tasks, outboxes, reports, gate sources, artifacts, recordings, logs, or Guard files; retained resources continue consuming disk.
