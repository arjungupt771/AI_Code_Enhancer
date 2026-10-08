
from typing import Literal

from pydantic import (
    BaseModel,
    ConfigDict,
    Field,
    field_validator,
)


Severity = Literal[
    "info",
    "warning",
    "error",
]

Category = Literal[
    "security",
    "performance",
    "style",
    "bug",
]


class ReviewIssue(BaseModel):
    """A single code-review finding from AI or static analysis."""

    model_config = ConfigDict(
        extra="ignore"
    )

    source: Literal["ai", "static"] = "ai"

    tool: str | None = None

    rule_id: str | None = None

    severity: Severity

    category: Category

    message: str = Field(
        min_length=1,
        max_length=1000,
    )

    explanation: str | None = Field(
        default=None,
        max_length=3000,
    )

    score: float | None = Field(
        default=None,
        ge=0,
        le=1,
    )

    file_path: str | None = None

    line: int | None = Field(
        default=None,
        ge=1,
    )

    column: int | None = Field(
        default=None,
        ge=1,
    )

    suggestion: str | None = None

    @field_validator(
        "message",
        "explanation",
    )
    @classmethod
    def normalize_text(
        cls,
        value: str | None,
    ) -> str | None:
        return value.strip() if value else value



class CategoryScore(BaseModel):
    score: int = Field(ge=0, le=100)
    issues: int = Field(ge=0)


class FileScore(BaseModel):
    score: int = Field(ge=0, le=100)
    issues: int = Field(ge=0)


class QualityScoreResponse(BaseModel):
    overall: int = Field(ge=0, le=100)
    categories: dict[str, CategoryScore] = Field(
        default_factory=dict
    )
    files: dict[str, FileScore] = Field(
        default_factory=dict
    )
    severity_counts: dict[str, int] = Field(
        default_factory=dict
    )
    total_issues: int = Field(ge=0)

class DependencyInfo(BaseModel):
    """Dependency information returned by repository analysis."""

    name: str
    version_spec: str | None = None
    source_file: str
    dependency_type: str


class DependencySummary(BaseModel):
    """Repository dependency summary."""

    manifests: list[str] = Field(
        default_factory=list
    )

    dependencies: list[DependencyInfo] = Field(
        default_factory=list
    )

    total_dependencies: int = Field(
        ge=0
    )

    dependency_types: dict[str, int] = Field(
        default_factory=dict
    )

class ArchitectureNodeResponse(BaseModel):
    """A node in the repository architecture graph."""

    id: str
    label: str
    node_type: str
    path: str | None = None


class ArchitectureEdgeResponse(BaseModel):
    """A directed relationship in the architecture graph."""

    source: str
    target: str
    edge_type: str


class ArchitectureSummary(BaseModel):
    """Repository architecture graph summary."""

    nodes: list[ArchitectureNodeResponse] = Field(
        default_factory=list
    )
    edges: list[ArchitectureEdgeResponse] = Field(
        default_factory=list
    )
    cycles: list[list[str]] = Field(
        default_factory=list
    )
    total_nodes: int = Field(ge=0)
    total_edges: int = Field(ge=0)
    cycle_count: int = Field(ge=0)

class RepositorySummary(BaseModel):
    """Repository-level analysis summary."""

    total_files: int = Field(ge=0)

    analyzed_files: int = Field(ge=0)

    files_with_issues: int = Field(
        ge=0
    )

    total_issues: int = Field(
        ge=0
    )

    languages: dict[str, int] = Field(
        default_factory=dict
    )

    extensions: dict[str, int] = Field(
        default_factory=dict
    )

    analyzed_paths: list[str] = Field(
        default_factory=list
    )

class ReviewResponse(BaseModel):
    """Normalized response returned by the review service."""

    issues: list[ReviewIssue] = Field(
        default_factory=list
    )

    summary: str | None = None

    fixed_code: str = ""

    quality_score: QualityScoreResponse | None = None

    repository: RepositorySummary | None = None

    dependency_summary: DependencySummary | None = None

    architecture: ArchitectureSummary | None = None


class FixRequest(BaseModel):
    code: str
    language: str
    issues: list[ReviewIssue] = Field(default_factory=list)
    model: str | None = None

    @field_validator("code", "language")
    @classmethod
    def validate_non_blank(cls, value: str) -> str:
        if not value.strip():
            raise ValueError("Field cannot be blank.")
        return value