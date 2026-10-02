# herdr-suite-site

Canonical, reviewable documentation for the StructuPath Herdr Suite, published at <https://herdr.structupath.ai>.

The product surface is organized by workflow readiness:

- **Explore / Swarm** is the ready first workflow: bounded parallel candidates, reviewable worktrees, operator-selected harvest, and optional GitHub draft PR handoff. A separate strict candidate handoff requires passing validation and Browser QA plus an exact-SHA operator review before publication; it is an unreleased development path, not an automatic merge.
- **Deliver / Conductor** is an attended Stage 3 lifecycle: task-bound roles, exact-SHA gates, operator approval receipts, single-local-ref apply, and archival stand-down on exactly Herdr 0.7.5.
- **Browser** provides Chromium launch, external attach, shared sessions, agent-browser recording, and repeatable desktop/mobile QA. **Guard** provides text policy and an optional fail-open harness reporter.

The four plugins can be installed together, but they do not form one automatic runtime pipeline.

## Local Console

With Node.js 20 or newer:

```sh
npm run console -- --demo
# For real projects, copy console/example.json to a private location, then:
npm run console -- --config /absolute/private/console.json --check
npm run console -- --config /absolute/private/console.json
```

The local server binds to `127.0.0.1:4317` by default. Console reads only
explicit project paths and optional saved Swarm, Conductor, Guard, Browser QA,
candidate-status, and PR-status observations. Save Swarm's read-only
`candidate-status <slot>` TSV for the `candidateStatus` observation; point that
project at the slot worktree so Console can compare its clean HEAD with the
saved SHA. Missing, stale, failed, or rejected evidence is displayed, never
treated as permission to push, merge, or apply.

An optional `suiteComponent` on local site, Browser, Guard, Swarm, and
Conductor checkout entries displays local pin and upstream comparisons. These
use local Git refs and may be stale: Console never fetches, pulls, installs,
updates, or runs its copy-only review commands. It has no mutating controls.
It probes the selected Herdr binary and the running server separately;
Conductor's pinned release supports exactly Herdr `0.7.5`, so a running
`0.8.2` server remains incompatible even with a selected `0.7.5` CLI.
The isolated `0.9.3` Conductor synthetic smoke is not a release promotion.
Browser's separate `0.9.3` real-browser integration passed two of three
scenarios; screencast delivered no image and fell back to polling, so
suite-wide streaming compatibility is not established.

The public website serves documentation, not a remote controller; Console
is a local app, not a fifth plugin. See the
[local Console instructions](console/README.md) and
[Console guide](https://herdr.structupath.ai/docs/console/) for the five-checkout
configuration example and observation limits.

## Source and publishing contract

- Author documentation in `docs-src/`.
- Plugin evidence is pinned in `data/plugins.json` from reviewed sibling manifests and READMEs.
- `docs/**/*.html` is committed generated output for the existing legacy GitHub Pages deployment.
- `index.html` is a dependency-free static landing/onboarding surface.
- GitHub Pages settings and `CNAME` are intentionally unchanged.

## Truthful suite boundaries

- Swarm agents commit locally; the operator reviews and selects what merges. A clean-slot selection can perform the merge after preview, so selection is the approval action.
- Guard's pane watcher is advisory/best-effort. Its optional Claude Code hook can deny reported Bash calls before execution but fails open on unavailable or malformed responses; it is not a sandbox or same-user security boundary.
- Conductor creates and harvests its own worktrees. It supports attended preview, unauthenticated operator receipts, and one-local-ref apply. It does not delegate to Swarm or provide a suite adapter, unattended automation, or general automatic recovery.
- Write-capable agents and plugins are trusted same-user principals. Worktrees isolate changes for review, not security.
- Compatibility/testing claims are plugin-specific and pinned in `data/plugins.json`; there is no blanket suite-wide tested-version or marketplace claim.
- Conductor exposes seven actions: `assemble`, `board`, `status`, `harvest`, `preview`, `apply`, and `stand-down`.

## Build and check

```bash
python3 -m pip install -r requirements-docs.txt
python3 scripts/build_docs.py
python3 scripts/build_docs.py --check
python3 scripts/check_docs.py
python3 -m py_compile scripts/build_docs.py scripts/check_docs.py
npm run validate
```

`npm run validate` also checks Console syntax and runs its real-Git adapter and HTTP boundary tests.

For repeatable browser checks, serve this checkout with `python3 -m http.server 4381 --bind 127.0.0.1`, then use the Browser QA runner from its trusted checkout:

```bash
node /trusted/herdr-browser/bin/qa.mjs run \
  --config docs-src/site-qa.json --repo . \
  --output /private/new-site-qa-run --json
```

The saved scenario checks landing-to-Console navigation and all plugin guides at desktop and mobile viewport sizes. Commit changes before collecting evidence intended to identify a clean candidate. Output must be outside the repository in a new directory with an existing parent; review screenshots separately for layout. See the [Browser guide](https://herdr.structupath.ai/docs/browser/) for prerequisites and evidence limits.

See [`docs/pages-cutover.md`](docs/pages-cutover.md) for the source-of-truth and publishing contract.
