"""Deterministic code-quality scoring based on review findings."""

from collections import Counter, defaultdict
from dataclasses import dataclass
from typing import Iterable

from backend.schemas import ReviewIssue


SEVERITY_PENALTIES = {
    "error": 12,
    "warning": 5,
    "info": 1,
}

CATEGORY_WEIGHTS = {
    "security": 1.25,
    "bug": 1.15,
    "performance": 1.0,
    "style": 0.75,
}


@dataclass(frozen=True)
class QualityScore:
    overall: int
    category_scores: dict[str, int]
    file_scores: dict[str, int]
    severity_counts: dict[str, int]
    category_counts: dict[str, int]
    total_issues: int


def _clamp_score(value: float) -> int:
    return max(0, min(100, round(value)))


def _issue_penalty(issue: ReviewIssue) -> float:
    severity_penalty = SEVERITY_PENALTIES[issue.severity]
    category_weight = CATEGORY_WEIGHTS.get(
        issue.category,
        1.0,
    )

    return severity_penalty * category_weight


def _score_from_penalty(penalty: float) -> int:
    return _clamp_score(100 - penalty)


def calculate_quality_score(
    issues: Iterable[ReviewIssue | dict],
) -> QualityScore:
    """Calculate deterministic project, category, and file quality scores."""

    issue_list = [
        issue
        if isinstance(issue, ReviewIssue)
        else ReviewIssue.model_validate(issue)
        for issue in issues
    ]

    severity_counts = Counter(
        issue.severity
        for issue in issue_list
    )

    category_counts = Counter(
        issue.category
        for issue in issue_list
    )

    total_penalty = sum(
        _issue_penalty(issue)
        for issue in issue_list
    )

    category_penalties: dict[str, float] = defaultdict(float)
    file_penalties: dict[str, float] = defaultdict(float)

    for issue in issue_list:
        penalty = _issue_penalty(issue)

        category_penalties[
            issue.category
        ] += penalty

        if issue.file_path:
            file_penalties[
                issue.file_path
            ] += penalty

    category_scores = {
        category: _score_from_penalty(penalty)
        for category, penalty in category_penalties.items()
    }

    file_scores = {
        file_path: _score_from_penalty(penalty)
        for file_path, penalty in file_penalties.items()
    }

    return QualityScore(
        overall=_score_from_penalty(
            total_penalty
        ),
        category_scores=category_scores,
        file_scores=file_scores,
        severity_counts=dict(
            severity_counts
        ),
        category_counts=dict(
            category_counts
        ),
        total_issues=len(issue_list),
    )