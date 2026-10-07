from fastapi.testclient import TestClient

import api.routes as routes

from main import app

from schemas import (
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