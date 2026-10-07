

from pathlib import PurePath

from fastapi import HTTPException, UploadFile

from core_config import MAX_FILE_SIZE_BYTES, MAX_FILES


ALLOWED_EXTENSIONS = frozenset(
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


def validate_filename(filename: str) -> str:
    """Validate and normalize a browser-supplied source filename."""

    if not filename:
        raise HTTPException(
            status_code=400,
            detail="Uploaded file must have a filename.",
        )

    # Reject Windows-style path separators.
    if "\\" in filename:
        raise HTTPException(
            status_code=400,
            detail="Invalid filename.",
        )

    safe_name = PurePath(filename).name

    if safe_name != filename or filename in {".", ".."}:
        raise HTTPException(
            status_code=400,
            detail="Invalid filename.",
        )

    extension = PurePath(filename).suffix.lower()

    if not extension:
        raise HTTPException(
            status_code=400,
            detail=f"File '{filename}' has no extension.",
        )

    if extension not in ALLOWED_EXTENSIONS:
        raise HTTPException(
            status_code=400,
            detail=f"Unsupported file type '{extension}'.",
        )

    return filename


async def read_source_file(
    uploaded_file: UploadFile,
) -> tuple[str, str]:
    """Read one UTF-8 source file within the local size limit."""

    filename = validate_filename(
        uploaded_file.filename or ""
    )

    content = await uploaded_file.read(
        MAX_FILE_SIZE_BYTES + 1
    )

    if len(content) > MAX_FILE_SIZE_BYTES:
        raise HTTPException(
            status_code=413,
            detail=(
                f"File '{filename}' exceeds the local "
                f"size limit of "
                f"{MAX_FILE_SIZE_BYTES // 1024} KB."
            ),
        )

    try:
        decoded = content.decode("utf-8")
    except UnicodeDecodeError as exc:
        raise HTTPException(
            status_code=400,
            detail=f"File '{filename}' is not valid UTF-8 text.",
        ) from exc

    if not decoded.strip():
        raise HTTPException(
            status_code=400,
            detail=f"File '{filename}' is empty.",
        )

    return filename, decoded


def validate_file_count(
    files: list[UploadFile],
) -> None:
    """Keep local review requests within a reasonable size."""

    if len(files) > MAX_FILES:
        raise HTTPException(
            status_code=413,
            detail=(
                f"A maximum of {MAX_FILES} "
                "files can be reviewed at once."
            ),
        )