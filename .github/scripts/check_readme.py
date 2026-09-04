#!/usr/bin/env python3
"""Validate the profile README before it is merged.

Catches the mistakes that silently break these profiles: an automation marker
deleted during an edit, a renamed asset that leaves a dead image, or inline
markup that GitHub's sanitiser will strip.
"""

from __future__ import annotations

import re
import sys
from pathlib import Path

README = Path("README.md")

# Every block a scheduled workflow rewrites. Losing one means the workflow will
# fail on its next run, so catch it here instead.
MARKERS = [
    ("<!-- ACTIVITY:START -->", "<!-- ACTIVITY:END -->"),
    ("<!-- REPOS:START -->", "<!-- REPOS:END -->"),
    ("<!-- COUNTERS:START -->", "<!-- COUNTERS:END -->"),
    ("<!-- BLOG-POST-LIST:START -->", "<!-- BLOG-POST-LIST:END -->"),
    ("<!--START_SECTION:waka-->", "<!--END_SECTION:waka-->"),
]

# GitHub's HTML pipeline removes these even though they are valid HTML.
FORBIDDEN_PATTERNS = [
    (r"<style\b", "inline <style> tags are stripped by GitHub"),
    (r"<script\b", "inline <script> tags are stripped by GitHub"),
    (r"<svg\b", "inline <svg> is stripped by GitHub; reference an SVG file instead"),
    (r"\bclass\s*=", "class attributes are stripped by GitHub; use align="),
    (r"\bid\s*=", "id attributes are stripped by GitHub"),
]

RELATIVE_ASSET = re.compile(r"(?:src|srcset|href)=\"((?!https?://|#|mailto:)[^\"]+)\"")
RELATIVE_LINK = re.compile(r"\[[^\]]*\]\(([^)\s]+)(?:\s+\"[^\"]*\")?\)")


def relative_targets(content: str) -> set[str]:
    """Collect every repository-relative path referenced by the README."""
    targets = set()
    for match in RELATIVE_ASSET.findall(content) + RELATIVE_LINK.findall(content):
        if match.startswith(("http://", "https://", "#", "mailto:", "data:")):
            continue
        targets.add(match)
    return targets


def main() -> int:
    if not README.exists():
        print(f"::error::{README} is missing.")
        return 1

    content = README.read_text(encoding="utf-8")
    problems: list[str] = []

    for start, end in MARKERS:
        if content.count(start) != 1 or content.count(end) != 1:
            problems.append(
                f"Marker pair {start} / {end} must appear exactly once "
                f"(found {content.count(start)} / {content.count(end)})."
            )
        elif content.index(start) > content.index(end):
            problems.append(f"Marker pair {start} / {end} is out of order.")

    for path in sorted(relative_targets(content)):
        target = Path(path.split("?")[0].split("#")[0])
        if target.is_absolute() or not target.exists():
            problems.append(f"Referenced path does not exist: {path}")
        elif target.suffix.lower() == ".svg" and target.stat().st_size == 0:
            problems.append(f"SVG asset is empty: {path}")

    for pattern, reason in FORBIDDEN_PATTERNS:
        if re.search(pattern, content, re.IGNORECASE):
            problems.append(f"README contains markup GitHub will remove — {reason}.")

    if len(content.encode("utf-8")) > 512_000:
        problems.append("README exceeds 512 KB; GitHub will refuse to render it.")

    for problem in problems:
        print(f"::error::{problem}")

    if problems:
        print(f"\n{len(problems)} problem(s) found.")
        return 1

    labels = re.findall(r"<!--\s*(.*?)\s*-->", "".join(start for start, _ in MARKERS))
    markers = ", ".join(labels)
    print(f"README checks passed ({len(content):,} characters, markers: {markers}).")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
