#!/usr/bin/env python3
"""Refresh the public-activity block in the profile README.

Uses only Python's standard library so the workflow needs no install step.
Events come from the public GitHub API and the README is rewritten only when
the rendered output actually changes.

Events that would make the feed read as noise are filtered out: commits to this
profile repository (which are mostly the automation itself) and repeats of the
same event type on the same repository.
"""

from __future__ import annotations

import os
from pathlib import Path

from profile_common import (  # noqa: E402  (sys.path is prepared by the module)
    github_json,
    is_profile_repo,
    relative_day,
    truncate,
    username,
    write_block,
)

README = Path(os.environ.get("README_PATH", "README.md"))
START = "<!-- ACTIVITY:START -->"
END = "<!-- ACTIVITY:END -->"
MAX_ITEMS = int(os.environ.get("ACTIVITY_ITEMS", "5"))


def fetch_events() -> list[dict]:
    """Fetch the most recent public events for the profile account."""
    payload = github_json(f"/users/{username()}/events/public?per_page=100")
    if not isinstance(payload, list):
        raise RuntimeError("Unexpected payload shape for the events endpoint.")
    return payload


def fetch_showable_repos() -> set[str]:
    """Names of repositories that carry enough information to be worth showing.

    Repositories with no description, no topics, and no stars are usually
    scratch copies created from a template. They are allowed into the feed only
    if nothing better is available.
    """
    payload = github_json(f"/users/{username()}/repos?per_page=100&sort=pushed")
    if not isinstance(payload, list):
        return set()
    return {
        repo.get("name", "")
        for repo in payload
        if isinstance(repo, dict)
        and (repo.get("description") or repo.get("topics") or repo.get("stargazers_count"))
    }


def commit_headline(payload: dict) -> str | None:
    """Return the first commit subject, collapsed to a single line."""
    commits = payload.get("commits") or []
    if not commits:
        return None
    message = (commits[0].get("message") or "").strip().splitlines()
    return truncate(message[0], 60) if message and message[0] else None


def event_summary(event: dict) -> tuple[str, str, str] | None:
    """Return (label, subject, detail) for the event types worth showing."""
    repo_name = event.get("repo", {}).get("name", "")
    if is_profile_repo(repo_name):
        return None

    event_type = event.get("type")
    payload = event.get("payload", {})
    url = f"https://github.com/{repo_name}" if repo_name else ""
    subject = f"[{repo_name}]({url})" if repo_name else "a repository"

    if event_type == "PushEvent":
        count = len(payload.get("commits") or [])
        branch = (payload.get("ref") or "").removeprefix("refs/heads/")
        if count:
            noun = "commit" if count == 1 else "commits"
            headline = commit_headline(payload)
            detail = f"{count} {noun}, latest {headline}" if headline else f"{count} {noun}"
            if branch:
                detail += f" on `{branch}`"
            return "Push", subject, detail
        # The public Events API sometimes omits the commit list entirely. Report
        # the reliable fact instead of a misleading "0 commits".
        detail = f"updated `{branch}`" if branch else "updated"
        return "Push", subject, detail

    if event_type == "CreateEvent":
        ref_type = payload.get("ref_type", "repository")
        ref = payload.get("ref")
        # Creating the default branch is an artefact of initialising a
        # repository, not something a visitor cares about.
        if ref_type == "branch" and ref in {"main", "master", "develop"}:
            return None
        return "Create", subject, f"{ref_type} `{ref}`" if ref else ref_type

    if event_type == "PullRequestEvent":
        action = payload.get("action", "updated")
        pull_request = payload.get("pull_request") or {}
        number = pull_request.get("number")
        link = pull_request.get("html_url")
        reference = f"[#{number}]({link})" if number and link else "a pull request"
        return "Pull request", subject, f"{action} {reference}"

    if event_type == "IssuesEvent":
        action = payload.get("action", "updated")
        issue = payload.get("issue") or {}
        number = issue.get("number")
        link = issue.get("html_url")
        reference = f"[#{number}]({link})" if number and link else "an issue"
        return "Issue", subject, f"{action} {reference}"

    if event_type == "IssueCommentEvent":
        issue = payload.get("issue") or {}
        number = issue.get("number")
        link = issue.get("html_url")
        reference = f"[#{number}]({link})" if number and link else "an issue"
        return "Comment", subject, f"on {reference}"

    if event_type == "ReleaseEvent":
        release = payload.get("release") or {}
        tag = release.get("tag_name")
        return "Release", subject, f"published `{tag}`" if tag else "published a release"

    if event_type == "WatchEvent":
        return "Starred", subject, ""

    if event_type == "ForkEvent":
        forkee = payload.get("forkee") or {}
        fork_url = forkee.get("html_url")
        target = f"[{repo_name}]({fork_url})" if fork_url else subject
        return "Forked", target, ""

    if event_type == "PublicEvent":
        return "Open sourced", subject, ""

    return None


def render_activity(events: list[dict], showable: set[str]) -> str:
    """Pick a varied set of the most recent meaningful events.

    Events on repositories that look like real work come first. If that leaves
    the panel nearly empty, the newest remaining events top it up so the
    section is never blank.
    """
    preferred: list[str] = []
    fallback: list[str] = []
    seen: set[tuple[str, str]] = set()

    for event in events:
        summary = event_summary(event)
        if not summary:
            continue
        # One entry per (event type, repository) keeps the panel varied.
        key = (event.get("type", ""), event.get("repo", {}).get("name", ""))
        if key in seen:
            continue
        seen.add(key)

        label, subject, detail = summary
        when = relative_day(event.get("created_at"))
        if detail:
            line = f"- **{label}** in {subject}: {detail}, {when}"
        else:
            line = f"- **{label}** {subject}, {when}"

        repo = event.get("repo", {}).get("name", "").split("/")[-1]
        (preferred if repo in showable else fallback).append(line)

    lines = (preferred + fallback)[:MAX_ITEMS]
    if not lines:
        lines.append("- Recent public activity will appear here as projects are updated.")
    return "\n".join(lines)


def main() -> int:
    try:
        events = fetch_events()
        changed = write_block(README, START, END, render_activity(events, fetch_showable_repos()))
    except (OSError, RuntimeError, ValueError) as error:
        print(f"::error::{error}")
        return 1

    print("Updated README activity." if changed else "README activity is already current.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
