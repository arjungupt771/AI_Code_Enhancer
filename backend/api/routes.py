"""HTTP routes for the local AI Code Enhancer API."""

import logging
from pathlib import Path
from typing import Annotated

from fastapi import (
    APIRouter,
    File,
    Form,
    HTTPException,
    UploadFile,
)

from backend.analyzers import (
    create_hybrid_analyzer,
    deduplicate_findings,
    static_finding_to_review_issue,
)
from backend.core.file_validation import (
    read_source_file,
    validate_file_count,
)
from backend.core_config import (
    DEFAULT_MODEL,
    GEMINI_API_KEY,
)
from backend.repository import RepositoryAnalyzer
from backend.schemas import (
    FixRequest,
    ReviewResponse,
)
from backend.scoring import calculate_quality_score
from backend.services.llm import review_code_with_llm


logger = logging.getLogger(__name__)

router = APIRouter()

STATIC_ANALYZER = create_hybrid_analyzer()
REPOSITORY_ANALYZER = RepositoryAnalyzer()


def validate_api_configuration() -> None:
    if not GEMINI_API_KEY:
        raise HTTPException(
            status_code=500,
            detail=(
                "AI service is not configured. "
                "Set GEMINI_API_KEY in the local .env file."
            ),
        )


@router.get("/health")
async def health_check() -> dict[str, str]:
    return {
        "status": "ok",
        "service": "AI Code Enhancer",
    }


@router.post(
    "/review-code",
    response_model=ReviewResponse,
)
async def review_code(
    files: Annotated[
        list[UploadFile],
        File(...),
    ],
    file_paths: Annotated[
        list[str] | None,
        Form(),
    ] = None,
    language: Annotated[
        str,
        Form(...),
    ] = "",
    model: Annotated[
        str,
        Form(),
    ] = DEFAULT_MODEL,
) -> ReviewResponse:

    validate_api_configuration()

    if not files:
        raise HTTPException(
            status_code=400,
            detail=(
                "At least one source file "
                "is required."
            ),
        )

    if not language.strip():
        raise HTTPException(
            status_code=400,
            detail="Programming language is required.",
        )

    validate_file_count(files)

    # New frontend requests provide explicit repository
    # relative paths. Older requests/tests may not, so
    # fall back to the uploaded filename.
    if file_paths is not None:
        if len(file_paths) != len(files):
            raise HTTPException(
                status_code=400,
                detail=(
                    "Each uploaded file must have "
                    "exactly one relative path."
                ),
            )
    else:
        file_paths = [
            uploaded_file.filename or ""
            for uploaded_file in files
        ]

    all_code: dict[str, str] = {}
    static_files: list[tuple[Path, str]] = []

    for uploaded_file, requested_path in zip(
        files,
        file_paths,
    ):
        filename, content = await read_source_file(
            uploaded_file
        )

        # Use the explicitly supplied repository path
        # when available, while keeping the existing
        # uploaded-file validation intact.
        path_to_analyze = (
            requested_path.strip()
            or filename
        )

        try:
            repository_result = (
                REPOSITORY_ANALYZER.analyze(
                    [
                        (
                            Path(path_to_analyze),
                            content,
                        )
                    ]
                )
            )
        except ValueError as exc:
            raise HTTPException(
                status_code=400,
                detail=str(exc),
            ) from exc

        if not repository_result.files:
            raise HTTPException(
                status_code=400,
                detail=(
                    "Unsupported or invalid file path "
                    f"'{path_to_analyze}'."
                ),
            )

        normalized_path = (
            repository_result.files[0]
            .path
            .as_posix()
        )

        if normalized_path in all_code:
            raise HTTPException(
                status_code=400,
                detail=(
                    f"Duplicate file "
                    f"'{normalized_path}'."
                ),
            )

        all_code[normalized_path] = content

        static_files.append(
            (
                Path(normalized_path),
                content,
            )
        )

    try:
        # Build the repository-level representation.
        repository_result = (
            REPOSITORY_ANALYZER.analyze(
                static_files
            )
        )

        repository_files = [
            (
                repository_file.path,
                repository_file.content,
            )
            for repository_file
            in repository_result.files
        ]

        # Run static analysis across the repository.
        static_result = (
            STATIC_ANALYZER.analyze_files(
                repository_files
            )
        )

        static_findings = deduplicate_findings(
            static_result.static_findings
        )

        static_issues = [
            static_finding_to_review_issue(
                finding
            )
            for finding in static_findings
        ]

        # Run AI review across all analyzed repository
        # files while preserving their relative paths.
        ai_code = {
            repository_file.path.as_posix():
                repository_file.content
            for repository_file
            in repository_result.files
        }

        ai_response = review_code_with_llm(
            ai_code,
            language.strip(),
            mode="review",
            model_name=(
                model.strip()
                or DEFAULT_MODEL
            ),
        )

        # Combine static and AI findings.
        combined_issues = (
            static_issues +
            ai_response.issues
        )

        # Calculate repository-wide quality score.
        quality = calculate_quality_score(
            combined_issues
        )

        # Identify files containing issues.
        issue_files = set()

        for issue in combined_issues:
            if isinstance(issue, dict):
                file_path = issue.get(
                    "file_path"
                )
            else:
                file_path = issue.file_path

            if file_path:
                issue_files.add(file_path)

        repository_summary = {
            "total_files": (
                repository_result.total_files
            ),
            "analyzed_files": (
                repository_result.supported_files
            ),
            "files_with_issues": len(
                issue_files
            ),
            "total_issues": len(
                combined_issues
            ),
            "languages": (
                repository_result.language_counts
            ),
            "extensions": (
                repository_result.extension_counts
            ),
            "analyzed_paths": (
                repository_result.analyzed_paths
            ),
        }

        return ReviewResponse(
            issues=combined_issues,
            summary=ai_response.summary,
            quality_score={
                "overall": quality.overall,
                "categories": {
                    category: {
                        "score": score,
                        "issues": (
                            quality.category_counts.get(
                                category,
                                0,
                            )
                        ),
                    }
                    for category, score
                    in quality.category_scores.items()
                },
                "files": {
                    file_path: {
                        "score": score,
                        "issues": sum(
                            1
                            for issue
                            in combined_issues
                            if (
                                issue.get(
                                    "file_path"
                                )
                                if isinstance(
                                    issue,
                                    dict,
                                )
                                else issue.file_path
                            ) == file_path
                        ),
                    }
                    for file_path, score
                    in quality.file_scores.items()
                },
                "severity_counts": (
                    quality.severity_counts
                ),
                "total_issues": (
                    quality.total_issues
                ),
            },
            repository=repository_summary,
        )

    except HTTPException:
        raise

    except Exception as exc:
        logger.exception(
            "Code review failed"
        )

        raise HTTPException(
            status_code=502,
            detail=(
                "Code review failed. "
                "Check the local AI configuration "
                "and try again."
            ),
        ) from exc


@router.post("/fix-code")
async def fix_code(
    request: FixRequest,
) -> dict[str, str]:

    validate_api_configuration()

    try:
        fixed_code = review_code_with_llm(
            request.code,
            request.language,
            mode="fix",
            issues=request.issues,
            model_name=(
                request.model
                or DEFAULT_MODEL
            ),
        )

    except Exception as exc:
        logger.exception(
            "Code fix generation failed"
        )

        raise HTTPException(
            status_code=502,
            detail=(
                "Code fix generation failed. "
                "Check the local AI configuration "
                "and try again."
            ),
        ) from exc

    return {
        "fixed_code": (
            fixed_code
            if isinstance(fixed_code, str)
            else ""
        )
    }