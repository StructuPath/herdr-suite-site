# 🐝 Explore with Swarm (`structupath.swarm`)

**Explore is the suite's ready first workflow.** Swarm tries one bounded task several ways in parallel. Each agent gets a Swarm-owned git worktree and branch from a recorded base SHA; agents commit locally and the operator reviews and harvests selected work.

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

## First Explore run

Use a clean Git repository and choose a task small enough to review. The operator—not an agent's displayed state—is the merge gate.

### 1. Install and prove registration

Requirements: Herdr `>=0.7.4`, Git `>=2.38` recommended, Node.js `>=20`, and macOS or Linux.

```bash
herdr plugin install StructuPath/herdr-swarm
herdr plugin list
herdr plugin action list
```

**Ready branch:** `structupath.swarm` is enabled and the five action IDs in the table above are visible.

**Failure branch:** do not fan out if the plugin or actions are missing. Verify the requirements, then inspect:

```bash
herdr plugin log list --plugin structupath.swarm
herdr status server
```

### 2. Open Fan out

Choose **Fan out agents** from Herdr's plugin actions menu. Herdr plugins cannot ship default keybindings; this optional user-owned binding opens the same action:

```toml
# ~/.config/herdr/config.toml
[[keys.command]]
key = "prefix+s"
type = "plugin_action"
command = "structupath.swarm.fanout"
description = "swarm fan-out"
```

### 3. Enter one bounded task and comparison criterion

Start with two or three slots. In the interactive prompt, finish the task with a single `.` on its own line. For example:

```text
Add retry with exponential backoff to the HTTP client.
Keep the public API unchanged.
Add a test for two failures followed by success.
Run the existing test suite.

Comparison criterion: among passing candidates, choose the smallest diff
with the clearest failure-path test.
.
```

Fresh worktrees omit ignored dependencies, `.env` files, and caches. If every agent fails immediately, add a reviewed plugin-config `setup.sh` or tell agents to install required dependencies, then start a new run.

### 4. Inspect every credible candidate

Open Status and use `1`–`9` to visit each slot. Compare committed and uncommitted counts against the recorded fork SHA. A 0.7.5+ slot can remain labeled `working` after it finishes until Harvest previews it; state is informative, not a completion gate.

Open Harvest, preview each candidate's diff, run its tests, and compare it against the criterion declared before fan-out. Dirty slots offer WIP commit, skip, or discard; review the backup behavior before discarding.

### 5. Treat clean-slot selection as approval

> **Merge warning:** selecting a clean slot in Harvest performs a review-first `--no-ff` merge. If the base branch is checked out, Swarm asks for explicit confirmation. If the base is not checked out anywhere, a plugin-owned detached worktree can advance the base ref after the preview without another confirmation screen. Treat slot selection as the approval action.

Use `q` to leave Status or Harvest without selecting a candidate. Invoke Abort to stop an active run: it closes Swarm-owned panes and removes clean plugin-owned worktrees, while keeping branches and anything questionable.

### Success definition

A first Explore run is successful when one chosen branch is merged without conflict, its tests pass on the base, the resulting diff meets the stated comparison criterion, and skipped work remains recoverable on branches until deliberate pruning.

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

Per-slot overrides remain interactive-only. If a zero-TTY input is missing, the script exits with a named-variable error instead of waiting on an unreadable prompt.

## Safe exit and cleanup

- `q` closes Status or Harvest without selecting work.
- Abort stops the active run and preserves branches; it never deletes branches.
- Prune is a dry run by default and is separately gated for merged branches and backup refs.
- Closing the parent workspace stops Swarm agents silently. Committed work remains harvestable; uncommitted editor state may not.
- Ignored files are not included in WIP commits or discard snapshots. Inspect the archive-time inventory before acknowledging worktree removal.

Use the plugin README's [Safety model](https://github.com/StructuPath/herdr-swarm#safety-model) and [Uninstall / cleanup](https://github.com/StructuPath/herdr-swarm#uninstall--cleanup) sections before destructive cleanup.
