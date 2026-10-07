"""Gemini-backed AI review service with validated structured output."""

import json
import logging
import re
from typing import Any

from pydantic import ValidationError

from core_config import (
    DEFAULT_MODEL,
    GEMINI_API_KEY,
)
from schemas import (
    ReviewIssue,
    ReviewResponse,
)


logger = logging.getLogger(__name__)


def _get_client():
    """Create Gemini client lazily."""

    if not GEMINI_API_KEY:
        raise RuntimeError(
            "GEMINI_API_KEY is not configured."
        )

    try:
        from google import genai
    except ImportError as exc:
        raise RuntimeError(
            "The Gemini SDK is not installed. "
            "Run: pip install -r requirements.txt"
        ) from exc

    return genai.Client(
        api_key=GEMINI_API_KEY
    )


def _format_code_input(
    code_text: str | dict[str, str],
) -> str:

    if isinstance(code_text, dict):
        return "\n".join(
            (
                f"=== FILE: {filename} ===\n"
                f"{content}\n"
            )
            for filename, content
            in code_text.items()
        )

    return code_text


def _strip_json_fences(
    text: str,
) -> str:

    text = text.strip()

    if text.startswith("```"):
        text = re.sub(
            r"^```(?:json)?\s*",
            "",
            text,
            flags=re.IGNORECASE,
        )

        text = re.sub(
            r"\s*```$",
            "",
            text,
        )

    return text.strip()


def _parse_review_response(
    text: str,
) -> ReviewResponse:

    raw = _strip_json_fences(text)

    try:
        parsed: Any = json.loads(raw)

    except json.JSONDecodeError as exc:
        logger.warning(
            "AI returned invalid JSON: %s",
            exc,
        )

        raise ValueError(
            "AI returned invalid structured review data."
        ) from exc

    if isinstance(parsed, list):
        parsed = {
            "issues": parsed
        }

    if not isinstance(parsed, dict):
        raise ValueError(
            "AI review response must be a JSON object."
        )

    raw_issues = parsed.get(
        "issues",
        [],
    )

    if not isinstance(raw_issues, list):
        raise ValueError(
            "AI review response contains "
            "an invalid issues field."
        )

    valid_issues: list[ReviewIssue] = []

    for raw_issue in raw_issues:

        if not isinstance(
            raw_issue,
            dict,
        ):
            logger.warning(
                "Ignoring invalid AI finding: %r",
                raw_issue,
            )
            continue

        try:
            valid_issues.append(
                ReviewIssue.model_validate(
                    raw_issue
                )
            )

        except ValidationError as exc:
            logger.warning(
                "Ignoring malformed AI finding: %s",
                exc,
            )

    return ReviewResponse(
        issues=valid_issues
    )


def review_code_with_llm(
    code_text: str | dict[str, str],
    language: str,
    *,
    mode: str = "review",
    issues: list[ReviewIssue] | None = None,
    model_name: str | None = None,
) -> ReviewResponse | str:

    if mode not in {
        "review",
        "fix",
    }:
        raise ValueError(
            "Unsupported mode. "
            "Expected 'review' or 'fix'."
        )

    client = _get_client()

    model = (
        model_name
        or DEFAULT_MODEL
    )

    formatted_code = (
        _format_code_input(code_text)
    )

    if mode == "fix":

        issues_text = json.dumps(
            [
                (
                    issue.model_dump()
                    if isinstance(
                        issue,
                        ReviewIssue,
                    )
                    else issue
                )
                for issue
                in (issues or [])
            ],
            indent=2,
        )

        prompt = f"""
You are a senior software engineer performing
targeted local code remediation.

Language:
{language}

Reported issues:
{issues_text}

Original code:
{formatted_code}

Instructions:
- Fix only the reported issues.
- Do not change unrelated logic or APIs.
- Preserve existing functionality.
- Preserve existing coding style where reasonable.
- Return ONLY the corrected source code.
- Do not use Markdown code fences.
- Do not provide explanations.
"""

        response = client.models.generate_content(
            model=model,
            contents=prompt,
        )

        return (
            response.text or ""
        ).strip()

    prompt = f"""
You are a strict software code-review engine.

Review the following {language} source code.

Return ONLY valid JSON with this structure:

{{
  "issues": [
    {{
      "line": 1,
      "severity": "error",
      "category": "bug",
      "message": "Clear explanation of the issue.",
      "explanation": "Why it matters and how to address it.",
      "score": 0.95
    }}
  ]
}}

Rules:
- line must be an integer starting from 1.
- severity must be one of:
  info, warning, error.
- category must be one of:
  security, performance, style, bug.
- score is optional and must be between 0 and 1.
- Do not include Markdown.
- Do not include explanations outside JSON.
- If there are no issues, return:
  {{"issues": []}}

Source code:
{formatted_code}
"""

    response = client.models.generate_content(
        model=model,
        contents=prompt,
    )

    return _parse_review_response(
        response.text or ""
    )