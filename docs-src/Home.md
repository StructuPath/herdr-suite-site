# Herdr Suite: supervised AgentOps

Herdr-native tools for human-supervised agent work, built and maintained by [StructuPath](https://github.com/StructuPath). **Explore** is the ready first workflow. **Deliver** is an advanced assembly pattern. Browser and Guard provide supporting visibility and text-policy capabilities.

This repository is the canonical suite documentation source; each plugin README remains the detailed runtime reference.

## Start with Explore

[Explore with Swarm](Swarm) when you have one bounded coding task and want to compare several implementations. Swarm records a base SHA, gives each agent a separate worktree and branch, reports concrete change counts, and lets the operator preview and harvest a selected candidate.

The operator defines the comparison criterion, reviews diffs and tests, and chooses what lands. Agents commit locally and never push.

## Deliver is advanced

[Deliver with Conductor](Conductor) is a human/trusted-orchestrator assembly pattern: visible role workers, `.conductor/task.md` and `.conductor/report.md` files, a run board, and reconciliation in a Conductor integration worktree.

The pinned runtime does not provide product-enforced approval gates, durable autonomous recovery, cryptographic report attestation, or Swarm-backed worktree creation/harvest.

## Supporting trust capabilities

- [Browser](Browser) exposes a workspace browser session that an agent or operator can drive and record. The session is a trusted same-user boundary, and recordings may contain sensitive content.
- [Guard](Guard) observes rendered terminal text and offers advisory/best-effort policy. It is not a sandbox or authorization boundary for agent TUIs.

## Pinned compatibility evidence

| Plugin | ID | Pinned release | Minimum Herdr | Explicitly tested | Purpose |
| --- | --- | --- | --- | --- | --- |
| [Browser](Browser) | `structupath.browser` | `0.5.0` | `0.7.0` | `0.7.4` | Supporting browser visibility and recording |
| [Guard](Guard) | `structupath.guard` | `0.1.0` | `0.7.5` | `0.7.5` | Supporting advisory text policy, audit, alert, and best-effort interrupt |
| [Swarm](Swarm) | `structupath.swarm` | `0.1.0` | `0.7.4` | `0.7.4`, `0.7.5` | Ready Explore workflow: parallel candidates and review-first harvest |
| [Conductor](Conductor) | `structupath.conductor` | `0.1.0` | `0.7.5` | `0.7.5` | Advanced Deliver pattern: role workers, reports, and reconciliation |

Versions are plugin-specific evidence pinned in [`data/plugins.json`](https://github.com/StructuPath/herdr-suite-site/blob/main/data/plugins.json), not a claim that every plugin was tested on one suite-wide Herdr version.

## Composition and supervision boundaries

These plugins can be installed together, but the current runtime is not a single automatic pipeline.

| Component | System provides | Operator remains responsible for |
| --- | --- | --- |
| Explore / Swarm | Worktree fan-out, change counts, previews, guarded harvest | Task bounds, candidate review, tests, slot selection, cleanup |
| Deliver / Conductor | Role panes, task/report files, run board, integration harvest | Dispatch, report validation, approval, conflict handling, recovery |
| Browser | Shared visual browser surface and recording | Session privacy, action review, sensitive recording handling |
| Guard | Best-effort text matching, audit, alerts, interrupt attempts | Authoritative hooks, sandboxing, access control, log protection |

Herdr plugins and write-capable agents run as the same operating-system user. Treat them as **trusted same-user principals**. Worktrees reduce accidental file collisions and make changes reviewable; they are not sandboxes and do not prevent a worker from accessing other same-user files or processes.

## Install by capability

```bash
# Ready first workflow
herdr plugin install StructuPath/herdr-swarm

# Advanced assembly pattern
herdr plugin install StructuPath/herdr-conductor

# Supporting visibility and policy
herdr plugin install StructuPath/herdr-browser
herdr plugin install StructuPath/herdr-guard
```

These commands are not a blanket claim about marketplace visibility. Inspect source and manifests before installing local plugins.

## Health checks

```bash
herdr plugin list
herdr plugin action list
herdr plugin log list
herdr status server
```

`plugin list` confirms that a manifest parsed and is enabled; `plugin action list` confirms action registration. See each plugin page for its exact actions, prerequisites, and limits.
