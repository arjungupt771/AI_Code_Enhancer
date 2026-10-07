import pytest

from pydantic import ValidationError

from schemas import (
    FixRequest,
    ReviewIssue,
    ReviewResponse,
)


def test_valid_issue_is_accepted():

    issue = ReviewIssue(
        line=4,
        severity="warning",
        category="security",
        message=(
            "Potential hardcoded credential."
        ),
        score=0.92,
    )

    assert issue.line == 4
    assert issue.score == 0.92


def test_invalid_issue_values_are_rejected():

    with pytest.raises(ValidationError):
        ReviewIssue(
            line=0,
            severity="warning",
            category="security",
            message="Bad line",
        )

    with pytest.raises(ValidationError):
        ReviewIssue(
            line=1,
            severity="critical",
            category="security",
            message="Bad severity",
        )


def test_review_response_defaults_to_empty_findings():

    response = ReviewResponse()

    assert response.issues == []
    assert response.fixed_code == ""


def test_fix_request_rejects_blank_code():

    with pytest.raises(ValidationError):
        FixRequest(
            code="   ",
            language="Python",
            issues=[],
        )


def test_fix_request_rejects_blank_language():

    with pytest.raises(ValidationError):
        FixRequest(
            code="print(1)",
            language="   ",
            issues=[],
        )