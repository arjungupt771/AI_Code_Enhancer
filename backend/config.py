"""Backward-compatible configuration exports."""

from core_config import (
    CORS_ORIGINS,
    DEFAULT_MODEL,
    GEMINI_API_KEY,
    MAX_FILE_SIZE_BYTES,
)

__all__ = [
    "CORS_ORIGINS",
    "DEFAULT_MODEL",
    "GEMINI_API_KEY",
    "MAX_FILE_SIZE_BYTES",
]