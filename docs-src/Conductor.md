# 🎩 Deliver with Conductor (`structupath.conductor`)

**Attended Stage 3 delivery.** Conductor `0.4.0` coordinates task-bound builders, validators, and reviewers as visible Herdr agent panes, then supports an explicitly approved fast-forward of one local ref. An operator drives every transition and records each approval receipt. It requires exactly Herdr `0.7.5`, protocol `17`, API schema `1`; it is not an authenticated approval system, suite adapter, unattended pipeline, general automatic recovery service, cryptographic attestation system, or same-user security boundary.

Repo: [StructuPath/herdr-conductor](https://github.com/StructuPath/herdr-conductor) · Detailed reference: the repo [README](https://github.com/StructuPath/herdr-conductor#readme)

## Pinned evidence

| Field | Value |
| --- | --- |
| Plugin release | `0.4.0` |
| Minimum Herdr | `0.7.5` |
| Explicitly tested Herdr | `0.7.5` |
| Evidence commit | `ad170ee8e00be8979a7e1ae20bc6375e5e6f94d3` |
| Manifest SHA-256 | `b8898d549216485c2bd599a101808030ce534b9c32625b6e6bdc51da04644672` |

The retained [Stage 2 source manifest](https://github.com/StructuPath/herdr-conductor/blob/712863c34d6126c9d95fa3b9bd6caf5220cbfc43/docs/evidence/stage2-runtime-source-manifest.json) and [installed-Herdr live contract report](https://github.com/StructuPath/herdr-conductor/blob/712863c34d6126c9d95fa3b9bd6caf5220cbfc43/docs/evidence/2026-07-28-stage2-live-contracts.md) remain historical compatibility evidence. Older and newer Herdr binaries do not satisfy Conductor's exact 0.7.5 requirement; passing local tests is not evidence that another Herdr version is supported.

A separate [developer smoke on 2026-09-14](https://github.com/StructuPath/herdr-conductor/blob/ad170ee8e00be8979a7e1ae20bc6375e5e6f94d3/docs/evidence/2026-09-14-developer-installed-action-smoke.md) exercised all seven installed actions on a running Herdr 0.7.5 server, including Stage 3 preview, approval refusal, attended single-ref apply, replay, and completed stand-down. It found and fixed the omitted stand-down reason after apply. The smoke used synthetic local worker sessions and operator-produced deterministic reports, not a real model agent. This bounded observation is not independent-human review, formal release attestation, live crash-recovery proof, or broader production certification.

## All seven actions

| Action ID | Attended behavior |
| --- | --- |
| `structupath.conductor.assemble` | Bind the exact repository/workspace, publish immutable producer tasks and private report outboxes, create run-unique worktrees/refs, then start task-bound panes and agents. |
| `structupath.conductor.board` | Print one passive lifecycle snapshot for the invoking repository/workspace; it does not open, focus, or mutate a pane. |
| `structupath.conductor.status` | Print context-bound task, report, integration, gate, and exact live-identity status. |
| `structupath.conductor.harvest` | Collect terminal reports, reject invalid committed reports durably, perform deterministic zero-or-one-CAS integration, and dispatch reviewer/validator tasks at the exact observed integration SHA. |
| `structupath.conductor.preview` | Journal the proposed local-ref fast-forward, exact integration and target observations, and gate assertions; return the exact approval command. |
| `structupath.conductor.apply` | Consume a matching operator approval receipt once, then perform or resolve the attempt's single local-ref compare-and-swap. |
| `structupath.conductor.stand-down` | Revalidate each complete live pane/agent tuple before close, archive strict authority, and retain all worktrees, branches, tasks, reports, outboxes, gate sources, recordings, logs, artifacts, and Guard files. |

Conductor owns this lifecycle. It does **not** invoke Swarm or provide an automatic Conductor→Swarm pipeline. Supported composition remains human-selected and sequential.

## Attended quickstart

Use Herdr exactly 0.7.5, Node.js 20 or current LTS, Python 3.11+, and Git with 40-hex SHA-1 object IDs. Create `.herdr-conductor.json` in a clean Git repository. This first-run example explicitly disables apply:

```json
{
  "version": 3,
  "apply": null,
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

Commit `.herdr-conductor.json` before assembly so the repository is clean, then explicitly drive the lifecycle from that Herdr workspace:

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

### Optional attended apply

To enable apply for a new run, set `apply` to `{ "target_ref": "refs/heads/release" }` before assembly. The named local branch must already exist, differ from the integration branch, be checked out in no worktree, and remain exactly at the run's integration base. The proposed change must be a nonempty, rename-free fast-forward. Configuration v2 remains supported with apply disabled; do not edit a run-bound configuration mid-run.

After producer and gate collection, use this sequence instead of standing down immediately:

1. Invoke `herdr plugin action invoke preview --plugin structupath.conductor`.
2. Review the exact target, diff, gate assertions, and preview entry digest.
3. Follow the exact `npm run apply:approve` command returned by preview and provide the operator's canonical approve or reject receipt through stdin. Do not manufacture a receipt from a generic example or treat a worker's `approve` report as operator consent.
4. Invoke `herdr plugin action invoke apply --plugin structupath.conductor` only for the reviewed, approved attempt.
5. Inspect status, then invoke stand-down when finished.

The receipt is consumed durably before any Git effect and cannot be reused. A moved target records an unapplied outcome with zero target changes. Only the attended apply action can resolve an uncertain apply publication from an exact target-SHA observation; other ambiguous operations remain refused. Rejected or voided attempts permit a fresh preview, up to eight attempts. Apply never pushes, tags, publishes, deploys, or updates multiple refs.

## Trust and completion limits

- State is strict, non-executable private JSON indexed by physical Git common-directory and Herdr workspace identity. Atomic writes, repository locks, generations, canonical digests, and hash-chained journals are cooperative coordination controls—not authentication.
- Tasks and reports are closed, bounded, duplicate-key-rejecting, identity-bound documents. Worker command results, criteria, `delivered`, `approve`, and `pass` values remain unauthenticated assertions—not proof, approval receipts, or authorization.
- Reviewer and validator sources are retained detached worktrees at the exact observed integration SHA. Read-only modes and separate writable outboxes prevent ordinary accidental writes; they do not constrain a malicious same-UID process.
- Missing, malformed, duplicate, foreign, stale, replayed, ambiguous, dirty, or durability-uncertain authority fails closed. Integration performs exactly zero or one target compare-and-swap.
- Herdr `0.7.5` closes by `pane_id`. Conductor re-reads the full workspace, pane, terminal, agent, cwd, run, and generation tuple immediately before close, but a same-user TOCTOU window remains.
- The repository lock does not stop unrelated Git or same-user processes. Worktrees are review boundaries, not sandboxes. Guard observes rendered text and cannot prove prevention.
- Stage 3 receipts are unauthenticated same-user operator records, not signatures or authorization proof. Apply changes one configured local ref; it does not provide general automatic recovery, suite adapters, unattended orchestration, automatic cleanup/prune, or Browser promotion.
- Stand-down closes only identity-proven panes and archives authority. It does not remove worktrees, branches, tasks, outboxes, reports, gate sources, artifacts, recordings, logs, or Guard files; retained resources continue consuming disk.
