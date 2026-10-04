# 🐝 Explore with Swarm (`structupath.swarm`)

**Explore is the suite's ready first workflow.** Swarm tries one bounded task several ways in parallel. Each agent gets a Swarm-owned git worktree and branch from a recorded base SHA; agents commit locally and the operator reviews and harvests selected work.

Repo: [StructuPath/herdr-swarm](https://github.com/StructuPath/herdr-swarm) · Detailed reference: the repo [README](https://github.com/StructuPath/herdr-swarm#readme)

## Pinned evidence

| Field | Value |
| --- | --- |
| Plugin release | `0.5.0` |
| Minimum Herdr | `0.7.4` |
| Explicitly tested Herdr | `0.7.4`, `0.7.5` |
| Evidence commit | `f750bc7d61f99d857e2276c5493fbe91254c9e7f` |

Version 0.5.0 adds the workflow described under **Pick the winner** below. The pinned [readiness record](https://github.com/StructuPath/herdr-swarm/blob/f750bc7d61f99d857e2276c5493fbe91254c9e7f/docs/readiness.md) documents a 2026-10-04 live end-to-end run of that flow on Herdr 0.8.2:

- fan-out with per-slot tasks, slot variables, and cloned dependencies;
- finish detection, validate, compare, and broadcast;
- a merge at the compared commit;
- a conflict handed to a resolver, reviewed read-only, and landed;
- the review flagging a file slipped into the merge;
- archive with exact cleanup approvals, and prune dry-run.

That run used scripted stand-in agents, not real model agents. It did not cover the status pane, which opens through the plugin action, or Herdr 0.7.4. The broad tested-version record remains 0.7.4/0.7.5.

An earlier bounded 0.8.2 smoke (0.4.0) exercised fan-out, committed work, merge, automatic archive, abort, and prune dry-run. It found and fixed archive-state reconciliation and the newer runtime's `done` agent state.

An isolated Herdr 0.9.3/protocol 22 smoke (0.4.0-era) registered all five actions and
used a disposable, no-remote repository with an inert local shell preset.
Scripted fan-out created one worktree and started one pane; the attended abort
closed that pane, removed the clean worktree, archived the run, and kept its
branch. Local validation passed 259/259. This does not verify a real model
agent, merge/harvest, or GitHub transport on 0.9.3, so the published
tested-version record remains 0.7.4/0.7.5.

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

Open Status and use `1`–`9` to visit each slot. Compare committed and uncommitted counts against the recorded fork SHA. While Status is open, finish detection marks a slot `finished` when its agent writes the `.swarm-done` marker or exits, and shows elapsed time per slot. State is informative, not a completion gate.

Open Harvest. Press `w` for the ranked compare view, `v` to run your `validate.sh` on a slot, or preview each candidate's diff, run its tests, and compare it against the criterion declared before fan-out. Dirty slots offer WIP commit, skip, or discard; review the backup behavior before discarding.

### 5. Treat clean-slot selection as approval

> **Merge warning:** selecting a clean slot in Harvest performs a review-first `--no-ff` merge. If the base branch is checked out, Swarm asks for explicit confirmation. If the base is not checked out anywhere, a plugin-owned detached worktree can advance the base ref after the preview without another confirmation screen. Treat slot selection as the approval action.

Use `q` to leave Status or Harvest without selecting a candidate. Invoke Abort to stop an active run: it closes Swarm-owned panes and removes clean plugin-owned worktrees, while keeping branches and anything questionable.

### Success definition

A first Explore run is successful when one chosen branch is merged without conflict, its tests pass on the base, the resulting diff meets the stated comparison criterion, and skipped work remains recoverable on branches until deliberate pruning.

## Pick the winner

Version 0.5.0 covers the whole path from fan-out to a landed winner. Each step is opt-in or read-only unless stated, and nothing merges without the operator's selection or confirmation. The [pinned README](https://github.com/StructuPath/herdr-swarm/blob/f750bc7d61f99d857e2276c5493fbe91254c9e7f/README.md#the-workflow-050) is the detailed reference.

| Step | What it does |
| --- | --- |
| **Prepare slots** | Fan-out clones the repository's ignored `node_modules` (or a configured `clone-paths` list) into each worktree with copy-on-write. On Linux it's skipped where copy-on-write is unavailable; on macOS `cp -c` falls back to a full copy. Each slot gets `HERDR_SWARM_RUN_ID`, `HERDR_SWARM_SLOT`, and its own port range (10 per slot from 4100). `setup.sh` always receives them, and the agent receives them on Herdr 0.7.5+. |
| **Different tasks per slot** | `<!-- swarm-slot: N -->` lines split `HERDR_SWARM_TASK_FILE` into per-slot sections after a shared preamble. Before anything is created, fan-out warns when slots given *different* tasks name the same tracked file. |
| **Know when done** | Status records a slot `finished` when its agent writes `.swarm-done` or exits, and sends one Herdr notification when all slots are done. |
| **Check** | `v` (or `harvest-step.sh validate <slot>`) runs your plugin-config `validate.sh` against the slot's clean commit and records the result bound to that SHA. It can run automatically on finish if you opt in. The strict candidate handoff uses this result by default. |
| **Compare** | `w` ranks slots by checks on their current commit, then commits, then finished. It never ranks by diff size. It shows files, `+/-`, dirty count, the files each pair both changed, and elapsed time. `d` shows the diff between two slots. |
| **Merge the winner** | `m` merges the chosen slot **at the exact commit compared**, and refuses if it moved. Only if that merge lands are the finished losers skipped and archived. Branches are always kept. |
| **Steer** | `harvest-step.sh broadcast` types one single-line message into every running slot's agent. It only does so where the slot's own agent program leads the pane, never into a shell, an editor, or an agent Herdr reports as blocked. |
| **Resolve conflicts** | For a conflict in Swarm's own detached merge tree, `g` starts a resolver agent beside the slot (Herdr 0.7.5+). `c` reviews its commit **read-only**: it lists every path changed beyond git's own automatic merge and the full diffstat. Only `y` records exactly the reviewed commit and lands it through the compare-and-swap. A merge you resolve by hand concludes the same way. |

Elapsed time is shown; token usage and cost aren't, because Herdr carries no usage data and agents do not report it.

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

See the [pinned GitHub handoff contract](https://github.com/StructuPath/herdr-swarm/blob/f750bc7d61f99d857e2276c5493fbe91254c9e7f/docs/github-handoff.md) for the exact evidence and output schemas. [Console](Console) can display an explicitly saved PR-status observation alongside project and QA evidence.

### Strict candidate handoff

Version 0.5.0 includes `candidate-status <slot>` and
`publish-candidate-pr <slot>`. In the active run, select a clean committed
slot, record typed passing validation checks (the result `validate <slot>`
records is used when no file is named), a separately passing [Browser QA](Browser) result
for the same SHA, and an explicit operator review bound to the run ID, slot,
and SHA. Set `HERDR_SWARM_CANDIDATE_VALIDATION_FILE`,
`HERDR_SWARM_CANDIDATE_BROWSER_QA_FILE`, and
`HERDR_SWARM_CANDIDATE_REVIEW_FILE` to regular private files. The review JSON
has `schema_version: 1`, `kind: "herdr-swarm-operator-review"`, `run_id`,
numeric `slot`, `head_sha`, and `decision: "approved"` or `"rejected"`.
Run `bash scripts/harvest-step.sh candidate-status 1`, optionally save its
`candidate_status` TSV output for [Console](Console), then, after operator
inspection, run `bash scripts/harvest-step.sh publish-candidate-pr 1`.
The publish verb rereads every input and refuses missing, stale, failed,
rejected, invalid, or dirty candidates before a push or PR creation. It never
merges or authorizes Conductor apply.

The disposable live-CLI smoke observed a blocked preview and exit 36 without
a Git push or `gh`, then a ready preview, audited push to a **local bare Git
repository**, and a draft-PR result from a **stubbed GitHub transport**.
It does not establish real GitHub authentication, CI, or remote PR creation.
Caller-supplied evidence and the operator JSON are not attestations; an
existing PR is reused without replacing its body, so reported evidence may
not be attached to that PR. The pinned `docs/github-handoff.md` linked above
defines the contract.

After a remote PR is merged, preview again. Harvest recognizes merge ancestry and squash merges whose tree changes are contained in the base. Prune uses ancestry, so squash-merged branches may remain for deliberate review.

## Safety and trust boundary

Swarm isolates working trees and provides reviewable branches; it does not sandbox agents. Write agents are trusted same-user principals and can access anything their operating-system user can access. Agents are instructed to commit locally and never push, while the operator remains the merge gate.

Harvest uses review-first, `--no-ff` merges and checks base drift. Dirty discards first create backup refs. Abort keeps branches, and prune is dry-run/env-gated. Active runs resolve by physical repository identity; conflicting generations are refused rather than guessed.

Ignored files remain outside Git's safety net. Removal requires the exact one-use `cleanup_approval` JSON returned by the inventory preview, bound to the resource, path, run, generation, and inventory digest. A generic yes is insufficient, and changed inventory invalidates approval. This also applies to ignored files in detached merge worktrees, and to `node_modules` cloned into a slot. Large sets are summarized by top-level directory in the prompt, while the approval still covers every exact file.

**Broadcast** types text into agents, so it refuses multi-line text, control characters, and a leading `-`. It only types into a pane whose foreground program is the slot's own agent. On Herdr 0.7.5+, Swarm reports agent state itself, so an open approval prompt does not read as `blocked`: do not broadcast while an agent may be asking for approval.

**The conflict resolver** never handles a conflict in your own checked-out branch. Its merge tree is kept until Swarm can *prove* the resolver is gone; an uncertain state blocks abort and conclude. A resolution's second parent must be the exact slot commit the merge started with. Hunk-level changes inside conflicted files are not flagged separately, so review the conflicted files' content.

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

For a different task per slot, split the task file with `<!-- swarm-slot: N -->` lines (see **Pick the winner** above). Without `HERDR_SWARM_SLOTS`, the highest section number sets the slot count. Sections that don't fit the run, or a near-miss marker, refuse before anything is created. If a zero-TTY input is missing, the script exits with a named-variable error instead of waiting on an unreadable prompt.

## Safe exit and cleanup

- `q` closes Status or Harvest without selecting work.
- Abort stops the active run and preserves branches; it never deletes branches.
- Prune is a dry run by default and is separately gated for merged branches and backup refs.
- Closing the parent workspace stops Swarm agents silently. Committed work remains harvestable; uncommitted editor state may not.
- Ignored files are not included in WIP commits or discard snapshots. Review the archive inventory and supply its exact one-use cleanup approval before removal.

Use the plugin README's [Safety model](https://github.com/StructuPath/herdr-swarm#safety-model) and [Uninstall / cleanup](https://github.com/StructuPath/herdr-swarm#uninstall--cleanup) sections before destructive cleanup.
