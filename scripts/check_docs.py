#!/usr/bin/env python3
"""Check canonical docs evidence, generated HTML, local links, and truth claims."""

from __future__ import annotations

import argparse
import hashlib
import html
import json
import pathlib
import re
import struct
import subprocess
import sys
import tomllib
from typing import Any
from urllib.parse import unquote, urlsplit

SITE = pathlib.Path(__file__).resolve().parent.parent
DOCS_SRC = SITE / "docs-src"
DATA_FILE = SITE / "data" / "plugins.json"
BASE_URL = "https://herdr.structupath.ai"
SOCIAL_IMAGE = SITE / "media" / "herdr-suite-social.jpg"
SOCIAL_IMAGE_URL = f"{BASE_URL}/media/herdr-suite-social.jpg"

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
    "verified Conductor teardown": re.compile(
        r"(?:verified\s+conductor-owned\s+(?:worker\s+)?panes|"
        r"stand-down[^.\n]{0,120}verif(?:y|ies|ied)[^.\n]{0,80}(?:ownership|owned))",
        re.IGNORECASE,
    ),
    "unsafe Conductor stand-down quickstart": re.compile(
        r"herdr\s+plugin\s+action\s+invoke\s+stand-down\s+--plugin\s+structupath\.conductor",
        re.IGNORECASE,
    ),
}

PUBLIC_TEXT_FILES = [
    SITE / "README.md",
    SITE / "index.html",
    SITE / "llms.txt",
    *sorted(DOCS_SRC.glob("*.md")),
]


