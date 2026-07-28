#!/usr/bin/env python3
"""Generate committed /docs HTML from this repository's canonical docs-src Markdown.

Usage:
    python3 scripts/build_docs.py
    python3 scripts/build_docs.py --check

The check mode fails when committed HTML differs from a clean regeneration.
"""

import html
import pathlib
import sys

import markdown

SITE = pathlib.Path(__file__).resolve().parent.parent
DOCS_SRC = SITE / "docs-src"

BASE_URL = "https://herdr.structupath.ai"
SOCIAL_IMAGE_URL = f"{BASE_URL}/media/herdr-suite-social.jpg"
SOCIAL_IMAGE_ALT = (
    "Herdr Swarm terminal footage showing worktree candidates ready for review"
)

# (source file stem, slug, nav title, site URL, useful page summary)
PAGES = [
    (
        "Home",
        "index",
        "Overview",
        "/docs/",
        "Explore bounded coding tasks with reviewable worktree candidates, then use the Herdr Suite's supporting tools for supervised agent work.",
    ),
    (
        "Swarm",
        "swarm",
        "Explore · Swarm",
        "/docs/swarm/",
        "Run one bounded coding task in separate worktrees, compare candidate diffs and tests, and harvest the reviewed result with Swarm.",
    ),
    (
        "Conductor",
        "conductor",
        "Deliver · Conductor",
        "/docs/conductor/",
        "Coordinate visible role workers, inspect report files, and reconcile reviewed branches with Conductor's advanced supervised assembly pattern.",
    ),
    (
        "Browser",
        "browser",
        "Browser",
        "/docs/browser/",
        "Open, drive, and record a Herdr workspace browser session while keeping its trusted same-user privacy boundary explicit.",
    ),
    (
        "Guard",
        "guard",
        "Guard",
        "/docs/guard/",
        "Audit rendered terminal text with advisory policy, alerts, and best-effort interrupts while relying on native controls for enforcement.",
    ),
]

# docs-src internal links -> published site URLs
LINK_MAP = {stem: url for stem, _, _, url, _ in PAGES}

TEMPLATE = """<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{tab_title} — Herdr Suite docs</title>
<meta name="description" content="{desc}">
<link rel="canonical" href="{canonical_url}">
<meta property="og:title" content="{social_title}">
<meta property="og:description" content="{desc}">
<meta property="og:url" content="{canonical_url}">
<meta property="og:type" content="article">
<meta property="og:image" content="{social_image_url}">
<meta property="og:image:alt" content="{social_image_alt}">
<meta property="og:image:width" content="1200">
<meta property="og:image:height" content="630">
<meta name="twitter:card" content="summary_large_image">
<meta name="twitter:title" content="{social_title}">
<meta name="twitter:description" content="{desc}">
<meta name="twitter:image" content="{social_image_url}">
<meta name="twitter:image:alt" content="{social_image_alt}">
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link href="https://fonts.googleapis.com/css2?family=Archivo:wght@400;500;600;700;800&family=IBM+Plex+Mono:wght@400;500;600&display=swap" rel="stylesheet">
<link rel="stylesheet" href="/docs/docs.css">
</head>
<body>

<a class="skip-link" href="#main-content">Skip to content</a>
<nav class="nav" aria-label="Main">
  <div class="nav-inner">
    <a class="wordmark" href="/"><span class="mark">H</span>herdr&nbsp;suite</a>
    <div class="nav-links">
      <a href="/#explore">Explore</a>
      <a href="/#deliver">Deliver · advanced</a>
      <a href="/#trust">Trust</a>
    </div>
    <div class="nav-spacer"></div>
    <a class="nav-docs" href="/docs/" aria-current="page">Docs</a>
    <a class="btn" href="/#first-run">Start Explore</a>
  </div>
</nav>

<div class="layout">
  <main class="prose" id="main-content" tabindex="-1">
<div class="crumb">{crumb}</div>
{content}
{pager}
  </main>

  <aside class="sidebar" aria-label="Docs navigation">
    <h4>Docs</h4>
    <ul><li><a href="/docs/"{a_index}>Overview</a></li></ul>
    <h4>Workflows</h4>
    <ul>
      <li><a href="/docs/swarm/"{a_swarm}>Explore · Swarm</a></li>
      <li><a href="/docs/conductor/"{a_conductor}>Deliver · Conductor <small>advanced</small></a></li>
    </ul>
    <h4>Trust capabilities</h4>
    <ul>
      <li><a href="/docs/browser/"{a_browser}>Browser</a></li>
      <li><a href="/docs/guard/"{a_guard}>Guard</a></li>
    </ul>
    <h4>Links</h4>
    <ul>
      <li><a class="ext" href="https://github.com/StructuPath/herdr-suite-site/tree/main/docs-src">Docs source</a></li>
      <li><a class="ext" href="https://github.com/StructuPath">GitHub</a></li>
      <li><a href="/llms.txt">llms.txt</a></li>
    </ul>
  </aside>
</div>

<footer class="foot-slim">
  <div class="inner">
    <span>MIT © StructuPath · Not affiliated with the Herdr project. Canonical source:
    <a href="https://github.com/StructuPath/herdr-suite-site/tree/main/docs-src">docs-src</a>.</span>
    <span><a href="/">herdr.structupath.ai</a></span>
  </div>
</footer>

</body>
</html>
"""


