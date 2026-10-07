"""Validated API request and response models."""

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


class ReviewResponse(BaseModel):
    """Normalized response returned by the review service."""

    issues: list[ReviewIssue] = Field(
        default_factory=list
    )

    summary: str | None = None

    fixed_code: str = ""


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