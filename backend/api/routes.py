"""HTTP routes for the local AI Code Enhancer API."""

import logging
from pathlib import Path
from typing import Annotated
from backend.scoring import calculate_quality_score
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
from backend.schemas import (
    FixRequest,
    ReviewResponse,
)
from backend.services.llm import review_code_with_llm


logger = logging.getLogger(__name__)

router = APIRouter()

STATIC_ANALYZER = create_hybrid_analyzer()


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
    language: Annotated[
        str,
        Form(...),
    ],
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

    all_code: dict[str, str] = {}
    static_files: list[tuple[Path, str]] = []

    for uploaded_file in files:
        filename, content = await read_source_file(
            uploaded_file
        )

        if filename in all_code:
            raise HTTPException(
                status_code=400,
                detail=f"Duplicate file '{filename}'.",
            )

        all_code[filename] = content
        static_files.append(
            (Path(filename), content)
        )

    try:
        # Run static analysis
        static_result = STATIC_ANALYZER.analyze_files(
            static_files
        )

        static_findings = deduplicate_findings(
            static_result.static_findings
        )

        static_issues = [
            static_finding_to_review_issue(finding)
            for finding in static_findings
        ]

        # Run AI review
        ai_response = review_code_with_llm(
            all_code,
            language.strip(),
            mode="review",
            model_name=(
                model.strip()
                or DEFAULT_MODEL
            ),
        )

        # Combine findings
        combined_issues = (
            static_issues + ai_response.issues
        )
        quality = calculate_quality_score(combined_issues)

        return ReviewResponse(
            issues=combined_issues,
            summary=ai_response.summary,
        )

    except Exception as exc:
        logger.exception(
            "Code review failed"
        )
        raise



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