from pathlib import Path

from backend.analyzers import (
    StaticFinding,
    create_hybrid_analyzer,
    deduplicate_findings,
)


def test_hybrid_analyzer_runs_python_analysis():
    analyzer = create_hybrid_analyzer()

    findings = analyzer.analyze_file(
        Path("example.py"),
        """
import os

def hello():
    print("hello")
""",
    )

    assert isinstance(findings, list)
    assert any(
        finding.tool == "ruff"
        for finding in findings
    )


def test_hybrid_analyzer_runs_javascript_analysis():
    analyzer = create_hybrid_analyzer()

    findings = analyzer.analyze_file(
        Path("example.js"),
        """
const value = 1;
console.log(value);
""",
    )

    assert isinstance(findings, list)


def test_hybrid_analyzer_skips_unsupported_files():
    analyzer = create_hybrid_analyzer()

    findings = analyzer.analyze_file(
        Path("README.md"),
        "# Hello",
    )

    assert findings == []


def test_deduplication_removes_identical_findings():
    finding = StaticFinding(
        tool="ruff",
        rule_id="F401",
        message="Unused import",
        severity="error",
        category="bug",
        file_path="main.py",
        line=1,
    )

    duplicate = finding.model_copy()

    result = deduplicate_findings(
        [finding, duplicate]
    )

    assert len(result) == 1


def test_deduplication_preserves_different_findings():
    first = StaticFinding(
        tool="ruff",
        rule_id="F401",
        message="Unused import",
        severity="error",
        category="bug",
        file_path="main.py",
        line=1,
    )

    second = StaticFinding(
        tool="ruff",
        rule_id="F841",
        message="Unused variable",
        severity="error",
        category="bug",
        file_path="main.py",
        line=5,
    )

    result = deduplicate_findings(
        [first, second]
    )

    assert len(result) == 2