from pathlib import Path

from analyzers import (
    JavaScriptAnalyzer,
    PythonAnalyzer,
    StaticFinding,
    create_default_registry,
)


def test_python_analyzer_supports_python_files():
    analyzer = PythonAnalyzer()

    assert analyzer.supports(Path("main.py"))
    assert not analyzer.supports(Path("main.js"))


def test_javascript_analyzer_supports_javascript_files():
    analyzer = JavaScriptAnalyzer()

    assert analyzer.supports(Path("app.js"))
    assert analyzer.supports(Path("component.tsx"))
    assert not analyzer.supports(Path("main.py"))


def test_registry_selects_python_analyzer():
    registry = create_default_registry()

    analyzers = registry.for_file(Path("main.py"))

    assert len(analyzers) == 1
    assert isinstance(analyzers[0], PythonAnalyzer)


def test_registry_selects_javascript_analyzer():
    registry = create_default_registry()

    analyzers = registry.for_file(Path("app.jsx"))

    assert len(analyzers) == 1
    assert isinstance(analyzers[0], JavaScriptAnalyzer)


def test_static_finding_defaults_to_static_source():
    finding = StaticFinding(
        tool="ruff",
        rule_id="F401",
        message="Unused import",
        severity="warning",
        category="bug",
        file_path="main.py",
        line=1,
    )

    assert finding.source == "static"