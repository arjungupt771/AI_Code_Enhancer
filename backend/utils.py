import google.generativeai as genai
from config import GEMINI_API_KEY
import json
import re

genai.configure(api_key=GEMINI_API_KEY)


def _format_code_input(code_text):
    """Convert code input to a single string. Accepts either a str or a dict of {filename: content}."""
    if isinstance(code_text, dict):
        parts = []
        for fname, content in code_text.items():
            # Use a neutral header marker to avoid language-specific comment syntax
            parts.append(f"=== FILE: {fname} ===\n{content}\n")
        return "\n".join(parts)
    return code_text


def review_code_with_llm(code_text, language, mode="review", issues=None, model_name="gemini-2.5-flash"):
    """Review or fix code using the Gemini LLM.

    Args:
        code_text (str|dict): The source code (or dict of files) to review or fix.
        language (str): The programming language of the code.
        mode (str): Either "review" (default) to get JSON issues, or "fix" to return the fixed code.

    Returns:
        dict|str: In "review" mode returns a dict like {"issues": [...]}, in "fix" mode returns fixed code string.
    """
    model = genai.GenerativeModel(model_name)

    formatted_code = _format_code_input(code_text)

    if mode == "fix":
        prompt = f"""
You are a senior software engineer.

Fix the following code issues carefully.
Do NOT change unrelated logic.

Language: {language}

Original Code:
{formatted_code}

Return ONLY the fixed code.
"""
        response = model.generate_content(prompt)
        return response.text.strip()

    # Default: review mode (returns structured JSON under the key 'issues')
    prompt = f"""
You are a strict code review engine.

Review the following {language} code and return feedback
STRICTLY as a JSON array.

Rules:
- Output ONLY valid JSON
- Do NOT add explanations outside JSON
- Do NOT wrap in markdown
- Do NOT add backticks
- Do NOT add comments

For each issue return :
- line: number (line number in code, start from 1)
- severity: one of ["info", "warning", "error"]
- category (security | performance | style | bug)
- message: clear explanation of the issue or suggestion

If no issues are found, return an empty array [].

Code:
{formatted_code}
"""

    response = model.generate_content(prompt)

    # Try to parse JSON; if parsing fails, try to extract JSON array from text; otherwise return a safe dict
    text = response.text.strip()
    try:
        parsed = json.loads(text)
        if isinstance(parsed, list):
            return {"issues": parsed}
        if isinstance(parsed, dict) and "issues" in parsed:
            return parsed
        # If parsed but not in expected format, wrap it
        return {"issues": parsed}
    except Exception:
        # Try to find the first JSON array in the text
        m = re.search(r"(\[.*\])", text, re.S)
        if m:
            try:
                parsed = json.loads(m.group(1))
                return {"issues": parsed}
            except Exception:
                pass

    # Final fallback: return empty issues and include raw text for debugging
    return {"issues": [], "raw": text}

