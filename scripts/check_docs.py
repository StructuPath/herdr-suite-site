#!/usr/bin/env python3
"""Check canonical docs evidence, generated HTML, local links, and truth claims."""

from __future__ import annotations

import argparse
import hashlib
import html
import json
import pathlib
import re
import subprocess
import sys
import tomllib
from typing import Any
from urllib.parse import unquote, urlsplit

SITE = pathlib.Path(__file__).resolve().parent.parent
DOCS_SRC = SITE / "docs-src"
DATA_FILE = SITE / "data" / "plugins.json"

FORBIDDEN_CLAIMS = {
    "blanket marketplace claim": re.compile(
        r"marketplace-listed|straight from the herdr marketplace", re.IGNORECASE
    ),
    "blanket suite tested-version claim": re.compile(
        r"verified on herdr\s+0\.7\.5|all four[^\n]{0,100}(?:tested|verified)",
        re.IGNORECASE,
    ),
    "Guard enforcement claim": re.compile(r"guard\s+enforces", re.IGNORECASE),
    "unimplemented Conductor-to-Swarm pipeline": re.compile(
        r"conductor\s+decides[^\n]{0,120}swarm\s+isolates", re.IGNORECASE
    ),
}

PUBLIC_TEXT_FILES = [
    SITE / "README.md",
    SITE / "index.html",
    SITE / "llms.txt",
    *sorted(DOCS_SRC.glob("*.md")),
]


def load_plugins() -> list[dict[str, Any]]:
    payload = json.loads(DATA_FILE.read_text(encoding="utf-8"))
    if payload.get("schema_version") != 1:
        raise ValueError("data/plugins.json schema_version must be 1")
    plugins = payload.get("plugins")
    if not isinstance(plugins, list) or not plugins:
        raise ValueError("data/plugins.json plugins must be a non-empty list")
    return plugins


def expected_tested(plugin: dict[str, Any]) -> str:
    versions = plugin["tested_herdr_versions"]
    if not isinstance(versions, list) or not all(isinstance(item, str) for item in versions):
        raise ValueError(f"{plugin['slug']}: tested_herdr_versions must be a string list")
    return "`, `".join(versions)


def check_plugin_doc(plugin: dict[str, Any], text: str) -> list[str]:
    slug = str(plugin["slug"])
    prefix = re.escape(str(plugin["id"]))
    documented_actions = set(re.findall(rf"{prefix}\.([a-z][a-z0-9-]*)", text))
    expected_actions = set(plugin["actions"])
    errors = []
    if documented_actions != expected_actions:
        errors.append(
            f"docs-src/{plugin['name']}.md action drift: "
            f"expected {sorted(expected_actions)}, found {sorted(documented_actions)}"
        )

    rows = {
        "Plugin release": str(plugin["version"]),
        "Minimum Herdr": str(plugin["min_herdr_version"]),
        "Explicitly tested Herdr": expected_tested(plugin),
        "Evidence commit": str(plugin["commit"]),
    }
    for label, value in rows.items():
        pattern = re.compile(
            rf"^\|\s*{re.escape(label)}\s*\|\s*`{re.escape(value)}`\s*\|\s*$",
            re.MULTILINE,
        )
        if not pattern.search(text):
            errors.append(f"docs-src/{plugin['name']}.md version/evidence drift: {label} != {value}")

    if str(plugin["id"]) != f"structupath.{slug}":
        errors.append(f"data/plugins.json id/slug drift for {slug}")
    return errors


