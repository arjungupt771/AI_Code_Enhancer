"""Models for repository dependency analysis."""

from dataclasses import dataclass


@dataclass(frozen=True)
class Dependency:
    """A normalized project dependency."""

    name: str
    version_spec: str | None
    source_file: str
    dependency_type: str


@dataclass
class DependencyAnalysis:
    """Repository dependency analysis result."""

    manifests_found: list[str]
    dependencies: list[Dependency]

    @property
    def dependency_count(self) -> int:
        return len(self.dependencies)

    @property
    def manifest_count(self) -> int:
        return len(self.manifests_found)

    @property
    def dependencies_by_type(
        self,
    ) -> dict[str, int]:
        counts: dict[str, int] = {}

        for dependency in self.dependencies:
            counts[dependency.dependency_type] = (
                counts.get(
                    dependency.dependency_type,
                    0,
                )
                + 1
            )

        return counts