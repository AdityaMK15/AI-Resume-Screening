import re

from .models import CandidateProfile, ProjectEntry, RawResume
from .config import AI_SIGNALS, PYTHON_SIGNALS


# Common technical skills that may appear in resumes.
KNOWN_SKILLS = sorted(
    set(
        PYTHON_SIGNALS
        + AI_SIGNALS
        + [
            "JavaScript",
            "Java",
            "C++",
            "C",
            "TypeScript",
            "Node.js",
            "Express.js",
            "React",
            "React.js",
            "MongoDB",
            "MySQL",
            "PostgreSQL",
            "SQL",
            "AWS",
            "Azure",
            "GCP",
            "Docker",
            "Kubernetes",
            "Git",
            "Linux",
            "REST",
            "RESTful APIs",
            "FastAPI",
            "Flask",
            "Django",
            "Spring Boot",
            "JWT",
            "Redis",
            "TensorFlow",
            "PyTorch",
            "Pandas",
            "NumPy",
        ]
    ),
    key=len,
    reverse=True,
)


SECTION_HEADERS = {
    "skills": [
        "technical skills",
        "skills",
        "technical expertise",
        "technologies",
        "tech stack",
        "core competencies",
    ],
    "projects": [
        "projects",
        "academic projects",
        "personal projects",
        "key projects",
        "project experience",
    ],
}


def _extract_email(text: str) -> str | None:
    """Extract an email address from resume text."""
    match = re.search(
        r"\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}\b",
        text,
    )

    return match.group(0) if match else None


def _extract_phone(text: str) -> str | None:
    """Extract a likely phone number."""
    matches = re.findall(
        r"(?<!\d)(?:\+?\d[\d\s().-]{8,}\d)(?!\d)",
        text,
    )

    if not matches:
        return None

    # Clean excessive spaces while preserving useful formatting.
    phone = re.sub(r"\s+", " ", matches[0]).strip()

    return phone


def _extract_github_url(text: str) -> str | None:
    """Extract a GitHub profile URL."""
    match = re.search(
        r"https?://(?:www\.)?github\.com/[A-Za-z0-9_.-]+/?",
        text,
        flags=re.IGNORECASE,
    )

    return match.group(0).rstrip("/") if match else None


def _extract_name(text: str) -> str:
    """
    Extract a likely candidate name.

    Most resumes place the candidate's name near the top.
    """
    lines = [line.strip() for line in text.splitlines() if line.strip()]

    if not lines:
        return "Unknown Candidate"

    # Ignore common headings that may appear at the beginning.
    ignored = {
        "resume",
        "curriculum vitae",
        "cv",
        "profile",
        "about me",
    }

    for line in lines[:10]:
        cleaned = re.sub(r"[^A-Za-z .'-]", "", line).strip()

        words = cleaned.split()

        if (
            cleaned.lower() not in ignored
            and 2 <= len(words) <= 5
            and all(word.replace("-", "").replace("'", "").isalpha()
                    for word in words)
        ):
            return cleaned

    return lines[0]


def _find_section_lines(text: str, section_type: str) -> list[str]:
    """Return lines belonging to a particular resume section."""

    lines = [line.strip() for line in text.splitlines() if line.strip()]

    headers = SECTION_HEADERS.get(section_type, [])

    start_index = None

    for index, line in enumerate(lines):
        normalized = line.lower().rstrip(":").strip()

        if normalized in headers:
            start_index = index + 1
            break

    if start_index is None:
        return []

    # Stop when another common section begins.
    all_headers = set(
        header
        for values in SECTION_HEADERS.values()
        for header in values
    )

    other_sections = {
        "education",
        "experience",
        "internship experience",
        "work experience",
        "certifications",
        "achievements",
        "achievements & extracurriculars",
        "extracurriculars",
        "contact",
        "summary",
        "objective",
    }

    section_lines = []

    for line in lines[start_index:]:
        normalized = line.lower().rstrip(":").strip()

        if normalized in all_headers or normalized in other_sections:
            break

        section_lines.append(line)

    return section_lines


def _extract_skills(text: str) -> list[str]:
    """Extract known technical skills from the resume."""

    # Prefer the skills section.
    skill_lines = _find_section_lines(text, "skills")

    # If a skills section isn't detected, search the whole resume.
    search_text = "\n".join(skill_lines) if skill_lines else text

    found_skills = []

    for skill in KNOWN_SKILLS:
        pattern = re.escape(skill)

        if re.search(
            rf"(?<![A-Za-z0-9+#.-]){pattern}(?![A-Za-z0-9+#.-])",
            search_text,
            flags=re.IGNORECASE,
        ):
            found_skills.append(skill)

    return found_skills


def _extract_projects(text: str) -> list[ProjectEntry]:
    """Extract project entries using project-section heuristics."""

    project_lines = _find_section_lines(text, "projects")

    if not project_lines:
        return []

    projects: list[ProjectEntry] = []

    current_title: str | None = None
    current_description: list[str] = []
    current_technologies: list[str] = []

    def save_current_project() -> None:
        nonlocal current_title
        nonlocal current_description
        nonlocal current_technologies

        if current_title:
            projects.append(
                ProjectEntry(
                    title=current_title,
                    description=" ".join(current_description).strip(),
                    technologies=current_technologies,
                )
            )

        current_title = None
        current_description = []
        current_technologies = []

    for line in project_lines:
        # Bullet points are normally descriptions.
        if line.startswith(("•", "-", "*")):
            description = line.lstrip("•-* ").strip()

            if current_title:
                current_description.append(description)

                for skill in KNOWN_SKILLS:
                    if re.search(
                        rf"(?<![A-Za-z0-9+#.-]){re.escape(skill)}"
                        rf"(?![A-Za-z0-9+#.-])",
                        description,
                        flags=re.IGNORECASE,
                    ):
                        if skill not in current_technologies:
                            current_technologies.append(skill)

            continue

        # A non-bullet line is treated as a possible project title.
        if current_title:
            save_current_project()

        current_title = line

    save_current_project()

    return projects


def extract_candidate_info(raw_resume: RawResume) -> CandidateProfile:
    """
    Extract structured candidate information from raw resume text.
    """

    text = raw_resume.raw_text or ""

    name = _extract_name(text)
    email = _extract_email(text)
    phone = _extract_phone(text)
    github_url = _extract_github_url(text)
    skills = _extract_skills(text)
    projects = _extract_projects(text)

    return CandidateProfile(
        name=name,
        email=email,
        phone=phone,
        skills=skills,
        projects=projects,
        github_url=github_url,
        raw_text=text,
    )