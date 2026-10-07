from .base import Analyzer
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


__all__ = [
    "Analyzer",
    "AnalyzerRegistry",
    "JavaScriptAnalyzer",
    "PythonAnalyzer",
    "StaticFinding",
    "create_default_registry",
]