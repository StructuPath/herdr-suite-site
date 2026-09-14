# 🐝 Explore with Swarm (`structupath.swarm`)

**Explore is the suite's ready first workflow.** Swarm tries one bounded task several ways in parallel. Each agent gets a Swarm-owned git worktree and branch from a recorded base SHA; agents commit locally and the operator reviews and harvests selected work.

Repo: [StructuPath/herdr-swarm](https://github.com/StructuPath/herdr-swarm) · Detailed reference: the repo [README](https://github.com/StructuPath/herdr-swarm#readme)

## Pinned evidence

| Field | Value |
| --- | --- |
| Plugin release | `0.4.0` |
| Minimum Herdr | `0.7.4` |
| Explicitly tested Herdr | `0.7.4`, `0.7.5` |
| Evidence commit | `09dd1f22c95ca9c9e4cdb0e3510f886360d5f0fb` |

The pinned source also records a [bounded Herdr 0.8.2 live smoke](https://github.com/StructuPath/herdr-swarm/blob/09dd1f22c95ca9c9e4cdb0e3510f886360d5f0fb/docs/readiness.md): fan-out, committed work, merge, automatic archive, abort, and prune dry-run. It found and fixed archive-state reconciliation and the newer runtime's `done` agent state. Version 0.4.0 retains these fixes and adds the explicit GitHub draft-PR handoff below; broad Herdr compatibility evidence remains 0.7.4/0.7.5.

## Actions

| Action ID | Behavior |
| --- | --- |
| `structupath.swarm.fanout` | Prompt for task/slots and create one worktree, branch, and agent per slot |
| `structupath.swarm.status` | Show each slot's state, branch, and committed/uncommitted counts |
| `structupath.swarm.harvest` | Review and merge selected slot branches, or explicitly publish a branch for PR review |
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

Setup logs preserve command output verbatim. Keep credentials out of setup output and review logs before sharing them.

### 4. Inspect every credible candidate

Open Status and use `1`–`9` to visit each slot. Compare committed and uncommitted counts against the recorded fork SHA. A 0.7.5+ slot can remain labeled `working` after it finishes until Harvest previews it; state is informative, not a completion gate.

Open Harvest, preview each candidate's diff, run its tests, and compare it against the criterion declared before fan-out. Dirty slots offer WIP commit, skip, or discard; review the backup behavior before discarding.

### 5. Treat clean-slot selection as approval

> **Merge warning:** selecting a clean slot in Harvest performs a review-first `--no-ff` merge. If the base branch is checked out, Swarm asks for explicit confirmation. If the base is not checked out anywhere, a plugin-owned detached worktree can advance the base ref after the preview without another confirmation screen. Treat slot selection as the approval action.

Use `q` to leave Status or Harvest without selecting a candidate. Invoke Abort to stop an active run: it closes Swarm-owned panes and removes clean plugin-owned worktrees, while keeping branches and anything questionable.

### Success definition

A first Explore run is successful when one chosen branch is merged without conflict, its tests pass on the base, the resulting diff meets the stated comparison criterion, and skipped work remains recoverable on branches until deliberate pruning.

## Publish for PR review

In Harvest, press `p`, then select a slot to publish its branch. The script equivalent is `scripts/harvest-step.sh publish <slot>` from the installed plugin root. Publication uses an ordinary push to `origin`, or the explicit `HERDR_SWARM_PUBLISH_REMOTE` override; it never force-pushes and does not create a GitHub PR itself.

### Explicit GitHub draft handoff

For a GitHub PR, press `g`, then select a slot in Harvest, or invoke `publish-pr` below. This selection or command authorizes both the audited-commit push and draft PR creation, with no second confirmation. It creates a draft or reuses the exact matching open PR; an existing ready-for-review PR stays ready. The five plugin actions remain unchanged.

From the trusted installed Swarm checkout in the same configured run context:

```bash
# Optional evidence must describe this slot's exact committed candidate.
HERDR_SWARM_VALIDATION_FILE=/absolute/private/qa/result.json \
  bash scripts/harvest-step.sh publish-pr 1

# Read GitHub PR/CI state without pushing or editing GitHub.
bash scripts/harvest-step.sh pr-status 1
```

Authenticate `gh` first. The named remote (default `origin`) must have exactly one fetch and push URL identifying the same GitHub.com repository. Fork destinations and GitHub Enterprise are outside this first release. The recorded run base branch and selected slot branch determine PR identity. Existing ownership, fork ancestry, non-empty-work, and ordinary-push guards remain active. Only committed work travels.

`HERDR_SWARM_VALIDATION_FILE` optionally accepts typed check statuses or a [Browser QA](Browser) `result.json` for the exact published SHA. Browser evidence must explicitly record a clean tree, no changes during the run, and all three scenario policies enabled: `failOnConsoleError`, `failOnPageError`, and `failOnFailedRequest`. Without a file, validation is `not_run`, never passed. Supplied evidence is unauthenticated; Swarm does not execute its checks. Failed or pending checks can accompany a draft. The PR includes bounded check names/statuses and identifiers, not task text, raw logs, URLs, screenshots, or local paths.

An existing exact repository/head/base open PR is reused without changing its title, body, or state. `validation_attached: false` on reuse means its body may describe an older SHA; review and update that evidence manually. Closed/merged matches and ambiguous discovery refuse handoff.

Imported Browser QA summaries must agree with per-run outcomes and counts. Unresolved requests or incomplete telemetry cannot produce a passing handoff check.

A failed push creates no PR. A GitHub failure after a successful push leaves the published branch and local receipt intact. Inspect the error and retry the same command; a lost creation response triggers exact-PR rediscovery. A mismatched GitHub head refuses success and requires inspection, never a force-push correction.

Press `c`, then a slot, for the pane's CI view. `pr-status` emits a `ci_status` tab-separated JSON record with `passed`, `failed`, `pending`, `not_run`, `unknown`, or `no_pr` status. Compare `head_sha` and `local_head_sha`: a passing remote check is not current candidate evidence when `matches_local_head` is false. Passing checks do not establish branch-protection completeness or authorize a merge. The command uses GitHub reads and the local run lock; it does not fetch, push, merge, or edit a PR.

See the [pinned GitHub handoff contract](https://github.com/StructuPath/herdr-swarm/blob/09dd1f22c95ca9c9e4cdb0e3510f886360d5f0fb/docs/github-handoff.md) for the exact evidence and output schemas. [Console](Console) can display an explicitly saved PR-status observation alongside project and QA evidence.

After a remote PR is merged, preview again. Harvest recognizes merge ancestry and squash merges whose tree changes are contained in the base. Prune uses ancestry, so squash-merged branches may remain for deliberate review.

## Safety and trust boundary

Swarm isolates working trees and provides reviewable branches; it does not sandbox agents. Write agents are trusted same-user principals and can access anything their operating-system user can access. Agents are instructed to commit locally and never push, while the operator remains the merge gate.

Harvest uses review-first, `--no-ff` merges and checks base drift. Dirty discards first create backup refs. Abort keeps branches, and prune is dry-run/env-gated. Active runs resolve by physical repository identity; conflicting generations are refused rather than guessed.

Ignored files remain outside Git's safety net. Removal requires the exact one-use `cleanup_approval` JSON returned by the inventory preview, bound to the resource, path, run, generation, and inventory digest. A generic yes is insufficient, and changed inventory invalidates approval. This also applies to ignored files in detached merge worktrees.

## Scripted fan-out

Interactive fan-out uses the action. A zero-TTY run must invoke the pane script directly because action-spawned panes do not inherit caller environment in the pinned runtime:

```bash
HERDR_SWARM_SLOTS=3 \
HERDR_SWARM_PRESETS=claude,claude,codex \
HERDR_SWARM_TASK_FILE=/path/brief.md \
HERDR_SWARM_DETRITUS=rename \
HERDR_WORKSPACE_ID='replace-with-repo-workspace-id' \
  bash "$(herdr plugin list --json | jq -r '.plugins[] | select(.id=="structupath.swarm").root')/scripts/fanout-pane.sh"
```

Per-slot overrides remain interactive-only. If a zero-TTY input is missing, the script exits with a named-variable error instead of waiting on an unreadable prompt.

## Safe exit and cleanup

- `q` closes Status or Harvest without selecting work.
- Abort stops the active run and preserves branches; it never deletes branches.
- Prune is a dry run by default and is separately gated for merged branches and backup refs.
- Closing the parent workspace stops Swarm agents silently. Committed work remains harvestable; uncommitted editor state may not.
- Ignored files are not included in WIP commits or discard snapshots. Review the archive inventory and supply its exact one-use cleanup approval before removal.

Use the plugin README's [Safety model](https://github.com/StructuPath/herdr-swarm#safety-model) and [Uninstall / cleanup](https://github.com/StructuPath/herdr-swarm#uninstall--cleanup) sections before destructive cleanup.
