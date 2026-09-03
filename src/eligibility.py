from .config import AI_SIGNALS, PYTHON_SIGNALS
from .models import CandidateProfile, EligibilityResult


def _normalise(text: str) -> str:
    """Convert text to lowercase for easier matching."""
    return text.lower().strip()


def _find_matching_signals(text: str, signals: list[str]) -> list[str]:
    """Find configured signals present in the given text."""
    text_normalised = _normalise(text)

    matched = []

    for signal in signals:
        if _normalise(signal) in text_normalised:
            matched.append(signal)

    return matched


def check_eligibility(profile: CandidateProfile) -> EligibilityResult:
    """
    Check whether a candidate satisfies the mandatory requirements.

    A candidate must have:
    1. Python evidence
    2. Meaningful AI/LLM/RAG/agentic evidence
    """

    rejection_reasons: list[str] = []
    matched_skills: list[str] = []

    # Combine skills, project technologies and project descriptions.
    evidence_parts = []

    evidence_parts.extend(profile.skills)

    for project in profile.projects:
        evidence_parts.append(project.title)
        evidence_parts.append(project.description)
        evidence_parts.extend(project.technologies)

    evidence_text = " ".join(evidence_parts)

    # Check Python evidence.
    python_matches = _find_matching_signals(
        evidence_text,
        PYTHON_SIGNALS,
    )

    # Check AI evidence.
    ai_matches = _find_matching_signals(
        evidence_text,
        AI_SIGNALS,
    )

    # Remove duplicates while preserving order.
    for signal in python_matches + ai_matches:
        if signal not in matched_skills:
            matched_skills.append(signal)

    has_python = len(python_matches) > 0
    has_ai = len(ai_matches) > 0

    # Apply mandatory eligibility rules.
    if not has_python:
        rejection_reasons.append(
            "Missing Python evidence"
        )

    if not has_ai:
        rejection_reasons.append(
            "Missing meaningful AI/LLM/RAG/agentic evidence"
        )

    eligible = has_python and has_ai

    return EligibilityResult(
        candidate=profile,
        eligible=eligible,
        rejection_reasons=rejection_reasons,
        matched_skills=matched_skills,
    )