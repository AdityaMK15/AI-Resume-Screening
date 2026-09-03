import logging
import os

from dotenv import load_dotenv
from openai import OpenAI
from pydantic import BaseModel, Field
from .config import (
    LLM_MODEL_NAME,
    OPENAI_API_KEY_ENV,
    USE_LLM_EXTRACTION,
    USE_MOCK_LLM,
)
from .models import CandidateProfile

logger = logging.getLogger(__name__)

load_dotenv()


class LLMProjectAnalysis(BaseModel):
    project_summary: str = ""
    meaningful_ai_evidence: list[str] = Field(default_factory=list)
    technologies: list[str] = Field(default_factory=list)
    strengths: list[str] = Field(default_factory=list)
    concerns: list[str] = Field(default_factory=list)
    is_thin_wrapper: bool = False


def _get_client() -> OpenAI | None:
    api_key = os.getenv(OPENAI_API_KEY_ENV)

    if not api_key:
        logger.warning("OPENAI_API_KEY is not configured")
        return None

    try:
        return OpenAI(api_key=api_key)
    except Exception as exc:
        logger.warning("Could not initialize OpenAI client: %s", exc)
        return None


def analyze_candidate_with_llm(
    candidate: CandidateProfile,
) -> LLMProjectAnalysis | None:

    # Development/testing mode.
    # This does not call the OpenAI API.
    if USE_MOCK_LLM:
        return LLMProjectAnalysis(
            project_summary="Candidate demonstrated an AI project using Python, RAG and LangChain.",
            meaningful_ai_evidence=[
                "Used RAG for information retrieval",
                "Used embeddings and vector search",
                "Used LangChain for AI workflow",
            ],
            technologies=[
                "Python",
                "LangChain",
                "RAG",
                "Embeddings",
                "Vector Search",
            ],
            strengths=[
                "Demonstrates meaningful AI project experience",
                "Uses retrieval and embeddings",
            ],
            concerns=[],
            is_thin_wrapper=False,
        )

    # Don't call the API when LLM is disabled.
    if not USE_LLM_EXTRACTION:
        print("LLM DISABLED: USE_LLM_EXTRACTION is false")
        return None

    client = _get_client()

    if client is None:
        print("LLM CLIENT ERROR: OpenAI client could not be created")
        return None

    projects_text = []

    for project in candidate.projects:
        projects_text.append(
            f"""
Project Title: {project.title}
Description: {project.description}
Technologies: {", ".join(project.technologies)}
"""
        )

    if not projects_text:
        return LLMProjectAnalysis(
            project_summary="No project information available.",
            concerns=["No projects were extracted from the resume."],
        )

    prompt = f"""
Analyze the candidate's projects for an AI/software engineering role.

Candidate:
{candidate.name}

Skills:
{", ".join(candidate.skills)}

Projects:
{"".join(projects_text)}

Focus on:
1. Meaningful AI, LLM, RAG, or agentic work.
2. Actual project depth and implementation evidence.
3. Technologies used.
4. Strengths.
5. Concerns such as simple API wrappers or tutorial-style projects.

Do not invent information that is not present in the resume.
Return only information supported by the provided resume.
"""

    try:
        response = client.responses.parse(
            model=LLM_MODEL_NAME,
            input=[
                {
                    "role": "system",
                    "content": (
                        "You are a technical resume screening assistant. "
                        "Analyze only the evidence provided."
                    ),
                },
                {
                    "role": "user",
                    "content": prompt,
                },
            ],
            text_format=LLMProjectAnalysis,
        )

        result = response.output_parsed

        if result is None:
            logger.warning("LLM returned no structured result")
            return None

        return result

    except Exception as exc:
        print("LLM ERROR:", exc)
        return None