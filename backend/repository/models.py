"""Models used by repository-level analysis."""

from dataclasses import dataclass, field
from pathlib import Path


@dataclass(frozen=True)
class RepositoryFile:
    """A source file belonging to an analyzed repository."""

    path: Path
    content: str
    extension: str


@dataclass
class RepositoryAnalysis:
    """Repository-level statistics produced during analysis."""

    files: list[RepositoryFile] = field(
        default_factory=list
    )

    total_files: int = 0
    supported_files: int = 0

    language_counts: dict[str, int] = field(
        default_factory=dict
    )

    extension_counts: dict[str, int] = field(
        default_factory=dict
    )

    files_with_issues: int = 0
    total_issues: int = 0

    @property
    def analyzed_paths(self) -> list[str]:
        """Return normalized repository-relative paths."""

        return [
            file.path.as_posix()
            for file in self.files
        ]