from src.eligibility import check_eligibility
from src.models import CandidateProfile, ProjectEntry


def test_candidate_with_python_and_ai_is_eligible():
    candidate = CandidateProfile(
        name="Eligible Candidate",
        skills=["Python", "LangChain", "RAG"],
        projects=[
            ProjectEntry(
                title="AI Resume Analyzer",
                description="Built a RAG system using LangChain and embeddings.",
                technologies=["Python", "LangChain", "RAG"],
            )
        ],
    )

    result = check_eligibility(candidate)

    assert result.eligible is True
    assert "Python" in result.matched_skills
    assert any("RAG" in skill or "LangChain" in skill for skill in result.matched_skills)


def test_candidate_without_ai_is_rejected():
    candidate = CandidateProfile(
        name="Python Candidate",
        skills=["Python", "FastAPI"],
        projects=[
            ProjectEntry(
                title="Backend API",
                description="Built a REST API using Python and FastAPI.",
                technologies=["Python", "FastAPI"],
            )
        ],
    )

    result = check_eligibility(candidate)

    assert result.eligible is False
    assert any("AI" in reason for reason in result.rejection_reasons)


def test_candidate_without_python_is_rejected():
    candidate = CandidateProfile(
        name="AI Candidate",
        skills=["JavaScript", "LangChain", "RAG"],
        projects=[
            ProjectEntry(
                title="AI Chatbot",
                description="Built a chatbot using LangChain and RAG.",
                technologies=["LangChain", "RAG"],
            )
        ],
    )

    result = check_eligibility(candidate)

    assert result.eligible is False
    assert any("Python" in reason for reason in result.rejection_reasons)