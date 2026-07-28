# 🎩 Deliver with Conductor (`structupath.conductor`)

**Advanced assembly pattern.** Conductor runs a role-differentiated team—such as builder, validator, and reviewer—as visible Herdr agent panes. A human or trusted orchestrating agent drives every step; the current runtime is not safe for unattended or persisted-state use.

Repo: [StructuPath/herdr-conductor](https://github.com/StructuPath/herdr-conductor) · Detailed reference: the repo [README](https://github.com/StructuPath/herdr-conductor#readme)

## Pinned evidence

| Field | Value |
| --- | --- |
| Plugin release | `0.1.0` |
| Minimum Herdr | `0.7.5` |
| Explicitly tested Herdr | `0.7.5` |
| Evidence commit | `d4c6527e36991b234861781af34fe16c7ef16f4b` |

## All five actions

| Action ID | Current behavior |
| --- | --- |
| `structupath.conductor.assemble` | Read `.herdr-conductor.json`, create the declared team, and open the board |
| `structupath.conductor.board` | Open the live board with one row per worker |
| `structupath.conductor.status` | Print the board's recorded role/kind/pane/state/cwd data once |
| `structupath.conductor.harvest` | Select the newest global run and merge writing-role branches into an integration worktree, reporting conflicts without forcing |
| `structupath.conductor.stand-down` | Read recorded pane IDs from executable run state and request their closure without live ownership verification |

> **Current safety boundary:** do not invoke `harvest` or `stand-down` on existing, persisted, shared, or ambiguous state. The pinned runtime selects the newest run globally rather than by repository/workspace identity, sources executable state, and does not compare a live pane identity before closing it. Typing a run ID confirms only the selected ID; it does not make that selection repository-safe.

Conductor owns its worktree lifecycle and harvest implementation. It does **not** call Swarm to create worktrees or harvest branches. Swarm is a separate workflow that a human or trusted orchestrator may invoke later with an explicitly selected commit; there is no automatic Conductor→Swarm pipeline.

## Inspection-only quickstart

Use a clean, disposable Git repository and a reviewed `.herdr-conductor.json`. These commands assemble and inspect the team; they do not establish a safe mutation, reconciliation, or teardown path:

```bash
herdr plugin action invoke assemble --plugin structupath.conductor
herdr plugin action invoke status --plugin structupath.conductor
herdr plugin action invoke board --plugin structupath.conductor
```

Stop after inspection in the pinned runtime. Do not use the current transport helpers to dispatch work, and do not invoke the current harvest or stand-down actions. Wait for a release with repository-bound run identity, non-executable durable state, live resource verification, explicit approval consumption, and recovery semantics before treating Deliver as an operational workflow.

## Current trust and completion limits

- Write-capable workers and the orchestrator are trusted same-user principals. Worktrees separate changes for review; they are not sandboxes or same-user security boundaries.
- `read-only` is role metadata and prompt intent in the pinned runtime, not product-enforced filesystem or process isolation.
- Guard is a best-effort rendered-text policy observer. Its audit and interrupt-request records do not prove that a command was prevented.
- Run state is shell-sourced executable text. There is no durable restart/adoption protocol, repository-bound active-run index, atomic approval journal, or trusted attestation.
- Dry-run still writes run state and `.conductor` scaffolding in the base checkout, although it does not create role worktrees or branches; it is not filesystem-immutable.
- The validator worktree and reviewer's base checkout remain at the original base branch; neither is advanced to the reconciled integration result. Their PASS/APPROVE output cannot certify that integration tree.
- Workers exchange `.conductor/task.md` and `.conductor/report.md`. An agent becoming `idle` can mean it asked a question or completed any turn; only a fresh report containing the completion sentinel satisfies the current await helper, and that sentinel is not an identity or correctness proof.
