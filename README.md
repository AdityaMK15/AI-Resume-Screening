# AI Resume Screening & Ranking System

An AI-assisted resume screening system that processes PDF resumes, filters candidates based on Python and meaningful AI experience, scores eligible candidates, enriches them using GitHub data, and produces a ranked JSON shortlist.

## Features

- PDF resume ingestion using `pdfplumber`
- Structured candidate information extraction
- Hard eligibility filtering
- Deterministic 100-point scoring system
- GitHub profile enrichment
- LLM-based semantic project analysis
- Pydantic structured outputs
- Graceful handling of malformed resumes and API failures
- Duplicate resume detection
- JSON output
- Automated tests

## Project Architecture

```text
PDF Resumes
     |
     v
Ingestion
     |
     v
Candidate Extraction
     |
     v
Eligibility Filter
     |
     +--------> Rejected Candidates
     |
     v
Deterministic Scoring
     |
     v
GitHub Enrichment
     |
     v
LLM Project Analysis
     |
     v
Ranking
     |
     v
results.json