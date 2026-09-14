# Herdr Console

A dependency-free local read-only application, separate from the public suite
website. Node 20+ and Git are required. Run from the suite checkout:

```sh
npm run console -- --demo
# Or select actual repositories and observation files:
npm run console -- --config /absolute/private/console.json
```

Open the exact `http://127.0.0.1:4317` address printed by the server. Use
`--port 4320` if needed. Stop with Ctrl+C. `--check` prints a JSON snapshot and
exits without opening a server. No install/build step or paid service is needed.

`example.json` selects this checkout. Copy and edit it in a private location.
Paths resolve relative to the configuration file. Select 1–20 Git worktree roots:

```json
{
  "schemaVersion": 1,
  "herdrBinary": "/absolute/path/to/herdr",
  "projects": [{
    "id": "app",
    "name": "My application",
    "path": "/absolute/project",
    "swarmManifest": "/private/run-workspace.json",
    "conductorStatus": "/private/conductor-status.json",
    "guardAudit": "/private/audit.jsonl",
    "qaReport": "/private/qa-run/result.json",
    "pullRequestStatus": "/private/pr-status.tsv"
  }]
}
```

All fields except `id`, `name`, `path`, and the top-level version/projects are
optional. Do not commit private configuration, reports, or screenshots. The
Console reads only explicit paths, does not discover runs recursively, and
does not invoke plugin actions. Readiness probes are version commands, not an
installation or authenticated live-workflow check. Source versions come from
the suite's pinned `data/plugins.json`; Conductor requires exactly Herdr 0.7.5.

## Observation contracts

- **Git:** current branch, commit, worktree count, and changed-file count. An
  unborn repository or unavailable path displays an error, not an empty success.
- **Swarm:** existing run manifest, matched to the configured repository root.
  Slot status is recorded metadata, not proof of live agent activity.
- **Conductor:** save JSON from its existing `scripts/stage1-runtime.mjs status`
  in the correct Herdr workspace/repository. The Console matches its physical
  Git repository key and displays the saved lifecycle and worker statuses. It
  never derives authority from a partial journal. Refresh status before acting.
- **Guard:** counts from one configured audit JSONL file. Raw command text,
  messages, and matched lines are omitted. Counts do not prove enforcement.
- **Browser QA:** the new Browser runner's `result.json`, schemaVersion 1 and
  kind `herdr-browser-qa`. A current result must match clean HEAD and report a
  clean, unchanged checkout. Screenshot/diagnostic files stay in the runner's
  private output directory; this server does not serve arbitrary artifacts.
- **GitHub handoff:** save Swarm `scripts/harvest-step.sh pr-status <slot>` output
  to the configured TSV file. The single `ci_status` JSON record supplies the
  PR URL and CI summary. Reported commit must match the configured clean HEAD
  for current status. This can intentionally be stale when reviewing a slot
  from the base worktree. Refresh through Swarm for new GitHub information.

Each observed file shows its modification time. Refresh re-reads observations
with a five-second cache, never polls or mutates the plugins. Missing,
unrecognized, oversized, foreign, or malformed inputs show as unavailable.
Observation files must be regular, non-symlink files of at most 2 MiB; one Guard
file may contain at most 10,000 entries. These are cooperative local summaries,
not authenticated attestations. Copy buttons only copy existing commands.

The server binds only to IPv4 loopback, checks Host/Origin, requires a custom
header for the data endpoint, serves only exact asset routes, and permits only
GET. Do not reverse-proxy or expose it publicly. It trusts the local OS user,
selected executable, configured repositories, and their parent directories.

## Build and verify

```sh
npm run build
npm test
# With the demo server above running and herdr-browser checked out beside this repo:
node ../herdr-browser/bin/qa.mjs run --config console/scenarios/console.json \
  --repo . --output /private/new-console-qa-run --json
```

The output directory must not exist, its parent must exist, and it must be
outside the tested repository. The saved scenario exercises project filtering,
evidence display, and command controls at desktop and mobile sizes. Demo QA
proves that interface against synthetic observations; real-Git and HTTP tests
cover the data adapter and read-only server boundaries separately.
