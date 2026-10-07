"""Application entry point for the local AI Code Enhancer API."""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from backend.api.routes import router
from backend.core_config import CORS_ORIGINS


app = FastAPI(
    title="AI Code Enhancer",
    description=(
        "Local AI-assisted code review "
        "and remediation API."
    ),
    version="1.1.0",
)


app.add_middleware(
    CORSMiddleware,
    allow_origins=CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["GET", "POST"],
    allow_headers=["*"],
)


app.include_router(router)