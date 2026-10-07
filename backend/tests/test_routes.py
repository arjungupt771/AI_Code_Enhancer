from fastapi.testclient import TestClient

import backend.api.routes as routes

from backend.main import app

from backend.schemas import (
    ReviewIssue,
    ReviewResponse,
)


client = TestClient(app)


def test_health_endpoint():
    response = client.get("/health")

    assert response.status_code == 200

    assert response.json() == {
        "status": "ok",
        "service": "AI Code Enhancer",
    }


def test_review_rejects_unsupported_file():
    response = client.post(
        "/review-code",
        files={
            "files": (
                "notes.txt",
                b"hello",
                "text/plain",
            )
        },
        data={
            "language": "Python",
            "model": "gemini-2.5-flash",
        },
    )

    assert response.status_code == 400

    assert (
        "Unsupported file type"
        in response.json()["detail"]
    )


def test_review_returns_validated_schema(
    monkeypatch,
):

    def fake_review(*args, **kwargs):
        return ReviewResponse(
            issues=[
                ReviewIssue(
                    line=2,
                    severity="warning",
                    category="style",
                    message=(
                        "Prefer a descriptive "
                        "variable name."
                    ),
                )
            ]
        )

    monkeypatch.setattr(
        routes,
        "review_code_with_llm",
        fake_review,
    )

    monkeypatch.setattr(
        routes,
        "GEMINI_API_KEY",
        "test-key",
    )

    response = client.post(
        "/review-code",
        files={
            "files": (
                "main.py",
                b"x = 1\nprint(x)\n",
                "text/x-python",
            )
        },
        data={
            "language": "Python",
            "model": "gemini-2.5-flash",
        },
    )

    assert response.status_code == 200

    body = response.json()

    assert body["issues"][0]["line"] == 2

    assert (
        body["issues"][0]["category"]
        == "style"
    )


def test_fix_endpoint_returns_fixed_code(
    monkeypatch,
):

    def fake_fix(*args, **kwargs):
        return "print('fixed')"

    monkeypatch.setattr(
        routes,
        "review_code_with_llm",
        fake_fix,
    )

    monkeypatch.setattr(
        routes,
        "GEMINI_API_KEY",
        "test-key",
    )

    response = client.post(
        "/fix-code",
        json={
            "code": "print('broken')",
            "language": "Python",
            "issues": [
                {
                    "line": 1,
                    "severity": "error",
                    "category": "bug",
                    "message": "Example issue",
                }
            ],
        },
    )

    assert response.status_code == 200

    assert response.json() == {
        "fixed_code": "print('fixed')"
    }

def test_review_merges_static_and_ai_findings(
    monkeypatch,
):
    def fake_review(*args, **kwargs):
        return ReviewResponse(
            issues=[
                ReviewIssue(
                    source="ai",
                    line=3,
                    severity="warning",
                    category="style",
                    message="AI detected a readability issue.",
                )
            ]
        )

    monkeypatch.setattr(
        routes,
        "review_code_with_llm",
        fake_review,
    )

    monkeypatch.setattr(
        routes,
        "GEMINI_API_KEY",
        "test-key",
    )

    response = client.post(
        "/review-code",
        files={
            "files": (
                "main.py",
                b"import os\n\nprint('hello')\n",
                "text/x-python",
            )
        },
        data={
            "language": "Python",
            "model": "gemini-2.5-flash",
        },
    )

    assert response.status_code == 200

    issues = response.json()["issues"]

    assert len(issues) >= 2

    static_issues = [
        issue
        for issue in issues
        if issue["source"] == "static"
    ]

    ai_issues = [
        issue
        for issue in issues
        if issue["source"] == "ai"
    ]

    assert len(static_issues) >= 1
    assert len(ai_issues) == 1

    assert static_issues[0]["tool"] == "ruff"
    assert static_issues[0]["rule_id"] in {
        "F401",
        "I001",
    }

    assert (
        ai_issues[0]["message"]
        == "AI detected a readability issue."
    )

def test_review_deduplicates_static_findings(
    monkeypatch,
):
    def fake_review(*args, **kwargs):
        return ReviewResponse(
            issues=[]
        )

    monkeypatch.setattr(
        routes,
        "review_code_with_llm",
        fake_review,
    )

    monkeypatch.setattr(
        routes,
        "GEMINI_API_KEY",
        "test-key",
    )

    response = client.post(
        "/review-code",
        files={
            "files": (
                "main.py",
                b"import os\n",
                "text/x-python",
            )
        },
        data={
            "language": "Python",
            "model": "gemini-2.5-flash",
        },
    )

    assert response.status_code == 200

    issues = response.json()["issues"]

    static_issues = [
        issue
        for issue in issues
        if issue["source"] == "static"
    ]

    keys = {
        (
            issue["file_path"],
            issue["line"],
            issue["rule_id"],
        )
        for issue in static_issues
    }

    assert len(keys) == len(static_issues)