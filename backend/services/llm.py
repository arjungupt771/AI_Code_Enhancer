"""Multi-provider LLM review and targeted remediation service.

The application intentionally supports only two providers: Google Gemini and Groq.
Provider selection is explicit, while model names remain configurable through the
local environment.
"""

import json
import logging
import re
from typing import Any

from pydantic import ValidationError

from backend.core_config import (
    DEFAULT_GROQ_MODEL,
    DEFAULT_MODEL,
    GROQ_API_KEY,
    GEMINI_API_KEY,
)
from backend.schemas import ReviewIssue, ReviewResponse

logger = logging.getLogger(__name__)

SUPPORTED_PROVIDERS = {"gemini", "groq"}


def normalize_provider(provider: str | None, model: str | None = None) -> str:
    """Resolve an explicit provider or infer it from a Groq model name."""
    if provider:
        normalized = provider.strip().lower()
        if normalized not in SUPPORTED_PROVIDERS:
            raise ValueError("Provider must be 'gemini' or 'groq'.")
        return normalized

    if model and model.strip().lower().startswith(("llama", "mixtral", "gemma")):
        return "groq"

    return "gemini"


def default_model_for_provider(provider: str) -> str:
    return DEFAULT_GROQ_MODEL if provider == "groq" else DEFAULT_MODEL


def _get_gemini_client():
    if not GEMINI_API_KEY:
        raise RuntimeError("GEMINI_API_KEY is not configured.")

    try:
        from google import genai
    except ImportError as exc:
        raise RuntimeError(
            "The Gemini SDK is not installed. Run: pip install -r requirements.txt"
        ) from exc

    return genai.Client(api_key=GEMINI_API_KEY)


def _get_groq_client():
    if not GROQ_API_KEY:
        raise RuntimeError("GROQ_API_KEY is not configured.")

    try:
        from groq import Groq
    except ImportError as exc:
        raise RuntimeError(
            "The Groq SDK is not installed. Run: pip install -r requirements.txt"
        ) from exc

    return Groq(api_key=GROQ_API_KEY)


def _format_code_input(code_text: str | dict[str, str]) -> str:
    if isinstance(code_text, dict):
        return "\n".join(
            f"=== FILE: {filename} ===\n{content}\n"
            for filename, content in code_text.items()
        )
    return code_text


def _strip_json_fences(text: str) -> str:
    text = text.strip()
    if text.startswith("```"):
        text = re.sub(r"^```(?:json)?\s*", "", text, flags=re.IGNORECASE)
        text = re.sub(r"\s*```$", "", text)
    return text.strip()


def _parse_review_response(text: str) -> ReviewResponse:
    raw = _strip_json_fences(text)
    try:
        parsed: Any = json.loads(raw)
    except json.JSONDecodeError as exc:
        logger.warning("AI returned invalid JSON: %s", exc)
        raise ValueError("AI returned invalid structured review data.") from exc

    if isinstance(parsed, list):
        parsed = {"issues": parsed}
    if not isinstance(parsed, dict):
        raise ValueError("AI review response must be a JSON object.")

    raw_issues = parsed.get("issues", [])
    if not isinstance(raw_issues, list):
        raise ValueError("AI review response contains an invalid issues field.")

    valid_issues: list[ReviewIssue] = []
    for raw_issue in raw_issues:
        if not isinstance(raw_issue, dict):
            logger.warning("Ignoring invalid AI finding: %r", raw_issue)
            continue
        try:
            valid_issues.append(ReviewIssue.model_validate(raw_issue))
        except ValidationError as exc:
            logger.warning("Ignoring malformed AI finding: %s", exc)

    return ReviewResponse(
        issues=valid_issues,
        summary=parsed.get("summary"),
    )


def _review_prompt(code: str, language: str) -> str:
    return f"""
You are a strict senior software engineer performing repository-aware code review.

Review the following {language} source code.

Return ONLY valid JSON with this structure:
{{
  "summary": "One concise sentence summarizing the most important findings.",
  "issues": [
    {{
      "line": 1,
      "severity": "error",
      "category": "security",
      "message": "Clear explanation of the issue.",
      "explanation": "Why it matters and how to address it.",
      "score": 0.95
    }}
  ]
}}

Rules:
- line must be an integer starting from 1.
- severity must be one of: info, warning, error.
- category must be one of: security, performance, maintainability, reliability, style.
- score is optional and must be between 0 and 1.
- Do not invent issues merely to fill the response.
- Prefer precise, actionable findings over generic advice.
- Do not include Markdown outside the JSON object.
- If there are no issues, return {{"summary":"No significant issues found.","issues":[]}}.

Source code:
{code}
"""


def _fix_prompt(code: str, language: str, issues: list[ReviewIssue]) -> str:
    issues_text = json.dumps([issue.model_dump() for issue in issues], indent=2)
    return f"""
You are a senior software engineer performing targeted local code remediation.

Language:
{language}

Reported issues:
{issues_text}

Original code:
{code}

Instructions:
- Fix ONLY the reported issues.
- Do not change unrelated logic, APIs, formatting, or behavior.
- Preserve existing functionality and coding style where reasonable.
- Return ONLY valid JSON in this exact shape:
{{"replacement_code":"..."}}
- The replacement_code value must contain the complete corrected source code.
- Do not use Markdown fences.
- Do not include explanations outside the JSON object.
"""


def _generate(provider: str, model: str, prompt: str) -> str:
    if provider == "gemini":
        response = _get_gemini_client().models.generate_content(
            model=model,
            contents=prompt,
        )
        return (response.text or "").strip()

    response = _get_groq_client().chat.completions.create(
        model=model,
        messages=[
            {"role": "system", "content": "You are a precise software engineering assistant."},
            {"role": "user", "content": prompt},
        ],
        temperature=0.1,
    )
    return (response.choices[0].message.content or "").strip()


def review_code_with_llm(
    code_text: str | dict[str, str],
    language: str,
    *,
    mode: str = "review",
    issues: list[ReviewIssue] | None = None,
    model_name: str | None = None,
    provider: str | None = None,
) -> ReviewResponse | str:
    if mode not in {"review", "fix"}:
        raise ValueError("Unsupported mode. Expected 'review' or 'fix'.")

    resolved_provider = normalize_provider(provider, model_name)
    model = model_name.strip() if model_name and model_name.strip() else default_model_for_provider(resolved_provider)
    formatted_code = _format_code_input(code_text)

    if mode == "fix":
        raw = _generate(resolved_provider, model, _fix_prompt(formatted_code, language, issues or []))
        cleaned = _strip_json_fences(raw)
        try:
            parsed = json.loads(cleaned)
            replacement = parsed.get("replacement_code", "") if isinstance(parsed, dict) else ""
            if replacement:
                return replacement.strip()
        except json.JSONDecodeError:
            logger.warning("Provider returned non-JSON fix output; using raw text fallback.")
        return cleaned

    return _parse_review_response(
        _generate(resolved_provider, model, _review_prompt(formatted_code, language))
    )
