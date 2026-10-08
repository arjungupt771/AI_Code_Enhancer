

import difflib
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
from backend.architecture import (
    ArchitectureAnalyzer,
)
from backend.core_config import (
    DEFAULT_MODEL,
    DEFAULT_GROQ_MODEL,
    GEMINI_API_KEY,
    GROQ_API_KEY,
)
from backend.dependencies import (
    DependencyAnalyzer,
)
from backend.repository import (
    RepositoryAnalyzer,
)
from backend.schemas import (
    FixRequest,
    FixResponse,
    ReviewResponse,
)
from backend.scoring import (
    calculate_quality_score,
)
from backend.services.llm import (
    review_code_with_llm,
)


logger = logging.getLogger(__name__)

router = APIRouter()

STATIC_ANALYZER = create_hybrid_analyzer()

REPOSITORY_ANALYZER = RepositoryAnalyzer()

DEPENDENCY_ANALYZER = DependencyAnalyzer()
ARCHITECTURE_ANALYZER = ArchitectureAnalyzer()

def validate_api_configuration(provider: str) -> None:
    if provider == "gemini" and not GEMINI_API_KEY:
        raise HTTPException(
            status_code=500,
            detail="Gemini is not configured. Set GEMINI_API_KEY in the local .env file.",
        )
    if provider == "groq" and not GROQ_API_KEY:
        raise HTTPException(
            status_code=500,
            detail="Groq is not configured. Set GROQ_API_KEY in the local .env file.",
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
    provider: Annotated[
        str,
        Form(),
    ] = "gemini",
) -> ReviewResponse:

    provider = provider.strip().lower()
    if provider not in {"gemini", "groq"}:
        raise HTTPException(status_code=400, detail="Provider must be 'gemini' or 'groq'.")
    validate_api_configuration(provider)

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

    # New frontend requests provide explicit
    # repository-relative paths.
    #
    # Older requests/tests may not provide them,
    # so fall back to the uploaded filename.
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

    static_files: list[
        tuple[Path, str]
    ] = []

    for uploaded_file, requested_path in zip(
        files,
        file_paths,
    ):
        filename, content = await read_source_file(
            uploaded_file
        )

        # Use the explicitly supplied repository
        # path when available.
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
        # -------------------------------------------------
        # Repository-level analysis
        # -------------------------------------------------

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

        # -------------------------------------------------
        # Dependency analysis
        # -------------------------------------------------

        dependency_result = (
            DEPENDENCY_ANALYZER.analyze(
                repository_files
            )
        )

        dependency_summary = {
            "manifests": (
                dependency_result.manifests_found
            ),
            "dependencies": [
                {
                    "name": dependency.name,
                    "version_spec": (
                        dependency.version_spec
                    ),
                    "source_file": (
                        dependency.source_file
                    ),
                    "dependency_type": (
                        dependency.dependency_type
                    ),
                }
                for dependency
                in dependency_result.dependencies
            ],
            "total_dependencies": (
                dependency_result.dependency_count
            ),
            "dependency_types": (
                dependency_result
                .dependencies_by_type
            ),
        }


        architecture_result = (
            ARCHITECTURE_ANALYZER.analyze(
                repository_files
            )
        )

        architecture_summary = {
            "nodes": [
                {
                "id": node.id,
                "label": node.label,
                "node_type": node.node_type,
                "path": node.path,
                }
                for node in architecture_result.nodes
            ],

            "edges":[
                {
                    "source": edge.source,
                    "target": edge.target,
                    "edge_type": edge.edge_type,
                }
                for edge in architecture_result.edges
            ],
            "cycles": architecture_result.cycles,
            "total_nodes": architecture_result.total_nodes,
            "total_edges": architecture_result.total_edges,
            "cycle_count": architecture_result.cycle_count,
        }

        # -------------------------------------------------
        # Static analysis
        # -------------------------------------------------

        static_result = (
            STATIC_ANALYZER.analyze_files(
                repository_files
            )
        )

        static_findings = (
            deduplicate_findings(
                static_result.static_findings
            )
        )

        static_issues = [
            static_finding_to_review_issue(
                finding
            )
            for finding in static_findings
        ]

        # -------------------------------------------------
        # AI review
        # -------------------------------------------------

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
                or (DEFAULT_GROQ_MODEL if provider == "groq" else DEFAULT_MODEL)
            ),
            provider=provider,
        )

        # -------------------------------------------------
        # Combine findings
        # -------------------------------------------------

        combined_issues = (
            static_issues
            + ai_response.issues
        )

        # -------------------------------------------------
        # Quality scoring
        # -------------------------------------------------

        quality = calculate_quality_score(
            combined_issues
        )

        # -------------------------------------------------
        # Files containing issues
        # -------------------------------------------------

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

        # -------------------------------------------------
        # Repository summary
        # -------------------------------------------------

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

        # -------------------------------------------------
        # Final response
        # -------------------------------------------------

        return ReviewResponse(
            issues=combined_issues,
            architecture=architecture_summary,
            summary=ai_response.summary,

            quality_score={
                "overall": quality.overall,
                "risk_level": quality.risk_level,

                "categories": {
                    category: {
                        "score": score,
                        "issues": quality.category_counts.get(category, 0),
                    }
                    for category, score in quality.category_scores.items()
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
                                else (
                                    issue.file_path
                                )
                            )
                            == file_path
                        ),
                    }
                    for file_path, score
                    in quality
                    .file_scores
                    .items()
                },

                "severity_counts": (
                    quality.severity_counts
                ),

                "total_issues": (
                    quality.total_issues
                ),
            },

            repository=repository_summary,

            dependency_summary=(
                dependency_summary
            ),
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


@router.post("/fix-code", response_model=FixResponse)
async def fix_code(request: FixRequest) -> FixResponse:
    provider = request.provider
    validate_api_configuration(provider)

    model = request.model or (
        DEFAULT_GROQ_MODEL if provider == "groq" else DEFAULT_MODEL
    )

    try:
        fixed_code = review_code_with_llm(
            request.code,
            request.language,
            mode="fix",
            issues=request.issues,
            model_name=model,
            provider=provider,
        )
    except Exception as exc:
        logger.exception("Code fix generation failed")
        raise HTTPException(
            status_code=502,
            detail=(
                "Code fix generation failed. Check the selected AI provider "
                "configuration and try again."
            ),
        ) from exc

    if not isinstance(fixed_code, str) or not fixed_code.strip():
        raise HTTPException(status_code=502, detail="The AI provider returned an empty code fix.")

    patch_lines = list(
        difflib.unified_diff(
            request.code.splitlines(),
            fixed_code.splitlines(),
            fromfile="original",
            tofile="fixed",
            lineterm="",
        )
    )
    patch = "\n".join(patch_lines)
    additions = sum(1 for line in patch_lines if line.startswith("+") and not line.startswith("+++"))
    deletions = sum(1 for line in patch_lines if line.startswith("-") and not line.startswith("---"))

    return FixResponse(
        fixed_code=fixed_code,
        patch=patch,
        additions=additions,
        deletions=deletions,
        provider=provider,
        model=model,
    )
