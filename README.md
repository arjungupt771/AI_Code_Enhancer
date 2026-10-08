# AI Code Enhancer

> **AI-powered repository intelligence, code review, and automated remediation platform.**

AI Code Enhancer combines deterministic static analysis with LLM-powered code review to analyze source repositories, identify bugs, security vulnerabilities, performance problems, maintainability issues, and code-quality concerns — and generate targeted fixes that can be reviewed through an interactive diff workflow.

The project is built with a **React + Monaco Editor frontend** and a **FastAPI backend**, with support for **Google Gemini** and **Groq** as the AI providers.

---

## ✨ What It Does

AI Code Enhancer goes beyond sending individual code snippets to an LLM.

It analyzes a repository through multiple layers:

```text
                    Source Repository
                           │
                           ▼
                 Repository Analysis
                           │
             ┌─────────────┼─────────────┐
             ▼             ▼             ▼
        Static Analysis  Dependency   Architecture
                         Analysis       Analysis
             │             │             │
             └─────────────┼─────────────┘
                           ▼
                    AI Code Review
                    Gemini / Groq
                           │
                           ▼
                 Finding Normalization
                           │
                           ▼
                    Quality Scoring
                           │
                           ▼
                 Review Findings
                           │
                           ▼
                  AI Remediation
                           │
                           ▼
                     Unified Diff
                           │
                    ┌──────┴──────┐
                    ▼             ▼
                  Review        Apply
```

This creates a hybrid analysis workflow where deterministic tooling provides objective signals while AI provides higher-level reasoning and remediation.

---

# 🚀 Features

## 🔍 AI-Powered Code Review

Analyze source code using LLM-powered review to identify:

- 🐛 Potential bugs
- 🔐 Security vulnerabilities
- ⚡ Performance problems
- 🧹 Maintainability issues
- 🎨 Code-quality and style problems
- ⚠️ Severity-ranked findings
- 📍 Line-level findings
- 💡 Improvement recommendations

---

## 🤖 Multi-Provider AI Engine

The project currently supports two LLM providers:

### Google Gemini

Used for high-quality code analysis and remediation.

### Groq

Provides an alternative high-speed inference path for AI-powered analysis.

The application uses a provider abstraction so the rest of the analysis pipeline does not need to depend directly on a specific LLM provider.

```text
                 AI Review Engine
                       │
              ┌────────┴────────┐
              ▼                 ▼
           Gemini              Groq
```

Only these two providers are intentionally supported in the current version.

---

## 🧪 Hybrid Static + AI Analysis

AI Code Enhancer combines deterministic tooling with AI analysis.

Static analysis helps identify issues that can be detected reliably by dedicated tools, while the LLM provides contextual reasoning and higher-level recommendations.

```text
Source Code
    │
    ├──► Static Analysis
    │       ├── Ruff
    │       ├── Bandit
    │       └── JavaScript / TypeScript analysis
    │
    └──► AI Analysis
            ├── Gemini
            └── Groq

                 ↓

          Finding Aggregation
                 ↓
          Finding Normalization
                 ↓
            Quality Score
```

This reduces dependence on a single analysis technique.

---

## 📦 Repository Analysis

The application can work with multi-file repositories rather than only isolated code snippets.

Repository analysis provides information about:

- Source files
- Directory structure
- File relationships
- Supported source types
- Repository-level findings

This allows the AI review process to reason about code in a broader project context.

---

## 🔗 Dependency Analysis

The project analyzes relationships between source files and their dependencies.

This helps identify:

- Import relationships
- Module dependencies
- Dependency structure
- Potential dependency-related problems

---

## 🏗️ Architecture Analysis

AI Code Enhancer can analyze the structural relationships within a repository.

The architecture analysis can identify:

- File-to-file relationships
- Import graphs
- Dependency structure
- Circular dependencies
- Architectural relationships

The frontend presents this information in an interactive repository-analysis workflow.

---

## 📊 Code Quality Scoring

The project aggregates analysis results into an overall quality assessment.

The scoring system considers areas such as:

- Overall quality
- Security
- Performance
- Maintainability
- Reliability
- Style

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

The score provides a quick high-level view while the individual findings provide the detailed reasoning behind it.

---

## 🔧 AI-Powered Remediation

Detected issues can be passed back to the AI engine to generate targeted remediation.

Instead of blindly replacing an entire source file, the application provides an interactive workflow:

```text
Finding
   ↓
Generate AI Fix
   ↓
Proposed Changes
   ↓
Unified Diff
   ↓
Review
   ↓
Apply / Reject
```

This makes AI-generated modifications easier to inspect before applying them.

---

## 📝 Monaco Editor

