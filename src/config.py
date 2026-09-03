"""
Application configuration for the AI Resume Screening system.

This module contains:
- Scoring weights
- Screening keywords
- API configuration
- Runtime settings

Secrets are never stored directly in this file.
Sensitive values are read from environment variables.
"""
import os
from dotenv import load_dotenv

load_dotenv()


# ---------------------------------------------------------------------------
# General application settings
# ---------------------------------------------------------------------------

APP_NAME = "AI Resume Screening System"


# ---------------------------------------------------------------------------
# LLM configuration
# ---------------------------------------------------------------------------

LLM_MODEL_NAME = os.getenv("LLM_MODEL_NAME", "gpt-4o-mini")

USE_LLM_EXTRACTION = os.getenv(
    "USE_LLM_EXTRACTION",
    "false",
).lower() == "true"
USE_MOCK_LLM = os.getenv("USE_MOCK_LLM", "false").lower() == "true"

OPENAI_API_KEY_ENV = "OPENAI_API_KEY"


# ---------------------------------------------------------------------------
# GitHub configuration
# ---------------------------------------------------------------------------

GITHUB_TOKEN_ENV = "GITHUB_TOKEN"

GITHUB_REQUEST_TIMEOUT = 5

GITHUB_ACTIVITY_DAYS = 90


# ---------------------------------------------------------------------------
# Candidate scoring weights
# ---------------------------------------------------------------------------

SCORING_WEIGHTS = {
    "ai_project_depth": 40,
    "python_backend": 30,
    "cloud_fullstack": 15,
    "github": 10,
    "engineering_depth": 5,
}


# ---------------------------------------------------------------------------
# Python evidence
# ---------------------------------------------------------------------------

PYTHON_EVIDENCE_KEYWORDS = {
    "python",
}


# ---------------------------------------------------------------------------
# AI / LLM / Agentic evidence
# ---------------------------------------------------------------------------

AI_EVIDENCE_KEYWORDS = {
    "langchain",
    "langgraph",
    "google adk",
    "llamaindex",
    "llama index",
    "rag",
    "retrieval augmented generation",
    "embeddings",
    "vector search",
    "vector database",
    "tool calling",
    "tool-calling",
    "multi-agent",
    "multi agent",
    "agentic",
    "ai agent",
    "llm",
    "large language model",
    "evaluation pipeline",
}


# ---------------------------------------------------------------------------
# Backend / engineering signals
# ---------------------------------------------------------------------------

PYTHON_BACKEND_KEYWORDS = {
    "python",
    "fastapi",
    "django",
    "flask",
    "asyncio",
    "async",
    "postgresql",
    "postgres",
    "redis",
}


CLOUD_FULLSTACK_KEYWORDS = {
    "gcp",
    "google cloud",
    "docker",
    "deployment",
    "deployed",
    "react",
    "next.js",
    "nextjs",
}


ENGINEERING_DEPTH_KEYWORDS = {
    "testing",
    "pytest",
    "unit test",
    "integration test",
    "architecture",
    "caching",
    "cache",
    "queue",
    "message queue",
    "observability",
    "logging",
    "monitoring",
    "concurrency",
    "failure handling",
    "error handling",
    "retry",
}


# ---------------------------------------------------------------------------
# Project-quality signals
# ---------------------------------------------------------------------------

AI_DEPTH_POSITIVE_SIGNALS = {
    "retrieval",
    "vector search",
    "embeddings",
    "tool calling",
    "tool-calling",
    "state management",
    "stateful",
    "orchestration",
    "evaluation",
    "evaluation pipeline",
    "reranking",
    "document processing",
    "workflow",
    "multi-agent",
    "multi agent",
}


AI_THIN_WRAPPER_SIGNALS = {
    "api call",
    "api-call",
    "simple chatbot",
    "basic chatbot",
    "called openai api",
    "called llm api",
    "llm api wrapper",
}


# ---------------------------------------------------------------------------
# Resume parsing section headings
# ---------------------------------------------------------------------------

SKILLS_SECTION_HEADERS = {
    "skills",
    "technical skills",
    "technical skill",
    "technologies",
    "technology",
    "tech stack",
    "technical expertise",
    "programming languages",
}


PROJECT_SECTION_HEADERS = {
    "projects",
    "project",
    "academic projects",
    "personal projects",
    "relevant projects",
    "selected projects",
}
PYTHON_SIGNALS = [
    "Python",
    "FastAPI",
    "Flask",
    "Django",
    "Django REST Framework",
    "Pandas",
    "NumPy",
]

AI_SIGNALS = [
    "LLM",
    "AI",
    "Artificial Intelligence",
    "RAG",
    "LangChain",
    "LangGraph",
    "LlamaIndex",
    "Google ADK",
    "embeddings",
    "vector search",
    "tool calling",
    "tool-calling",
    "multi-agent",
    "agents",
    "agentic",
    "PyTorch",
    "TensorFlow",
    "OpenAI",
]