from .ingest import ingest_resumes
from .extract import extract_candidate_info
from .eligibility import check_eligibility
from .scoring import score_candidate
from .github_enrich import enrich_with_github
from .llm_adapter import analyze_candidate_with_llm


def process_resumes(input_dir: str) -> dict:
    """
    Run the complete resume screening pipeline.
    """

    # Step 1: Ingest resumes
    resumes, ingestion_summary = ingest_resumes(input_dir)

    candidates = []
    rejected_candidates = []

    for resume in resumes:

        # Skip unreadable resumes
        if not resume.parse_success:
            rejected_candidates.append({
                "filename": resume.filename,
                "name": None,
                "eligible": False,
                "rejection_reasons": [
                    resume.parse_error or "Resume could not be parsed"
                ],
            })
            continue

        # Step 2: Extract candidate information
        candidate = extract_candidate_info(resume)

        # Step 3: Check eligibility
        eligibility = check_eligibility(candidate)

        # Reject candidates who don't meet the hard requirements
        if not eligibility.eligible:
            rejected_candidates.append({
                "filename": resume.filename,
                "name": candidate.name,
                "eligible": False,
                "matched_skills": eligibility.matched_skills,
                "rejection_reasons": eligibility.rejection_reasons,
            })
            continue

        # Step 4: Deterministic scoring
        score = score_candidate(candidate, eligibility)

        # Step 5: GitHub enrichment
        github_result = enrich_with_github(candidate.github_url)

        # Step 6: LLM semantic analysis
        llm_result = analyze_candidate_with_llm(candidate)

        # Add GitHub score
        score.github = github_result.score

        # Recalculate total score
        score.total_score = (
            score.ai_project_depth
            + score.python_backend
            + score.cloud_fullstack
            + score.github
            + score.engineering_depth
        )

        # Add LLM information to strengths/concerns
        if llm_result:
            score.strengths.extend(llm_result.strengths)
            score.concerns.extend(llm_result.concerns)

        candidates.append({
            "filename": resume.filename,
            "name": candidate.name,
            "email": candidate.email,
            "github_url": candidate.github_url,
            "eligible": True,
            "total_score": score.total_score,
            "score_breakdown": {
                "ai_project_depth": score.ai_project_depth,
                "python_backend": score.python_backend,
                "cloud_fullstack": score.cloud_fullstack,
                "github": score.github,
                "engineering_depth": score.engineering_depth,
            },
            "matched_skills": eligibility.matched_skills,
            "project_summary": (
                llm_result.project_summary
                if llm_result
                else "No LLM analysis available."
            ),
            "github_summary": github_result.summary,
            "strengths": score.strengths,
            "concerns": score.concerns,
        })

    # Rank eligible candidates by total score
    candidates.sort(
        key=lambda candidate: candidate["total_score"],
        reverse=True,
    )

    # Add ranking
    for rank, candidate in enumerate(candidates, start=1):
        candidate["rank"] = rank

    # Batch summary
    batch_summary = {
        "total_resumes": ingestion_summary["total_files_found"],
        "successfully_parsed": ingestion_summary["successfully_parsed"],
        "eligible": len(candidates),
        "rejected": len(rejected_candidates),
        "failed_unreadable": ingestion_summary["failed"],
    }

    return {
        "ranked_candidates": candidates,
        "rejected_candidates": rejected_candidates,
        "batch_summary": batch_summary,
    }