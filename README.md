# herdr-suite-site

Canonical, reviewable documentation for the StructuPath Herdr Suite, published at <https://herdr.structupath.ai>.

The product surface is organized by workflow readiness:

- **Explore / Swarm** is the ready first workflow: bounded parallel candidates, reviewable worktrees, and operator-selected harvest.
- **Deliver / Conductor** is an attended Stage 3 lifecycle: task-bound roles, exact-SHA gates, operator approval receipts, single-local-ref apply, and archival stand-down on exactly Herdr 0.7.5.
- **Browser** provides Chromium launch, external attach, shared sessions, and agent-browser recording. **Guard** provides text policy and an optional fail-open harness reporter.

The four plugins can be installed together, but they do not form one automatic runtime pipeline.

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
```

See [`docs/pages-cutover.md`](docs/pages-cutover.md) for the source-of-truth and publishing contract.