def load_plugins() -> list[dict[str, Any]]:
    try:
        payload = json.loads(DATA_FILE.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as error:
        raise ValueError(
            f"unable to load {DATA_FILE.relative_to(SITE)}: {error}"
        ) from error
    if payload.get("schema_version") != 1:
        raise ValueError("data/plugins.json schema_version must be 1")
    plugins = payload.get("plugins")
    if not isinstance(plugins, list) or not plugins:
        raise ValueError("data/plugins.json plugins must be a non-empty list")
    return plugins


def expected_tested(plugin: dict[str, Any]) -> str:
    versions = plugin["tested_herdr_versions"]
    if not isinstance(versions, list) or not all(
        isinstance(item, str) for item in versions
    ):
        raise ValueError(
            f"{plugin['slug']}: tested_herdr_versions must be a string list"
        )
    return "`, `".join(versions) if versions else "pending transport hotfix"


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
            errors.append(
                f"docs-src/{plugin['name']}.md version/evidence drift: {label} != {value}"
            )

    if str(plugin["id"]) != f"structupath.{slug}":
        errors.append(f"data/plugins.json id/slug drift for {slug}")
    return errors


def check_llms_summaries(plugins: list[dict[str, Any]], text: str) -> list[str]:
    errors = []
    for plugin in plugins:
        release = re.compile(
            rf"^(?:-\s+)?{re.escape(str(plugin['name']))}\s+"
            rf"\(`{re.escape(str(plugin['id']))}`\)\s+release\s+"
            rf"{re.escape(str(plugin['version']))}:",
            re.MULTILINE,
        )
        if not release.search(text):
            errors.append(f"llms.txt release summary drift for {plugin['slug']}")

    guard = next(plugin for plugin in plugins if plugin["slug"] == "guard")
    tested = ", ".join(guard["tested_herdr_versions"])
    guard_evidence = re.compile(
        rf"^-\s+Guard\s+\(`{re.escape(str(guard['id']))}`\)\s+release\s+"
        rf"{re.escape(str(guard['version']))}:\s+manifest minimum Herdr\s+"
        rf"{re.escape(str(guard['min_herdr_version']))};\s+"
        rf"evidence records testing with\s+{re.escape(tested)}\.",
        re.MULTILINE,
    )
    if not guard_evidence.search(text):
        errors.append("llms.txt tested-version summary drift for guard")
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
        errors.append(
            f"plugin set drift: expected {sorted(expected_slugs)}, found {sorted(seen_slugs)}"
        )

    home = (DOCS_SRC / "Home.md").read_text(encoding="utf-8")
    llms = (SITE / "llms.txt").read_text(encoding="utf-8")
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
    errors.extend(check_llms_summaries(plugins, llms))
    return errors


def check_forbidden_claims(files: list[pathlib.Path] = PUBLIC_TEXT_FILES) -> list[str]:
    errors = []
    for path in files:
        text = path.read_text(encoding="utf-8")
        for label, pattern in FORBIDDEN_CLAIMS.items():
            match = pattern.search(text)
            if match:
                line = text.count("\n", 0, match.start()) + 1
                errors.append(
                    f"{path.relative_to(SITE)}:{line}: forbidden {label}: {match.group(0)!r}"
                )
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
                errors.append(
                    f"{path.relative_to(SITE)} missing Explore contract marker: {marker!r}"
                )

    landing = (SITE / "index.html").read_text(encoding="utf-8")
    errors.extend(check_landing_explore_boundary(landing))
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


def check_landing_explore_boundary(landing: str) -> list[str]:
    """Require the same-user boundary inside Explore onboarding, before Deliver."""
    start = '<section class="explore" id="explore">'
    end = '<section id="deliver">'
    if start not in landing or end not in landing:
        return ["index.html missing scoped Explore/onboarding region"]
    region = re.sub(r"\s+", " ", landing.split(start, 1)[1].split(end, 1)[0])
    required = [
        "Worktrees separate changes for review",
        "not sandboxes",
        "trusted same-user principals",
    ]
    return [
        f"index.html Explore/onboarding region missing trust boundary: {marker!r}"
        for marker in required
        if marker.casefold() not in region.casefold()
    ]


def jpeg_dimensions(path: pathlib.Path) -> tuple[int, int]:
    """Read JPEG dimensions without adding an image-library dependency."""
    data = path.read_bytes()
    if not data.startswith(b"\xff\xd8"):
        raise ValueError("not a JPEG file")
    offset = 2
    start_of_frame = {
        0xC0,
        0xC1,
        0xC2,
        0xC3,
        0xC5,
        0xC6,
        0xC7,
        0xC9,
        0xCA,
        0xCB,
        0xCD,
        0xCE,
        0xCF,
    }
    while offset < len(data):
        if data[offset] != 0xFF:
            offset += 1
            continue
        while offset < len(data) and data[offset] == 0xFF:
            offset += 1
        marker = data[offset]
        offset += 1
        if marker in {0xD8, 0xD9}:
            continue
        length = struct.unpack(">H", data[offset : offset + 2])[0]
        if marker in start_of_frame:
            height, width = struct.unpack(">HH", data[offset + 3 : offset + 7])
            return width, height
        offset += length
    raise ValueError("JPEG dimensions not found")


def tag_attributes(tag: str) -> dict[str, str]:
    return {
        key.casefold(): html.unescape(value)
        for key, _, value in re.findall(
            r"([:\w-]+)\s*=\s*([\"'])(.*?)\2", tag, re.DOTALL
        )
    }


def check_social_metadata() -> list[str]:
    errors = []
    routes = {SITE / "index.html": f"{BASE_URL}/"}
    for page in sorted((SITE / "docs").glob("**/*.html")):
        route = f"/{page.relative_to(SITE).as_posix().removesuffix('index.html')}"
        routes[page] = f"{BASE_URL}{route}"
    for page, canonical_url in routes.items():
        text = page.read_text(encoding="utf-8")
        tags = [
            tag_attributes(tag)
            for tag in re.findall(r"<(?:meta|link)\b[^>]*>", text, re.IGNORECASE)
        ]
        canonical = next(
            (tag.get("href") for tag in tags if tag.get("rel") == "canonical"),
            None,
        )
        if canonical != canonical_url:
            errors.append(
                f"{page.relative_to(SITE)} canonical {canonical!r} != {canonical_url!r}"
            )
        metadata = {
            tag.get("property") or tag.get("name"): tag.get("content")
            for tag in tags
            if tag.get("property") or tag.get("name")
        }
        expected = {
            "og:url": canonical_url,
            "og:image": SOCIAL_IMAGE_URL,
            "og:image:width": "1200",
            "og:image:height": "630",
            "twitter:card": "summary_large_image",
            "twitter:image": SOCIAL_IMAGE_URL,
        }
        for key, value in expected.items():
            if metadata.get(key) != value:
                errors.append(
                    f"{page.relative_to(SITE)} metadata {key} {metadata.get(key)!r} != {value!r}"
                )
        for key in (
            "description",
            "og:description",
            "og:image:alt",
            "twitter:description",
            "twitter:image:alt",
        ):
            value = metadata.get(key) or ""
            if len(value) < 40 or value.startswith("Repo:"):
                errors.append(
                    f"{page.relative_to(SITE)} metadata {key} is missing or not useful"
                )
    try:
        dimensions = jpeg_dimensions(SOCIAL_IMAGE)
    except (OSError, ValueError, struct.error) as error:
        errors.append(f"unable to validate social image: {error}")
    else:
        if dimensions != (1200, 630):
            errors.append(f"social image dimensions {dimensions} != (1200, 630)")
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
    """Keep the pinned Conductor quickstart inspection-only and visibly bounded."""
    if rendered_html is None:
        page = SITE / "docs" / "conductor" / "index.html"
        try:
            rendered_html = page.read_text(encoding="utf-8")
        except OSError as error:
            return [f"unable to read generated Conductor guide: {error}"]

    start = "<h2>Inspection-only quickstart</h2>"
    end = "<h2>Current trust and completion limits</h2>"
    if start not in rendered_html or end not in rendered_html:
        return ["generated Conductor guide is missing the inspection-only quickstart"]
    quickstart = rendered_html.split(start, 1)[1].split(end, 1)[0]
    bash_blocks = [
        html.unescape(block)
        for block in re.findall(
            r'<pre><code class="language-bash">(.*?)</code></pre>',
            quickstart,
            re.DOTALL,
        )
    ]
    expected = (
        "herdr plugin action invoke assemble",
        "herdr plugin action invoke status",
        "herdr plugin action invoke board",
    )
    errors = []
    if not any(all(snippet in block for snippet in expected) for block in bash_blocks):
        errors.append(
            "Conductor inspection actions are not one rendered bash code block"
        )
    forbidden = (
        "conductor_pin_active_run",
        "conductor_dispatch",
        "herdr plugin action invoke harvest",
        "herdr plugin action invoke stand-down",
    )
    for command in forbidden:
        if command in quickstart:
            errors.append(
                f"Conductor inspection-only quickstart contains unsafe command: {command}"
            )
    required_boundaries = (
        "Stop after inspection",
        "do not invoke the current harvest or stand-down actions",
    )
    for marker in required_boundaries:
        if marker.casefold() not in quickstart.casefold():
            errors.append(f"Conductor quickstart missing safety boundary: {marker!r}")

    public_text = re.sub(
        r"\s+", " ", html.unescape(re.sub(r"<[^>]+>", " ", rendered_html))
    )
    required_contract = (
        "selects the newest run globally rather than by repository/workspace identity",
        "without live ownership verification",
        "sources executable state",
        "not product-enforced filesystem or process isolation",
        "does not create role worktrees or branches",
        "neither is advanced to the reconciled integration result",
        "there is no automatic Conductor→Swarm pipeline",
    )
    for marker in required_contract:
        if marker.casefold() not in public_text.casefold():
            errors.append(f"Conductor guide missing safety contract: {marker!r}")
    return errors


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
            if (
                re.fullmatch(r"[A-Za-z_][A-Za-z0-9_-]*", target)
                and target not in source_names
            ):
                errors.append(
                    f"{page.relative_to(SITE)}: broken docs-src link {target!r}"
                )
    return errors


def check_sibling_manifests(
    root: pathlib.Path, plugins: list[dict[str, Any]]
) -> list[str]:
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
            errors.append(
                f"{slug}: sibling HEAD {head} != pinned commit {plugin['commit']}"
            )
        digest = hashlib.sha256(manifest).hexdigest()
        if digest != plugin["manifest_sha256"]:
            errors.append(
                f"{slug}: manifest digest {digest} != {plugin['manifest_sha256']}"
            )
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
                errors.append(
                    f"{slug}: manifest {field} {actual!r} != pinned {plugin[field]!r}"
                )
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

    llms = (SITE / "llms.txt").read_text(encoding="utf-8")
    guard = next(item for item in plugins if item["slug"] == "guard")
    inflated_release = llms.replace(
        f"Guard (`{guard['id']}`) release {guard['version']}:",
        f"Guard (`{guard['id']}`) release {guard['version']}0:",
        1,
    )
    if not check_llms_summaries(plugins, inflated_release):
        failures.append("self-test did not detect llms release boundary drift")
    tested = ", ".join(guard["tested_herdr_versions"])
    inflated_tested = llms.replace(
        f"evidence records testing with {tested}.",
        f"evidence records testing with {tested}0.",
        1,
    )
    if not check_llms_summaries(plugins, inflated_tested):
        failures.append("self-test did not detect llms tested-version boundary drift")
    forbidden_samples = {
        "Guard enforcement claim": ("Guard enforces every agent command.",),
        "verified Conductor teardown": (
            "Close verified Conductor-owned worker panes.",
            "Stand-down closes worker panes after Conductor verifies their ownership.",
        ),
        "unsafe Conductor stand-down quickstart": (
            "herdr plugin action invoke stand-down --plugin structupath.conductor",
        ),
    }
    for label, samples in forbidden_samples.items():
        pattern = FORBIDDEN_CLAIMS.get(label)
        if pattern is None or not all(pattern.search(sample) for sample in samples):
            failures.append(f"self-test did not detect {label}")

    conductor_html = (SITE / "docs" / "conductor" / "index.html").read_text(
        encoding="utf-8"
    )
    broken_fences = conductor_html.replace(
        '<pre><code class="language-bash">', '<p><code class="language-bash">'
    )
    if not check_conductor_quickstart(broken_fences):
        failures.append("self-test did not detect broken quickstart code fences")
    quickstart_end = "<h2>Current trust and completion limits</h2>"
    unsafe_commands = (
        "conductor_pin_active_run",
        "conductor_dispatch",
        "herdr plugin action invoke harvest",
        "herdr plugin action invoke stand-down",
    )
    for command in unsafe_commands:
        mutated = conductor_html.replace(
            quickstart_end, f"<p>{command}</p>{quickstart_end}", 1
        )
        findings = check_conductor_quickstart(mutated)
        if not any(command in finding for finding in findings):
            failures.append(
                f"self-test did not reject Conductor quickstart command: {command}"
            )
    safety_markers = (
        "Stop after inspection",
        "do not invoke the current harvest or stand-down actions",
        "selects the newest run globally rather than by repository/workspace identity",
        "without live ownership verification",
        "sources executable state",
        "not product-enforced filesystem or process isolation",
        "does not create role worktrees or branches",
        "neither is advanced to the reconciled integration result",
        "there is no automatic Conductor→Swarm pipeline",
    )
    for marker in safety_markers:
        mutated = conductor_html.replace(marker, "REMOVED SAFETY CONTRACT", 1)
        if mutated == conductor_html or not check_conductor_quickstart(mutated):
            failures.append(
                f"self-test did not detect missing Conductor safety marker: {marker}"
            )
    landing = (SITE / "index.html").read_text(encoding="utf-8")
    weakened_boundary = re.sub(
        r"trusted\s+same-user\s+principals", "agents", landing, count=1
    )
    if not check_landing_explore_boundary(weakened_boundary):
        failures.append("self-test did not detect a weakened Explore trust boundary")
    if not failures:
        print(
            "OK: self-test detected action, version, llms-version, forbidden-claim, "
            "Conductor quickstart/safety-contract, and Explore-boundary mutations"
        )
    return failures


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--sibling-root",
        type=pathlib.Path,
        help="optionally verify herdr-{browser,guard,swarm,conductor} checkouts at this path",
    )
    parser.add_argument(
        "--self-test", action="store_true", help="prove drift checks detect mutations"
    )
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
    errors.extend(check_social_metadata())
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
