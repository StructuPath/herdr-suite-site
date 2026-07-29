# herdr-suite-site

Canonical, reviewable documentation for the StructuPath Herdr Suite, published at <https://herdr.structupath.ai>.

The product surface is organized by workflow readiness:

- **Explore / Swarm** is the ready first workflow: bounded parallel candidates, reviewable worktrees, and operator-selected harvest.
- **Deliver / Conductor** is an attended Stage 1 lifecycle: visible role panes, strict run state, identity-checked harvest, and archival stand-down.
- **Browser** and **Guard** are supporting visibility and advisory text-policy capabilities.

The four plugins can be installed together, but they do not form one automatic runtime pipeline.

## Source and publishing contract

- Author documentation in `docs-src/`.
- Plugin evidence is pinned in `data/plugins.json` from reviewed sibling manifests and READMEs.
- `docs/**/*.html` is committed generated output for the existing legacy GitHub Pages deployment.
- `index.html` is a dependency-free static landing/onboarding surface.
- GitHub Pages settings and `CNAME` are intentionally unchanged.

## Truthful suite boundaries

- Swarm agents commit locally; the operator reviews and selects what merges. A clean-slot selection can perform the merge after preview, so selection is the approval action.
- Guard is advisory/best-effort rendered-text policy for agent TUIs; it is not a sandbox or authorization boundary.
- Conductor creates and harvests its own worktrees and does not delegate either operation to Swarm. The pinned runtime has no Stage 2 task/report or approval contracts, suite adapter, unattended automation, or automatic recovery.
- Write-capable agents and plugins are trusted same-user principals. Worktrees isolate changes for review, not security.
- Compatibility/testing claims are plugin-specific and pinned in `data/plugins.json`; there is no blanket suite-wide tested-version or marketplace claim.
- Conductor exposes five actions: `assemble`, `board`, `status`, `harvest`, and `stand-down`.

## Build and check

```bash
python3 -m pip install -r requirements-docs.txt
python3 scripts/build_docs.py
python3 scripts/build_docs.py --check
python3 scripts/check_docs.py
python3 -m py_compile scripts/build_docs.py scripts/check_docs.py
```

See [`docs/pages-cutover.md`](docs/pages-cutover.md) for the source-of-truth and publishing contract.
