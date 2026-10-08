from pathlib import Path

from backend.dependencies import (
    DependencyAnalyzer,
)


def test_requirements_are_extracted():
    files = [
        (
            Path("requirements.txt"),
            """
            fastapi==0.115.0
            uvicorn>=0.30
            pytest
            # comment
            """,
        )
    ]

    result = DependencyAnalyzer().analyze(
        files
    )

    assert result.manifest_count == 1
    assert result.dependency_count == 3

    names = {
        dependency.name
        for dependency in result.dependencies
    }

    assert names == {
        "fastapi",
        "uvicorn",
        "pytest",
    }


def test_package_json_sections_are_extracted():
    files = [
        (
            Path("package.json"),
            """
            {
              "dependencies": {
                "react": "^18.3.0"
              },
              "devDependencies": {
                "jest": "^29.0.0"
              }
            }
            """,
        )
    ]

    result = DependencyAnalyzer().analyze(
        files
    )

    assert result.dependency_count == 2

    dependency_types = {
        dependency.name:
        dependency.dependency_type
        for dependency
        in result.dependencies
    }

    assert dependency_types["react"] == "runtime"
    assert dependency_types["jest"] == "development"


def test_pyproject_dependencies_are_extracted():
    files = [
        (
            Path("pyproject.toml"),
            """
            [project]
            dependencies = [
                "fastapi>=0.115",
                "pydantic>=2",
            ]
            """,
        )
    ]

    result = DependencyAnalyzer().analyze(
        files
    )

    assert result.dependency_count == 2


def test_maven_dependencies_are_extracted():
    files = [
        (
            Path("pom.xml"),
            """
            <dependencies>
              <dependency>
                <groupId>org.springframework</groupId>
                <artifactId>spring-core</artifactId>
                <version>6.1.0</version>
              </dependency>
            </dependencies>
            """,
        )
    ]

    result = DependencyAnalyzer().analyze(
        files
    )

    assert result.dependency_count == 1

    dependency = result.dependencies[0]

    assert (
        dependency.name
        == "org.springframework:spring-core"
    )

    assert (
        dependency.version_spec
        == "6.1.0"
    )


def test_unsupported_files_are_ignored():
    files = [
        (
            Path("README.md"),
            "# Project",
        ),
        (
            Path("main.py"),
            "print('hello')",
        ),
    ]

    result = DependencyAnalyzer().analyze(
        files
    )

    assert result.manifest_count == 0
    assert result.dependency_count == 0


def test_duplicate_manifest_paths_are_ignored():
    files = [
        (
            Path("requirements.txt"),
            "fastapi==0.115",
        ),
        (
            Path("requirements.txt"),
            "fastapi==0.115",
        ),
    ]

    result = DependencyAnalyzer().analyze(
        files
    )

    assert result.manifest_count == 1
    assert result.dependency_count == 1


def test_dependency_analysis_groups_dependency_types():
    files = [
        (
            Path("package.json"),
            """
            {
              "dependencies": {
                "react": "^18.3.0"
              },
              "devDependencies": {
                "jest": "^29.0.0",
                "eslint": "^9.0.0"
              }
            }
            """,
        )
    ]

    result = DependencyAnalyzer().analyze(
        files
    )

    assert result.dependencies_by_type == {
        "runtime": 1,
        "development": 2,
    }


def test_dependency_analysis_supports_multiple_manifests():
    files = [
        (
            Path("requirements.txt"),
            """
            fastapi>=0.115
            pydantic>=2
            """,
        ),
        (
            Path("package.json"),
            """
            {
              "dependencies": {
                "react": "^18.3.0"
              }
            }
            """,
        ),
    ]

    result = DependencyAnalyzer().analyze(
        files
    )

    assert result.manifest_count == 2
    assert result.dependency_count == 3

    assert set(
        result.manifests_found
    ) == {
        "requirements.txt",
        "package.json",
    }