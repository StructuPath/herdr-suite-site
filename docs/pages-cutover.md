# GitHub Pages docs cutover

The reviewable canonical documentation lives in `docs-src/` in this repository. The files under `docs/` remain committed generated HTML so the existing legacy GitHub Pages deployment continues to serve the same paths without a Pages settings change.

## Authoring and publishing

1. Edit `docs-src/*.md`, `data/plugins.json`, or the generator.
2. Install the pinned renderer: `python3 -m pip install -r requirements-docs.txt`.
3. Run `python3 scripts/build_docs.py`.
4. Run `python3 scripts/check_docs.py`.
5. Review and commit both the source and regenerated `docs/**/*.html`.

`python3 scripts/build_docs.py --check` verifies that committed HTML exactly matches the canonical Markdown. The checker also validates local links, plugin action/version evidence, forbidden suite-wide claims, and generated output.

## Evidence updates

`data/plugins.json` pins the sibling repository commit, plugin version, minimum Herdr version, explicitly evidenced tested versions, action IDs, and SHA-256 digest of `herdr-plugin.toml`. Update it only after reviewing the manifest and README at the new commit. A repository topic or install command alone is not evidence of marketplace listing or broad compatibility.

The former scheduled external-wiki sync and self-commit workflow was removed. Do not reintroduce a workflow that fetches mutable external docs and pushes generated changes. This cutover intentionally does **not** change the repository's GitHub Pages settings, custom domain, or `CNAME`.