def check_data_and_docs(plugins: list[dict[str, Any]]) -> list[str]:
    errors = []
    seen_slugs = set()
    required = {
        "slug",
        "name",
        "id",
        "repository",
        "commit",
        "version",
        "min_herdr_version",
        "tested_herdr_versions",
        "manifest_sha256",
        "actions",
    }
    for plugin in plugins:
        missing = required - plugin.keys()
        if missing:
            errors.append(f"data/plugins.json missing {sorted(missing)} in {plugin}")
            continue
        slug = str(plugin["slug"])
        if slug in seen_slugs:
            errors.append(f"data/plugins.json duplicate slug: {slug}")
        seen_slugs.add(slug)
        if not re.fullmatch(r"[0-9a-f]{40}", str(plugin["commit"])):
            errors.append(f"{slug}: commit must be a full 40-character SHA")
        if not re.fullmatch(r"[0-9a-f]{64}", str(plugin["manifest_sha256"])):
            errors.append(f"{slug}: manifest_sha256 must be a SHA-256 digest")
        actions = plugin["actions"]
        if not isinstance(actions, list) or len(actions) != len(set(actions)):
            errors.append(f"{slug}: actions must be a unique list")
        page = DOCS_SRC / f"{plugin['name']}.md"
        if not page.exists():
            errors.append(f"missing canonical page: {page.relative_to(SITE)}")
            continue
        errors.extend(check_plugin_doc(plugin, page.read_text(encoding="utf-8")))

    expected_slugs = {"browser", "guard", "swarm", "conductor"}
    if seen_slugs != expected_slugs:
        errors.append(f"plugin set drift: expected {sorted(expected_slugs)}, found {sorted(seen_slugs)}")

    home = (DOCS_SRC / "Home.md").read_text(encoding="utf-8")
    for plugin in plugins:
        tested = expected_tested(plugin)
        row = re.compile(
            rf"^\|\s*\[{re.escape(str(plugin['name']))}\]\({re.escape(str(plugin['name']))}\)"
            rf"\s*\|\s*`{re.escape(str(plugin['id']))}`\s*\|\s*`{re.escape(str(plugin['version']))}`"
            rf"\s*\|\s*`{re.escape(str(plugin['min_herdr_version']))}`\s*\|\s*`{re.escape(tested)}`\s*\|",
            re.MULTILINE,
        )
        if not row.search(home):
            errors.append(f"docs-src/Home.md summary drift for {plugin['slug']}")
    return errors


def check_forbidden_claims(files: list[pathlib.Path] = PUBLIC_TEXT_FILES) -> list[str]:
    errors = []
    for path in files:
        text = path.read_text(encoding="utf-8")
        for label, pattern in FORBIDDEN_CLAIMS.items():
            match = pattern.search(text)
            if match:
                line = text.count("\n", 0, match.start()) + 1
                errors.append(f"{path.relative_to(SITE)}:{line}: forbidden {label}: {match.group(0)!r}")
    return errors


def check_explore_contract() -> list[str]:
    """Keep the ready workflow, onboarding safety, and media contract visible."""
    required_markers = {
        SITE / "index.html": [
            "Explore a change three ways.",
            "Start Explore",
            "plugin actions menu",
            "Comparison criterion:",
            "Clean-slot merge warning",
            "Success means",
            "Abort keeps branches",
            "product-enforced approval gates",
            "not a sandbox",
        ],
        DOCS_SRC / "Home.md": [
            "**Explore** is the ready first workflow",
            "**Deliver** is an advanced assembly pattern",
            "current runtime is not a single automatic pipeline",
        ],
        DOCS_SRC / "Swarm.md": [
            "First Explore run",
            "plugin actions menu",
            'key = "prefix+s"',
            "Comparison criterion:",
            "Merge warning:",
            "Success definition",
            "preserves branches",
        ],
    }
    errors = []
    for path, markers in required_markers.items():
        text = path.read_text(encoding="utf-8")
        for marker in markers:
            if marker.casefold() not in text.casefold():
                errors.append(f"{path.relative_to(SITE)} missing Explore contract marker: {marker!r}")

    landing = (SITE / "index.html").read_text(encoding="utf-8")
    video = re.search(r"<video\b([^>]*)>", landing, re.IGNORECASE | re.DOTALL)
    if video is None:
        errors.append("index.html missing Explore proof video")
    else:
        attributes = video.group(1)
        if "controls" not in attributes:
            errors.append("index.html Explore proof video must be user-controlled")
        if "poster=" not in attributes:
            errors.append("index.html Explore proof video must have a poster")
        if "autoplay" in attributes:
            errors.append("index.html Explore proof video must not autoplay")
    return errors


