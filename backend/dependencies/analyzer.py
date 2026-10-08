"""Repository dependency analyzer."""

from pathlib import Path

from .models import (
    DependencyAnalysis,
)
from .parsers import (
    parse_cargo_toml,
    parse_go_mod,
    parse_package_json,
    parse_pom_xml,
    parse_pyproject,
    parse_requirements,
)


PARSERS = {
    "requirements.txt": parse_requirements,
    "requirements-dev.txt": parse_requirements,
    "requirements-test.txt": parse_requirements,
    "package.json": parse_package_json,
    "pyproject.toml": parse_pyproject,
    "pom.xml": parse_pom_xml,
    "go.mod": parse_go_mod,
    "Cargo.toml": parse_cargo_toml,
}


class DependencyAnalyzer:
    """Detect and extract repository dependencies."""

    def analyze(
        self,
        files: list[tuple[Path, str]],
    ) -> DependencyAnalysis:
        manifests = []
        dependencies = []

        seen_manifests = set()

        for path, content in files:
            filename = path.name

            parser = PARSERS.get(filename)

            if parser is None:
                continue

            normalized_path = path.as_posix()

            if normalized_path in seen_manifests:
                continue

            seen_manifests.add(
                normalized_path
            )
            manifests.append(
                normalized_path
            )

            dependencies.extend(
                parser(
                    content,
                    normalized_path,
                )
            )

        # Deduplicate dependencies while
        # preserving manifest information.
        unique = []
        seen = set()

        for dependency in dependencies:
            key = (
                dependency.name.lower(),
                dependency.source_file,
                dependency.dependency_type,
            )

            if key in seen:
                continue

            seen.add(key)
            unique.append(dependency)

        return DependencyAnalysis(
            manifests_found=manifests,
            dependencies=unique,
        )