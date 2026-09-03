import logging
import os
import re
from datetime import datetime, timedelta, timezone

import requests
from dotenv import load_dotenv

from .config import (
    GITHUB_ACTIVITY_DAYS,
    GITHUB_REQUEST_TIMEOUT,
    GITHUB_TOKEN_ENV,
)
from .models import GithubEnrichment


logger = logging.getLogger(__name__)

load_dotenv()

# Cache GitHub results so the same username is not requested repeatedly.
_GITHUB_CACHE: dict[str, GithubEnrichment] = {}


def _extract_username(github_url: str) -> str | None:
    """Extract GitHub username from a GitHub profile URL."""

    if not github_url:
        return None

    match = re.search(
        r"github\.com/([A-Za-z0-9-]+)",
        github_url,
        flags=re.IGNORECASE,
    )

    if not match:
        return None

    return match.group(1)


def _github_headers() -> dict[str, str]:
    """Build headers for GitHub API requests."""

    headers = {
        "Accept": "application/vnd.github+json",
        "User-Agent": "AI-Resume-Screening-System",
    }

    token = os.getenv(GITHUB_TOKEN_ENV)

    if token:
        headers["Authorization"] = f"Bearer {token}"

    return headers


def _make_request(url: str) -> requests.Response | None:
    """Make a fault-tolerant GitHub API request."""

    try:
        response = requests.get(
            url,
            headers=_github_headers(),
            timeout=GITHUB_REQUEST_TIMEOUT,
        )

        if response.status_code != 200:
            logger.warning(
                "GitHub API returned status %s for %s",
                response.status_code,
                url,
            )
            return None

        return response

    except requests.RequestException as exc:
        logger.warning(
            "GitHub API request failed: %s",
            exc,
        )
        return None


def _score_recent_activity(events: list[dict]) -> int:
    """Score recent GitHub activity from 0 to 5."""

    cutoff = datetime.now(timezone.utc) - timedelta(
        days=GITHUB_ACTIVITY_DAYS
    )

    recent_events = 0

    for event in events:
        created_at = event.get("created_at")

        if not created_at:
            continue

        try:
            event_time = datetime.fromisoformat(
                created_at.replace("Z", "+00:00")
            )

            if event_time >= cutoff:
                recent_events += 1

        except (ValueError, TypeError):
            continue

    if recent_events >= 10:
        return 5

    if recent_events >= 6:
        return 4

    if recent_events >= 3:
        return 3

    if recent_events >= 1:
        return 2

    return 0


def _is_relevant_repository(repository: dict) -> bool:
    """Check whether a repository appears relevant to software engineering."""

    language = (repository.get("language") or "").lower()
    description = (repository.get("description") or "").lower()
    name = (repository.get("name") or "").lower()

    topics = [
        str(topic).lower()
        for topic in repository.get("topics", [])
    ]

    relevance_signals = {
        "python",
        "javascript",
        "typescript",
        "java",
        "c++",
        "go",
        "rust",
        "ai",
        "machine-learning",
        "deep-learning",
        "llm",
        "rag",
        "langchain",
        "langgraph",
        "backend",
        "api",
        "fastapi",
        "django",
        "flask",
        "react",
        "node",
        "nodejs",
        "docker",
    }

    searchable_text = " ".join(
        [language, description, name, *topics]
    )

    return any(
        signal in searchable_text
        for signal in relevance_signals
    )


def _score_repositories(repositories: list[dict]) -> int:
    """Score maintained/relevant repositories from 0 to 5."""

    cutoff = datetime.now(timezone.utc) - timedelta(
        days=GITHUB_ACTIVITY_DAYS
    )

    maintained_count = 0
    relevant_count = 0

    for repository in repositories:
        updated_at = repository.get("updated_at")

        if updated_at:
            try:
                updated_time = datetime.fromisoformat(
                    updated_at.replace("Z", "+00:00")
                )

                if updated_time >= cutoff:
                    maintained_count += 1

            except (ValueError, TypeError):
                pass

        if _is_relevant_repository(repository):
            relevant_count += 1

    score = 0

    # Maintenance score: 0-3.
    if maintained_count >= 5:
        score += 3
    elif maintained_count >= 3:
        score += 2
    elif maintained_count >= 1:
        score += 1

    # Relevance score: 0-2.
    if relevant_count >= 3:
        score += 2
    elif relevant_count >= 1:
        score += 1

    return min(5, score)


def _safe_json_list(
    response: requests.Response | None,
    description: str,
) -> list[dict]:
    """Safely read a GitHub API response expected to contain a list."""

    if response is None:
        return []

    try:
        data = response.json()

        if isinstance(data, list):
            return data

        logger.warning(
            "Unexpected GitHub response for %s",
            description,
        )

    except ValueError:
        logger.warning(
            "Could not parse GitHub response for %s",
            description,
        )

    return []


def enrich_with_github(
    github_url: str | None,
) -> GithubEnrichment:
    """
    Enrich a candidate using public GitHub information.

    GitHub problems never cause the resume screening batch to fail.
    """

    # No GitHub URL.
    if not github_url:
        return GithubEnrichment(
            status="unavailable",
            score=0,
            summary="No GitHub profile provided",
        )

    username = _extract_username(github_url)

    if not username:
        return GithubEnrichment(
            status="invalid",
            score=0,
            summary="Invalid GitHub profile URL",
        )

    # Use cached result if available.
    if username in _GITHUB_CACHE:
        logger.info(
            "Using cached GitHub result for %s",
            username,
        )
        return _GITHUB_CACHE[username]

    # Check whether the GitHub user exists.
    user_response = _make_request(
        f"https://api.github.com/users/{username}"
    )

    if user_response is None:
        result = GithubEnrichment(
            status="unavailable",
            score=0,
            summary="GitHub profile could not be accessed",
        )

        _GITHUB_CACHE[username] = result

        return result

    # Get public repositories.
    repo_response = _make_request(
        f"https://api.github.com/users/{username}/repos"
        "?per_page=100&sort=updated"
    )

    repositories = _safe_json_list(
        repo_response,
        "repositories",
    )

    # Get public activity.
    events_response = _make_request(
        f"https://api.github.com/users/{username}/events/public"
        "?per_page=100"
    )

    events = _safe_json_list(
        events_response,
        "public events",
    )

    # Calculate the two GitHub components.
    activity_score = _score_recent_activity(events)

    repository_score = _score_repositories(
        repositories
    )

    total_score = min(
        10,
        activity_score + repository_score,
    )

    public_repositories = len(repositories)

    summary = (
        f"GitHub user '{username}' has "
        f"{public_repositories} public repositories. "
        f"Recent activity score: {activity_score}/5. "
        f"Maintained/relevant repository score: "
        f"{repository_score}/5."
    )

    result = GithubEnrichment(
        status="success",
        score=total_score,
        summary=summary,
    )

    _GITHUB_CACHE[username] = result

    logger.info(
        "GitHub enrichment completed for %s: %s/10",
        username,
        result.score,
    )

    return result