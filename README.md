<<<<<<< HEAD
# AI_Code_Enhancer
=======
# GENAI-Project 🔍💡

A small app for automated code review and fixes using an LLM (Gemini / Google Generative AI).

---

## ✅ Overview

- Backend: FastAPI service that accepts code files and returns issues or fixed code.
- Frontend: React app with a code uploader and review UI.

---

## ⚙️ Requirements

- Python 3.10+ (backend)
- Node.js 16+ / npm (frontend)
- A Gemini (Google Generative AI) API key for code reviews (set as `GEMINI_API_KEY` in `backend/config.py` or as an env var in your environment)

Backend Python packages used (install with pip):
- fastapi
- uvicorn
- google-generativeai
- python-multipart

Example install (from repo root):

```bash
# Backend
cd backend
python -m venv .venv
.\.venv\Scripts\activate   # Windows PowerShell
pip install fastapi uvicorn google-generativeai python-multipart

# Frontend
cd frontend
npm install
```

Note: `backend/requirements.txt` currently is empty — add pinned package versions there after validating in your environment.

---

## 🚀 Run locally

Backend (development):

```bash
cd backend
# set GEMINI_API_KEY in config.py or environment
uvicorn main:app --reload --host 127.0.0.1 --port 8000
```

Frontend (development):

```bash
cd frontend
npm start
```

---

## 📡 API Endpoints

1) POST /review-code

- Accepts: multipart form with `files` (one or more files), `language` (string), and optional `model` (string).
- Returns: JSON with the review results:

Example response:

```json
{
  "issues": [
    { "line": 10, "severity": "warning", "category": "style", "message": "..." }
  ],
  "fixedCode": ""  
}
```

Notes:
- `issues` is always present as an array (may be empty).
- `fixedCode` is returned if the reviewer also supplies a suggested fix (currently usually blank).

2) POST /fix-code

- Accepts: JSON body with `code` (string), `language` (string), and `issues` (array)
- Returns: JSON with `fixed_code` key containing the fixed code string.

Example response:
```json
{ "fixed_code": "..." }
```

---

## 🔧 Usage examples (curl)

Upload a file for review:

```bash
curl -v -F "files=@./backend/test.py;type=text/plain" -F "language=python" -F "model=gemini-2.5-flash" http://127.0.0.1:8000/review-code
```

Request a fix:

```bash
curl -X POST http://127.0.0.1:8000/fix-code \
  -H "Content-Type: application/json" \
  -d '{"code":"print(1)","language":"python","issues":[]}'
```

---

## 🛠️ Implementation notes & TODOs

- The backend `utils.review_code_with_llm` returns `{"issues": [...]}` on review, and a plain string for fixes. The frontend expects `issues` in review responses; please keep the client and server in sync on the exact schema.
- Add unit/integration tests for the endpoints and utils parsing.
- Add pinned versions to `backend/requirements.txt`.

---

## 🤝 Contributing

Open a PR, add tests for your changes, keep changes small and focused.

---

## 📬 Questions

If you want, I can:
- add automated tests for `/review-code` and `review_code_with_llm`
- add a `requirements.txt` with pinned versions
- standardize response keys between endpoints (e.g., `fixedCode` vs `fixed_code`)

---

© GENAI-Project
>>>>>>> 48e5cde (Initial commit)
