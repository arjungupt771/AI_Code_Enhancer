"""Dependency manifest parsers."""

import json
import re
from pathlib import Path

from .models import Dependency


def _clean_name(name: str) -> str:
    return name.strip()


def _dependency(
    name: str,
    version_spec: str | None,
    source_file: str,
    dependency_type: str,
) -> Dependency:
    return Dependency(
        name=_clean_name(name),
        version_spec=(
            version_spec.strip()
            if version_spec
            else None
        ),
        source_file=source_file,
        dependency_type=dependency_type,
    )


def parse_requirements(
    content: str,
    source_file: str,
) -> list[Dependency]:
    """Parse standard Python requirements files."""

    dependencies = []

    for raw_line in content.splitlines():
        line = raw_line.strip()

        if not line or line.startswith("#"):
            continue

        if line.startswith((
            "-r ",
            "--requirement ",
            "-c ",
            "--constraint ",
            "--index-url",
            "--extra-index-url",
            "--trusted-host",
        )):
            continue

        line = line.split(" #", 1)[0].strip()

        match = re.match(
            r"^([A-Za-z0-9_.-]+)\s*(.*)$",
            line,
        )

        if not match:
            continue

        name, version_spec = match.groups()

        dependencies.append(
            _dependency(
                name,
                version_spec or None,
                source_file,
                "runtime",
            )
        )

    return dependencies


def parse_package_json(
    content: str,
    source_file: str,
) -> list[Dependency]:
    """Parse npm package.json dependencies."""

    try:
        data = json.loads(content)
    except json.JSONDecodeError:
        return []

    dependencies = []

    sections = (
        ("dependencies", "runtime"),
        ("devDependencies", "development"),
        ("peerDependencies", "peer"),
        ("optionalDependencies", "optional"),
    )

    for section, dependency_type in sections:
        values = data.get(section, {})

        if not isinstance(values, dict):
            continue

        for name, version in values.items():
            dependencies.append(
                _dependency(
                    name,
                    str(version),
                    source_file,
                    dependency_type,
                )
            )

    return dependencies

def parse_pyproject(
    content: str,
    source_file: str,
) -> list[Dependency]:
    """Parse PEP 621 dependencies from pyproject.toml."""

    dependencies = []

    in_project = False
    in_dependencies = False
    dependency_lines: list[str] = []

    for raw_line in content.splitlines():
        line = raw_line.strip()

        if line.startswith("["):
            if line == "[project]":
                in_project = True
            else:
                in_project = False

            if in_dependencies:
                dependency_lines.append("]")

            in_dependencies = False
            continue

        if not in_project:
            continue

        if not in_dependencies:
            if line.startswith("dependencies") and "=" in line:
                _, value = line.split(
                    "=",
                    1,
                )

                value = value.strip()

                if value.startswith("["):
                    in_dependencies = True
                    dependency_lines = [value]

                    if "]" in value:
                        in_dependencies = False
                continue

        else:
            dependency_lines.append(line)

            if "]" in line:
                in_dependencies = False

    # Parse the collected TOML array values.
    dependency_text = " ".join(
        dependency_lines
    )

    matches = re.findall(
        r'"([^"]+)"',
        dependency_text,
    )

    for dependency in matches:
        match = re.match(
            r"^([A-Za-z0-9_.-]+)\s*(.*)$",
            dependency,
        )

        if not match:
            continue

        name, version_spec = match.groups()

        dependencies.append(
            _dependency(
                name,
                version_spec or None,
                source_file,
                "runtime",
            )
        )

    return dependencies

def parse_pom_xml(
    content: str,
    source_file: str,
) -> list[Dependency]:
    """Parse Maven dependencies from pom.xml."""

    dependencies = []

    blocks = re.findall(
        r"<dependency>(.*?)</dependency>",
        content,
        flags=re.DOTALL,
    )

    for block in blocks:
        group_match = re.search(
            r"<groupId>\s*([^<]+)\s*</groupId>",
            block,
        )
        artifact_match = re.search(
            r"<artifactId>\s*([^<]+)\s*</artifactId>",
            block,
        )
        version_match = re.search(
            r"<version>\s*([^<]+)\s*</version>",
            block,
        )

        if not artifact_match:
            continue

        artifact = artifact_match.group(1).strip()

        if group_match:
            name = (
                f"{group_match.group(1).strip()}:"
                f"{artifact}"
            )
        else:
            name = artifact

        dependencies.append(
            _dependency(
                name,
                (
                    version_match.group(1).strip()
                    if version_match
                    else None
                ),
                source_file,
                "runtime",
            )
        )

    return dependencies


def parse_go_mod(
    content: str,
    source_file: str,
) -> list[Dependency]:
    """Parse Go module dependencies."""

    dependencies = []

    in_require_block = False

    for raw_line in content.splitlines():
        line = raw_line.strip()

        if line == "require (":
            in_require_block = True
            continue

        if in_require_block and line == ")":
            in_require_block = False
            continue

        if line.startswith("require ") or in_require_block:
            line = line.replace(
                "require ",
                "",
                1,
            ).strip()

            parts = line.split()

            if len(parts) >= 2:
                dependencies.append(
                    _dependency(
                        parts[0],
                        parts[1],
                        source_file,
                        "runtime",
                    )
                )

    return dependencies


def parse_cargo_toml(
    content: str,
    source_file: str,
) -> list[Dependency]:
    """Parse Cargo.toml dependencies."""

    dependencies = []

    in_dependencies = False

    for raw_line in content.splitlines():
        line = raw_line.strip()

        if line.startswith("["):
            in_dependencies = (
                line == "[dependencies]"
                or line.startswith(
                    "[dependencies."
                )
            )
            continue

        if not in_dependencies or "=" not in line:
            continue

        name, value = line.split(
            "=",
            1,
        )

        name = name.strip()

        if not re.match(
            r"^[A-Za-z0-9_-]+$",
            name,
        ):
            continue

        value = value.strip()

        if value.startswith('"'):
            version = value.strip('"')
        else:
            version_match = re.search(
                r'version\s*=\s*"([^"]+)"',
                value,
            )
            version = (
                version_match.group(1)
                if version_match
                else None
            )

        dependencies.append(
            _dependency(
                name,
                version,
                source_file,
                "runtime",
            )
        )

    return dependencies