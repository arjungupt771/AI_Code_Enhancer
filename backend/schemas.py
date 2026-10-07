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
    """A single AI-detected code-review finding."""

    model_config = ConfigDict(
        extra="ignore"
    )

    line: int = Field(
        ge=1
    )

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

    fixed_code: str = ""


class FixRequest(BaseModel):
    """Request for an AI-generated correction."""

    code: str = Field(
        min_length=1
    )

    language: str = Field(
        min_length=1
    )

    issues: list[ReviewIssue] = Field(
        default_factory=list
    )

    model: str | None = None

    @field_validator(
        "code",
        "language",
        "model",
    )
    @classmethod
    def reject_blank_strings(
        cls,
        value: str | None,
    ) -> str | None:
        if value is None:
            return value

        value = value.strip()

        if not value:
            raise ValueError(
                "Value cannot be blank"
            )

        return value