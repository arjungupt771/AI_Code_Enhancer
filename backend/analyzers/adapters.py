"""Conversion functions between different finding representations."""

from .models import StaticFinding


def static_finding_to_review_issue(
    finding: StaticFinding,
) -> dict:
    """Convert a StaticFinding to a ReviewIssue dict.
    
    Args:
        finding: A StaticFinding from static analysis.
        
    Returns:
        A dictionary compatible with ReviewIssue schema.
    """
    return {
        "source": "static",
        "tool": finding.tool,
        "rule_id": finding.rule_id,
        "severity": finding.severity,
        "category": finding.category,
        "message": finding.message,
        "file_path": finding.file_path,
        "line": finding.line,
        "column": finding.column,
        "suggestion": finding.suggestion,
    }
