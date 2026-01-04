from fastapi import FastAPI, UploadFile, Form, File, Body
from fastapi.middleware.cors import CORSMiddleware
from typing import List, Optional
from utils import review_code_with_llm  # Assume utils handles Gemini/LLM logic

app = FastAPI()

# Allow frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"], 
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.post("/review-code")
async def review_code(
    files: List[UploadFile] = File(...),
    language: str = Form(...),
    model: str = Form("gemini-2.5-flash")  # default model
):
    """
    Handles multi-file uploads, model selection, and returns:
    {
        "issues": [...],
        "fixedCode": "..."
    }
    """
    all_code = {}
    for f in files:
        content = await f.read()
        all_code[f.filename] = content.decode("utf-8")

    # Call LLM/Gemini API for review
    # utils.review_code_with_model should handle:
    # - model selection (gpt-4, claude, gemini, local)
    # - return structured issues (line, severity, category, message, explanation)
    # - return fixed code (optional)
    review_result = review_code_with_llm(all_code, language, mode="review")

    return {
        "issues": review_result.get("issues", []),
        "fixedCode": review_result.get("fixedCode", "")
    }

@app.post("/fix-code")
async def fix_code(
    code: str = Body(...),
    language: str = Body(...),
    issues: list = Body(...)
):
    """
    issues = [{ line, message, category }]
    """

    fixed_code = review_code_with_llm(
        code,
        language,
        mode="fix",
        issues=issues
    )

    return {"fixed_code": fixed_code}