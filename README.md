# herdr-suite-site

Canonical, reviewable documentation for the StructuPath Herdr Suite, published at <https://herdr.structupath.ai>.

- Author documentation in `docs-src/`.
- Plugin evidence is pinned in `data/plugins.json` from reviewed sibling manifests and READMEs.
- `docs/**/*.html` is committed generated output for the existing legacy GitHub Pages deployment.
- GitHub Pages settings and `CNAME` are intentionally unchanged.

## Truthful suite boundaries

- Guard is advisory/best-effort for agent TUIs; it is not an authorization boundary.
- Conductor currently creates and harvests its own worktrees and does not delegate either operation to Swarm.
- Write-capable agents and plugins are trusted same-user principals. Worktrees isolate changes for review, not security.
- Compatibility/testing claims are plugin-specific and pinned in `data/plugins.json`; there is no blanket suite-wide tested-version or marketplace claim.
- Conductor exposes five actions: `assemble`, `board`, `status`, `harvest`, and `stand-down`.

## Build and check

```bash
python3 -m pip install -r requirements-docs.txt
python3 scripts/build_docs.py
python3 scripts/check_docs.py
```

Use `python3 scripts/build_docs.py --check` to verify committed HTML without rewriting it. See [`docs/pages-cutover.md`](docs/pages-cutover.md) for the source-of-truth and publishing contract.
