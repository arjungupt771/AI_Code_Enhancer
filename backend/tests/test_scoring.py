from backend.scoring import calculate_quality_score
from backend.schemas import ReviewIssue


def test_quality_score_has_five_dimensions():
    result = calculate_quality_score(
        [
            ReviewIssue(severity="error", category="security", message="secret leak"),
            ReviewIssue(severity="warning", category="maintainability", message="complex function"),
            ReviewIssue(severity="warning", category="reliability", message="unchecked failure"),
        ]
    )

    assert set(result.category_scores) == {
        "security", "performance", "maintainability", "reliability", "style"
    }
    assert result.category_scores["security"] < 100
    assert result.category_scores["performance"] == 100
    assert result.risk_level in {"Low", "Moderate", "High", "Critical"}


def test_legacy_bug_and_analysis_categories_are_normalized():
    result = calculate_quality_score(
        [
            ReviewIssue(severity="warning", category="bug", message="bug"),
            ReviewIssue(severity="info", category="analysis", message="analysis finding"),
        ]
    )

    assert result.category_counts["reliability"] == 1
    assert result.category_counts["maintainability"] == 1