The frontend uses **Monaco Editor** to provide a development-environment-style editing experience.

It supports:

- Source-code viewing
- Code editing
- Finding navigation
- Line-level issue inspection
- Diff visualization
- Proposed fix review

---

# 🏗️ Architecture

```text
┌───────────────────────────────────────────┐
│              React Frontend               │
│                                           │
│  ┌────────────┐  ┌────────────────────┐  │
│  │ File / Repo│  │   Monaco Editor    │  │
│  │   Upload   │  │   + Diff Viewer    │  │
│  └──────┬─────┘  └─────────┬──────────┘  │
│         │                   │             │
│         └──────────┬────────┘             │
└────────────────────┼─────────────────────┘
                     │ HTTP
                     ▼
┌───────────────────────────────────────────┐
│              FastAPI Backend              │
│                                           │
│  Repository Analysis                      │
│  Dependency Analysis                      │
│  Architecture Analysis                   │
│  Static Analysis                          │
│  AI Review                                │
│  Quality Scoring                           │
│  Remediation                              │
└────────────────────┬──────────────────────┘
                     │
          ┌──────────┴──────────┐
          ▼                     ▼
┌──────────────────┐   ┌──────────────────┐
│ Static Analysis  │   │   AI Providers   │
│                  │   │                  │
│ Ruff             │   │ Google Gemini    │
│ Bandit           │   │ Groq             │
│ JS/TS Analysis   │   │                  │
└────────┬─────────┘   └────────┬─────────┘
         │                      │
         └──────────┬───────────┘
                    ▼
          ┌────────────────────┐
          │ Finding Aggregator │
          │ + Normalization    │
          │ + Quality Scoring  │
          └──────────┬─────────┘
                     │
                     ▼
             Review Findings
                     │
                     ▼
              AI Remediation
                     │
                     ▼
                Unified Diff
```

---

# 🛠️ Tech Stack

## Frontend

- React
- Monaco Editor
- Axios
- Tailwind CSS
- JavaScript

## Backend

- Python
- FastAPI
- Pydantic
- Uvicorn
- Static analysis tooling
- Repository analysis utilities

## AI

- Google Gemini
- Groq

## Analysis

- Ruff
- Bandit
- JavaScript / TypeScript analysis
- Dependency analysis
- Architecture analysis
- Custom finding normalization
- Quality scoring

---

# 📂 Project Structure

```text
AI_Code_Enhancer/
│
├── backend/
│   ├── app/
│   │   ├── ai/
│   │   ├── analyzers/
│   │   ├── ...
│   │
│   ├── tests/
│   ├── main.py
│   ├── config.py
│   ├── requirements.txt
│   └── ...
│
├── frontend/
│   ├── public/
│   ├── src/
│   │   ├── components/
│   │   ├── ...
│   │   └── App.js
│   ├── package.json
│   └── package-lock.json
│
├── .env.example
├── .gitignore
└── README.md
```

> The exact internal module structure may evolve as the project develops.

---

# ⚙️ Installation

## Prerequisites

Make sure the following are installed:

- Python 3.10+
- Node.js
- npm
- A Google Gemini API key
- A Groq API key

---

## 1. Clone the Repository

```bash
git clone https://github.com/arjungupt771/AI_Code_Enhancer.git
cd AI_Code_Enhancer
```

---

# 2. Backend Setup

Create and activate a virtual environment:

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

Install backend dependencies:

```bash
pip install -r requirements.txt
```

---

# 3. Configure Environment Variables

Return to the project root:

```bash
cd ..
```

Create the local environment file:

```bash
cp .env.example .env
```

On Windows, you can also create `.env` manually from `.env.example`.

Configure your API credentials:

```env
GEMINI_API_KEY=your_gemini_api_key_here
GROQ_API_KEY=your_groq_api_key_here
```

Configure the models according to the environment variables supported by the backend.

Example:

```env
GEMINI_MODEL=gemini-2.5-flash
GROQ_MODEL=openai/gpt-oss-120b
```

Never commit `.env` or real API keys to GitHub.

---

# 4. Start the Backend

From the project root:

```bash
cd backend
uvicorn main:app --reload --host 127.0.0.1 --port 8000
```

The backend will be available at:

```text
http://127.0.0.1:8000
```

FastAPI's interactive documentation is available at:

```text
http://127.0.0.1:8000/docs
```

---

# 5. Start the Frontend

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

If the frontend supports a configurable backend URL, configure it through the frontend environment file.

Example:

```env
REACT_APP_API_BASE_URL=http://127.0.0.1:8000
```

---

# 🔄 Application Workflow

A typical repository review follows this process:

