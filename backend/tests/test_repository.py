from pathlib import Path

import pytest

from backend.repository import (
    RepositoryAnalyzer,
)
from backend.repository.filters import (
    get_language_for_path,
    is_ignored_path,
    is_supported_source,
    normalize_repository_path,
)


def test_normalize_nested_repository_path():
    result = normalize_repository_path(
        "src/utils/helpers.py"
    )

    assert result == (
        "src/utils/helpers.py"
    )


def test_normalize_windows_path():
    result = normalize_repository_path(
        r"src\utils\helpers.py"
    )

    assert result == (
        "src/utils/helpers.py"
    )


def test_reject_absolute_repository_path():
    with pytest.raises(ValueError):
        normalize_repository_path(
            "/tmp/project/main.py"
        )


def test_reject_parent_traversal():
    with pytest.raises(ValueError):
        normalize_repository_path(
            "../main.py"
        )


def test_ignore_node_modules():
    assert is_ignored_path(
        "frontend/node_modules/react/index.js"
    )


def test_ignore_git_directory():
    assert is_ignored_path(
        ".git/config"
    )


def test_do_not_ignore_source_directory():
    assert not is_ignored_path(
        "src/components/App.jsx"
    )


def test_supported_python_file():
    assert is_supported_source(
        "backend/main.py"
    )


def test_supported_typescript_file():
    assert is_supported_source(
        "frontend/src/App.tsx"
    )


def test_unsupported_binary_file():
    assert not is_supported_source(
        "assets/logo.png"
    )


def test_language_detection():
    assert (
        get_language_for_path(
            "backend/main.py"
        )
        == "Python"
    )

    assert (
        get_language_for_path(
            "frontend/src/App.tsx"
        )
        == "TypeScript"
    )


def test_repository_analyzer_filters_and_summarizes():
    analyzer = RepositoryAnalyzer()

    result = analyzer.analyze(
        [
            (
                Path(
                    "backend/main.py"
                ),
                "print('hello')",
            ),
            (
                Path(
                    "frontend/src/App.jsx"
                ),
                "export default App;",
            ),
            (
                Path(
                    "frontend/node_modules/pkg/index.js"
                ),
                "ignored",
            ),
            (
                Path(
                    "assets/logo.png"
                ),
                "ignored",
            ),
        ]
    )

    assert result.total_files == 4
    assert result.supported_files == 2

    assert result.analyzed_paths == [
        "backend/main.py",
        "frontend/src/App.jsx",
    ]

    assert result.language_counts == {
        "JavaScript": 1,
        "Python": 1,
    }

    assert result.extension_counts == {
        ".jsx": 1,
        ".py": 1,
    }


def test_repository_analyzer_deduplicates_paths():
    analyzer = RepositoryAnalyzer()

    result = analyzer.analyze(
        [
            (
                Path("main.py"),
                "print(1)",
            ),
            (
                Path("main.py"),
                "print(2)",
            ),
        ]
    )

    assert result.supported_files == 1

    assert result.analyzed_paths == [
        "main.py"
    ]