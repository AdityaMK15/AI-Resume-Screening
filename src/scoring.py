from .config import (
    AI_SIGNALS,
    PYTHON_SIGNALS,
    PYTHON_BACKEND_KEYWORDS,
    CLOUD_FULLSTACK_KEYWORDS,
    ENGINEERING_DEPTH_KEYWORDS,
    AI_DEPTH_POSITIVE_SIGNALS,
    AI_THIN_WRAPPER_SIGNALS,
)

from .models import CandidateProfile, EligibilityResult, ScoreBreakdown


def _normalise(text: str) -> str:
    """Convert text to lowercase for easier matching."""
    return text.lower().strip()


def _matches(text: str, signals) -> list[str]:
    """Return configured signals found in the candidate evidence."""
    text = _normalise(text)

    matched = []

    for signal in signals:
        if _normalise(signal) in text:
            matched.append(signal)

    return matched


def _build_evidence_text(profile: CandidateProfile) -> str:
    """Combine skills and project information into one searchable text."""
    parts = list(profile.skills)

    for project in profile.projects:
        parts.append(project.title)
        parts.append(project.description)
        parts.extend(project.technologies)

    return " ".join(parts)


def _score_ai_project_depth(
    profile: CandidateProfile,
    evidence_text: str,
) -> tuple[int, list[str], list[str]]:
    """
    Score AI / Agentic / RAG project depth out of 40.
    """

    ai_matches = _matches(evidence_text, AI_SIGNALS)

    strengths = []
    concerns = []

    if not ai_matches:
        return (
            0,
            strengths,
            ["No meaningful AI/LLM/RAG/agentic project evidence"],
        )

    # Basic AI evidence.
    score = min(15, len(ai_matches) * 3)

    # Find AI-related projects.
    ai_projects = []

    for project in profile.projects:

        project_text = " ".join(
            [
                project.title,
                project.description,
                *project.technologies,
            ]
        )

        if _matches(project_text, AI_SIGNALS):
            ai_projects.append(project)

    # Reward AI implementation inside actual projects.
    if ai_projects:
        score += 15

        strengths.append(
            f"AI evidence demonstrated in {len(ai_projects)} project(s)"
        )

    # Reward deeper AI project implementation.
    for project in ai_projects:

        project_text = " ".join(
            [
                project.title,
                project.description,
            ]
        )

        depth_matches = _matches(
            project_text,
            AI_DEPTH_POSITIVE_SIGNALS,
        )

        if depth_matches:
            score += min(10, len(depth_matches) * 2)

            strengths.append(
                "AI project depth: "
                + ", ".join(depth_matches[:5])
            )

    # Penalize thin AI/API-wrapper projects.
    thin_matches = _matches(
        evidence_text,
        AI_THIN_WRAPPER_SIGNALS,
    )

    if thin_matches:
        score -= min(15, len(thin_matches) * 5)

        concerns.append(
            "AI evidence appears thin or wrapper/API focused"
        )

    score = max(0, min(40, score))

    strengths.append(
        "AI signals: "
        + ", ".join(ai_matches[:6])
    )

    return score, strengths, concerns


def _score_python_backend(
    profile: CandidateProfile,
    evidence_text: str,
) -> tuple[int, list[str]]:
    """
    Score Python / Backend strength out of 30.
    """

    python_matches = _matches(
        evidence_text,
        PYTHON_SIGNALS,
    )

    backend_matches = _matches(
        evidence_text,
        PYTHON_BACKEND_KEYWORDS,
    )

    score = 0

    # Python evidence.
    score += min(15, len(python_matches) * 5)

    # Backend evidence.
    score += min(10, len(backend_matches) * 3)

    # Reward actual project evidence.
    backend_projects = 0

    for project in profile.projects:

        project_text = " ".join(
            [
                project.title,
                project.description,
                *project.technologies,
            ]
        )

        project_matches = _matches(
            project_text,
            list(PYTHON_SIGNALS)
            + list(PYTHON_BACKEND_KEYWORDS),
        )

        if project_matches:
            backend_projects += 1

    score += min(5, backend_projects * 2)

    score = min(30, score)

    strengths = []

    if python_matches:
        strengths.append(
            "Python evidence: "
            + ", ".join(python_matches)
        )

    if backend_matches:
        strengths.append(
            "Backend evidence: "
            + ", ".join(backend_matches[:5])
        )

    return score, strengths


def _score_cloud_fullstack(
    evidence_text: str,
) -> tuple[int, list[str]]:
    """
    Score Cloud / Deployment / Full-stack strength out of 15.
    """

    matches = _matches(
        evidence_text,
        CLOUD_FULLSTACK_KEYWORDS,
    )

    score = min(15, len(matches) * 3)

    strengths = []

    if matches:
        strengths.append(
            "Cloud/full-stack evidence: "
            + ", ".join(matches[:6])
        )

    return score, strengths


def _score_engineering_depth(
    evidence_text: str,
) -> tuple[int, list[str]]:
    """
    Score engineering depth out of 5.
    """

    matches = _matches(
        evidence_text,
        ENGINEERING_DEPTH_KEYWORDS,
    )

    score = min(5, len(matches))

    strengths = []

    if matches:
        strengths.append(
            "Engineering practices: "
            + ", ".join(matches[:5])
        )

    return score, strengths


def score_candidate(
    profile: CandidateProfile,
    eligibility: EligibilityResult,
) -> ScoreBreakdown:
    """
    Calculate a deterministic candidate score out of 100.

    GitHub is 0 at this stage.
    Step 5 will add the GitHub score.
    """

    # Do not score rejected candidates.
    if not eligibility.eligible:
        return ScoreBreakdown(
            ai_project_depth=0,
            python_backend=0,
            cloud_fullstack=0,
            github=0,
            engineering_depth=0,
            total_score=0,
            strengths=[],
            concerns=[
                "Candidate is not eligible for scoring"
            ],
        )

    evidence_text = _build_evidence_text(profile)

    strengths: list[str] = []
    concerns: list[str] = []

    # AI / Agentic / RAG score.
    ai_score, ai_strengths, ai_concerns = (
        _score_ai_project_depth(
            profile,
            evidence_text,
        )
    )

    # Python / Backend score.
    python_score, python_strengths = (
        _score_python_backend(
            profile,
            evidence_text,
        )
    )

    # Cloud / Full-stack score.
    cloud_score, cloud_strengths = (
        _score_cloud_fullstack(
            evidence_text,
        )
    )

    # Engineering depth score.
    engineering_score, engineering_strengths = (
        _score_engineering_depth(
            evidence_text,
        )
    )

    strengths.extend(ai_strengths)
    strengths.extend(python_strengths)
    strengths.extend(cloud_strengths)
    strengths.extend(engineering_strengths)

    concerns.extend(ai_concerns)

    # GitHub will be implemented in Step 5.
    github_score = 0

    # Final score.
    total_score = (
        ai_score
        + python_score
        + cloud_score
        + github_score
        + engineering_score
    )

    total_score = max(0, min(100, total_score))

    return ScoreBreakdown(
        ai_project_depth=ai_score,
        python_backend=python_score,
        cloud_fullstack=cloud_score,
        github=github_score,
        engineering_depth=engineering_score,
        total_score=total_score,
        strengths=strengths,
        concerns=concerns,
    )