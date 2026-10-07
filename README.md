# AI Code Enhancer

**AI-powered intelligent code review and automated remediation platform.**

AI Code Enhancer analyzes source code using AI to identify potential bugs, security vulnerabilities, performance issues, and code-quality problems. It can also generate fixes for detected issues through an interactive code-review workflow.

---

## ✨ Overview

AI Code Enhancer combines a **React + Monaco Editor frontend** with a **FastAPI backend** and an AI-powered code-review engine.

The current workflow is:

```text
Upload Source Code
        ↓
FastAPI Backend
        ↓
AI Code Review
        ↓
Structured Findings
        ↓
Review Issues
        ↓
Generate Fix
        ↓
Review / Apply Changes
```

The project is being developed incrementally toward a full **AI-assisted developer productivity platform**.

---

## 🚀 Current Features

- 📁 Multi-file source-code upload
- 📝 Monaco-based code editor
- 🤖 AI-powered code review
- 🔍 Issue detection and categorization
- ⚠️ Severity classification
- 📍 Line-level issue reporting
- 🛡️ Security issue detection
- ⚡ Performance issue detection
- 🐛 Potential bug detection
- 🎨 Code-style recommendations
- 🔧 AI-generated code fixes
- 🔀 Code diff workflow
- 💻 Support for multiple programming languages
- ⚙️ Configurable Gemini model

---

## 🏗️ Current Architecture

```text
┌──────────────────────────┐
│      React Frontend      │
│                          │
│    Monaco Code Editor    │
│    File Explorer / UI    │
└────────────┬─────────────┘
             │
             │ HTTP
             ▼
┌──────────────────────────┐
│      FastAPI Backend     │
│                          │
│   /review-code           │
│   /fix-code              │
│   /health                │
└────────────┬─────────────┘
             │
             ▼
┌──────────────────────────┐
│       AI Engine          │
│                          │
│      Gemini LLM          │
└────────────┬─────────────┘
             │
             ▼
┌──────────────────────────┐
│     Review Findings      │
│                          │
│  Security                │
│  Performance             │
│  Bugs                    │
│  Style                   │
└──────────────────────────┘
```

---

## 🛠️ Tech Stack

### Frontend

- React
- Monaco Editor
- Axios
- Tailwind CSS

### Backend

- Python
- FastAPI
- Google Generative AI
- Pydantic
- Uvicorn

### AI

- Google Gemini

---

## 📂 Project Structure

```text
AI_Code_Enhancer/
│
├── backend/
│   ├── config.py
│   ├── main.py
│   ├── requirements.txt
│   └── utils.py
│
├── frontend/
│   ├── public/
│   ├── src/
│   │   ├── components/
│   │   ├── App.js
│   │   └── ...
│   ├── package.json
│   └── package-lock.json
│
├── .env.example
├── .gitignore
├── package.json
├── package-lock.json
└── README.md
```

---

# ⚙️ Installation

## Prerequisites

Make sure the following are installed:

- Python 3.10+
- Node.js 16+
- npm
- A Google Gemini API key

---

## 1. Clone the repository

```bash
git clone https://github.com/arjungupt771/AI_Code_Enhancer.git
cd AI_Code_Enhancer
```

---

## 2. Backend Setup

Create a Python virtual environment:

```bash
cd backend

python -m venv .venv
```

### Linux / macOS

```bash
source .venv/bin/activate
```

### Windows

```powershell
.venv\Scripts\activate
```

Install dependencies:

```bash
pip install -r requirements.txt
```

---

## 3. Configure Environment Variables

Return to the project root:

```bash
cd ..
```

Create your environment file:

```bash
cp .env.example .env
```

Then add your Gemini API key:

```env
GEMINI_API_KEY=your_gemini_api_key
DEFAULT_MODEL=gemini-2.5-flash
CORS_ORIGINS=http://localhost:3000,http://127.0.0.1:3000
```

**Never commit `.env` or API keys to GitHub.**

---

## 4. Start the Backend

```bash
cd backend

uvicorn main:app --reload --host 127.0.0.1 --port 8000
```

The backend will be available at:

```text
http://127.0.0.1:8000
```

FastAPI documentation is available at:

```text
http://127.0.0.1:8000/docs
```

---

## 5. Start the Frontend

Open another terminal:

```bash
cd frontend
npm install
npm start
```

The frontend will normally be available at:

```text
http://localhost:3000
```

---

# 📡 API

## `GET /health`

Checks whether the backend is running.

### Response

```json
{
  "status": "ok",
  "service": "AI Code Enhancer"
}
```

---

## `POST /review-code`

Reviews one or more source files.

### Request

Multipart form data:

```text
files
language
model
```

Example:

```bash
curl -X POST \
  -F "files=@./example.py" \
  -F "language=python" \
  -F "model=gemini-2.5-flash" \
  http://127.0.0.1:8000/review-code
```

### Response

```json
{
  "issues": [
    {
      "line": 10,
      "severity": "warning",
      "category": "security",
      "message": "Potential security issue detected."
    }
  ],
  "fixedCode": ""
}
```

---

## `POST /fix-code`

Generates a corrected version of source code based on detected issues.

### Request

```json
{
  "code": "print('example')",
  "language": "python",
  "issues": [],
  "model": "gemini-2.5-flash"
}
```

### Response

```json
{
  "fixed_code": "..."
}
```

---

# 🔐 Security

The application is designed to avoid storing secrets directly in source code.

