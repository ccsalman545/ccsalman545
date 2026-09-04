"""Shared helpers for the profile README generators.

Kept dependency-free on purpose: the workflows run on plain ``python3`` with no
install step, which keeps them fast and avoids supply-chain surface area.
"""

from __future__ import annotations

import json
import os
import re
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any
from urllib.error import HTTPError, URLError
from urllib.request import Request, urlopen

API_ROOT = "https://api.github.com"
USER_AGENT = "ccsalman545-profile-readme"
API_VERSION = "2022-11-28"

# Allow ``from profile_common import ...`` whether the script is run directly or
# imported as a module (sys.path only contains the script directory on direct runs).
sys.path.insert(0, str(Path(__file__).resolve().parent))


def username() -> str:
    """Return the profile account name, overridable for forks and testing."""
    return os.environ.get("PROFILE_USERNAME", "ccsalman545")


def is_profile_repo(name: str) -> bool:
    """True when ``name`` is the profile repository itself."""
    return name.strip().lower() == f"{username()}/{username()}".lower()


def github_json(path: str, *, timeout: int = 30) -> Any:
    """GET a JSON payload from the GitHub REST API.

    Uses the short-lived ``GITHUB_TOKEN`` when Actions provides one, which lifts
    the unauthenticated 60-requests-per-hour limit.
    """
    headers = {
        "Accept": "application/vnd.github+json",
        "User-Agent": USER_AGENT,
        "X-GitHub-Api-Version": API_VERSION,
    }
    token = os.environ.get("GITHUB_TOKEN")
    if token:
        headers["Authorization"] = f"Bearer {token}"

    request = Request(f"{API_ROOT}{path}", headers=headers)
    try:
        with urlopen(request, timeout=timeout) as response:  # nosec B310 - fixed API root
            return json.load(response)
    except HTTPError as error:  # pragma: no cover - network dependent
        raise RuntimeError(
            f"GitHub API returned {error.code} for {path}: {error.reason}"
        ) from error
    except (URLError, TimeoutError) as error:  # pragma: no cover - network dependent
        raise RuntimeError(f"Could not reach the GitHub API for {path}: {error}") from error


def iso_date(value: str | None, fmt: str = "%b %d, %Y") -> str:
    """Format a GitHub timestamp as a stable, human-readable UTC date."""
    if not value:
        return "unknown"
    try:
        moment = datetime.fromisoformat(value.replace("Z", "+00:00"))
    except ValueError:
        return value
    return moment.strftime(fmt)


def relative_day(value: str | None) -> str:
    """Return a short relative age such as ``today`` or ``12 days ago``."""
    if not value:
        return "recently"
    try:
        moment = datetime.fromisoformat(value.replace("Z", "+00:00"))
    except ValueError:
        return "recently"
    if moment.tzinfo is None:
        moment = moment.replace(tzinfo=timezone.utc)

    days = (datetime.now(timezone.utc) - moment).days
    if days <= 0:
        return "today"
    if days == 1:
        return "yesterday"
    if days < 30:
        return f"{days} days ago"
    if days < 60:
        return "last month"
    if days < 365:
        return f"{days // 30} months ago"
    years = days // 365
    return "last year" if years == 1 else f"{years} years ago"


def escape_cell(text: str) -> str:
    """Make arbitrary text safe to place inside a Markdown table cell."""
    return text.replace("\\", "\\\\").replace("|", "\\|").replace("\n", " ").strip()


def truncate(text: str, limit: int = 96) -> str:
    """Shorten text to ``limit`` characters without cutting a word in half."""
    cleaned = " ".join(text.split())
    if len(cleaned) <= limit:
        return cleaned
    return cleaned[: limit - 1].rsplit(" ", 1)[0].rstrip(",.;:") + "…"


def replace_block(content: str, start: str, end: str, body: str) -> str:
    """Swap the text between two HTML comment markers.

    Raises when the marker pair is missing so a typo fails the workflow loudly
    instead of silently appending a duplicate section.
    """
    pattern = re.compile(
        rf"({re.escape(start)})(.*?)(\n?{re.escape(end)})", re.DOTALL
    )
    replacement = f"{start}\n{body}\n{end}"
    updated, count = pattern.subn(replacement, content, count=1)
    if count != 1:
        raise RuntimeError(f"README markers {start!r} / {end!r} are missing or malformed.")
    return updated


def write_block(readme: Path, start: str, end: str, body: str) -> bool:
    """Rewrite one marker block; return True only when the file changed."""
    content = readme.read_text(encoding="utf-8")
    updated = replace_block(content, start, end, body)
    if updated == content:
        return False
    readme.write_text(updated, encoding="utf-8")
    return True
