"""Central configuration for the local AI Code Enhancer application."""

from dataclasses import dataclass
import os

from dotenv import load_dotenv

load_dotenv()

LOCAL_CORS_DEFAULTS = (
    "http://localhost:3000",
    "http://127.0.0.1:3000",
)

DEFAULT_MAX_FILE_SIZE = 2 * 1024 * 1024
DEFAULT_MAX_FILES = 100


def _parse_origins(value: str | None) -> tuple[str, ...]:
    if not value:
        return LOCAL_CORS_DEFAULTS

    origins = tuple(
        origin.strip()
        for origin in value.split(",")
        if origin.strip()
    )

    return origins or LOCAL_CORS_DEFAULTS


def _parse_positive_int(value: str | None, default: int) -> int:
    try:
        parsed = int(value or "")
    except (TypeError, ValueError):
        return default

    return parsed if parsed > 0 else default


@dataclass(frozen=True)
class Settings:
    gemini_api_key: str | None
    default_model: str
    cors_origins: tuple[str, ...]
    max_file_size_bytes: int
    max_files: int


settings = Settings(
    gemini_api_key=os.getenv("GEMINI_API_KEY"),
    default_model=(
        os.getenv("DEFAULT_MODEL", "gemini-2.5-flash").strip()
        or "gemini-2.5-flash"
    ),
    cors_origins=_parse_origins(
        os.getenv("CORS_ORIGINS")
    ),
    max_file_size_bytes=_parse_positive_int(
        os.getenv("MAX_FILE_SIZE_BYTES"),
        DEFAULT_MAX_FILE_SIZE,
    ),
    max_files=_parse_positive_int(
        os.getenv("MAX_FILES"),
        DEFAULT_MAX_FILES,
    ),
)


# Backward-compatible exports.
GEMINI_API_KEY = settings.gemini_api_key
DEFAULT_MODEL = settings.default_model
CORS_ORIGINS = list(settings.cors_origins)
MAX_FILE_SIZE_BYTES = settings.max_file_size_bytes
MAX_FILES = settings.max_files