Environment variables are used for sensitive configuration such as:

```text
GEMINI_API_KEY
```

The following should never be committed:

```text
.env
.venv/
node_modules/
__pycache__/
```

---

# 🧪 Testing

Backend validation can be performed using:

```bash
python -m py_compile backend/config.py
python -m py_compile backend/main.py
python -m py_compile backend/utils.py
```

API health can be checked with:

```bash
curl http://127.0.0.1:8000/health
```

Automated endpoint and AI-layer tests are part of the project roadmap.

---

# 🗺️ Development Roadmap

AI Code Enhancer is being developed through incremental phases.

## Phase 1 — Clean & Stabilize

- Repository cleanup
- Dependency management
- Environment-based configuration
- API validation
- Error handling
- Health endpoint
- Backend testing
- Frontend/API contract cleanup

**Status:** 🚧 In Progress

---

## Phase 2 — Static Analysis Engine

Introduce deterministic analysis alongside AI:

```text
Source Code
     ↓
Static Analysis
     ↓
Ruff / Bandit / ESLint / TypeScript
     ↓
Detected Findings
```

Planned capabilities:

- Python linting
- Security analysis
- JavaScript/TypeScript analysis
- Static-analysis result normalization
- Analysis result aggregation

**Status:** ⏳ Planned

---

## Phase 3 — Structured AI Review Engine

Upgrade the AI architecture with:

- Multi-provider LLM abstraction
- Gemini
- OpenAI
- Anthropic
- Ollama / local models
- Pydantic response schemas
- Structured AI output validation
- Reliable model routing

Target architecture:

```text
                LLM Router
                    │
       ┌────────────┼────────────┐
       ▼            ▼            ▼
    Gemini        OpenAI      Anthropic
                                 │
                              Ollama
```

**Status:** ⏳ Planned

---

## Phase 4 — Code Intelligence

Introduce higher-level code-quality analysis:

- Overall code-quality score
- Security score
- Performance score
- Maintainability score
- Reliability score
- Dedicated security scanning mode
- Risk prioritization

Example:

```text
CODE QUALITY

Overall          78 / 100
Security         91
Performance      67
Maintainability  74
Reliability      71
Style            86
```

**Status:** ⏳ Planned

---

## Phase 5 — Safe Automated Remediation

Move from complete code regeneration toward targeted patches.

Planned workflow:

```text
Finding
   ↓
AI-generated Patch
   ↓
Unified Diff
   ↓
Review
   ↓
┌──────────┐
│ Apply    │
│ Reject   │
└──────────┘
```

This will reduce the risk of unrelated code changes during automated remediation.

**Status:** ⏳ Planned

---

## Phase 6 — AI Test Generation

Add automated test generation:

```text
Source Code
     ↓
AI Analysis
     ↓
Generate Tests
     ↓
Run Tests
     ↓
Test Results
```

Planned capabilities:

- Unit-test generation
- Edge-case generation
- Negative test generation
- Test execution
- Pass/fail reporting
- Coverage reporting

**Status:** ⏳ Planned

---

## Phase 7 — GitHub Integration

Allow developers to connect repositories and review pull requests.

Target workflow:

```text
GitHub Repository
        ↓
Pull Request
        ↓
Changed Files
        ↓
Static Analysis + AI Review
        ↓
Review Report
        ↓
AI-generated Fixes
        ↓
GitHub Review
```

Planned capabilities:

- Repository selection
- Branch selection
- Pull-request analysis
- Changed-file review
- AI review comments
- Fix generation
- Pull-request integration

**Status:** ⏳ Planned

---

## Phase 8 — CI/CD

The final stage will integrate AI Code Enhancer into development pipelines.

```text
Developer
    ↓
Pull Request
    ↓
GitHub Actions
    ↓
Static Analysis
    ↓
AI Review
    ↓
Quality / Security Gates
    ↓
Pass / Fail
```

Potential quality gates:

```text
❌ Critical security issues
❌ Quality score below threshold
❌ High-severity bugs

        ↓

   Merge blocked
```

**Status:** ⏳ Planned

---

# 🎯 Project Vision

The long-term goal is to evolve AI Code Enhancer from a simple AI code reviewer into an **AI-powered developer productivity and automated code-remediation platform**.

The target architecture is:

```text
                     AI CODE ENHANCER
                            │
             ┌──────────────┴──────────────┐
             │                             │
      Static Analysis                  AI Engine
             │                             │
     Ruff / Bandit /                  Gemini / OpenAI /
     ESLint / etc.                    Claude / Ollama
             │                             │
             └──────────────┬──────────────┘
                            ↓
                    Review Aggregator
                            │
             ┌──────────────┼──────────────┐
             ▼              ▼              ▼
       Quality Score     Findings       Security
             │              │              │
             └──────────────┼──────────────┘
                            ↓
                     AI Remediation
                            ↓
                      Unified Diff
                            │
                   ┌────────┴────────┐
                   ▼                 ▼
              Apply Patch      Generate Tests
                   │                 │
                   └────────┬────────┘
                            ↓
                       GitHub PR
                            ↓
                       CI / CD
```

---

## 🤝 Contributing

Contributions are welcome.

When contributing:

1. Keep changes focused.
2. Add tests for new functionality.
3. Avoid committing secrets.
4. Keep frontend and backend API contracts synchronized.
5. Document significant architectural changes.

---

## 📄 License

This project is currently maintained as an AI engineering portfolio project.