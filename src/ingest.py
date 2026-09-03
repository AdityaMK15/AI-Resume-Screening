import hashlib
import logging
from pathlib import Path

import pdfplumber

from .models import RawResume


logger = logging.getLogger(__name__)


def _calculate_file_hash(file_path: Path) -> str:
    """Calculate SHA-256 hash of a file."""
    sha256 = hashlib.sha256()

    with file_path.open("rb") as file:
        for chunk in iter(lambda: file.read(8192), b""):
            sha256.update(chunk)

    return sha256.hexdigest()


def _extract_pdf_text(file_path: Path) -> str:
    """Extract text from a PDF using pdfplumber."""
    text_parts = []

    with pdfplumber.open(file_path) as pdf:
        for page in pdf.pages:
            page_text = page.extract_text()

            if page_text:
                text_parts.append(page_text)

    return "\n".join(text_parts).strip()


def ingest_resumes(input_dir: str) -> tuple[list[RawResume], dict]:
    """
    Read and extract text from all PDF resumes in the input directory.

    Returns:
        tuple:
            - list of RawResume objects
            - summary dictionary
    """

    input_path = Path(input_dir)

    resumes: list[RawResume] = []

    # Used to detect identical files.
    seen_hashes: set[str] = set()

    # Used to detect duplicate filenames.
    seen_filenames: set[str] = set()

    total_files_found = 0
    skipped_files = 0
    successfully_parsed = 0
    failed = 0
    duplicates_skipped = 0

    if not input_path.exists():
        logger.error("Input directory does not exist: %s", input_dir)

        summary = {
            "total_files_found": 0,
            "successfully_parsed": 0,
            "failed": 0,
            "duplicates_skipped": 0,
            "skipped_non_pdf": 0,
        }

        return resumes, summary

    if not input_path.is_dir():
        logger.error("Input path is not a directory: %s", input_dir)

        summary = {
            "total_files_found": 0,
            "successfully_parsed": 0,
            "failed": 0,
            "duplicates_skipped": 0,
            "skipped_non_pdf": 0,
        }

        return resumes, summary

    # Walk through all files, including files inside subdirectories.
    for file_path in input_path.rglob("*"):

        if not file_path.is_file():
            continue

        total_files_found += 1

        # Skip non-PDF files.
        if file_path.suffix.lower() != ".pdf":
            skipped_files += 1
            logger.info("Skipping non-PDF file: %s", file_path.name)
            continue

        filename = file_path.name

        # Detect duplicate filename.
        if filename in seen_filenames:
            duplicates_skipped += 1

            resumes.append(
                RawResume(
                    filename=filename,
                    raw_text="",
                    parse_success=False,
                    parse_error="Duplicate filename",
                    is_duplicate=True,
                )
            )

            logger.warning(
                "Duplicate filename skipped: %s",
                filename,
            )

            continue

        seen_filenames.add(filename)

        # Calculate file hash to detect identical files.
        try:
            file_hash = _calculate_file_hash(file_path)
        except Exception as exc:
            failed += 1

            logger.exception(
                "Could not calculate hash for %s",
                file_path.name,
            )

            resumes.append(
                RawResume(
                    filename=filename,
                    raw_text="",
                    parse_success=False,
                    parse_error=f"Could not read file: {exc}",
                    is_duplicate=False,
                )
            )

            continue

        # Detect duplicate content.
        if file_hash in seen_hashes:
            duplicates_skipped += 1

            resumes.append(
                RawResume(
                    filename=filename,
                    raw_text="",
                    parse_success=False,
                    parse_error="Duplicate file content",
                    is_duplicate=True,
                )
            )

            logger.warning(
                "Duplicate file content skipped: %s",
                filename,
            )

            continue

        seen_hashes.add(file_hash)

        # Extract text from PDF.
        try:
            raw_text = _extract_pdf_text(file_path)

            # A PDF may open successfully but contain no extractable text.
            if not raw_text.strip():
                raise ValueError(
                    "PDF contains no extractable text"
                )

            resumes.append(
                RawResume(
                    filename=filename,
                    raw_text=raw_text,
                    parse_success=True,
                    parse_error=None,
                    is_duplicate=False,
                )
            )

            successfully_parsed += 1

            logger.info(
                "Successfully parsed: %s",
                filename,
            )

        except Exception as exc:
            failed += 1

            logger.exception(
                "Failed to parse PDF: %s",
                filename,
            )

            resumes.append(
                RawResume(
                    filename=filename,
                    raw_text="",
                    parse_success=False,
                    parse_error=str(exc),
                    is_duplicate=False,
                )
            )

    summary = {
        "total_files_found": total_files_found,
        "successfully_parsed": successfully_parsed,
        "failed": failed,
        "duplicates_skipped": duplicates_skipped,
        "skipped_non_pdf": skipped_files,
    }

    logger.info(
        "Ingestion complete: %s",
        summary,
    )

    return resumes, summary