def check_generated_docs() -> list[str]:
    result = subprocess.run(
        [sys.executable, str(SITE / "scripts" / "build_docs.py"), "--check"],
        cwd=SITE,
        capture_output=True,
        text=True,
    )
    if result.returncode == 0:
        return []
    detail = (result.stdout + result.stderr).strip()
    return [f"generated docs check failed: {detail}"]


def check_conductor_quickstart(rendered_html: str | None = None) -> list[str]:
    """Require every quickstart shell example to render as a fenced code block."""
    if rendered_html is None:
        page = SITE / "docs" / "conductor" / "index.html"
        try:
            rendered_html = page.read_text(encoding="utf-8")
        except OSError as error:
            return [f"unable to read generated Conductor guide: {error}"]

    start = "<h2>Minimal supervised quickstart</h2>"
    end = "<h2>Trust and completion model</h2>"
    if start not in rendered_html or end not in rendered_html:
        return ["generated Conductor guide is missing the quickstart section"]
    quickstart = rendered_html.split(start, 1)[1].split(end, 1)[0]
    bash_blocks = [
        html.unescape(block)
        for block in re.findall(
            r'<pre><code class="language-bash">(.*?)</code></pre>',
            quickstart,
            re.DOTALL,
        )
    ]
    expected_blocks = {
        "assemble action": ("herdr plugin action invoke assemble",),
        "pinned run dispatch": (
            ". /path/to/herdr-conductor/scripts/lib.sh",
            "conductor_pin_active_run",
            "Selected Conductor run:",
            "read -r verified_run",
            "conductor_dispatch builder-engine",
        ),
        "harvest action": ("herdr plugin action invoke harvest",),
    }
    return [
        f"Conductor quickstart {label} is not a rendered bash code block"
        for label, snippets in expected_blocks.items()
        if not any(
            all(snippet in block for snippet in snippets) for block in bash_blocks
        )
    ]


def local_target(url: str) -> pathlib.Path | None:
    parsed = urlsplit(url)
    if parsed.scheme or parsed.netloc or not parsed.path.startswith("/"):
        return None
    route = unquote(parsed.path).lstrip("/")
    target = SITE / route
    if not route or parsed.path.endswith("/"):
        target /= "index.html"
    return target


def check_local_links() -> list[str]:
    errors = []
    html_files = [SITE / "index.html", *sorted((SITE / "docs").glob("**/*.html"))]
    for page in html_files:
        text = page.read_text(encoding="utf-8")
        for url in re.findall(r"(?:href|src)=[\"']([^\"']+)[\"']", text):
            target = local_target(url)
            if target is not None and not target.is_file():
                errors.append(f"{page.relative_to(SITE)}: broken local link {url!r}")

    source_names = {path.stem for path in DOCS_SRC.glob("*.md")}
    for page in DOCS_SRC.glob("*.md"):
        text = page.read_text(encoding="utf-8")
        for target in re.findall(r"\[[^]]+\]\(([^)]+)\)", text):
            if re.fullmatch(r"[A-Za-z_][A-Za-z0-9_-]*", target) and target not in source_names:
                errors.append(f"{page.relative_to(SITE)}: broken docs-src link {target!r}")
    return errors