def convert(md_text: str) -> str:
    html = markdown.markdown(md_text, extensions=["tables", "fenced_code"])
    # docs-src internal links -> site URLs
    for stem, url in LINK_MAP.items():
        html = html.replace(f'href="{stem}"', f'href="{url}"')
    # horizontal-scroll wrapper for tables
    html = html.replace("<table>", '<div class="table-scroll"><table>')
    html = html.replace("</table>", "</table></div>")
    return html


def pager_html(i: int) -> str:
    prev = PAGES[i - 1] if i > 0 else None
    nxt = PAGES[i + 1] if i + 1 < len(PAGES) else None
    left = (
        f'<a href="{prev[3]}"><span class="lbl">Previous</span>{prev[2]}</a>'
        if prev
        else "<span></span>"
    )
    right = (
        f'<a href="{nxt[3]}" style="text-align:right"><span class="lbl">Next</span>{nxt[2]}</a>'
        if nxt
        else "<span></span>"
    )
    return f'    <nav class="pager" aria-label="Docs pages">{left}{right}</nav>'


def rendered_pages() -> list[tuple[pathlib.Path, str]]:
    """Return output paths and deterministic rendered HTML for every docs page."""
    missing = [stem for stem, *_ in PAGES if not (DOCS_SRC / f"{stem}.md").exists()]
    if missing:
        raise FileNotFoundError(f"docs source pages missing: {missing} in {DOCS_SRC}")

    pages = []
    for i, (stem, slug, title, url, summary) in enumerate(PAGES):
        md_text = (DOCS_SRC / f"{stem}.md").read_text(encoding="utf-8")
        actives = {
            f"a_{s}": (' class="active"' if s == slug else "")
            for _, s, _, _, _ in PAGES
        }
        tab_title = "Overview" if slug == "index" else f"{title} guide"
        social_title = f"{tab_title} — Herdr Suite docs"
        page_html = TEMPLATE.format(
            tab_title=html.escape(tab_title),
            social_title=html.escape(social_title, quote=True),
            desc=html.escape(summary, quote=True),
            canonical_url=html.escape(f"{BASE_URL}{url}", quote=True),
            social_image_url=html.escape(SOCIAL_IMAGE_URL, quote=True),
            social_image_alt=html.escape(SOCIAL_IMAGE_ALT, quote=True),
            crumb=("Docs" if slug == "index" else "Docs / Plugins"),
            content=convert(md_text),
            pager=pager_html(i),
            **actives,
        )
        out = (
            SITE / "docs" / ("index.html" if slug == "index" else f"{slug}/index.html")
        )
        pages.append((out, page_html))
    return pages


def main() -> int:
    if sys.argv[1:] not in ([], ["--check"]):
        print(__doc__)
        return 2

    check = sys.argv[1:] == ["--check"]
    stale = []
    try:
        pages = rendered_pages()
    except FileNotFoundError as error:
        print(f"ERROR: {error}")
        return 1

    for out, page_html in pages:
        relative = out.relative_to(SITE)
        if check:
            if not out.exists() or out.read_text(encoding="utf-8") != page_html:
                stale.append(str(relative))
            continue
        out.parent.mkdir(parents=True, exist_ok=True)
        out.write_text(page_html, encoding="utf-8")
        print(f"wrote {relative}")

    if stale:
        print(f"ERROR: generated docs are stale: {', '.join(stale)}")
        return 1
    if check:
        print(f"OK: {len(pages)} generated docs pages are current")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
