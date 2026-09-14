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

## Add saved observations

Each project can optionally name these files. Omit any source you do not use; example paths are placeholders, not files Console creates.

| Project field | Expected source | What the dashboard can show |
| --- | --- | --- |
| `swarmManifest` | Explicit Swarm run manifest JSON | Saved run and slot metadata, not authoritative lifecycle or live agent activity |
| `conductorStatus` | Saved JSON from Conductor's existing status command | Observed lifecycle, workers, legal next operations, and file modification time |
| `guardAudit` | Explicit Guard audit JSONL | Event counts from the supplied audit file |
| `qaReport` | Browser QA `result.json` | Test summary, recorded Git identity, freshness, and artifact counts |
| `pullRequestStatus` | Saved Swarm `pr-status` TSV output | Validated GitHub PR link, CI summary, and head freshness |

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

Refreshing the dashboard rereads configured files with a five-second cache; an old file remains a saved observation even after refresh. File modification times are shown. Observation files must be regular, non-symlink files of at most 2 MiB, with at most 10,000 entries in a Guard audit file. Missing, foreign, malformed, or oversized observations show as unavailable, not as successful checks.

## Read the evidence before acting

The project overview reports Git branch, commit, dirty state, and worktree count. Tool health covers the selected Herdr binary, Node, Git, and agent-browser. Compatibility advice comes from the site's pinned plugin records: it is not proof that every plugin works on the selected runtime. In particular, Conductor's supported runtime remains exactly Herdr 0.7.5.

QA freshness compares the report's Git commit with the current repository and checks dirty state and changes observed during the test. A matching commit does not prove that a web server served a build from that commit. Review the [Browser QA workflow](Browser), assertions, and private artifacts before accepting a candidate.

Next commands are suggestions you can copy and review. Console does not start agents, run QA, merge, push, create pull requests, approve Conductor operations, or edit state. Use [Swarm](Swarm) for the explicit PR handoff and [Conductor](Conductor) for attended lifecycle operations. Approval stays with the operator.

Keep the configuration, saved observations, and QA artifacts private. Project paths and reports can contain sensitive information; the local dashboard is not a sharing or remote administration service. It displays artifact counts but does not serve arbitrary screenshots or diagnostics. Do not reverse-proxy or expose it publicly.
