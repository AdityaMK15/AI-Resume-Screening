from src.eligibility import check_eligibility
from src.models import CandidateProfile, ProjectEntry
from src.scoring import score_candidate


def create_eligible_candidate():
    return CandidateProfile(
        name="Test Candidate",
        skills=[
            "Python",
            "FastAPI",
            "LangChain",
            "RAG",
            "Docker",
        ],
        projects=[
            ProjectEntry(
                title="AI Resume Analyzer",
                description=(
                    "Built a RAG-based resume analyzer using Python, "
                    "LangChain, embeddings and vector search."
                ),
                technologies=[
                    "Python",
                    "FastAPI",
                    "LangChain",
                    "RAG",
                    "Docker",
                ],
            )
        ],
    )


def test_eligible_candidate_gets_score():
    candidate = create_eligible_candidate()

    eligibility = check_eligibility(candidate)
    score = score_candidate(candidate, eligibility)

    assert eligibility.eligible is True
    assert score.total_score > 0


def test_rejected_candidate_gets_zero_score():
    candidate = CandidateProfile(
        name="Python Only Candidate",
        skills=["Python", "FastAPI"],
        projects=[
            ProjectEntry(
                title="Backend API",
                description="Built a REST API using Python and FastAPI.",
                technologies=["Python", "FastAPI"],
            )
        ],
    )

    eligibility = check_eligibility(candidate)
    score = score_candidate(candidate, eligibility)

    assert eligibility.eligible is False
    assert score.total_score == 0


def test_score_is_within_100():
    candidate = create_eligible_candidate()

    eligibility = check_eligibility(candidate)
    score = score_candidate(candidate, eligibility)

    assert 0 <= score.total_score <= 100