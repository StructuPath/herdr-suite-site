#!/usr/bin/env python3
"""Generate /docs pages from the herdr-browser wiki (the canonical docs source).

Usage:  python3 scripts/build_docs.py <path-to-cloned-wiki>
Local:  uv run --with markdown scripts/build_docs.py ../herdr-browser.wiki
CI:     pip install markdown && python3 scripts/build_docs.py wiki

Wiki page -> site page mapping is PAGES below. _Sidebar.md and _Footer.md are ignored.
"""
import re
import sys
import pathlib

import markdown

SITE = pathlib.Path(__file__).resolve().parent.parent

# (wiki file stem, slug, nav title, site url)
PAGES = [
    ("Home",      "index",     "Overview",  "/docs/"),
    ("Browser",   "browser",   "Browser",   "/docs/browser/"),
    ("Guard",     "guard",     "Guard",     "/docs/guard/"),
    ("Swarm",     "swarm",     "Swarm",     "/docs/swarm/"),
    ("Conductor", "conductor", "Conductor", "/docs/conductor/"),
]

# wiki-internal links -> site urls
LINK_MAP = {stem: url for stem, _, _, url in PAGES}

TEMPLATE = """<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{tab_title} — Herdr Suite docs</title>
<meta name="description" content="{desc}">
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link href="https://fonts.googleapis.com/css2?family=Archivo:wght@400;500;600;700;800&family=IBM+Plex+Mono:wght@400;500;600&display=swap" rel="stylesheet">
<link rel="stylesheet" href="/docs/docs.css">
</head>
<body>

<nav class="nav" aria-label="Main">
  <div class="nav-inner">
    <a class="wordmark" href="/"><span class="mark">H</span>herdr&nbsp;suite</a>
    <div class="nav-links">
      <a href="/#plugins">Plugins</a>
      <a href="/#install">Install</a>
      <a href="/docs/" aria-current="page">Docs</a>
      <a href="/llms.txt">llms.txt</a>
    </div>
    <div class="nav-spacer"></div>
    <a class="nav-gh" href="https://github.com/StructuPath" aria-label="StructuPath on GitHub">
      <svg width="19" height="19" viewBox="0 0 16 16" fill="currentColor" aria-hidden="true"><path d="M8 0C3.58 0 0 3.58 0 8c0 3.54 2.29 6.53 5.47 7.59.4.07.55-.17.55-.38 0-.19-.01-.82-.01-1.49-2.01.37-2.53-.49-2.69-.94-.09-.23-.48-.94-.82-1.13-.28-.15-.68-.52-.01-.53.63-.01 1.08.58 1.23.82.72 1.21 1.87.87 2.33.66.07-.52.28-.87.51-1.07-1.78-.2-3.64-.89-3.64-3.95 0-.87.31-1.59.82-2.15-.08-.2-.36-1.02.08-2.12 0 0 .67-.21 2.2.82.64-.18 1.32-.27 2-.27s1.36.09 2 .27c1.53-1.04 2.2-.82 2.2-.82.44 1.1.16 1.92.08 2.12.51.56.82 1.27.82 2.15 0 3.07-1.87 3.75-3.65 3.95.29.25.54.73.54 1.48 0 1.07-.01 1.93-.01 2.2 0 .21.15.46.55.38A8.01 8.01 0 0 0 16 8c0-4.42-3.58-8-8-8Z"/></svg>
    </a>
    <a class="btn" href="/#install">Install</a>
  </div>
</nav>

<div class="layout">
  <aside class="sidebar" aria-label="Docs navigation">
    <h4>Docs</h4>
    <ul><li><a href="/docs/"{a_index}>Overview</a></li></ul>
    <h4>Plugins</h4>
    <ul>
      <li><a href="/docs/browser/"{a_browser}>🌐 Browser</a></li>
      <li><a href="/docs/guard/"{a_guard}>🛡️ Guard</a></li>
      <li><a href="/docs/swarm/"{a_swarm}>🐝 Swarm</a></li>
      <li><a href="/docs/conductor/"{a_conductor}>🎩 Conductor</a></li>
    </ul>
    <h4>Links</h4>
    <ul>
      <li><a class="ext" href="https://github.com/StructuPath/herdr-browser/wiki">GitHub wiki</a></li>
      <li><a class="ext" href="https://github.com/StructuPath">GitHub</a></li>
      <li><a href="/llms.txt">llms.txt</a></li>
    </ul>
  </aside>

  <main class="prose">
<div class="crumb">{crumb}</div>
{content}
{pager}
  </main>
</div>

<footer class="foot-slim">
  <div class="inner">
    <span>MIT © StructuPath · Not affiliated with the Herdr project. Docs are synced from the
    <a href="https://github.com/StructuPath/herdr-browser/wiki">GitHub wiki</a>.</span>
    <span><a href="/">herdr.structupath.ai</a></span>
  </div>
</footer>

</body>
</html>
"""


def convert(md_text: str) -> str:
    html = markdown.markdown(md_text, extensions=["tables", "fenced_code"])
    # wiki-internal links -> site urls
    for stem, url in LINK_MAP.items():
        html = html.replace(f'href="{stem}"', f'href="{url}"')
    # horizontal-scroll wrapper for tables
    html = html.replace("<table>", '<div class="table-scroll"><table>')
    html = html.replace("</table>", "</table></div>")
    return html


def first_sentence(md_text: str) -> str:
    for line in md_text.splitlines():
        line = line.strip()
        if line and not line.startswith(("#", ">", "|", "```", "-", "*")):
            plain = re.sub(r"\[([^\]]*)\]\([^)]*\)", r"\1", line)
            plain = re.sub(r"[`*_]", "", plain)
            return plain[:155].replace('"', "'")
    return "StructuPath Herdr Suite documentation."


def pager_html(i: int) -> str:
    prev = PAGES[i - 1] if i > 0 else None
    nxt = PAGES[i + 1] if i + 1 < len(PAGES) else None
    left = (f'<a href="{prev[3]}"><span class="lbl">Previous</span>{prev[2]}</a>'
            if prev else "<span></span>")
    right = (f'<a href="{nxt[3]}" style="text-align:right"><span class="lbl">Next</span>{nxt[2]}</a>'
             if nxt else "<span></span>")
    return f'    <nav class="pager" aria-label="Docs pages">{left}{right}</nav>'


def main() -> int:
    if len(sys.argv) != 2:
        print(__doc__)
        return 2
    wiki = pathlib.Path(sys.argv[1])
    missing = [stem for stem, *_ in PAGES if not (wiki / f"{stem}.md").exists()]
    if missing:
        print(f"ERROR: wiki pages missing: {missing} in {wiki} — refusing to build partial docs.")
        return 1
    for i, (stem, slug, title, url) in enumerate(PAGES):
        md_text = (wiki / f"{stem}.md").read_text(encoding="utf-8")
        actives = {f"a_{s}": (' class="active"' if s == slug else "") for _, s, _, _ in PAGES}
        html = TEMPLATE.format(
            tab_title=("Overview" if slug == "index" else f"{title} guide"),
            desc=first_sentence(md_text),
            crumb=("Docs" if slug == "index" else "Docs / Plugins"),
            content=convert(md_text),
            pager=pager_html(i),
            **actives,
        )
        out = SITE / "docs" / ("index.html" if slug == "index" else f"{slug}/index.html")
        out.parent.mkdir(parents=True, exist_ok=True)
        out.write_text(html, encoding="utf-8")
        print(f"wrote {out.relative_to(SITE)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
