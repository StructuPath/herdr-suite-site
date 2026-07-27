# 🐝 Swarm (`structupath.swarm`)

Swarm tries one task several ways in parallel. Each agent gets a Swarm-owned git worktree and branch from a recorded base SHA; agents commit locally and the operator reviews and harvests selected work.

Repo: [StructuPath/herdr-swarm](https://github.com/StructuPath/herdr-swarm) · Detailed reference: the repo [README](https://github.com/StructuPath/herdr-swarm#readme)

## Pinned evidence

| Field | Value |
| --- | --- |
| Plugin release | `0.1.0` |
| Minimum Herdr | `0.7.4` |
| Explicitly tested Herdr | `0.7.4`, `0.7.5` |
| Evidence commit | `0dc0a2b0a77e590d854fafd5eae0e76dbcc00017` |

## Actions

| Action ID | Behavior |
| --- | --- |
| `structupath.swarm.fanout` | Prompt for task/slots and create one worktree, branch, and agent per slot |
| `structupath.swarm.status` | Show each slot's state, branch, and committed/uncommitted counts |
| `structupath.swarm.harvest` | Review and merge selected slot branches back to the recorded base |
| `structupath.swarm.abort` | Stop agents and remove clean plugin-owned worktrees while keeping branches |
| `structupath.swarm.prune` | Dry-run, then explicitly prune eligible merged branches or backup refs |

Everyday flow: **Fan out → Status → Harvest → Prune**. Abort is available at any point.

## Safety and trust boundary

Swarm isolates working trees and provides reviewable branches; it does not sandbox agents. Write agents are trusted same-user principals and can access anything their operating-system user can access. Agents are instructed to commit locally and never push, while the operator remains the merge gate.

Harvest uses review-first, `--no-ff` merges and checks base drift. Dirty discards first create backup refs. Abort keeps branches, and prune is dry-run/env-gated. Ignored files remain outside Git's safety net; inspect the archive inventory before removing a worktree.

## Scripted fan-out

Interactive fan-out uses the action. A zero-TTY run must invoke the pane script directly because action-spawned panes do not inherit caller environment in the pinned runtime:

```bash
HERDR_SWARM_SLOTS=3 \
HERDR_SWARM_PRESETS=claude,claude,codex \
HERDR_SWARM_TASK_FILE=/path/brief.md \
HERDR_SWARM_DETRITUS=rename \
HERDR_WORKSPACE_ID=<repo-workspace-id> \
  bash "$(herdr plugin list --json | jq -r '.plugins[] | select(.id=="structupath.swarm").root')/scripts/fanout-pane.sh"
```

Fresh worktrees omit ignored dependencies, `.env` files, and caches. Use a reviewed plugin-config `setup.sh` or instruct workers to install required dependencies.
