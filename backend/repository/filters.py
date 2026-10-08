"""Filtering and normalization helpers for repositories."""

from pathlib import PurePosixPath


IGNORED_DIRECTORIES = frozenset(
    {
        ".git",
        ".hg",
        ".svn",
        ".venv",
        "venv",
        "env",
        "node_modules",
        "__pycache__",
        ".pytest_cache",
        ".ruff_cache",
        ".mypy_cache",
        ".tox",
        ".idea",
        ".vscode",
        "dist",
        "build",
        "coverage",
        ".next",
        "out",
        "target",
        "vendor",
    }
)


SUPPORTED_EXTENSIONS = frozenset(
    {
        ".py",
        ".js",
        ".jsx",
        ".ts",
        ".tsx",
        ".java",
        ".cpp",
        ".c",
        ".h",
        ".hpp",
        ".cs",
        ".go",
        ".rs",
        ".php",
        ".rb",
        ".swift",
        ".kt",
        ".kts",
        ".sql",
        ".html",
        ".css",
        ".json",
        ".md",
    }
)


EXTENSION_LANGUAGE_MAP = {
    ".py": "Python",
    ".js": "JavaScript",
    ".jsx": "JavaScript",
    ".ts": "TypeScript",
    ".tsx": "TypeScript",
    ".java": "Java",
    ".cpp": "C++",
    ".c": "C",
    ".h": "C/C++",
    ".hpp": "C++",
    ".cs": "C#",
    ".go": "Go",
    ".rs": "Rust",
    ".php": "PHP",
    ".rb": "Ruby",
    ".swift": "Swift",
    ".kt": "Kotlin",
    ".kts": "Kotlin",
    ".sql": "SQL",
    ".html": "HTML",
    ".css": "CSS",
    ".json": "JSON",
    ".md": "Markdown",
}


def normalize_repository_path(
    path: str,
) -> str:
    """
    Normalize a repository-relative path.

    Rejects absolute paths and parent traversal while
    preserving legitimate nested directories.
    """

    normalized = path.replace("\\", "/").strip()

    if not normalized:
        raise ValueError(
            "Repository path cannot be empty."
        )

    pure_path = PurePosixPath(normalized)

    if pure_path.is_absolute():
        raise ValueError(
            "Repository path must be relative."
        )

    parts = pure_path.parts

    if ".." in parts:
        raise ValueError(
            "Repository path cannot contain '..'."
        )

    cleaned_parts = [
        part
        for part in parts
        if part not in {"", "."}
    ]

    if not cleaned_parts:
        raise ValueError(
            "Repository path cannot be empty."
        )

    return PurePosixPath(
        *cleaned_parts
    ).as_posix()


def is_ignored_path(
    path: str,
) -> bool:
    """Return whether a repository path belongs to an ignored directory."""

    normalized = path.replace(
        "\\",
        "/",
    )

    parts = PurePosixPath(
        normalized
    ).parts

    return any(
        part in IGNORED_DIRECTORIES
        for part in parts
    )


def is_supported_source(
    path: str,
) -> bool:
    """Return whether a repository path has a supported source extension."""

    extension = (
        PurePosixPath(path)
        .suffix
        .lower()
    )

    return extension in SUPPORTED_EXTENSIONS


def get_language_for_path(
    path: str,
) -> str:
    """Return the display language associated with a repository path."""

    extension = (
        PurePosixPath(path)
        .suffix
        .lower()
    )

    return EXTENSION_LANGUAGE_MAP.get(
        extension,
        "Unknown",
    )