def check_sibling_manifests(root: pathlib.Path, plugins: list[dict[str, Any]]) -> list[str]:
    """Verify optional local sibling checkouts against the pinned reviewed evidence."""
    errors = []
    for plugin in plugins:
        slug = str(plugin["slug"])
        repo = root / f"herdr-{slug}"
        if not repo.is_dir():
            errors.append(f"missing sibling checkout: {repo}")
            continue
        try:
            head = subprocess.run(
                ["git", "-C", str(repo), "rev-parse", "HEAD"],
                check=True,
                capture_output=True,
                text=True,
            ).stdout.strip()
            manifest = subprocess.run(
                ["git", "-C", str(repo), "show", f"{head}:herdr-plugin.toml"],
                check=True,
                capture_output=True,
            ).stdout
        except subprocess.CalledProcessError as error:
            errors.append(f"{repo}: unable to read pinned manifest: {error}")
            continue
        if head != plugin["commit"]:
            errors.append(f"{slug}: sibling HEAD {head} != pinned commit {plugin['commit']}")
        digest = hashlib.sha256(manifest).hexdigest()
        if digest != plugin["manifest_sha256"]:
            errors.append(f"{slug}: manifest digest {digest} != {plugin['manifest_sha256']}")
        parsed = tomllib.loads(manifest.decode("utf-8"))
        manifest_actions = [action["id"] for action in parsed.get("actions", [])]
        comparisons = {
            "id": parsed.get("id"),
            "version": parsed.get("version"),
            "min_herdr_version": parsed.get("min_herdr_version"),
            "actions": manifest_actions,
        }
        for field, actual in comparisons.items():
            if actual != plugin[field]:
                errors.append(f"{slug}: manifest {field} {actual!r} != pinned {plugin[field]!r}")
    return errors


def run_self_test(plugins: list[dict[str, Any]]) -> list[str]:
    failures = []
    plugin = plugins[0]
    source = (DOCS_SRC / f"{plugin['name']}.md").read_text(encoding="utf-8")
    action = f"{plugin['id']}.{plugin['actions'][0]}"
    if not check_plugin_doc(plugin, source.replace(action, "removed.action", 1)):
        failures.append("self-test did not detect action drift")
    version = str(plugin["version"])
    if not check_plugin_doc(plugin, source.replace(f"`{version}`", "`999.0.0`", 1)):
        failures.append("self-test did not detect version drift")
    forbidden_sample = "Guard enforces every agent command."
    if not any(pattern.search(forbidden_sample) for pattern in FORBIDDEN_CLAIMS.values()):
        failures.append("self-test did not detect a forbidden claim")
    conductor_html = (SITE / "docs" / "conductor" / "index.html").read_text(
        encoding="utf-8"
    )
    broken_fences = conductor_html.replace(
        '<pre><code class="language-bash">', '<p><code class="language-bash">'
    )
    if not check_conductor_quickstart(broken_fences):
        failures.append("self-test did not detect broken quickstart code fences")
    if not failures:
        print(
            "OK: self-test detected action, version, forbidden-claim, "
            "and quickstart-rendering mutations"
        )
    return failures


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--sibling-root",
        type=pathlib.Path,
        help="optionally verify herdr-{browser,guard,swarm,conductor} checkouts at this path",
    )
    parser.add_argument("--self-test", action="store_true", help="prove drift checks detect mutations")
    args = parser.parse_args()

    try:
        plugins = load_plugins()
    except (OSError, ValueError, json.JSONDecodeError) as error:
        print(f"ERROR: {error}")
        return 1

    errors = []
    errors.extend(check_data_and_docs(plugins))
    errors.extend(check_forbidden_claims())
    errors.extend(check_explore_contract())
    errors.extend(check_generated_docs())
    errors.extend(check_conductor_quickstart())
    errors.extend(check_local_links())
    if args.sibling_root:
        errors.extend(check_sibling_manifests(args.sibling_root.resolve(), plugins))
    if args.self_test:
        errors.extend(run_self_test(plugins))

    if errors:
        for error in errors:
            print(f"ERROR: {error}")
        return 1
    print(
        f"OK: Explore contract, canonical docs, {len(plugins)} plugin evidence "
        "records, generated HTML, and local links"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
