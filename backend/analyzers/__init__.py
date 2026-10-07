from .adapters import (
    static_finding_to_review_issue,
)
from .base import Analyzer
from .deduplication import deduplicate_findings
from .hybrid import HybridAnalyzer, HybridReviewResult
from .javascript import JavaScriptAnalyzer
from .models import StaticFinding
from .python import PythonAnalyzer
from .registry import AnalyzerRegistry


def create_default_registry() -> AnalyzerRegistry:
    return AnalyzerRegistry(
        [
            PythonAnalyzer(),
            JavaScriptAnalyzer(),
        ]
    )


def create_hybrid_analyzer() -> HybridAnalyzer:
    registry = create_default_registry()

    return HybridAnalyzer(
        registry.all()
    )


__all__ = [
    "Analyzer",
    "AnalyzerRegistry",
    "HybridAnalyzer",
    "HybridReviewResult",
    "JavaScriptAnalyzer",
    "PythonAnalyzer",
    "StaticFinding",
    "create_default_registry",
    "create_hybrid_analyzer",
    "deduplicate_findings",
    "static_finding_to_review_issue",
]