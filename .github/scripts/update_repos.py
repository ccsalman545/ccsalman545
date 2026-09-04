#!/usr/bin/env python3
"""Refresh the featured-repository table, the counters row, and the badge data.

Everything here is derived from the public GitHub API, so the numbers on the
profile are never hand-maintained. Only Python's standard library is used.

Outputs
    README.md          <!-- REPOS:START --> table of featured repositories
    README.md          <!-- COUNTERS:START --> row of freshly numbered badges
    data/*.json        Shields.io ``endpoint`` payloads for reuse elsewhere
"""

from __future__ import annotations

import json
import os
from datetime import datetime, timezone
from pathlib import Path
from urllib.parse import quote

from profile_common import (  # noqa: E402  (sys.path is prepared by the module)
    escape_cell,
    github_json,
    is_profile_repo,
    iso_date,
    replace_block,
    truncate,
    username,
    write_block,
)

README = Path(os.environ.get("README_PATH", "README.md"))
DATA_DIR = Path(os.environ.get("DATA_PATH", "data"))
CONFIG = Path(os.environ.get("FEATURED_CONFIG", ".github/scripts/featured.json"))

REPOS_START = "<!-- REPOS:START -->"
REPOS_END = "<!-- REPOS:END -->"
COUNTERS_START = "<!-- COUNTERS:START -->"
COUNTERS_END = "<!-- COUNTERS:END -->"

FEATURED_COUNT = int(os.environ.get("FEATURED_COUNT", "6"))
DEFAULT_PINNED = [
    "Linux-Scripts",
    "Embedded-Projects",
    "FPGA-Vision-Processing",
    "muhammed-salman-portfolio",
    "Arduino-IoT",
]

BADGE_BASE = "https://img.shields.io/badge"


def pinned_names() -> list[str]:
    """Read the curated ordering from the environment, then the config file."""
    raw = os.environ.get("FEATURED_REPOS", "").strip()
    if raw:
        return [name.strip() for name in raw.split(",") if name.strip()]
    try:
        payload = json.loads(CONFIG.read_text(encoding="utf-8"))
        names = payload.get("pinned") if isinstance(payload, dict) else None
        if isinstance(names, list):
            return [str(name) for name in names]
    except (OSError, ValueError):
        pass
    return list(DEFAULT_PINNED)


def has_signal(repo: dict) -> bool:
    """True when a repository looks like real work rather than a scratch copy.

    Throwaway repositories usually arrive with no description, no topics, and
    no stars; those are kept off the profile unless they are explicitly pinned.
    """
    return bool(repo.get("description")) or bool(repo.get("topics")) or bool(repo.get("stargazers_count"))


def badge(label: str, message: str, color: str, logo: str | None = None) -> str:
    """Build a static Shields badge URL with every piece URL-encoded."""
    url = f"{BADGE_BASE}/{quote(label, safe='')}-{quote(message, safe='')}-{color}?style=flat-square"
    if logo:
        url += f"&logo={logo}&logoColor=white"
    return url


def fetch_account() -> dict:
    return github_json(f"/users/{username()}")


def fetch_repositories() -> tuple[list[dict], list[dict]]:
    """Return (featured repositories, every eligible repository)."""
    payload = github_json(f"/users/{username()}/repos?per_page=100&sort=pushed")
    if not isinstance(payload, list):
        raise RuntimeError("Unexpected payload shape for the repositories endpoint.")

    eligible = [
        repo
        for repo in payload
        if isinstance(repo, dict)
        and not repo.get("fork")
        and not repo.get("archived")
        and not repo.get("disabled")
        and not is_profile_repo(repo.get("full_name", ""))
    ]

    # Curated first, in the configured order; then the freshest repositories
    # that carry enough information to be worth showing a visitor.
    by_name = {repo.get("name", ""): repo for repo in eligible}
    featured: list[dict] = []
    for name in pinned_names():
        repo = by_name.get(name)
        if repo:
            featured.append(repo)

    featured_names = {repo.get("name") for repo in featured}
    fresh = [
        repo
        for repo in sorted(eligible, key=lambda r: r.get("pushed_at") or "", reverse=True)
        if repo.get("name") not in featured_names and has_signal(repo)
    ]
    featured.extend(fresh[: max(0, FEATURED_COUNT - len(featured))])
    return featured[:FEATURED_COUNT], eligible


def totals(repos: list[dict]) -> tuple[int, int]:
    stars = sum(int(repo.get("stargazers_count") or 0) for repo in repos)
    forks = sum(int(repo.get("forks_count") or 0) for repo in repos)
    return stars, forks


def stack_chips(repo: dict, limit: int = 2) -> str:
    """Render the language and topics as a short row of inline-code chips.

    GitHub reports ``language`` as null for repositories it cannot classify
    (shell-script and hardware projects, typically). Topics are the better
    signal there, so fall back to them before giving up.
    """
    chips: list[str] = []
    language = repo.get("language")
    if language:
        chips.append(language)
    for topic in repo.get("topics") or []:
        topic = topic.replace("-", " ")
        if topic.lower() not in {chip.lower() for chip in chips}:
            chips.append(topic)
        if len(chips) == limit:
            break
    if not chips:
        return "—"
    return " ".join(f"`{escape_cell(chip)}`" for chip in chips[:limit])