```text
1. Upload Repository
        ↓
2. Repository Structure Analysis
        ↓
3. Dependency Analysis
        ↓
4. Architecture Analysis
        ↓
5. Static Analysis
        ↓
6. AI Review
   ┌────┴────┐
   ▼         ▼
Gemini      Groq
   └────┬────┘
        ↓
7. Finding Normalization
        ↓
8. Quality Scoring
        ↓
9. Review Findings
        ↓
10. Generate AI Fix
        ↓
11. Review Unified Diff
        ↓
12. Apply or Reject Changes
```

---

# 📡 API

The backend exposes API endpoints for application health, code review, remediation, and supporting analysis workflows.

## `GET /health`

Checks whether the backend is running.

Example:

```bash
curl http://127.0.0.1:8000/health
```

---

## `POST /review-code`

Reviews uploaded source code and returns structured findings.

The review workflow can incorporate:

- Static analysis
- AI analysis
- Finding normalization
- Severity classification
- Quality scoring

The selected AI provider/model is used for the AI portion of the review.

---

## `POST /fix-code`

Generates a proposed remediation based on source code and detected findings.

The resulting changes can be reviewed through the frontend's diff workflow before being applied.

> API request/response schemas may evolve as the project continues to be refined. The FastAPI documentation at `/docs` is the authoritative local API reference.

---

# 🧪 Testing

Backend tests are located under:

```text
backend/tests/
```

Run the backend test suite with:

```bash
PYTHONPATH=. pytest backend/tests -q
```

You can also perform a Python compilation check:

```bash
python -m compileall -q backend
```

For the frontend:

```bash
cd frontend
npm run test:ci
```

Build verification:

```bash
npm run build
```

Before making a release/final push, verify both the backend test suite and frontend build successfully.

---

# 🔐 Security

AI Code Enhancer uses environment variables for sensitive configuration.

Never commit:

```text
.env
```

or actual API credentials.

The repository should also exclude local development artifacts such as:

```text
.venv/
node_modules/
__pycache__/
.pytest_cache/
*.db
build/
dist/
```

API keys should only exist in the local environment or an appropriate secret-management system.

---

# 🎯 Current Project Scope

The current version focuses on **local repository analysis and AI-assisted code review**.

The project intentionally prioritizes:

- Code quality
- Repository intelligence
- Static analysis
- AI reasoning
- Gemini + Groq integration
- Quality scoring
- AI remediation
- Interactive review
- Clean project architecture
- Portfolio-quality implementation

The project is **not currently focused on deployment infrastructure or production CI/CD integration**.

---

# 🗺️ Development Status

The original development roadmap has now been consolidated into the current implementation.

### ✅ Completed

- Repository cleanup and project stabilization
- Environment-based configuration
- FastAPI backend
- React frontend
- Monaco Editor integration
- Multi-file code analysis
- Static analysis integration
- Structured AI responses
- Gemini integration
- Groq integration
- Repository analysis
- Dependency analysis
- Architecture analysis
- Finding normalization
- Code-quality scoring
- AI-powered remediation
- Unified diff workflow
- Interactive review/apply workflow
- Backend test coverage
- Frontend integration

### 🔄 Future Improvements

Potential future improvements may include:

- More advanced language-specific analyzers
- Improved architecture visualization
- More sophisticated remediation validation
- Expanded test coverage
- Additional repository-level intelligence
- Improved review UX
- Performance optimization for large repositories

These are optional improvements rather than required components of the current project.

---

# 📈 Why This Project?

Traditional static analysis tools are effective at detecting deterministic problems, while LLMs are capable of understanding broader context and suggesting higher-level improvements.

AI Code Enhancer combines both approaches:

```text
             Static Analysis
                    │
                    │ Deterministic Findings
                    │
                    ▼
              ┌───────────┐
              │           │
              │ Aggregator│
              │           │
              └─────┬─────┘
                    │
                    │
              AI Analysis
                    │
                    │ Contextual Reasoning
                    ▼
              Unified Review
                    │
                    ▼
              Quality Score
                    │
                    ▼
             AI Remediation
```

The result is a more comprehensive development workflow than either static analysis or an isolated AI code-review prompt alone.

---

# 🤝 Contributing

Contributions and improvements are welcome.

When contributing:

1. Keep changes focused.
2. Add tests for new functionality.
3. Avoid committing secrets.
4. Keep frontend/backend API contracts synchronized.
5. Document significant architectural changes.
6. Preserve the existing provider abstraction.
7. Verify the project locally before submitting changes.

---

# 📄 License

This project is currently maintained as an **AI engineering portfolio project**.

---

## 👨‍💻 Author

**Arjun Gupta**

GitHub:  
https://github.com/arjungupt771

Repository:  
https://github.com/arjungupt771/AI_Code_Enhancer