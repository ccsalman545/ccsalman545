#!/usr/bin/env python3
"""Refresh the public-activity block in the profile README.

This deliberately uses only Python's standard library so the workflow has no
package-install step. GitHub events are fetched from the public API and the
README is changed only when the rendered activity is different.
"""

from __future__ import annotations

import json
import os
import re
import sys
from datetime import datetime
from pathlib import Path
from urllib.error import HTTPError, URLError
from urllib.request import Request, urlopen

PROFILE_USERNAME = os.environ.get("PROFILE_USERNAME", "ccsalman545")
README = Path("README.md")
START = "<!-- ACTIVITY:START -->"
END = "<!-- ACTIVITY:END -->"
MAX_ITEMS = 5


def fetch_events() -> list[dict]:
    """Fetch recent public events, using the workflow token when available."""
    headers = {
        "Accept": "application/vnd.github+json",
        "User-Agent": "ccsalman545-profile-activity",
        "X-GitHub-Api-Version": "2022-11-28",
    }
    token = os.environ.get("GITHUB_TOKEN")
    if token:
        headers["Authorization"] = f"Bearer {token}"

    request = Request(
        f"https://api.github.com/users/{PROFILE_USERNAME}/events/public?per_page=50",
        headers=headers,
    )
    try:
        with urlopen(request, timeout=20) as response:  # nosec B310: fixed GitHub API URL
            return json.load(response)
    except (HTTPError, URLError, TimeoutError) as error:
        raise RuntimeError(f"Could not fetch public GitHub activity: {error}") from error


def event_summary(event: dict) -> str | None:
    """Render the useful public event types as concise Markdown."""
    repo = event.get("repo", {}).get("name", "")
    # Do not let this scheduled workflow turn the dashboard into a list of its
    # own README updates. The profile repository itself is still visible above.
    if repo.lower() == f"{PROFILE_USERNAME}/{PROFILE_USERNAME}".lower():
        return None

    event_type = event.get("type")
    payload = event.get("payload", {})
    repo_link = f"[{repo}](https://github.com/{repo})" if repo else "a repository"

    if event_type == "PushEvent":
        commits = len(payload.get("commits", []))
        if commits:
            noun = "commit" if commits == 1 else "commits"
            return f"**Push** — pushed {commits} {noun} to {repo_link}"
        # GitHub's public Events API can omit individual commits from a push.
        # In that case, state the reliable information rather than publishing
        # a misleading "0 commits" count.
        branch = payload.get("ref", "").removeprefix("refs/heads/")
        suffix = f" on `{branch}`" if branch else ""
        return f"**Push** — updated {repo_link}{suffix}"

    if event_type == "CreateEvent":
        ref_type = payload.get("ref_type", "repository")
        ref = payload.get("ref")
        target = f" `{ref}`" if ref else ""
        return f"**Create** — created {ref_type}{target} in {repo_link}"

    if event_type == "PullRequestEvent":
        action = payload.get("action", "updated")
        pull_request = payload.get("pull_request", {})
        number = pull_request.get("number")
        link = pull_request.get("html_url")
        pr = f"[#{number}]({link})" if number and link else "a pull request"
        return f"**Pull request** — {action} {pr} in {repo_link}"

    if event_type == "IssuesEvent":
        action = payload.get("action", "updated")
        issue = payload.get("issue", {})
        number = issue.get("number")
        link = issue.get("html_url")
        item = f"[#{number}]({link})" if number and link else "an issue"
        return f"**Issue** — {action} {item} in {repo_link}"

    if event_type == "WatchEvent":
        return f"**Starred** — bookmarked {repo_link}"

    if event_type == "ForkEvent":
        return f"**Forked** — created a fork of {repo_link}"

    return None


def event_date(event: dict) -> str:
    """Return a stable, readable UTC date for an event."""
    created = event.get("created_at", "")
    try:
        return datetime.fromisoformat(created.replace("Z", "+00:00")).strftime("%b %d, %Y")
    except ValueError:
        return created or "recently"


def render_activity(events: list[dict]) -> str:
    """Select and render up to MAX_ITEMS of meaningful project activity."""
    lines: list[str] = []
    for event in events:
        summary = event_summary(event)
        if summary:
            lines.append(f"- {summary} · {event_date(event)}")
        if len(lines) == MAX_ITEMS:
            break

    if not lines:
        lines.append("- Recent public activity will appear here as projects are updated.")
    return "\n".join(lines)


def update_readme(block: str) -> bool:
    """Replace the marker block and return whether README content changed."""
    content = README.read_text(encoding="utf-8")
    pattern = re.compile(
        rf"({re.escape(START)})(.*?)(\n{re.escape(END)})", re.DOTALL
    )
    replacement = f"{START}\n{block}\n{END}"
    updated, matches = pattern.subn(replacement, content, count=1)
    if matches != 1:
        raise RuntimeError("README activity markers are missing or malformed.")
    if updated == content:
        return False
    README.write_text(updated, encoding="utf-8")
    return True


def main() -> int:
    try:
        changed = update_readme(render_activity(fetch_events()))
    except (OSError, RuntimeError, json.JSONDecodeError) as error:
        print(f"::error::{error}", file=sys.stderr)
        return 1

    print("Updated README activity." if changed else "README activity is already current.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
