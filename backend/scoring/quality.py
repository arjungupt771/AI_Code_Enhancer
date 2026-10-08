"""Deterministic multi-dimensional code-quality scoring."""

from collections import Counter, defaultdict
from dataclasses import dataclass
from typing import Iterable

from backend.schemas import ReviewIssue


SEVERITY_PENALTIES = {"error": 12.0, "warning": 5.0, "info": 1.0}
CATEGORY_WEIGHTS = {
    "security": 1.30,
    "reliability": 1.20,
    "performance": 1.10,
    "maintainability": 1.00,
    "style": 0.80,
    "bug": 1.20,  # backward-compatible static finding category
}
QUALITY_CATEGORIES = ("security", "performance", "maintainability", "reliability", "style")


@dataclass(frozen=True)
class QualityScore:
    overall: int
    category_scores: dict[str, int]
    file_scores: dict[str, int]
    severity_counts: dict[str, int]
    category_counts: dict[str, int]
    total_issues: int
    risk_level: str


def _clamp_score(value: float) -> int:
    return max(0, min(100, round(value)))


def _normalized_category(category: str) -> str:
    if category == "bug":
        return "reliability"
    if category == "analysis":
        return "maintainability"
    return category


def _issue_penalty(issue: ReviewIssue) -> float:
    return SEVERITY_PENALTIES[issue.severity] * CATEGORY_WEIGHTS.get(issue.category, 1.0)


def _score_from_penalty(penalty: float) -> int:
    return _clamp_score(100 - penalty)


def _risk_level(score: int) -> str:
    if score >= 90:
        return "Low"
    if score >= 75:
        return "Moderate"
    if score >= 50:
        return "High"
    return "Critical"


def calculate_quality_score(issues: Iterable[ReviewIssue | dict]) -> QualityScore:
    issue_list = [
        issue if isinstance(issue, ReviewIssue) else ReviewIssue.model_validate(issue)
        for issue in issues
    ]

    severity_counts = Counter(issue.severity for issue in issue_list)
    category_counts = Counter(_normalized_category(issue.category) for issue in issue_list)

    total_penalty = sum(_issue_penalty(issue) for issue in issue_list)
    category_penalties: dict[str, float] = defaultdict(float)
    file_penalties: dict[str, float] = defaultdict(float)

    for issue in issue_list:
        penalty = _issue_penalty(issue)
        category_penalties[_normalized_category(issue.category)] += penalty
        if issue.file_path:
            file_penalties[issue.file_path] += penalty

    category_scores = {
        category: _score_from_penalty(category_penalties.get(category, 0.0))
        for category in QUALITY_CATEGORIES
    }

    category_weights = {
        "security": 1.30,
        "performance": 1.10,
        "maintainability": 1.00,
        "reliability": 1.20,
        "style": 0.80,
    }
    weight_total = sum(category_weights.values())
    overall = _clamp_score(
        sum(category_scores[key] * weight for key, weight in category_weights.items()) / weight_total
    )

    return QualityScore(
        overall=overall,
        category_scores=category_scores,
        file_scores={path: _score_from_penalty(penalty) for path, penalty in file_penalties.items()},
        severity_counts=dict(severity_counts),
        category_counts=dict(category_counts),
        total_issues=len(issue_list),
        risk_level=_risk_level(overall),
    )
