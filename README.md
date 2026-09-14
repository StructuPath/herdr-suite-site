# herdr-suite-site

Canonical, reviewable documentation for the StructuPath Herdr Suite, published at <https://herdr.structupath.ai>.

The product surface is organized by workflow readiness:

- **Explore / Swarm** is the ready first workflow: bounded parallel candidates, reviewable worktrees, operator-selected harvest, and explicit GitHub draft PR handoff with validation summaries.
- **Deliver / Conductor** is an attended Stage 3 lifecycle: task-bound roles, exact-SHA gates, operator approval receipts, single-local-ref apply, and archival stand-down on exactly Herdr 0.7.5.
- **Browser** provides Chromium launch, external attach, shared sessions, agent-browser recording, and repeatable desktop/mobile QA. **Guard** provides text policy and an optional fail-open harness reporter.

The four plugins can be installed together, but they do not form one automatic runtime pipeline.

## Local Console

With Node.js 20 or newer, run `npm run console -- --demo` for a labeled fixture dashboard. For real projects, use `npm run console -- --config /absolute/private/console.json`; add `--check` to print a snapshot and exit. The server binds to `127.0.0.1:4317` by default.

Console reads explicit project paths and optional saved Swarm, Conductor, Guard, and Browser QA observations. It shows tool health, Git state, evidence freshness, and copyable next commands. It has no mutating controls. The public website serves documentation, not a remote controller; Console is a local app, not a fifth plugin. See the [Console guide](https://herdr.structupath.ai/docs/console/) for configuration and evidence limits.

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
