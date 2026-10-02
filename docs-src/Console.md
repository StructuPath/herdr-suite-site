# Local Console

Console 0.1.0 brings explicitly configured projects, tool health, saved run observations, and browser QA evidence into one read-only local dashboard. It is a local app in the suite website repository, not a fifth Herdr plugin. The public website at `herdr.structupath.ai` serves documentation; it cannot inspect or control your projects.

## Start locally

Install Node.js 20 or newer and Git, then clone the suite site repository. Console has no package dependencies.

```bash
git clone https://github.com/StructuPath/herdr-suite-site.git
cd herdr-suite-site
npm run console -- --demo
```

Open the loopback address printed by the command, normally `http://127.0.0.1:4317`. Demo mode uses clearly labeled fixtures, not observations of your machine. Stop the server with Ctrl+C.

For your projects, save a private configuration file outside the published site:

```json
{
  "schemaVersion": 1,
  "projects": [
    {
      "id": "app",
      "name": "My app",
      "path": "/absolute/path/to/app"
    }
  ]
}
```

```bash
npm run console -- --config /absolute/private/console.json
npm run console -- --config /absolute/private/console.json --port 4318
npm run console -- --config /absolute/private/console.json --check
```

`--check` prints the snapshot as JSON and exits. The server binds only to `127.0.0.1`. Configure 1–20 Git worktree roots; relative paths resolve from the configuration file's directory. Console reads explicit paths; it does not recursively discover repositories or look for credentials. The optional top-level `herdrBinary` selects an explicit Herdr executable.

## Track local suite checkouts

Suite update readiness is opt-in. Add the optional `suiteComponent` field only
to projects that represent the five local suite checkouts. Each enum value may
appear at most once:

```json
{
  "schemaVersion": 1,
  "projects": [
    {
      "id": "suite-site",
      "name": "Suite site",
      "path": "/absolute/path/to/herdr-suite-site",
      "suiteComponent": "site"
    },
    {
      "id": "browser",
      "name": "Browser",
      "path": "/absolute/path/to/herdr-browser",
      "suiteComponent": "browser"
    },
    {
      "id": "guard",
      "name": "Guard",
      "path": "/absolute/path/to/herdr-guard",
      "suiteComponent": "guard"
    },
    {
      "id": "swarm",
      "name": "Swarm",
      "path": "/absolute/path/to/herdr-swarm",
      "suiteComponent": "swarm"
    },
    {
      "id": "conductor",
      "name": "Conductor",
      "path": "/absolute/path/to/herdr-conductor",
      "suiteComponent": "conductor"
    }
  ]
}
```

The allowed values are `site`, `browser`, `guard`, `swarm`, and `conductor`.
Once any is configured, the **Suite checkouts** area also shows unconfigured
component slots so gaps remain visible. Existing projects without
`suiteComponent` continue to work as before.

Plugin pins come from the suite site's reviewed `data/plugins.json`. The site
checkout has no pin. Console uses only local Git ancestry to describe a plugin
checkout as at, ahead of, behind, or diverged from its pin. If the pinned commit
is absent locally, it says so rather than guessing. An unavailable repository
has an unavailable relation.

Upstream ahead/behind counts compare HEAD with that checkout's configured
upstream ref. `no_upstream` means no upstream is configured; `unknown` means
the local comparison could not be made. Console does not contact a remote, so
none of these values prove what is currently on GitHub. Local refs can be stale.

To review a component, open a shell in the explicitly named checkout shown on
its card. Its controls only copy these static commands:

```bash
git status -sb
git fetch --prune
```

Console never runs the commands, fetches, pulls, installs, updates, or mutates a
checkout. After running a fetch yourself, refresh Console to compare the updated
local refs. Inspect the status and changes before deciding whether to update.
This is an update-readiness aid, not an updater or remote controller.

Conductor supports exactly Herdr 0.7.5. Herdr 0.8.2 is incompatible with
Conductor; the dashboard compares whichever Herdr binary you select.

## Add saved observations

Each project can optionally name these files. Omit any source you do not use; example paths are placeholders, not files Console creates.