def render_repos(repos: list[dict]) -> str:
    if not repos:
        return "- *No public repositories to feature yet.*"

    lines = [
        "| Repository | Stack | ★ | ⑂ | Pushed |",
        "| :-- | :-- | --: | --: | :-- |",
    ]
    for repo in repos:
        name = repo.get("name", "repository")
        url = repo.get("html_url", f"https://github.com/{username()}/{name}")
        description = truncate(repo.get("description") or "No description yet.")
        stars = repo.get("stargazers_count") or 0
        forks = repo.get("forks_count") or 0
        pushed = iso_date(repo.get("pushed_at"))

        lines.append(
            f"| [**{escape_cell(name)}**]({url})<br><sub>{escape_cell(description)}</sub> "
            f"| {stack_chips(repo)} | {stars} | {forks} | {pushed} |"
        )
    return "\n".join(lines)


def count_languages(repos: list[dict]) -> int:
    """Number of distinct primary languages across the eligible repositories."""
    return len({repo.get("language") for repo in repos if repo.get("language")})


def render_counters(
    stars: int, forks: int, public_repos: int, followers: int, languages: int
) -> str:
    refreshed = datetime.now(timezone.utc).strftime("%b %d, %Y")
    rows = [
        ("Repositories", public_repos, "0969DA", "https://github.com/ccsalman545?tab=repositories"),
        ("Languages", languages, "58A6FF", "https://github.com/ccsalman545?tab=repositories"),
        ("Followers", followers, "24292F", "https://github.com/ccsalman545?tab=followers"),
        ("Stars", stars, "6E40C9", "https://github.com/ccsalman545?tab=repositories"),
        ("Refreshed", refreshed, "0F766E", "https://github.com/ccsalman545/ccsalman545/actions"),
    ]
    badges = " ".join(
        f"[![{label}]({badge(label, str(value), color, 'github' if label != 'Refreshed' else None)})]({link})"
        for label, value, color, link in rows
    )
    return f'<div align="center">\n\n{badges}\n\n</div>'


def endpoint(label: str, message: str, color: str, named_logo: str | None = None) -> dict:
    """Shields.io endpoint schema payload."""
    payload = {
        "schemaVersion": 1,
        "label": label,
        "message": str(message),
        "color": color,
        "cacheSeconds": 43200,
        "style": "flat-square",
    }
    if named_logo:
        payload["namedLogo"] = named_logo
    return payload


def write_data(
    stars: int, forks: int, public_repos: int, followers: int, languages: int
) -> bool:
    """Publish Shields endpoint JSON files; return True when anything changed."""
    refreshed = datetime.now(timezone.utc).strftime("%b %d, %Y")
    files = {
        "stars.json": endpoint("stars", stars, "6e40c9", "github"),
        "forks.json": endpoint("forks", forks, "0f766e", "github"),
        "repos.json": endpoint("repositories", public_repos, "0969da", "github"),
        "followers.json": endpoint("followers", followers, "24292f", "github"),
        "languages.json": endpoint("languages", languages, "58a6ff"),
        "updated.json": endpoint("profile updated", refreshed, "0f766e"),
    }

    changed = False
    for filename, payload in files.items():
        target = DATA_DIR / filename
        rendered = json.dumps(payload, indent=2) + "\n"
        if target.exists() and target.read_text(encoding="utf-8") == rendered:
            continue
        target.write_text(rendered, encoding="utf-8")
        changed = True
    return changed


def main() -> int:
    try:
        account = fetch_account()
        repos, eligible = fetch_repositories()
    except (OSError, RuntimeError, ValueError) as error:
        print(f"::error::{error}")
        return 1

    public_repos = int(account.get("public_repos") or 0)
    followers = int(account.get("followers") or 0)
    stars, forks = totals(repos)
    languages = count_languages(eligible)

    try:
        # Apply both marker edits in one pass so the two blocks stay consistent.
        content = README.read_text(encoding="utf-8")
        content = replace_block(content, REPOS_START, REPOS_END, render_repos(repos))
        content = replace_block(
            content,
            COUNTERS_START,
            COUNTERS_END,
            render_counters(stars, forks, public_repos, followers, languages),
        )
        readme_changed = content != README.read_text(encoding="utf-8")
        if readme_changed:
            README.write_text(content, encoding="utf-8")
    except (OSError, RuntimeError) as error:
        print(f"::error::{error}")
        return 1

    DATA_DIR.mkdir(exist_ok=True)
    data_changed = write_data(stars, forks, public_repos, followers, languages)

    print(
        f"Featured {len(repos)} repositories · {stars} stars · {forks} forks · {languages} languages · "
        f"{public_repos} public repos · readme {'updated' if readme_changed else 'unchanged'} · "
        f"data {'updated' if data_changed else 'unchanged'}"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
