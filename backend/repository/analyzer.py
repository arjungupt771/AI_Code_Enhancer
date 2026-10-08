"""Repository-level analysis orchestration."""

from collections import Counter
from pathlib import Path

from .filters import (
    get_language_for_path,
    is_ignored_path,
    is_supported_source,
    normalize_repository_path,
)
from .models import (
    RepositoryAnalysis,
    RepositoryFile,
)


class RepositoryAnalyzer:
    """
    Builds a normalized representation of an uploaded repository.

    This class intentionally does not perform static analysis itself.
    Static analysis remains the responsibility of HybridAnalyzer.
    """

    def analyze(
        self,
        files: list[tuple[Path, str]],
    ) -> RepositoryAnalysis:
        """Normalize and summarize repository source files."""

        repository_files: list[
            RepositoryFile
        ] = []

        seen_paths: set[str] = set()

        for file_path, content in files:
            normalized_path = normalize_repository_path(
                str(file_path)
            )

            if is_ignored_path(
                normalized_path
            ):
                continue

            if not is_supported_source(
                normalized_path
            ):
                continue

            if normalized_path in seen_paths:
                continue

            seen_paths.add(normalized_path)

            extension = (
                Path(normalized_path)
                .suffix
                .lower()
            )

            repository_files.append(
                RepositoryFile(
                    path=Path(
                        normalized_path
                    ),
                    content=content,
                    extension=extension,
                )
            )

        language_counts = Counter(
            get_language_for_path(
                file.path.as_posix()
            )
            for file in repository_files
        )

        extension_counts = Counter(
            file.extension
            for file in repository_files
        )

        return RepositoryAnalysis(
            files=repository_files,
            total_files=len(files),
            supported_files=len(
                repository_files
            ),
            language_counts=dict(
                sorted(
                    language_counts.items()
                )
            ),
            extension_counts=dict(
                sorted(
                    extension_counts.items()
                )
            ),
        )