| Project field | Expected source | What the dashboard can show |
| --- | --- | --- |
| `swarmManifest` | Explicit Swarm run manifest JSON | Saved run and slot metadata, not authoritative lifecycle or live agent activity |
| `conductorStatus` | Saved JSON from Conductor's existing status command | Observed lifecycle, workers, legal next operations, and file modification time |
| `guardAudit` | Explicit Guard audit JSONL | Event counts from the supplied audit file |
| `qaReport` | Browser QA `result.json` | Test summary, recorded Git identity, freshness, and artifact counts |
| `pullRequestStatus` | Saved Swarm `pr-status` TSV output | Validated GitHub PR link, CI summary, and head freshness |
| `candidateStatus` | Saved Swarm `candidate-status` TSV output | Missing/stale candidate evidence, recorded review decision, and comparison to configured clean HEAD |

For Conductor, run its status command yourself in the correct Herdr workspace and repository, using the trusted plugin checkout and a private output path:

```bash
node /trusted/herdr-conductor/scripts/stage1-runtime.mjs status > /absolute/private/conductor-status.json
```

Point `conductorStatus` at that saved file. Console checks its repository key against the project's current Git common directory and rejects a status observation for another repository. It does not reconstruct lifecycle from journals.

For GitHub PR observations, save Swarm's existing tab-separated output in the correct configured run context:

```bash
bash /trusted/herdr-swarm/scripts/harvest-step.sh pr-status 1 > /absolute/private/pr-status.tsv
```

Set `pullRequestStatus` to that file. It expects the `ci_status` tab-separated JSON record, not raw JSON. The recorded head must match the configured clean repository to be labeled current; a base worktree can legitimately differ from a slot's PR head. Refresh through Swarm to observe new CI results. A saved passing status cannot authorize a merge.

For the explicit candidate handoff in the **unreleased local Swarm
checkout** (not the pinned 0.4.0 commit), save a read-only preview in the
selected slot's run context:

```bash
bash /trusted/herdr-swarm/scripts/harvest-step.sh candidate-status 1 > /absolute/private/candidate-status.tsv
```

Point `candidateStatus` at the TSV. It records a reported validation result,
Browser QA result, and operator review decision for the selected run, slot,
and commit. Configure the candidate's **slot worktree** as a project if you
want the dashboard to compare that saved SHA to its clean HEAD; a base
worktree may legitimately differ. Missing or stale files are visible, but
even a fresh “ready” preview is caller-supplied and not authorization to
publish, merge, or apply. Swarm revalidates before the separate attended
`publish-candidate-pr` action. Console never invokes it.

Refreshing the dashboard rereads configured files with a five-second cache; an old file remains a saved observation even after refresh. File modification times are shown. Observation files must be regular, non-symlink files of at most 2 MiB, with at most 10,000 entries in a Guard audit file. Missing, foreign, malformed, or oversized observations show as unavailable, not as successful checks.

## Read the evidence before acting

The project overview reports Git branch, commit, dirty state, and worktree count. Tool health distinguishes the selected Herdr binary from the running server reached by that binary's `status server` command; compatibility advice uses the running version, not the binary version. A stopped or unreachable server has unknown compatibility. Pinned plugin records and a matching server version do not prove installed actions or live integration. The pinned Conductor commit requires exactly Herdr 0.7.5; an unpinned candidate is not counted as released compatibility.

QA freshness compares the report's Git commit with the current repository and checks dirty state and changes observed during the test. A matching commit does not prove that a web server served a build from that commit. Review the [Browser QA workflow](Browser), assertions, and private artifacts before accepting a candidate.

Next commands are suggestions you can copy and review. Console does not start agents, run QA, merge, push, create pull requests, approve Conductor operations, or edit state. Use [Swarm](Swarm) for the explicit PR handoff and [Conductor](Conductor) for attended lifecycle operations. Approval stays with the operator.

Keep the configuration, saved observations, and QA artifacts private. Project paths and reports can contain sensitive information; the local dashboard is not a sharing or remote administration service. It displays artifact counts but does not serve arbitrary screenshots or diagnostics. Do not reverse-proxy or expose it publicly.
